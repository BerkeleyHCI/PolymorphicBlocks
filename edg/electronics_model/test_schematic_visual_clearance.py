"""Distinct electrical nets must also remain visually distinguishable.

The source/drain fixture uses the exact Q4 position and generic physical pin
geometry from the PDU handoff finding: old buses approached within 0.635 mm.
"""

from __future__ import annotations
from .KiCadSchematicTypes import PinKey, PinNets, Wire, Placement, Placements, Views
from .KiCadSchematicExporter import PhysicalComponent, SymbolView

import os
import unittest
import xml.etree.ElementTree as ET

from .KiCadSchematicExporter import generic, node, uid, S, effects, KiCadSchematicExporter
from .KiCadSchematicLayout import route_local
from .KiCadSchematicScene import wire_visual_conflict


def fixture() -> tuple[list[Placement], dict[str, SymbolView], dict[PinKey, str]]:
    transistor = PhysicalComponent(
        "system_power_or.fet",
        "Q4",
        "Test:SOIC8",
        "AO4407A",
        {
            "1": "source",
            "2": "source",
            "3": "source",
            "4": "gate",
            "5": "drain",
            "6": "drain",
            "7": "drain",
            "8": "drain",
        },
        None,
        "power",
    )
    parts = [transistor] + [
        PhysicalComponent("tap" + str(i), "TP" + str(i), "Test:One", "Tap", {"1": "io"}, None, "power") for i in (1, 2)
    ]
    views = {c.path: generic(c) for c in parts}
    # Preserve exact PDU fractional placement and 90-degree SOIC view.
    placed: list[Placement] = [(transistor, 79.18, 109.5, 90), (parts[1], 140, 150, 0), (parts[2], 180, 150, 0)]
    nets = {
        (transistor.path, n): ("source" if n in ("1", "2", "3") else "gate" if n == "4" else "drain")
        for n in transistor.pins
    }
    nets.update({(c.path, "1"): "source" for c in parts[1:]})
    return placed, views, nets


def segments(
    placed: Placements, views: Views, nets: PinNets
) -> tuple[list[Wire], dict[PinKey, tuple[float, float, float, float, float]], list[tuple[PinKey, str]], list[Wire]]:
    wires, escapes, failures = route_local(placed, views, nets)
    all_segments = list(wires)
    all_segments.extend((nets[key], (px, py), (ex, ey)) for key, (px, py, ex, ey, _) in escapes.items())
    return wires, escapes, failures, all_segments


class VisualClearanceTest(unittest.TestCase):
    def test_actual_source_drain_near_join_and_parallel_bus_are_rejected(self) -> None:
        self.assertTrue(wire_visual_conflict((67.75, 129.82), (75.37, 129.82), (76.005, 129.82), (90.61, 129.82)))
        self.assertTrue(wire_visual_conflict((75.37, 129.185), (95.69, 129.185), (79.18, 129.82), (90.61, 129.82)))

    def test_near_t_join_and_off_grid_stub_gap_are_rejected(self) -> None:
        # A configuration resistor must not look like an I2C pullup when its
        # separately connected branch stops half a routing cell from the bus.
        self.assertTrue(wire_visual_conflict((80, 80), (80, 89.365), (70, 90), (100, 90)))
        self.assertTrue(wire_visual_conflict((80, 80), (80, 89.9), (70, 90), (100, 90)))
        self.assertFalse(wire_visual_conflict((80, 80), (80, 88.73), (70, 90), (100, 90)))

    def test_legible_interior_perpendicular_crossing_is_preserved(self) -> None:
        self.assertFalse(wire_visual_conflict((40, 80), (100, 80), (70, 60), (70, 100)))
        self.assertTrue(wire_visual_conflict((40, 80), (100, 80), (70, 79.365), (70, 100)))
        self.assertTrue(wire_visual_conflict((40, 80), (100, 80), (70, 60), (70, 100), protected=((70.635, 80),)))

    def test_q4_route_has_no_source_drain_visual_near_join(self) -> None:
        placed, views, nets = fixture()
        _, _, failures, all_segments = segments(placed, views, nets)
        self.assertEqual(failures, [])
        conflicts = [
            (n, a, b, m, c, d)
            for i, (n, a, b) in enumerate(all_segments)
            for m, c, d in all_segments[i + 1 :]
            if n != m and wire_visual_conflict(a, b, c, d)
        ]
        self.assertEqual(conflicts, [])

    def test_q4_native_nets_keep_all_parallel_physical_pins(self) -> None:
        from .test_schematic_scene_native import NativeSceneTest

        clis = tuple(filter(None, os.environ.get("PB_SCHEMATIC_TEST_KICAD_CLIS", "").split(os.pathsep)))
        if not clis:
            self.skipTest("Set PB_SCHEMATIC_TEST_KICAD_CLIS for KiCad 9/10 native acceptance")
        placed, views, nets = fixture()
        _, _, failures, all_segments = segments(placed, views, nets)
        self.assertEqual(failures, [])
        root_id = uid("native-visual-clearance", "root")
        doc = node(
            "kicad_sch",
            node("version", 20250114),
            node("generator", S("eeschema")),
            node("uuid", root_id),
            node("paper", "A3"),
            node("lib_symbols", *[v.definition for v in views.values()]),
        )
        for c, x, y, angle in placed:
            symbol_id = uid(root_id, c.path)
            symbol = node(
                "symbol",
                node("lib_id", views[c.path].lib_id),
                node("at", x, y, angle),
                node("unit", 1),
                node("in_bom", S("yes")),
                node("on_board", S("yes")),
                node("dnp", S("no")),
                node("uuid", symbol_id),
            )
            for name, value in (("Reference", c.refdes), ("Value", c.value), ("Footprint", c.footprint)):
                symbol.append(node("property", name, value, node("at", x, y, 0), effects(hide=True)))
            symbol.extend(node("pin", n, node("uuid", uid(symbol_id, n))) for n in c.pins)
            symbol.append(
                node(
                    "instances",
                    node(
                        "project", "Fixture", node("path", "/" + root_id, node("reference", c.refdes), node("unit", 1))
                    ),
                )
            )
            doc.append(symbol)
        KiCadSchematicExporter._wires(doc, all_segments, "fixture", "visual-clearance")
        for cli in clis:
            with self.subTest(cli=cli):
                xml = ET.parse(NativeSceneTest.native(self, cli, doc, "netlist")).getroot()
                native = [
                    {(n.attrib["ref"], n.attrib["pin"]) for n in net.findall("node")}
                    for net in xml.findall("./nets/net")
                ]
                self.assertIn({("Q4", n) for n in ("1", "2", "3")} | {("TP1", "1"), ("TP2", "1")}, native)
                self.assertIn({("Q4", n) for n in ("5", "6", "7", "8")}, native)
