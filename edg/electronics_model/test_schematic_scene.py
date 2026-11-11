"""Regression checks for final-sheet label geometry and electrical anchors."""

from __future__ import annotations
from pathlib import Path
from .KiCadSchematicTypes import SExpr, Wire
from .KiCadSchematicExporter import PhysicalComponent, SymbolView

import copy
import unittest
from .KiCadSchematicExporter import node, children, S
from .KiCadSchematicScene import text_bounds, place_document_labels


def label(name: str, x: float, y: float, angle: float, identity: str) -> SExpr:
    return node(
        "global_label",
        name,
        node("at", x, y, angle),
        node("effects", node("font", node("size", 1.27, 1.27)), node("justify", S("left"))),
        node("uuid", identity),
        node("shape", S("bidirectional")),
    )


class SceneTest(unittest.TestCase):
    def test_late_label_moves_free_an_earlier_label_after_second_pass(self) -> None:
        import json
        from pathlib import Path
        import sexpdata

        fixture = json.loads(Path(__file__).with_name("test_schematic_scene_settling.json").read_text())
        doc = sexpdata.loads(fixture["document"])
        original = copy.deepcopy(doc)
        segments = [(net, tuple(a), tuple(b)) for net, a, b in fixture["segments"]]
        result = place_document_labels(doc, segments, "settling-regression")
        self.assertEqual(result["conflicts"], [])
        early = next(item for item in result["moves"] if item["name"] == "charger.ic.fbg")
        self.assertGreaterEqual(early["pass_index"], 2)
        self.assertLessEqual(result["passes"], 6)
        self.assertEqual(result["termination"], "stable")
        self.assertEqual(place_document_labels(original, segments, "settling-regression"), result)
        self.assertEqual(doc, original)

    def test_clear_scene_stops_after_one_stable_pass(self) -> None:
        doc = node("kicad_sch", node("lib_symbols"), label("clear", 80, 80, 0, "clear"))
        result = place_document_labels(doc, [("clear", (70, 80), (80, 80))], "clear")
        self.assertEqual(result["conflicts"], [])
        self.assertEqual(result["passes"], 1)
        self.assertEqual(result["termination"], "stable")

    def test_label_can_escape_beyond_ten_mm(self) -> None:
        definitions = node("lib_symbols")
        doc = node("kicad_sch", definitions, label("long_signal_label", 98, 80, 0, "wide-detour"))
        for name, box in (("left", (60, 65, 95, 95)), ("right", (101, 60, 140, 100))):
            x1, y1, x2, y2 = box
            definitions.append(
                node(
                    "symbol",
                    name,
                    node("symbol", name + "_0_1", node("rectangle", node("start", x1, -y1), node("end", x2, -y2))),
                )
            )
            doc.append(node("symbol", node("lib_id", name), node("at", 0, 0, 0)))
        result = place_document_labels(doc, [("signal", (98, 78), (98, 80))], "wide-detour")
        self.assertEqual(result["conflicts"], [])
        self.assertTrue(result["moves"])
        self.assertGreater(abs(result["moves"][0]["at"][1] - 80), 10.16)

    def test_label_escapes_bank_taller_than_thirty_mm(self) -> None:
        definitions = node("lib_symbols")
        doc = node("kicad_sch", definitions, label("long_signal_label", 98, 80, 0, "outer-detour"))
        for name, box in (("left", (60, 45, 95, 115)), ("right", (101, 40, 140, 120))):
            x1, y1, x2, y2 = box
            definitions.append(
                node(
                    "symbol",
                    name,
                    node("symbol", name + "_0_1", node("rectangle", node("start", x1, -y1), node("end", x2, -y2))),
                )
            )
            doc.append(node("symbol", node("lib_id", name), node("at", 0, 0, 0)))
        result = place_document_labels(doc, [("signal", (98, 78), (98, 80))], "outer-detour")
        self.assertEqual(result["conflicts"], [])
        self.assertTrue(result["moves"])
        self.assertGreater(abs(result["moves"][0]["at"][1] - 80), 30.48)

    def test_crossings_reject_endpoints_bends_anchors_and_overlap(self) -> None:
        from .KiCadSchematicScene import safe_wire_crossing

        a, b, c, d = (40, 50), (60, 50), (50, 40), (50, 60)
        self.assertEqual(safe_wire_crossing(a, b, c, d), (50, 50))
        self.assertIsNone(safe_wire_crossing(a, b, c, d, [(50, 50)]))
        self.assertIsNone(safe_wire_crossing(a, (50, 50), c, d))
        self.assertIsNone(safe_wire_crossing(a, b, (45, 50), (55, 50)))

    def test_foreign_wire_through_global_label_tip_triggers_repair(self) -> None:
        from .KiCadSchematicScene import label_bounds, segment_box

        doc = node("kicad_sch", node("lib_symbols"), label("power", 80, 80, 0, "tip"))
        foreign = ((79.4, 78.7), (79.4, 79.2))
        segments = [("power", (75, 80), (80, 80)), ("sense", *foreign)]
        result = place_document_labels(doc, segments, "tip-regression")
        self.assertTrue(result["moves"])
        self.assertEqual(result["conflicts"], [])
        item = children(doc, "global_label")[0]
        at = children(item, "at")[0]
        justify = str(children(children(item, "effects")[0], "justify")[0][1])
        self.assertFalse(
            segment_box(*foreign, label_bounds(item[1], at[1], at[2], at[3], justify=justify, outline=True))
        )

    def test_repeated_ic_pin_bus_preserves_external_label_outline(self) -> None:
        from .KiCadSchematicExporter import PhysicalComponent, SymbolView
        from .KiCadSchematicLayout import route_local
        from .KiCadSchematicScene import pin_label_bounds, segment_box

        # INA780's repeated shunt-sense pins (1/2) and power pins (14/8)
        # previously routed a sense bus through the power label's pointed end.
        c = PhysicalComponent("ina", "U1", "Test:INA", "INA780", {}, None, "ina")
        c.net_labels = {
            "1": "shunt_pos",
            "2": "shunt_pos",
            "14": "driver_daughter.pwr_pre_gate",
            "8": "driver_daughter.pwr_pre_gate",
        }
        view = SymbolView(
            node(
                "symbol",
                "Test",
                node("symbol", "Test_0_1", node("rectangle", node("start", 0, 15), node("end", 30, -20))),
            ),
            [("1", -2.54, 10.16, 0), ("14", -2.54, 5.08, 0), ("2", -2.54, 0, 0), ("8", -2.54, -10.16, 0)],
            "Test",
        )
        wiring = {(c.path, number): net for number, net in c.net_labels.items()}
        wires, escapes, failures = route_local([(c, 100, 100, 0)], {c.path: view}, wiring)
        self.assertEqual(failures, [])
        bounds = pin_label_bounds(c.net_labels["14"], *escapes[c.path, "14"][2:])
        self.assertTrue(any(net == "shunt_pos" for net, _, _ in wires))
        self.assertFalse(any(segment_box(a, b, bounds) for net, a, b in wires if net == "shunt_pos"))

    def test_rotated_instance_fields_reserve_native_horizontal_glyphs(self) -> None:
        from types import SimpleNamespace
        from .KiCadSchematicLayout import annotation_bounds
        from .KiCadSchematicScene import instance_property_at, segment_box

        component = PhysicalComponent("fet", "Q2", "FP", "SIR882BDP-T1-RE3-HXY", {}, None, "fixture")
        for rotation in (0, 90, 180, 270):
            with self.subTest(rotation=rotation):
                at = instance_property_at(node("at", 130, 120, rotation % 180), node("at", 110, 90, rotation))
                self.assertEqual(at[3], 0)
                bounds = annotation_bounds(component, 130, 117.46, rotation)
                # The observed PDU failure: a vertical wire 8 mm right of the
                # field center crossed its native horizontal part-number glyphs.
                self.assertTrue(segment_box((138, 118), (138, 122), bounds))
                self.assertLess(bounds[0], 119)
                self.assertGreater(bounds[2], 141)

    def test_dense_mixed_connector_labels_can_use_reserved_outer_lane(self) -> None:
        def entry(kind: str, name: str, y: float, identity: str) -> SExpr:
            effect = node(
                "effects",
                node("font", node("size", 1.27, 1.27)),
                node("justify", S("right"), *([S("bottom")] if kind == "label" else [])),
            )
            return node(
                kind,
                name,
                node("at", 100, y, 180),
                effect,
                node("uuid", identity),
                *([node("shape", S("bidirectional"))] if kind == "global_label" else []),
            )

        doc = node(
            "kicad_sch",
            node("lib_symbols"),
            node("rectangle", node("start", 20, 57.5), node("end", 150, 67.5)),
            node("text", "XXXXX", node("at", 120, 62.54, 0), node("effects", node("font", node("size", 5, 5)))),
            entry("global_label", "control.i2c.sda", 60, "a"),
            entry("label", "control.bms_alert", 62.54, "b"),
            entry("global_label", "control.taps[0]", 65.08, "c"),
        )
        segments = [(net, (100, y), (105.08, y)) for net, y in (("sda", 60), ("alert", 62.54), ("tap", 65.08))]
        report = place_document_labels(doc, segments, "dense")
        self.assertFalse(report["conflicts"])
        self.assertTrue(
            any(
                abs(children(item, "at")[0][1] - 100) > 5.08
                for kind in ("label", "global_label")
                for item in children(doc, kind)
            )
        )

    def test_unicode_rotated_text_and_outline_use_same_bounds(self) -> None:
        horizontal = text_bounds("输出.foo", 80, 80, 0, outline=True)
        vertical = text_bounds("输出.foo", 80, 80, 90, outline=True)
        self.assertAlmostEqual(horizontal[2] - horizontal[0], vertical[3] - vertical[1])
        self.assertGreater(horizontal[2] - horizontal[0], text_bounds("aa.foo", 80, 80, 0)[2] - 80)

    def fixture(self) -> tuple[SExpr, list[Wire]]:
        doc = node(
            "kicad_sch",
            node("lib_symbols"),
            label("control.isense_out", 100, 80, 90, "a"),
            label("cintref_amps.out.1", 101.27, 80, 90, "b"),
        )
        segments: list[Wire] = [("net_a", (100, 74.92), (100, 80)), ("net_b", (101.27, 74.92), (101.27, 80))]
        return doc, segments

    def test_vertical_collision_repaired_without_moving_original_wire_or_net(self) -> None:
        doc, segments = self.fixture()
        before = copy.deepcopy(segments)
        report = place_document_labels(doc, segments, "sheet")
        self.assertEqual(report["conflicts"], [])
        self.assertEqual(segments, before)
        self.assertEqual([x[1] for x in children(doc, "global_label")], ["control.isense_out", "cintref_amps.out.1"])
        self.assertTrue(all(children(x, "at")[0][3] == 0 for x in children(doc, "global_label")))
        for wire in children(doc, "wire"):
            a, b = children(wire, "pts")[0][1:]
            self.assertTrue(a[1] == b[1] or a[2] == b[2])

    def test_label_stays_inside_its_functional_region(self) -> None:
        from .KiCadSchematicReadability import text_item

        doc = node(
            "kicad_sch",
            node("lib_symbols"),
            node("rectangle", node("start", 40, 60), node("end", 110, 100)),
            label("long_control_signal", 100, 80, 0, "border-label"),
        )
        segments = [("signal", (60, 80), (100, 80))]
        result = place_document_labels(doc, segments, "border")
        self.assertEqual(result["conflicts"], [])
        item = children(doc, "global_label")[0]
        text = text_item("test", item[1], children(item, "at")[0], children(item, "effects")[0], "", "global_label")
        assert text is not None
        bounds = text.bounds
        self.assertGreaterEqual(bounds[0], 40)
        self.assertLessEqual(bounds[2], 110)
        self.assertEqual(segments, [("signal", (60, 80), (100, 80))])

    def test_pin_numbers_remain_obstacles_when_names_hidden(self) -> None:
        from .KiCadSchematicScene import pin_number_items, pin_name_items

        definition = node(
            "symbol",
            "Fixture",
            node("pin_names", S("hide")),
            node(
                "symbol",
                "Fixture_1_1",
                node(
                    "pin",
                    S("passive"),
                    S("line"),
                    node("at", -5.08, 0, 0),
                    node("length", 2.54),
                    node("name", "input"),
                    node("number", "3"),
                ),
            ),
        )
        self.assertEqual(pin_name_items(definition, 50, 50, 0), [])
        for rotation in (0, 90, 180, 270):
            items = pin_number_items(definition, 50, 50, rotation)
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0]["text"], "3")
        definition.append(node("pin_numbers", S("hide")))
        self.assertEqual(pin_number_items(definition, 50, 50, 0), [])

    def test_deterministic_and_unknown_anchors_not_extended(self) -> None:
        doc, segments = self.fixture()
        other = copy.deepcopy(doc)
        self.assertEqual(place_document_labels(doc, segments, "sheet"), place_document_labels(other, segments, "sheet"))
        self.assertEqual(doc, other)
        isolated = node("kicad_sch", node("lib_symbols"), label("single", 60, 60, 90, "x"))
        place_document_labels(isolated, [], "single")
        self.assertEqual(children(isolated, "wire"), [])

    def test_unknown_or_ambiguous_anchor_preserves_original_label(self) -> None:
        for segments in ([], [("a", (60, 55), (60, 60)), ("b", (55, 60), (65, 60))]):
            original = label("unknown", 60, 60, 90, "x")
            doc = node("kicad_sch", node("lib_symbols"), copy.deepcopy(original))
            result = place_document_labels(doc, segments, "unknown")
            self.assertEqual(children(doc, "global_label")[0], original)
            self.assertEqual(len(result["unresolved_anchors"]), 1)
            self.assertEqual(children(doc, "wire"), [])

    def test_one_label_per_graphical_island_including_disconnected_same_net(self) -> None:
        from types import SimpleNamespace
        from .KiCadSchematicScene import label_islands

        view = SymbolView([], [("1", 0, 0, 180)], "Test:Pin")
        placed = [
            (PhysicalComponent(p, "U1", "FP", "fixture", {"1": "pin"}, None, "fixture"), x, 60, 0)
            for p, x in [("a", 40), ("b", 60), ("c", 100)]
        ]
        views = {p.path: view for p, _, _, _ in placed}
        nets = {(p.path, "1"): "supply" for p, _, _, _ in placed}
        wire = [("supply", (45.08, 60), (65.08, 60))]
        chosen = label_islands(placed, views, nets, wire, {"supply"})
        self.assertEqual(chosen, {("a", "1"), ("c", "1")})

    def test_same_net_wire_does_not_strike_through_moved_text(self) -> None:
        from .KiCadSchematicScene import wire_through_text

        doc = node("kicad_sch", node("lib_symbols"), label("supply", 80, 80, 0, "supply"))
        segments = [("supply", (80, 80), (110, 80))]
        result = place_document_labels(doc, segments, "same-net")
        self.assertEqual(result["conflicts"], [])
        item = children(doc, "global_label")[0]
        at = children(item, "at")[0]
        terms = children(children(item, "effects")[0], "justify")[0]
        rect = text_bounds(item[1], at[1], at[2], at[3], justify=str(terms[1]))
        self.assertFalse(wire_through_text((80, 80), (110, 80), rect))

    def test_label_tail_reserializes_t_junction_on_existing_wire(self) -> None:
        original = label("branch", 80, 80, 90, "branch")
        doc = node("kicad_sch", node("lib_symbols"), original)
        segments = [("branch", (70, 80), (80, 80)), ("branch", (80, 80), (90, 80))]
        result = place_document_labels(doc, segments, "junction-regression")
        self.assertEqual(result["conflicts"], [])
        self.assertTrue(result["moves"])
        junctions = {tuple(children(item, "at")[0][1:3]) for item in children(doc, "junction")}
        self.assertIn((80, 80), junctions)
        self.assertEqual(children(original, "uuid")[0][1], "branch")

    def test_dense_generic_keeps_labels_readable_without_changing_pin_inventory(self) -> None:
        from .KiCadSchematicExporter import PhysicalComponent, generic

        component = PhysicalComponent(
            "mcu.ic", "U1", "Test:QFN", "MCU", {str(i): f"io{i}" for i in range(1, 25)}, None, "mcu"
        )
        view = generic(component)
        self.assertEqual({p[0] for p in view.pins}, set(component.pins))
        for side in (0, 180):
            rows = sorted(p[2] for p in view.pins if p[3] == side)
            self.assertTrue(all(b - a >= 3.81 - 0.0001 for a, b in zip(rows, rows[1:])))

    def test_readable_180_label_bounds_remain_on_justified_side_of_anchor(self) -> None:
        from .KiCadSchematicScene import label_bounds, pin_label_bounds

        # Native KiCad SVG renders this at text-anchor=end, extending left of
        # x=25.16. Applying an ordinary 180-degree text transform flips the box
        # incorrectly to the right and hides page-edge clipping from the planner.
        bounds = label_bounds("mcu.gpio.led_0", 25.16, 169.656, 180, justify="right")
        self.assertAlmostEqual(bounds[2], 25.16)
        self.assertLess(bounds[0], 12)
        self.assertEqual(bounds, label_bounds("mcu.gpio.led_0", 25.16, 169.656, 0, justify="right"))
        pin_box = pin_label_bounds("long.external.interface", 30, 80, 0)
        self.assertLess(pin_box[0], 12)

    def test_alternate_anchor_never_jumps_to_another_island_with_same_net_name(self) -> None:
        from .KiCadSchematicScene import wire_island_anchors

        segments = [
            ("supply", (40, 80), (50, 80)),
            ("supply", (50, 80), (50, 90)),
            ("supply", (45, 70), (55, 70)),
            ("other", (40, 80), (40, 90)),
        ]
        anchors = wire_island_anchors((40, 80), "supply", segments)
        self.assertIn((50, 90), anchors)
        self.assertNotIn((45, 70), anchors)
        self.assertNotIn((55, 70), anchors)
        self.assertNotIn((40, 90), anchors)

    def test_generic_bottom_pin_names_have_clearance_from_last_side_row(self) -> None:
        from .KiCadSchematicExporter import PhysicalComponent, generic
        from .KiCadSchematicScene import pin_name_items, overlap

        c = PhysicalComponent(
            "mcu.ic", "U1", "Test", "MCU", {"1": "gpio.led_2", "2": "gpio.led_1", "3": "gnd", "4": "vdd"}, None, "mcu"
        )
        names = pin_name_items(generic(c).definition, 80, 80, 0)
        side = next(t for t in names if t["text"] == "gpio.led_2")
        ground = next(t for t in names if t["text"] == "gnd")
        self.assertFalse(overlap(side["bounds"], ground["bounds"]))

    def test_anchor_budget_samples_distant_connected_wire_without_new_connections(self) -> None:
        from .KiCadSchematicScene import wire_island_anchors

        segments = [("output", (40 + i * 5.08, 80), (40 + (i + 1) * 5.08, 80)) for i in range(20)]
        candidates = wire_island_anchors((40, 80), "output", segments)
        self.assertLessEqual(len(candidates), 8)
        self.assertEqual(candidates[0], (40, 80))
        self.assertIn(segments[-1][2], candidates)
        self.assertTrue(all(point in {p for _, a, b in segments for p in (a, b)} for point in candidates))
