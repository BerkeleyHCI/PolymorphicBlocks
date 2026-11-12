"""Optional native acceptance of label-tail junctions and readable text frames.

Set PB_SCHEMATIC_TEST_KICAD_CLIS to an os.pathsep-separated CLI list, or
KICAD_CLI9 / KICAD_CLI10 to individual executables. These
fixtures exercise native connectivity and SVG geometry, not circuit semantics.
"""

from __future__ import annotations
from pathlib import Path
from .KiCadSchematicTypes import SExpr, Point
from .KiCadSchematicExporter import PhysicalComponent

from typing_extensions import override
import os
import re
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET

import sexpdata

from .KiCadSchematicExporter import KiCadSchematicExporter, children, effects, generic, node, uid, S
from .KiCadSchematicLayout import transform
from .KiCadSchematicScene import label_bounds, place_document_labels


def global_label(name: str, x: float, y: float, angle: float, justify: str) -> SExpr:
    eff = effects()
    eff.append(node("justify", S(justify)))
    return node(
        "global_label",
        name,
        node("at", x, y, angle),
        eff,
        node("uuid", uid("native-label-fixture", name)),
        node("shape", S("bidirectional")),
    )


def export_native(test: unittest.TestCase, cli: str, doc: SExpr, action: str) -> Path:
    temporary = tempfile.TemporaryDirectory()
    test.addCleanup(temporary.cleanup)
    folder = Path(temporary.name)
    schematic = folder / "Fixture.kicad_sch"
    schematic.write_text(sexpdata.dumps(doc), encoding="utf-8")
    output = folder / ("netlist.xml" if action == "netlist" else "svg")
    args = [cli, "sch", "export", action]
    if action == "netlist":
        args += ["--format", "kicadxml"]
    proc = subprocess.run(args + ["-o", str(output), str(schematic)], capture_output=True, text=True, timeout=60)
    test.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
    return output


