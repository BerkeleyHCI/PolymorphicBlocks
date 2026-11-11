"""Presentation descriptions cannot alter physical inventory or net identity."""

import json
import unittest
from dataclasses import replace
from types import SimpleNamespace
from unittest import mock
from .KiCadSchematicPresentation import SchematicPresentation
from .KiCadSchematicReadability import inspect_documents, text_width
from .KiCadSchematicExporter import (
    KiCadSchematicExporter,
    SchematicExportOptions,
    children,
)
from .test_schematic_export import GeneratedMappedBoard, GeneratedMappedPart
from ..core import Block
from .PassivePort import Passive
from .RefdesRefinementPass import RefdesRefinementPass
from ..core import ScalaCompiler
import sexpdata


class GroundTerminal(Block):
    def __init__(self):
        super().__init__()
        self.gnd = self.Port(Passive(), optional=True)


class SplitGroundBoard(Block):
    def contents(self):
        super().contents()
        self.raw = self.Block(GroundTerminal())
        self.system = self.Block(GroundTerminal())
        self.shunt = self.Block(GeneratedMappedPart())
        self.connect(self.raw.gnd, self.shunt.a)
        self.connect(self.system.gnd, self.shunt.b)


class PresentationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.compiled = ScalaCompiler.compile(GeneratedMappedBoard)
        cls.compiled.append_values(RefdesRefinementPass().run(cls.compiled))

    def test_annotations_and_pin_names_are_durable(self):
        presentation = SchematicPresentation.from_dict(
            dict(
                components={
                    "part": dict(
                        description="Target reset interface",
                        pin_names={"1": "RESET"},
                        display_value="Reset resistor",
                    )
                },
                interfaces=[dict(component="part", pin="2", name="Target EN")],
            )
        )
        options = SchematicExportOptions("Presentation", presentation=presentation)
        exporter = KiCadSchematicExporter()
        a = exporter.export(self.compiled, options)
        b = exporter.export(self.compiled, options)
        self.assertEqual(a.files, b.files)
        self.assertIn("Target reset interface", "".join(a.files.values()))
        self.assertIn("Target EN", "".join(a.files.values()))
        self.assertEqual(json.loads(a.files["readability.json"])["visual_approval"], "pending")
        self.assertEqual(
            exporter.readability(self.compiled, options),
            json.loads(a.files["readability.json"]),
        )
        doc = next(sexpdata.loads(v) for k, v in a.files.items() if k.endswith(".kicad_sch"))
        physical = [s for s in children(doc, "symbol") if any(p[1] == "PBPath" for p in children(s, "property"))]
        self.assertEqual(len(physical), 1)
        self.assertEqual({p[1] for p in children(physical[0], "pin")}, {"1", "2"})
        baseline = exporter.export(self.compiled, SchematicExportOptions("Presentation"))
        self.assertNotEqual(
            json.loads(a.files["manifest.json"])["fingerprint"],
            json.loads(baseline.files["manifest.json"])["fingerprint"],
        )

    def test_fingerprint_excludes_source_location_metadata(self):
        import copy

        compiled = copy.deepcopy(self.compiled)
        exporter = KiCadSchematicExporter()
        options = SchematicExportOptions("PortableFingerprint")
        before = exporter.export(compiled, options)
        entry = compiled.design.contents.meta.members.node["source_checkout_location"]
        entry.text_leaf = "/different/machine/checkout/board.py:123"
        after = exporter.export(compiled, options)
        self.assertEqual(before.files, after.files)

    def test_circuit_summary_and_boundary_are_measured_and_exported(self):
        presentation = SchematicPresentation.from_dict(dict(schema=2, circuits=[dict(
            id="interface", title="Reset interface", summary="Series interface between controller and target.",
            components=["part"], boundaries=[dict(component="part", pin="1", name="Controller reset", role="input")],
        )]))
        exporter = KiCadSchematicExporter()
        options = SchematicExportOptions("CircuitMeaning", presentation=presentation)
        bundle = exporter.export(self.compiled, options)
        self.assertEqual(bundle.files, exporter.export(self.compiled, options).files)
        model = json.loads(bundle.files["circuit-model.json"])["boards"][0]
        circuit = next(c for c in model["circuits"] if c["id"] == "interface")
        self.assertEqual(circuit["boundaries"][0]["component"], "part")
        documents = "".join(value for name, value in bundle.files.items() if name.endswith(".kicad_sch"))
        self.assertIn("Series interface between controller and target.", documents)
        self.assertIn("Controller reset:", documents)
        regions, _ = exporter.prepare_regions(self.compiled, options)
        plain, _ = exporter.prepare_regions(self.compiled, SchematicExportOptions("CircuitMeaning"))
        self.assertGreater(regions[0].bounds[3] - regions[0].bounds[1], plain[0].bounds[3] - plain[0].bounds[1])

    def test_tall_authored_circuit_notes_use_measured_side_column(self):
        from .KiCadSchematicExporter import PhysicalComponent, SymbolView, node
        component = PhysicalComponent("power", "U1", "Test:Power", "Power", {}, None, "Power")
        component.functional_circuit = SimpleNamespace(
            id="power", provenance="explicit", summary="Protected input and regulated output stage.",
            boundaries=(SimpleNamespace(component="power", pin="1", name="Protected supply input"),),
        )
        component.net_labels = {"1": "protected_supply"}
        view = SymbolView(node("symbol", "Test:Power"), [], "Test:Power")
        placed = [(component, 0, 0, 0)]
        # A 275 mm wide, 203.94 mm tall circuit (including title) already fills
        # the wide A3 height. Adding notes above it would exceed that space.
        import importlib
        exporter_module = importlib.import_module(__package__ + ".KiCadSchematicExporter")
        with (mock.patch.object(exporter_module, "graphic_bounds", return_value=(0, 0, 269, 192.4)),
              mock.patch.object(exporter_module, "annotation_bounds", return_value=(0, 0, 1, 1))):
            geometry = KiCadSchematicExporter._region_geometry(placed, {"power": view}, {}, {}, [], "Power")
            self.assertEqual(geometry, KiCadSchematicExporter._region_geometry(
                placed, {"power": view}, {}, {}, [], "Power"))
            ordinary = replace(component)
            plain = KiCadSchematicExporter._region_geometry([(ordinary, 0, 0, 0)], {"power": view}, {}, {}, [], "Power")
        with (mock.patch.object(exporter_module, "graphic_bounds", return_value=(0, 0, 365, 192.4)),
              mock.patch.object(exporter_module, "annotation_bounds", return_value=(0, 0, 1, 1))):
            overflow = KiCadSchematicExporter._region_geometry(placed, {"power": view}, {}, {}, [], "Power")
            self.assertGreater(overflow[0][3] - overflow[0][1], 205)
            self.assertEqual(len(overflow[2]), 1)  # Neither alternative fits: normal caller rejects it.
        # Real PDU converter title/body occupied 205.85 mm before notes.
        # Side mode may reduce only surplus title whitespace to fit this case.
        for content_bottom, expected_height in ((194.31, 204.58), (196.0, 204.54)):
            with (mock.patch.object(exporter_module, "graphic_bounds", return_value=(0, 0, 269, content_bottom)),
                  mock.patch.object(exporter_module, "annotation_bounds", return_value=(0, 0, 1, 1))):
                compact = KiCadSchematicExporter._region_geometry(placed, {"power": view}, {}, {}, [], "Power")
            self.assertEqual(len(compact[2]), 2)
            self.assertAlmostEqual(compact[0][3] - compact[0][1], expected_height)
            title = compact[1][0]
            self.assertLessEqual(title[3] + title[1] / 2, -1.27)
        bounds, headings, boxes = geometry
        self.assertLessEqual(bounds[2] - bounds[0], 375)
        self.assertLessEqual(bounds[3] - bounds[1], 205)
        self.assertAlmostEqual(bounds[3] - bounds[1], plain[0][3] - plain[0][1])
        self.assertEqual(len(boxes), 2)
        self.assertGreater(boxes[1][0], plain[0][2])
        self.assertTrue(any("Protected supply input" in line for line, *_ in headings))
        for line, size, x, y in headings:
            self.assertGreaterEqual(x, bounds[0])
            self.assertLessEqual(x + text_width(line, size), bounds[2])
            self.assertGreaterEqual(y - size, bounds[1])
            self.assertLessEqual(y + size, bounds[3])
        from .KiCadSchematicExporter import _RegionDrawing
        from .KiCadSchematicPlanner import SchematicRegion
        drawing = _RegionDrawing(SchematicRegion("power", "Power", "root", ("power",), bounds),
                                 placed, [], [], {}, headings, boxes)
        board = SimpleNamespace(prefix="board", views={"power": view}, pin_nets={}, names={}, net_regions={})
        doc = []
        KiCadSchematicExporter()._render_region(doc, board, drawing, SimpleNamespace(x=20, y=40),
                                               "sheet", "root", {}, None, [], [])
        text_nodes = children(doc, "text")
        self.assertEqual([node[1] for node in text_nodes], [line for line, *_ in headings])
        for text_node, (_, _, x, y) in zip(text_nodes, headings):
            at = children(text_node, "at")[0]
            self.assertAlmostEqual(at[1], round(x + 20 - bounds[0], 4))
            self.assertAlmostEqual(at[2], round(y + 40 - bounds[1], 4))

    def test_distinct_returns_are_named_without_merging_the_shunt(self):
        from .NetlistGenerator import NetlistTransform
        from .KiCadSchematicExporter import node
        compiled = ScalaCompiler.compile(SplitGroundBoard)
        compiled.append_values(RefdesRefinementPass().run(compiled))
        physical = next(iter(NetlistTransform(compiled).run().values()))
        net_pins = {net.name: {(str(pin.block_path), pin.pin_name) for pin in net.pins}
                    for net in physical.nets}
        self.assertEqual(set(net_pins), {"system.gnd", "raw.gnd"})
        self.assertNotEqual(next(net for net, pins in net_pins.items() if ("shunt", "1") in pins),
                            next(net for net, pins in net_pins.items() if ("shunt", "2") in pins))
        # Isolate the presentation behavior from an external symbol-library install.
        # Native multi-ground equality is separately exercised on real boards.
        import importlib
        module = importlib.import_module(__package__ + ".KiCadSchematicExporter")
        ground = node("symbol", "power:GND", node("symbol", "GND_0_1"))
        exporter = KiCadSchematicExporter()
        with mock.patch.object(module, "ground_symbol", return_value=ground):
            bundle = exporter.export(compiled, SchematicExportOptions("SplitGround"))
        documents = [sexpdata.loads(value) for name, value in bundle.files.items() if name.endswith(".kicad_sch")]
        grounds = [symbol for doc in documents for symbol in children(doc, "symbol")
                   if children(symbol, "lib_id")[0][1] == "power:GND"]
        self.assertEqual({prop[2] for symbol in grounds for prop in children(symbol, "property")
                          if prop[1] == "Value"}, {"system.gnd", "raw.gnd"})
        visible = [text[1] for doc in documents for text in children(doc, "text")]
        self.assertIn("system.gnd", visible)
        self.assertIn("raw.gnd", visible)
        self.assertEqual(len(grounds), 2)
        prepared, _, _, _ = exporter._prepare_boards(compiled, SchematicExportOptions("SplitGround"))
        labels = {label for board in prepared for region in board.regions.values()
                  for component, *_ in region.placed for label in component.ground_net_labels.values()}
        self.assertEqual(labels, {"system.gnd", "raw.gnd"})
        from .KiCadSchematicLayout import ground_bounds, ground_label_position
        from .KiCadSchematicScene import text_bounds
        for angle in (0, 90, 180, 270):
            x, y = ground_label_position(50, 50, angle)
            bounds = ground_bounds(50, 50, angle, "raw.gnd")
            text = text_bounds("raw.gnd", x, y)
            self.assertTrue(bounds[0] <= text[0] <= text[2] <= bounds[2])
            self.assertTrue(bounds[1] <= text[1] <= text[3] <= bounds[3])

    def test_distinct_return_model_native_roundtrip(self):
        import os
        import subprocess
        import tempfile
        from pathlib import Path
        from .KiCadSchematicExporter import node, effects, S
        from .NetlistGenerator import NetlistTransform
        from .SchematicVerification import verify_schematic_netlist
        clis = tuple(filter(None, os.environ.get("PB_SCHEMATIC_TEST_KICAD_CLIS", "").split(os.pathsep)))
        if not clis:
            clis = tuple(filter(None, (os.environ.get("KICAD_CLI9"), os.environ.get("KICAD_CLI10"))))
        if not clis:
            self.skipTest("Set PB_SCHEMATIC_TEST_KICAD_CLIS for native split-return acceptance")
        compiled = ScalaCompiler.compile(SplitGroundBoard)
        compiled.append_values(RefdesRefinementPass().run(compiled))
        physical = {str(scope): netlist for scope, netlist in NetlistTransform(compiled).run().items()}
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            # Minimal zero-length standard ground power pin: instance Value
            # carries its compiled net name, exactly as the installed libraries.
            definition = node("symbol", "GND", node("power"), node("pin_names", node("offset", 0)),
                node("in_bom", S("yes")), node("on_board", S("yes")),
                node("property", "Reference", "#PWR", node("at", 0, 0, 0), effects(hide=True)),
                node("property", "Value", "GND", node("at", 0, -3.81, 0), effects()),
                node("symbol", "GND_0_1"),
                node("symbol", "GND_1_1", node("pin", S("power_in"), S("line"), node("at", 0, 0, 90),
                    node("length", 0), node("name", "GND", effects()), node("number", "1", effects()))))
            library = node("kicad_symbol_lib", node("version", 20241209), node("generator", S("kicad_symbol_editor")), definition)
            (folder / "power.kicad_sym").write_text(sexpdata.dumps(library), encoding="utf-8")
            bundle = KiCadSchematicExporter().export(compiled, SchematicExportOptions(
                "SplitGround", symbol_library_dirs=(str(folder),)))
            bundle.write(folder / "artifacts")
            for index, cli in enumerate(clis):
                for board in json.loads(bundle.files["manifest.json"])["boards"]:
                    with self.subTest(cli=cli):
                        schematic = folder / "artifacts" / board["root"]
                        xml = folder / ("native" + str(index) + ".xml")
                        result = subprocess.run([cli, "sch", "export", "netlist", "--format", "kicadxml", "-o", str(xml), str(schematic)],
                                                capture_output=True, text=True, timeout=60)
                        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                        verify_schematic_netlist(physical[board["scope"]], xml)
                        import xml.etree.ElementTree as ET
                        nets = ET.parse(xml).getroot().findall("./nets/net")
                        self.assertEqual({net.attrib["name"] for net in nets}, {"raw.gnd", "system.gnd"})
                        self.assertEqual(sorted(len(net.findall("node")) for net in nets), [1, 1])
                        svg = folder / ("svg" + str(index))
                        result = subprocess.run([cli, "sch", "export", "svg", "-o", str(svg), str(schematic)],
                                                capture_output=True, text=True, timeout=60)
                        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                        self.assertTrue(list(svg.glob("*.svg")))

    def test_invalid_paths_and_pins_fail(self):
        for data in [
            dict(components={"missing": {}}),
            dict(components={"part": dict(pin_names={"77": "GATE"})}),
            dict(interfaces=[dict(component="part", pin="77", name="Load")]),
            dict(groups={"missing": "Power"}),
        ]:
            with self.subTest(data=data), self.assertRaises(ValueError):
                KiCadSchematicExporter().export(
                    self.compiled,
                    SchematicExportOptions("Invalid", presentation=SchematicPresentation.from_dict(data)),
                )

    def test_strict_schema(self):
        for value in [
            dict(schema=True),
            dict(unknown=1),
            dict(components={"part": dict(footprint="wrong")}),
            dict(interfaces=[dict(component="part")]),
        ]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                SchematicPresentation.from_dict(value)

    def test_scene_text_checks(self):
        def text(value, x):
            return f'(text "{value}" (at {x} 50 0) (effects (font (size 1.27 1.27))) (uuid "{value}"))'

        report = inspect_documents(
            {"a.kicad_sch": "(kicad_sch " + text("alpha", 50) + text("beta", 50) + ")"},
            [],
        )
        self.assertTrue(any(f["code"] == "text_collision" for f in report["findings"]))
        self.assertEqual(report["visual_approval"], "pending")
        self.assertGreater(text_width("界", 1), text_width("a", 1))
        self.assertEqual(
            report,
            inspect_documents(
                {"a.kicad_sch": "(kicad_sch " + text("alpha", 50) + text("beta", 50) + ")"},
                [],
            ),
        )

    def test_pin_name_scene_uses_library_y_up_coordinates(self):
        for rotation in (0, 90):
            doc = (
                '(kicad_sch (lib_symbols (symbol "Test:Part" (symbol "Part_1_1" (pin passive line (at 0 5 0) (length 1) (name "PIN") (number "1"))))) (symbol (lib_id "Test:Part") (at 40 50 '
                + str(rotation)
                + ') (property "PBPath" "part")))'
            )
            report = inspect_documents({"a.kicad_sch": doc}, [])
            text = next(t for t in report["scenes"][0]["texts"] if t["kind"] == "pin_name")
            x1, y1, x2, y2 = text["bounds"]
            if rotation == 0:
                self.assertAlmostEqual((y1 + y2) / 2, 45)
                self.assertAlmostEqual(x1, 41.508)
            else:
                self.assertAlmostEqual((x1 + x2) / 2, 35)
                self.assertAlmostEqual(y2, 48.492)
