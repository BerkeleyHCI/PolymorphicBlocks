"""Measured bridge proposals preserve terminal identity and disclose failures."""

from typing import Any, Mapping
from .KiCadSchematicTypes import PinKey, Placements, Placement, Views, PinNets, Bounds, RouteResult
from .KiCadSchematicExporter import PhysicalComponent, SymbolView
from .KiCadSchematicCircuits import SchematicCircuit
import unittest
from unittest.mock import patch

from .test_schematic_functional_placement import part, passive_view
from .KiCadSchematicExporter import generic
from .KiCadSchematicPower import power_template_candidates


def bridge() -> tuple[tuple[str, ...], dict[str, PhysicalComponent], dict[str, SymbolView], dict[PinKey, str]]:
    ic = part(
        "controller",
        {str(i): role for i, role in enumerate(("gnd", "sw1", "sw2", "hidrv1", "hidrv2", "lodrv1", "lodrv2"))},
    )
    coil = part("coil", {"1": "sw1", "2": "sw2"}, "Device:L")
    parts = [ic, coil]
    nets = {(ic.path, n): role for n, role in ic.pins.items()}
    nets.update({("coil", "1"): "sw1", ("coil", "2"): "sw2"})
    for i in (1, 2):
        hi = part("hi%d" % i, {"1": "gate", "2": "source", "3": "drain"})
        lo = part("lo%d" % i, {"1": "gate", "2": "source", "3": "drain"})
        parts.extend((hi, lo))
        nets.update(
            {
                (hi.path, "1"): "hidrv%d" % i,
                (hi.path, "2"): "sw%d" % i,
                (hi.path, "3"): "rail%d" % i,
                (lo.path, "1"): "lodrv%d" % i,
                (lo.path, "2"): "gnd",
                (lo.path, "3"): "sw%d" % i,
            }
        )
    by_path = {c.path: c for c in parts}
    views = {c.path: generic(c) for c in parts}
    views["coil"] = passive_view("Device:L")
    return tuple(sorted(by_path)), by_path, views, nets