class NativeSceneTest(unittest.TestCase):
    clis: tuple[str, ...]

    @classmethod
    @override
    def setUpClass(cls) -> None:
        cls.clis = tuple(filter(None, os.environ.get("PB_SCHEMATIC_TEST_KICAD_CLIS", "").split(os.pathsep)))
        if not cls.clis:
            cls.clis = tuple(filter(None, (os.environ.get("KICAD_CLI9"), os.environ.get("KICAD_CLI10"))))
        if not cls.clis:
            raise unittest.SkipTest("Set PB_SCHEMATIC_TEST_KICAD_CLIS or KICAD_CLI9/10 for native KiCad acceptance")

    def fixture(self) -> SExpr:
        root_id = uid("native-label-fixture", "root")
        doc = node(
            "kicad_sch",
            node("version", 20250114),
            node("generator", S("eeschema")),
            node("uuid", root_id),
            node("paper", "A3"),
            node("lib_symbols"),
        )
        libraries = children(doc, "lib_symbols")[0]
        for index, endpoint, rotation in ((1, 70, 180), (2, 90, 0)):
            component = PhysicalComponent(
                "part" + str(index), "U" + str(index), "Test:OnePin", "OnePin", {"1": "port"}, None, "Fixture"
            )
            view = generic(component)
            libraries.append(view.definition)
            _, dx, dy, _ = view.pins[0]
            dx, dy = transform(dx, dy, rotation)
            cx, cy = endpoint - dx, 80 - dy
            symbol_id = uid(root_id, component.path)
            symbol = node(
                "symbol",
                node("lib_id", view.lib_id),
                node("at", cx, cy, rotation),
                node("unit", 1),
                node("in_bom", S("yes")),
                node("on_board", S("yes")),
                node("dnp", S("no")),
                node("uuid", symbol_id),
            )
            for name, value in (("Reference", component.refdes), ("Value", "OnePin"), ("Footprint", "Test:OnePin")):
                symbol.append(node("property", name, value, node("at", cx, cy, 0), effects(hide=True)))
            symbol.extend(
                (
                    node("pin", "1", node("uuid", uid(symbol_id, "pin"))),
                    node(
                        "instances",
                        node(
                            "project",
                            "Fixture",
                            node("path", "/" + root_id, node("reference", component.refdes), node("unit", 1)),
                        ),
                    ),
                )
            )
            doc.append(symbol)
        return doc

    def test_label_tail_crosses_foreign_wire_without_joining_nets(self) -> None:
        from copy import deepcopy
        from .KiCadSchematicScene import safe_wire_crossing

        doc = self.fixture()
        for index, original in enumerate(list(children(doc, "symbol")), 3):
            symbol = deepcopy(original)
            children(symbol, "at")[0][2] -= 10
            children(symbol, "uuid")[0][1] = uid("crossing", str(index))
            for pin in children(symbol, "pin"):
                children(pin, "uuid")[0][1] = uid("crossing", str(index), pin[1])
            for prop in children(symbol, "property"):
                if prop[1] == "Reference":
                    prop[2] = "U" + str(index)
            path = children(children(children(symbol, "instances")[0], "project")[0], "path")[0]
            children(path, "reference")[0][1] = "U" + str(index)
            doc.append(symbol)
        # The label moves from (80,80) to (80,60). Its new tail crosses
        # the foreign wire at (80,70), strictly inside both unsplit segments.
        tail = ((80, 80), (80, 60))
        foreign = ((70, 70), (90, 70))
        self.assertEqual(safe_wire_crossing(*tail, *foreign), (80, 70))
        segments = [("branch", (70, 80), (90, 80)), ("branch", *tail), ("foreign", *foreign)]
        KiCadSchematicExporter._wires(doc, segments, "fixture", "crossing")
        doc.append(global_label("branch", 80, 60, 0, "left"))
        doc.append(global_label("foreign", 90, 70, 0, "left"))
        self.assertNotIn((80, 70), [tuple(children(j, "at")[0][1:]) for j in children(doc, "junction")])
        for cli in self.clis:
            with self.subTest(cli=cli):
                xml = ET.parse(export_native(self, cli, doc, "netlist")).getroot()
                nets = {
                    net.attrib["name"]: {(n.attrib["ref"], n.attrib["pin"]) for n in net.findall("node")}
                    for net in xml.findall("./nets/net")
                }
                self.assertEqual(nets["branch"], {("U1", "1"), ("U2", "1")})
                self.assertEqual(nets["foreign"], {("U3", "1"), ("U4", "1")})

    def test_label_tail_keeps_connected_physical_pins(self) -> None:
        doc = self.fixture()
        segments = [("branch", (70, 80), (80, 80)), ("branch", (80, 80), (90, 80))]
        KiCadSchematicExporter._wires(doc, segments, "fixture", "branch")
        doc.append(global_label("branch", 80, 80, 90, "left"))
        evidence = place_document_labels(doc, segments, "fixture")
        self.assertTrue(evidence["moves"])
        self.assertEqual(evidence["conflicts"], [])
        for cli in self.clis:
            with self.subTest(cli=cli):
                xml = ET.parse(export_native(self, cli, doc, "netlist")).getroot()
                components = {c.attrib["ref"] for c in xml.findall("./components/comp")}
                self.assertEqual(components, {"U1", "U2"})
                nets = [
                    {(n.attrib["ref"], n.attrib["pin"]) for n in net.findall("node")}
                    for net in xml.findall("./nets/net")
                ]
                self.assertIn({("U1", "1"), ("U2", "1")}, nets)
                connected = next(
                    net
                    for net in xml.findall("./nets/net")
                    if {(n.attrib["ref"], n.attrib["pin"]) for n in net.findall("node")} == {("U1", "1"), ("U2", "1")}
                )
                self.assertEqual(connected.attrib["name"], "branch")

    def test_all_label_angles_and_justifications_cover_native_glyphs(self) -> None:
        doc = self.fixture()
        cases = []
        for kind in ("global_label", "label"):
            for row, angle in enumerate((0, 90, 180, 270)):
                for column, justify in enumerate(("left", "right")):
                    name = f"{kind[0].upper()}FRAME{angle}{justify[0].upper()}"
                    x, y = 150 + column * 70, 100 + row * 35
                    item = global_label(name, x, y, angle, justify)
                    if kind == "label":
                        item[0] = S("label")
                        item[:] = [v for v in item if not (isinstance(v, list) and v and str(v[0]) == "shape")]
                        children(children(item, "effects")[0], "justify")[0].append(S("bottom"))
                    doc.append(item)
                    cases.append(
                        (
                            name,
                            label_bounds(
                                name,
                                x,
                                y,
                                angle,
                                justify=justify,
                                outline=kind == "global_label",
                                bottom=kind == "label",
                            ),
                        )
                    )
        for cli in self.clis:
            folder = export_native(self, cli, doc, "svg")
            svg = ET.parse(next(folder.glob("*.svg"))).getroot()
            parents = {child: parent for parent in svg.iter() for child in parent}
            for name, bounds in cases:
                with self.subTest(cli=cli, label=name):
                    group = next(
                        item
                        for item in svg.iter()
                        if item.tag.endswith("}g")
                        and any(child.tag.endswith("}desc") and child.text == name for child in item)
                    )
                    points: list[Point] = []
                    for path in group.iter():
                        if not path.tag.endswith("}path"):
                            continue
                        current = path
                        while current in parents:
                            self.assertNotIn(
                                "transform",
                                current.attrib,
                                "Native SVG changed to transformed glyph paths; update fixture measurement",
                            )
                            current = parents[current]
                        commands = path.attrib["d"]
                        self.assertFalse(set(re.findall(r"[A-Za-z]", commands)) - set("MLZmlz"))
                        values = [float(v) for v in re.findall(r"[-+]?(?:\d*\.\d+|\d+)", commands)]
                        self.assertEqual(len(values) % 2, 0)
                        points.extend(zip(values[::2], values[1::2]))
                    self.assertTrue(points)
                    actual = (
                        min(x for x, _ in points),
                        min(y for _, y in points),
                        max(x for x, _ in points),
                        max(y for _, y in points),
                    )
                    self.assertLessEqual(bounds[0], actual[0])
                    self.assertLessEqual(bounds[1], actual[1])
                    self.assertGreaterEqual(bounds[2], actual[2])
                    self.assertGreaterEqual(bounds[3], actual[3])

    def test_180_degree_label_bounds_cover_native_readable_text(self) -> None:
        doc = self.fixture()
        doc.append(global_label("LEFT_FRAME", 120, 180, 180, "right"))
        bounds = label_bounds("LEFT_FRAME", 120, 180, 180, justify="right", outline=True)
        self.assertLess(bounds[0], 120)
        self.assertLess(bounds[2], 122)
        for cli in self.clis:
            with self.subTest(cli=cli):
                folder = export_native(self, cli, doc, "svg")
                root = ET.parse(next(folder.glob("*.svg"))).getroot()
                text = next(item for item in root.iter() if item.tag.endswith("}text") and item.text == "LEFT_FRAME")
                self.assertEqual(text.attrib["text-anchor"], "end")
                hi = float(text.attrib["x"])
                lo = hi - float(text.attrib["textLength"])
                self.assertLessEqual(bounds[0], lo)
                self.assertGreaterEqual(bounds[2], hi)

    def test_label_can_reanchor_only_within_its_existing_native_wire_island(self) -> None:
        doc = self.fixture()
        segments = [("branch", (70, 80), (80, 80)), ("branch", (80, 80), (90, 80))]
        KiCadSchematicExporter._wires(doc, segments, "fixture", "branch")
        # A field at the old label anchor prevents all new tails from starting
        # there. A different vertex of the existing same-net wire remains safe.
        doc.append(node("text", "BLOCK", node("at", 80, 80, 0), effects(), node("uuid", uid("block-field"))))
        doc.append(global_label("branch", 80, 80, 90, "left"))
        evidence = place_document_labels(doc, segments, "fixture")
        self.assertTrue(evidence["moves"])
        self.assertNotEqual(tuple(evidence["moves"][0]["wire_anchor"]), (80, 80))
        for cli in self.clis:
            with self.subTest(cli=cli):
                xml = ET.parse(export_native(self, cli, doc, "netlist")).getroot()
                connected = [
                    net
                    for net in xml.findall("./nets/net")
                    if {(n.attrib["ref"], n.attrib["pin"]) for n in net.findall("node")} == {("U1", "1"), ("U2", "1")}
                ]
                self.assertEqual(len(connected), 1)
                self.assertEqual(connected[0].attrib["name"], "branch")


if __name__ == "__main__":
    unittest.main()
