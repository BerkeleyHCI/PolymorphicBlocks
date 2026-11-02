"""Presentation descriptions cannot alter physical inventory or net identity."""

import json
import unittest
from dataclasses import replace
from .KiCadSchematicPresentation import SchematicPresentation
from .KiCadSchematicReadability import inspect_documents, text_width
from .KiCadSchematicExporter import (
    KiCadSchematicExporter,
    SchematicExportOptions,
    children,
)
from .test_schematic_export import GeneratedMappedBoard
from .RefdesRefinementPass import RefdesRefinementPass
from ..core import ScalaCompiler
import sexpdata


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
