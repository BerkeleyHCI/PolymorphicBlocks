"""Verified LED-buck topology, bounded real routing, and cached scene rollback."""

from __future__ import annotations
from typing import Any, Mapping, Optional
from .KiCadSchematicTypes import Point, PinKey, PinNets, Placement, Placements, Views, RouteResult
from .KiCadSchematicExporter import PhysicalComponent, SymbolView, SchematicExport

import copy
import hashlib
from .KiCadSchematicCircuits import SchematicCircuit, CircuitStage
from .KiCadSchematicExporter import SymbolResolver
from .KiCadSchematicRouting import Router
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from .test_schematic_functional_placement import part, passive_view
from .KiCadSchematicExporter import (
    KiCadSchematicExporter,
    SchematicExportOptions,
    SchematicPlacement,
    generic,
    _PreparedBoard,
    _RegionDrawing,
)
from .KiCadSchematicLayout import freeze_annotations, route_local
from .KiCadSchematicPlanner import SchematicRegion
from .KiCadSchematicPower import (
    led_buck_topology,
    led_buck_candidates,
    compare_led_buck_variants,
    power_template,
)
from .KiCadSchematicOrientation import passive_orientation_rank

MODEL = "edg.parts.power.LedDriver_Tps92200.Tps92200_Device"


def led_buck_fixture() -> (
    tuple[tuple[str, ...], dict[str, PhysicalComponent], dict[str, SymbolView], dict[PinKey, str]]
):
    roles = {"1": "fb", "2": "dim", "3": "gnd", "4": "vin", "5": "sw", "6": "boot"}
    ic = part("driver.ic", roles)
    ic.hierarchy = ((ic.path, MODEL),)
    parts = {ic.path: ic}
    views = {ic.path: generic(ic)}
    nets = {(ic.path, n): role for n, role in roles.items()}
    for path, lib_id, terminals in (
        ("bootstrap", "Device:C", ("boot", "sw")),
        ("sense", "Device:R", ("gnd", "fb")),
        ("coil", "Device:L", ("sw", "out")),
        ("input_cap", "Device:C", ("vin", "gnd")),
        ("output_cap", "Device:C", ("out", "gnd")),
    ):
        parts[path] = part(path, {"1": "a", "2": "b"}, lib_id)
        views[path] = passive_view(lib_id)
        nets[path, "1"], nets[path, "2"] = terminals
    # Physical cathode terminal outside this region witnesses the LED load.
    nets["led_connector", "2"] = "fb"
    return tuple(sorted(parts)), parts, views, nets


def incumbent(parts: Mapping[str, PhysicalComponent], views: Views, nets: PinNets) -> list[Placement]:
    entries = power_template(tuple(sorted(parts)), parts, views, nets)
    assert entries is not None
    return freeze_annotations([(c, x + 180, y + 100, a) for c, x, y, a in entries], views)