class BridgeVariantTest(unittest.TestCase):
    def test_verified_topology_marks_switch_gate_and_both_rail_paths_primary(self) -> None:
        from .KiCadSchematicPower import topology_primary_nets

        members, by_path, views, nets = bridge()
        primary = topology_primary_nets(list(by_path.values()), views, nets)
        self.assertEqual(primary, {"sw1", "sw2", "rail1", "rail2", "hidrv1", "hidrv2", "lodrv1", "lodrv2"})
        self.assertNotIn("gnd", primary)
        # A gate-like spelling without the required physical connection is
        # insufficient to classify any of the topology as a converter.
        nets["hi1", "1"] = "hidrv1_looks_similar"
        self.assertFalse(topology_primary_nets(list(by_path.values()), views, nets))

    def test_primary_shunt_outer_rail_requires_its_real_ground_bank(self) -> None:
        from .KiCadSchematicPower import topology_primary_nets

        members, by_path, views, nets = bridge()
        for path, netlist in (
            ("shunt", ("rail1", "external")),
            ("local_bank", ("rail1", "gnd")),
            ("outer_bank", ("external", "gnd")),
        ):
            lib = "Device:R" if path == "shunt" else "Device:C"
            component = part(path, {"1": "a", "2": "b"}, lib)
            by_path[path] = component
            views[path] = passive_view(lib)
            nets.update({(path, "1"): netlist[0], (path, "2"): netlist[1]})
        self.assertIn("external", topology_primary_nets(list(by_path.values()), views, nets))
        nets["outer_bank", "2"] = "unrelated"
        self.assertNotIn("external", topology_primary_nets(list(by_path.values()), views, nets))

    def test_primary_endpoints_exclude_rail_banks_and_include_inductor(self) -> None:
        from .KiCadSchematicPower import topology_primary_endpoints

        members, by_path, views, nets = bridge()
        cap = part("rail_bank", {"1": "a", "2": "b"}, "Device:C")
        by_path[cap.path] = cap
        views[cap.path] = passive_view("Device:C")
        nets.update({("rail_bank", "1"): "rail1", ("rail_bank", "2"): "gnd"})
        endpoints = topology_primary_endpoints(list(by_path.values()), nets, views)
        self.assertIn(("coil", "2"), endpoints["sw2"])
        self.assertIn(("hi1", "3"), endpoints["rail1"])
        self.assertNotIn(("rail_bank", "1"), endpoints["rail1"])
        self.assertNotIn("gnd", endpoints)

    def test_driver_supply_bypass_avoids_controller_label_corridors(self) -> None:
        from .KiCadSchematicLayout import pins

        members, by_path, views, nets = bridge()
        controller = by_path["controller"]
        controller.pins["8"] = "regn"
        views["controller"] = generic(controller)
        nets["controller", "8"] = "driver_supply"
        cap = part("anonymous_bypass", {"1": "a", "2": "b"}, "Device:C")
        by_path[cap.path] = cap
        views[cap.path] = passive_view("Device:C")
        nets.update({("anonymous_bypass", "1"): "driver_supply", ("anonymous_bypass", "2"): "gnd"})
        from .KiCadSchematicPlacement import packing_bounds, atom_bounds

        def measured(entries: Placements, views: Views, nets: PinNets) -> Bounds:
            return packing_bounds(entries, views, nets) if len(entries) == 1 else (0, 0, 100, 100)

        with (
            patch("edg.electronics_model.KiCadSchematicPlacement._score", return_value=(0, 0, 0, 0)),
            patch("edg.electronics_model.KiCadSchematicPlacement.packing_bounds", side_effect=measured),
        ):
            candidates, _ = power_template_candidates(tuple(sorted(by_path)), by_path, views, nets)
        self.assertTrue(candidates)
        for _, entries in candidates:
            placed = {c.path: (x, y, a) for c, x, y, a in entries}
            supply = [(x, y) for number, x, y, _ in pins(views["controller"], *placed["controller"]) if number == "8"][
                0
            ]
            controller_bounds = packing_bounds([next(e for e in entries if e[0].path == "controller")], views, nets)
            cap_bounds = atom_bounds([next(e for e in entries if e[0].path == "anonymous_bypass")], views)
            self.assertTrue(
                cap_bounds[2] <= controller_bounds[0] - 12.065 or cap_bounds[0] >= controller_bounds[2] + 12.065
            )
            self.assertAlmostEqual(placed["anonymous_bypass"][1], supply[1], delta=0.635)
            self.assertEqual(placed["anonymous_bypass"][2], 0)

    def test_four_finite_deterministic_variants(self) -> None:
        args = bridge()
        # Geometry is tested independently by the scene tests; this fixture
        # isolates topology, deterministic enumeration and identity retention.
        with (
            patch("edg.electronics_model.KiCadSchematicPlacement._score", return_value=(0, 0, 0, 0)),
            patch("edg.electronics_model.KiCadSchematicPlacement.packing_bounds", return_value=(0, 0, 100, 100)),
        ):
            candidates, diagnostics = power_template_candidates(*args)
            repeat, repeated_diagnostics = power_template_candidates(*args)
        self.assertEqual(len(candidates), 4)
        self.assertEqual(diagnostics, repeated_diagnostics)
        self.assertEqual(candidates, repeat)
        for _, entries in candidates:
            self.assertEqual({c.path for c, _, _, _ in entries}, set(args[0]))
            by_path = {c.path: (x, y, a) for c, x, y, a in entries}
            for index in (1, 2):
                self.assertLess(by_path["hi%d" % index][1], by_path["lo%d" % index][1])
            self.assertLess(by_path["hi1"][0], by_path["coil"][0])
            self.assertLess(by_path["coil"][0], by_path["hi2"][0])
        self.assertEqual(args[1]["hi1"].pins, {"1": "gate", "2": "source", "3": "drain"})

    def test_rejection_reasons_are_specific(self) -> None:
        with (
            patch("edg.electronics_model.KiCadSchematicPlacement._score", return_value=(2, 3, 0, 0)),
            patch("edg.electronics_model.KiCadSchematicPlacement.packing_bounds", return_value=(0, 0, 500, 500)),
        ):
            candidates, diagnostics = power_template_candidates(*bridge())
        self.assertFalse(candidates)
        self.assertEqual(len(diagnostics), 4)
        for diagnostic in diagnostics:
            self.assertIn("escape conflict", diagnostic["reason"])
            self.assertIn("symbol or field collision", diagnostic["reason"])
            self.assertIn("overflow", diagnostic["reason"])

    def test_candidate_measurement_recomputes_automatic_fields(self) -> None:
        from .KiCadSchematicPower import compare_bridge_variants
        from unittest.mock import Mock

        members, by_path, views, nets = bridge()
        circuit = SchematicCircuit(
            id="bridge",
            title="Bridge",
            summary="Bridge test",
            template="four_switch_bridge",
            components=members + ("separate_support_continuation",),
            stages=(),
        )
        for component in by_path.values():
            component.functional_circuit = circuit
            component.annotation = (900, 900)
        placed: list[Placement] = [(by_path[path], index * 40, 0, 0) for index, path in enumerate(members)]

        def candidates(
            paths: tuple[str, ...], source: Mapping[str, PhysicalComponent], *_: Any
        ) -> tuple[list[tuple[str, list[Placement]]], list[dict[str, Any]]]:
            self.assertTrue(all(c.annotation is None for c in source.values()))
            self.assertTrue(all(c is not by_path[path] for path, c in source.items()))
            return [], []

        with patch("edg.electronics_model.KiCadSchematicPower.power_template_candidates", side_effect=candidates):
            compare_bridge_variants(placed, views, nets, ([], {}, []), Mock())
        self.assertTrue(all(c.annotation == (900, 900) for c in by_path.values()))

    def test_uncategorized_region_reuses_incumbent_route(self) -> None:
        from .KiCadSchematicPower import compare_bridge_variants
        from unittest.mock import Mock

        members, by_path, views, nets = bridge()
        placed: list[Placement] = [(by_path[path], index * 40, 0, 0) for index, path in enumerate(members)]
        route: RouteResult = ([], {}, [])
        router = Mock(side_effect=AssertionError("incumbent must be reused"))
        actual, cached, evidence = compare_bridge_variants(placed, views, nets, route, router)
        self.assertIs(actual, placed)
        self.assertIs(cached, route)
        self.assertIsNone(evidence)
        router.assert_not_called()

    def test_ambiguous_or_missing_topology_is_not_guessed(self) -> None:
        members, by_path, views, nets = bridge()
        nets["hi1", "1"] = "unrelated"
        candidates, diagnostics = power_template_candidates(members, by_path, views, nets)
        self.assertFalse(candidates)
        self.assertIn("topology ambiguity", diagnostics[0]["reason"])