class LedBuckTopologyTest(unittest.TestCase):
    def test_verified_bootstrap_sense_banks_and_return_witness(self) -> None:
        members, parts, views, nets = led_buck_fixture()
        t, reason = led_buck_topology(members, parts, views, nets)
        self.assertIsNone(reason)
        assert t is not None
        self.assertEqual((t["bootstrap"], t["sense"], t["coil"]), ("bootstrap", "sense", "coil"))
        self.assertEqual(t["input_caps"], ["input_cap"])
        self.assertEqual(t["output_caps"], ["output_cap"])
        self.assertEqual(t["load_return_witnesses"], [("led_connector", "2")])
        self.assertEqual(t["boot"], "boot")

    def test_similar_roles_on_unverified_model_do_not_select_template(self) -> None:
        members, parts, views, nets = led_buck_fixture()
        parts["driver.ic"].hierarchy = (("driver.ic", "custom.Tps92200_Lookalike"),)
        self.assertEqual(led_buck_topology(members, parts, views, nets), (None, None))

    def test_unique_bootstrap_and_sense_are_required(self) -> None:
        for original in ("bootstrap", "sense"):
            with self.subTest(original=original):
                members, parts, views, nets = led_buck_fixture()
                duplicate = copy.deepcopy(parts[original])
                duplicate.path = original + "_duplicate"
                parts[duplicate.path] = duplicate
                views[duplicate.path] = views[original]
                for n in duplicate.pins:
                    nets[duplicate.path, n] = nets[original, n]
                t, reason = led_buck_topology(tuple(sorted(parts)), parts, views, nets)
                self.assertIsNone(t)
                assert reason is not None
                self.assertIn("ambiguous", reason)

    def test_virtual_load_is_allowed_but_terminal_nets_must_be_distinct(self) -> None:
        members, parts, views, nets = led_buck_fixture()
        del nets["led_connector", "2"]
        topology, reason = led_buck_topology(members, parts, views, nets)
        self.assertIsNone(reason)
        assert topology is not None
        self.assertEqual(topology["load_return_witnesses"], [])
        nets["driver.ic", "6"] = "sw"
        reason = led_buck_topology(members, parts, views, nets)[1]
        assert reason is not None
        self.assertIn("not distinct", reason)

    def test_parallel_modeled_pads_preserve_identity_and_must_agree(self) -> None:
        members, parts, views, nets = led_buck_fixture()
        parts["driver.ic"].pins["7"] = "sw"
        nets["driver.ic", "7"] = "sw"
        t, reason = led_buck_topology(members, parts, views, nets)
        assert t is not None
        self.assertIsNone(reason)
        before = copy.deepcopy(parts["driver.ic"].pins)
        for _, entries in led_buck_candidates(t, parts, views, nets):
            self.assertEqual(next(c.pins for c, _, _, _ in entries if c.path == "driver.ic"), before)
        nets["driver.ic", "7"] = "different"
        reason = led_buck_topology(members, parts, views, nets)[1]
        assert reason is not None
        self.assertIn("roles do not match", reason)

    def test_authored_stages_and_nonconverter_templates_take_precedence(self) -> None:
        for template, stages in (("generic", ()), ("auto", ("stage",))):
            members, parts, views, nets = led_buck_fixture()
            parts["driver.ic"].functional_circuit = SchematicCircuit(
                "test",
                "Test",
                "Test",
                members,
                template=template,
                stages=tuple(CircuitStage(stage, members) for stage in stages),
            )
            reason = led_buck_topology(members, parts, views, nets)[1]
            assert reason is not None
            self.assertIn("take precedence", reason)

    def test_candidates_are_finite_deterministic_complete_and_preserve_inputs(self) -> None:
        args = led_buck_fixture()
        t, _ = led_buck_topology(*args)
        assert t is not None
        before = copy.deepcopy(args)
        candidates = led_buck_candidates(t, *args[1:])
        self.assertEqual(candidates, led_buck_candidates(t, *args[1:]))
        self.assertEqual(len(candidates), 4)
        for _, entries in candidates:
            self.assertEqual({c.path for c, _, _, _ in entries}, set(args[0]))
            positions = {c.path: (x, y, a) for c, x, y, a in entries}
            self.assertLess(positions["driver.ic"][0], positions["bootstrap"][0])
            self.assertLess(positions["bootstrap"][0], positions["coil"][0])
            self.assertLess(positions["sense"][0], positions["driver.ic"][0])
        self.assertEqual(args[3], before[3])
        self.assertEqual({p: c.pins for p, c in args[1].items()}, {p: c.pins for p, c in before[1].items()})


class LedBuckRoutingTest(unittest.TestCase):
    def compare(
        self, router: Router = route_local, *, source_annotations: Optional[Mapping[str, Optional[Point]]] = None
    ) -> tuple[list[Placement], RouteResult, tuple[list[Placement], RouteResult, dict[str, Any]]]:
        members, parts, views, nets = led_buck_fixture()
        placed = incumbent(parts, views, nets)
        baseline = route_local(placed, views, nets)
        selected, route, evidence = compare_led_buck_variants(
            placed, views, nets, baseline, router, source_annotations=source_annotations
        )
        assert evidence is not None
        return placed, baseline, (selected, route, evidence)

    def test_real_routes_reduce_crossings_and_weighted_cost_without_fallbacks(self) -> None:
        seen = []

        def router(placed: Placements, views: Views, pin_nets: PinNets, *, strategy: str = "baseline") -> RouteResult:
            seen.append(placed)
            return route_local(placed, views, pin_nets, strategy=strategy)

        placed, baseline, (selected, route, evidence) = self.compare(router)
        self.assertTrue(evidence["accepted"])
        self.assertEqual(len(evidence["trials"]), 4)
        self.assertLessEqual(evidence["route_trials"], 4)
        self.assertGreater(evidence["route_trials"], 0)
        self.assertEqual(len(seen), evidence["route_trials"])
        self.assertLess(evidence["after"]["crossings"], evidence["before"]["crossings"])
        self.assertLess(
            evidence["after"]["length_mm"] + 2.54 * evidence["after"]["bends"],
            evidence["before"]["length_mm"] + 2.54 * evidence["before"]["bends"],
        )
        self.assertEqual(route[2], [])
        self.assertEqual({c.path: c.pins for c, _, _, _ in placed}, {c.path: c.pins for c, _, _, _ in selected})
        _, _, repeated = self.compare()
        self.assertEqual(evidence, repeated[2])

    def test_every_candidate_keeps_authored_field_coordinates(self) -> None:
        seen = []

        def router(placed: Placements, views: Views, pin_nets: PinNets, *, strategy: str = "baseline") -> RouteResult:
            seen.append(placed)
            return route_local(placed, views, pin_nets, strategy=strategy)

        authored = {"sense": (25.4, 50.8)}
        self.compare(router, source_annotations=authored)
        self.assertTrue(seen)
        for entries in seen:
            self.assertEqual(next(c.annotation for c, _, _, _ in entries if c.path == "sense"), authored["sense"])

    def test_new_failed_endpoints_retain_cached_incumbent(self) -> None:
        def router(placed: Placements, views: Views, pin_nets: PinNets, *, strategy: str = "baseline") -> RouteResult:
            wires, endpoints, failed = route_local(placed, views, pin_nets, strategy=strategy)
            return wires, endpoints, failed + [(("driver.ic", "6"), "boot")]

        placed, baseline, (selected, route, evidence) = self.compare(router)
        self.assertIs(selected, placed)
        self.assertIs(route, baseline)
        self.assertFalse(evidence["accepted"])
        self.assertEqual(len(evidence["trials"]), 4)
        self.assertLessEqual(evidence["route_trials"], 4)
        routed = [t for t in evidence["trials"] if "metrics" in t]
        self.assertEqual(len(routed), evidence["route_trials"])
        self.assertTrue(routed)
        self.assertTrue(all(t["reason"] == "new failed endpoints" for t in routed))

    def test_collision_rejection_does_not_call_router(self) -> None:
        clean = dict(escape_conflicts=0, collisions=0, collision_pairs=[], clipped=False)
        collision = dict(clean, collisions=1, collision_pairs=[("sense", "driver.ic")])
        router = Mock(side_effect=AssertionError("colliding candidate must not route"))
        with patch("edg.electronics_model.KiCadSchematicOrientation._geometry", side_effect=[clean] + [collision] * 4):
            placed, baseline, (selected, route, evidence) = self.compare(router)
        self.assertIs(selected, placed)
        self.assertIs(route, baseline)
        self.assertEqual(evidence["route_trials"], 0)
        self.assertTrue(all("collision" in t["reason"] for t in evidence["trials"]))

    def test_ties_retain_incumbent_after_complete_bounded_coverage(self) -> None:
        metric = dict(
            primary_fallbacks=0, crossings=0, unrelated_intrusions=0, length_mm=100, bends=1, visual_conflicts=0
        )
        with patch("edg.electronics_model.KiCadSchematicOrientation.orientation_metrics", return_value=metric):
            placed, baseline, (selected, route, evidence) = self.compare()
        self.assertIs(selected, placed)
        self.assertIs(route, baseline)
        self.assertEqual(len(evidence["trials"]), 4)
        self.assertLessEqual(evidence["route_trials"], 4)
        self.assertGreater(evidence["route_trials"], 0)
        self.assertFalse(evidence["accepted"])


class LedBuckSceneGateTest(unittest.TestCase):
    def prepared(self) -> tuple[_PreparedBoard, _RegionDrawing]:
        _, parts, views, nets = led_buck_fixture()
        placed = incumbent(parts, views, nets)
        route = route_local(placed, views, nets)
        spec = SchematicRegion("region", "LED driver", "(root)", tuple(parts), (0, 0, 180, 100))
        drawing = _RegionDrawing(
            spec, placed, route[0], route[2], {"selected": "baseline"}, (), (), route, {p: None for p in parts}
        )
        board = _PreparedBoard(
            "(root)",
            "board_fixture",
            "root_fixture",
            views,
            nets,
            {net: net for net in nets.values()},
            {"region": drawing},
        )
        return board, drawing

    def test_authored_placements_are_not_moved_even_when_rotation_is_unlocked(self) -> None:
        board, drawing = self.prepared()
        options = SchematicExportOptions(
            "fixture", placements={"driver.ic": SchematicPlacement("LED driver", 150, 100, lock_rotation=False)}
        )
        exporter = KiCadSchematicExporter()
        with patch.object(
            exporter, "_serialize_prepared", side_effect=AssertionError("locked region must not serialize")
        ):
            boards, fingerprint = exporter._prepare_led_bucks(
                [board], "fingerprint", hashlib.sha256(b"prefix"), SymbolResolver(()), [], options
            )
        self.assertIs(boards[0].regions["region"], drawing)
        self.assertEqual(fingerprint, "fingerprint")
        self.assertEqual(drawing.routing["led_buck"]["route_trials"], 0)
        self.assertIn("authored placements", drawing.routing["led_buck"]["reason"])

    def test_new_serialized_finding_rolls_back_exact_cached_region(self) -> None:
        board, drawing = self.prepared()
        exporter = KiCadSchematicExporter()
        options = SchematicExportOptions("fixture", optimize_routes=False)
        baseline_bundle = SchematicExport({"board_fixture.kicad_sch": ""}, [])
        candidate_bundle = SchematicExport({"board_fixture.kicad_sch": ""}, [])

        def findings(bundle: SchematicExport) -> dict[str, dict[tuple[str, ...], float]]:
            return {
                "(root)": {} if bundle is baseline_bundle else {("text_body_contact", "sense:Value", "driver.ic"): 1.0}
            }

        with (
            patch.object(exporter, "_serialize_prepared", side_effect=[baseline_bundle, candidate_bundle]) as serialize,
            patch.object(exporter, "_passive_scene_issues", side_effect=findings),
            patch.object(exporter, "_prepared_fingerprint", return_value="candidate_fingerprint"),
            patch.object(exporter, "_region_geometry", return_value=((0, 0, 180, 100), (), ())),
        ):
            boards, fingerprint = exporter._prepare_led_bucks(
                [board], "fingerprint", hashlib.sha256(b"prefix"), SymbolResolver(()), [], options
            )
        self.assertEqual(serialize.call_count, 2)
        self.assertIs(boards[0].regions["region"], drawing)
        self.assertEqual(fingerprint, "fingerprint")
        evidence = drawing.routing["led_buck"]
        self.assertFalse(evidence["accepted"])
        self.assertEqual(evidence["after"], evidence["before"])
        self.assertIn("serialized scene", evidence["rollback_reason"])
        self.assertIn("attempted_after", evidence)

    def test_successful_serialized_gate_keeps_selected_region(self) -> None:
        board, drawing = self.prepared()
        exporter = KiCadSchematicExporter()
        options = SchematicExportOptions("fixture", optimize_routes=False)
        with (
            patch.object(
                exporter, "_serialize_prepared", return_value=SchematicExport({"board_fixture.kicad_sch": ""}, [])
            ),
            patch.object(exporter, "_passive_scene_issues", return_value={"(root)": {}}),
            patch.object(exporter, "_prepared_fingerprint", return_value="candidate_fingerprint"),
            patch.object(exporter, "_region_geometry", return_value=((0, 0, 160, 90), (), ())),
        ):
            boards, fingerprint = exporter._prepare_led_bucks(
                [board], "fingerprint", hashlib.sha256(b"prefix"), SymbolResolver(()), [], options
            )
        selected = boards[0].regions["region"]
        self.assertIsNot(selected, drawing)
        self.assertTrue(selected.routing["led_buck"]["accepted"])
        self.assertEqual(selected.routing["led_buck"]["content_bounds"], (0, 0, 160, 90))
        self.assertEqual(selected.spec.bounds, drawing.spec.bounds)
        from .KiCadSchematicRouting import route_metrics

        self.assertEqual(selected.routing["after"], route_metrics(selected.wires, selected.failed_routes))
        self.assertEqual(fingerprint, "candidate_fingerprint")
        self.assertEqual(selected.spec.components, drawing.spec.components)
        self.assertLess(
            passive_orientation_rank(selected.routing["led_buck"]["after"]),
            passive_orientation_rank(selected.routing["led_buck"]["before"]),
        )

    def test_more_sheets_roll_back_even_when_serialized_scene_is_clean(self) -> None:
        board, drawing = self.prepared()
        exporter = KiCadSchematicExporter()
        baseline_bundle = SchematicExport({"board_fixture.kicad_sch": ""}, [])
        candidate_bundle = SchematicExport(
            {"board_fixture.kicad_sch": "", "board_fixture_continuation.kicad_sch": ""}, []
        )
        with (
            patch.object(exporter, "_serialize_prepared", side_effect=[baseline_bundle, candidate_bundle]),
            patch.object(exporter, "_passive_scene_issues", return_value={"(root)": {}}),
            patch.object(exporter, "_prepared_fingerprint", return_value="candidate_fingerprint"),
            patch.object(exporter, "_region_geometry", return_value=((0, 0, 180, 100), (), ())),
        ):
            boards, fingerprint = exporter._prepare_led_bucks(
                [board],
                "fingerprint",
                hashlib.sha256(b"prefix"),
                SymbolResolver(()),
                [],
                SchematicExportOptions("fixture", optimize_routes=False),
            )
        self.assertIs(boards[0].regions["region"], drawing)
        self.assertEqual(fingerprint, "fingerprint")
        evidence = drawing.routing["led_buck"]
        self.assertFalse(evidence["accepted"])
        self.assertIn("fragmentation", evidence["rollback_reason"])
        self.assertEqual(evidence["scene_gate"]["before_sheets"], 1)
        self.assertEqual(evidence["scene_gate"]["after_sheets"], 2)

    def test_route_order_baseline_retains_incumbent_strategy_and_final_metrics(self) -> None:
        from .KiCadSchematicRouting import route_metrics

        board, drawing = self.prepared()
        drawing.routing["selected"] = "tree_search"
        exporter = KiCadSchematicExporter()

        def keep_supplied_route(
            entries: Placements, views: Views, nets: PinNets, route: RouteResult, router: Router
        ) -> tuple[RouteResult, dict[str, str]]:
            return route, {"selected": "baseline"}

        with (
            patch.object(
                exporter, "_serialize_prepared", return_value=SchematicExport({"board_fixture.kicad_sch": ""}, [])
            ),
            patch.object(exporter, "_passive_scene_issues", return_value={"(root)": {}}),
            patch.object(exporter, "_prepared_fingerprint", return_value="candidate_fingerprint"),
            patch.object(exporter, "_region_geometry", return_value=((0, 0, 180, 100), (), ())),
            patch(
                "edg.electronics_model.KiCadSchematicRouting.optimize_fixed_routes", side_effect=keep_supplied_route
            ) as order,
        ):
            boards, _ = exporter._prepare_led_bucks(
                [board],
                "fingerprint",
                hashlib.sha256(b"prefix"),
                SymbolResolver(()),
                [],
                SchematicExportOptions("fixture"),
            )
        selected = boards[0].regions["region"]
        self.assertTrue(selected.routing["led_buck"]["accepted"])
        self.assertEqual(order.call_count, 1)
        self.assertEqual(selected.routing["selected"], "tree_search")
        self.assertEqual(selected.routing["after"], route_metrics(selected.wires, selected.failed_routes))


if __name__ == "__main__":
    unittest.main()
