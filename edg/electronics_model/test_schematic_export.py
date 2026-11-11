"""Exporter tests use real compiled connectivity, independent of KiCad installation."""

import json
import tempfile
import unittest
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import sexpdata

from ..core import ScalaCompiler, GeneratorBlock, Block
from .CircuitBlock import FootprintBlock
from .PassivePort import Passive
from ..electronics_interfaces.test_netlist import TestBasicCircuit
from .NetlistGenerator import NetlistTransform
from .SchematicVerification import verify_schematic_netlist
from .RefdesRefinementPass import RefdesRefinementPass
from .KiCadSchematicExporter import (
    KiCadSchematicExporter,
    SchematicExportOptions,
    SchematicExport,
    SchematicPlacement,
    PhysicalComponent,
    SymbolResolver,
    children,
    NOTICE,
    generic,
)


class GeneratedMappedPart(GeneratorBlock, FootprintBlock):
    def __init__(self):
        super().__init__()
        self.a = self.Port(Passive(), optional=True)
        self.b = self.Port(Passive(), optional=True)

    def generate(self):
        super().generate()
        self.footprint(
            "R", "Resistor_SMD:R_0603_1608Metric", {"1": self.a, "2": self.b}, value="Long supplier description " * 8
        )
        self.schematic_symbol("Device:R", {"1": "1", "2": "2"})


class GeneratedMappedBoard(Block):
    def contents(self):
        super().contents()
        self.part = self.Block(GeneratedMappedPart())


class ManyGroupsBoard(Block):
    def contents(self):
        super().contents()
        for index in range(41):
            setattr(self, "group" + str(index), self.Block(GeneratedMappedBoard()))


class SchematicExportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.compiled = ScalaCompiler.compile(TestBasicCircuit)
        cls.compiled.append_values(RefdesRefinementPass().run(cls.compiled))

    def test_manifest_symbol_coverage_has_compiled_identity_and_fallback_reason(self):
        result = KiCadSchematicExporter().export(self.compiled, SchematicExportOptions("Coverage"))
        coverage = json.loads(result.files["manifest.json"])["symbol_coverage"]
        expected = {str(b.full_path) for n in NetlistTransform(self.compiled).run().values() for b in n.blocks}
        self.assertEqual({entry["component"] for entry in coverage}, expected)
        for entry in coverage:
            self.assertTrue(entry["compiled_class"])
            self.assertEqual(entry["status"], "fallback")
            self.assertEqual(entry["category"], "missing_mapping")
            self.assertEqual(entry["reason"], "no schematic symbol mapping")

    def test_explicit_mapping_precedence_and_failure_evidence(self):
        from unittest.mock import patch
        compiled = ScalaCompiler.compile(GeneratedMappedBoard)
        compiled.append_values(RefdesRefinementPass().run(compiled))
        for error, category in ((FileNotFoundError("Device:R"), "missing_library"),
                                (KeyError("R"), "missing_symbol"),
                                (LookupError("multi-unit symbol unsupported"), "unsupported_multi_unit"),
                                (LookupError("stacked or repeated symbol pins unsupported"), "unsupported_symbol")):
            with self.subTest(category=category), patch(
                    "edg.electronics_model.KiCadSymbolRegistry.infer_symbol", side_effect=AssertionError("explicit mapping replaced")), patch.object(
                    SymbolResolver, "resolve", side_effect=error):
                result = KiCadSchematicExporter().export(compiled, SchematicExportOptions("Coverage"))
                entry, = json.loads(result.files["manifest.json"])["symbol_coverage"]
                self.assertEqual(entry["mapping_source"], "explicit")
                self.assertEqual(entry["lib_id"], "Device:R")
                self.assertEqual(entry["category"], category)
                self.assertEqual(entry["status"], "fallback")
        with patch.object(SymbolResolver, "resolve", side_effect=ValueError("unmapped library pin 3")):
            with self.assertRaisesRegex(ValueError, "unmapped library pin"):
                KiCadSchematicExporter().export(compiled, SchematicExportOptions("Invalid"))

    def test_generated_symbol_metadata_and_long_description(self):
        compiled = ScalaCompiler.compile(GeneratedMappedBoard)
        compiled.append_values(RefdesRefinementPass().run(compiled))
        result = KiCadSchematicExporter().export(compiled, SchematicExportOptions("GeneratedMappedPart"))
        symbols = [
            symbol
            for name, content in result.files.items()
            if name.endswith(".kicad_sch")
            for symbol in children(sexpdata.loads(content), "symbol")
        ]
        self.assertEqual(len(symbols), 1)
        properties = {prop[1]: prop[2] for prop in children(symbols[0], "property")}
        self.assertEqual(properties["Value"], "Long supplier description " * 8)
        self.assertIn("\n", properties["PBDisplayValue"])

    def test_oversized_optimized_route_retains_fitting_baseline(self):
        from unittest import mock
        from .KiCadSchematicRouting import route_metrics
        def oversized(placed, views, nets, baseline, router):
            metric = route_metrics(baseline[0], baseline[2])
            candidate = (baseline[0] + [("oversized-trial", (15, 40), (400, 40))], baseline[1], baseline[2])
            return candidate, dict(before=metric, after=metric, selected="trial", candidates=2)
        with mock.patch("edg.electronics_model.KiCadSchematicRouting.optimize_fixed_routes", oversized):
            result = KiCadSchematicExporter().export(self.compiled, SchematicExportOptions("PageFit"))
        self.assertIn('rejected_for_page_fit', result.files['routing.json'])
        self.assertNotIn('oversized-trial', ''.join(v for k, v in result.files.items() if k.endswith('.kicad_sch')))

    def test_paginated_index_hierarchy(self):
        compiled = ScalaCompiler.compile(ManyGroupsBoard)
        compiled.append_values(RefdesRefinementPass().run(compiled))
        consolidated = KiCadSchematicExporter().export(compiled, SchematicExportOptions("ManyGroupsBoard"))
        self.assertLess(sum(name.endswith(".kicad_sch") for name in consolidated.files), 41)
        result = KiCadSchematicExporter().export(
            compiled,
            SchematicExportOptions(
                "ManyGroupsBoard", sheet_assignments={"group" + str(i): "Explicit sheet " + str(i) for i in range(41)}
            ),
        )
        self.assertEqual(len([name for name in result.files if "_contents_" in name]), 2)
        self.assertEqual(
            sum(
                len(children(sexpdata.loads(content), "symbol"))
                for name, content in result.files.items()
                if name.endswith(".kicad_sch")
            ),
            41,
        )
        if shutil.which("kicad-cli"):
            with tempfile.TemporaryDirectory() as directory:
                result.write(Path(directory))
                root = next(
                    name
                    for name in result.files
                    if name.endswith(".kicad_sch") and len(Path(name).stem.split("_")) == 2
                )
                output = Path(directory, "roundtrip.xml")
                subprocess.run(
                    [
                        "kicad-cli",
                        "sch",
                        "export",
                        "netlist",
                        "--format",
                        "kicadxml",
                        "-o",
                        str(output),
                        str(Path(directory, root)),
                    ],
                    check=True,
                    capture_output=True,
                    timeout=45,
                )
                verify_schematic_netlist(next(iter(NetlistTransform(compiled).run().values())), output)

    def test_large_generic_symbol_has_centered_two_sided_pins(self):
        component = PhysicalComponent(
            "mcu", "U1", "Package:QFP", "mcu", {str(i): "gpio" + str(i) for i in range(1, 97)}, None, "mcu"
        )
        view = generic(component)
        self.assertEqual(len(view.pins), 96)
        self.assertTrue(any(p[1] < 0 for p in view.pins))
        self.assertTrue(any(p[1] > 0 for p in view.pins))
        self.assertLess(max(p[2] for p in view.pins) - min(p[2] for p in view.pins), 180)

    def test_compiled_export_deterministic(self):
        exporter = KiCadSchematicExporter()
        options = SchematicExportOptions("TestBasicCircuit", source="test.TestBasicCircuit")
        first = exporter.export(self.compiled, options)
        self.assertEqual(first.files, exporter.export(self.compiled, options).files)
        self.assertTrue(first.diagnostics)
        symbols = []
        for name, content in first.files.items():
            if name.endswith(".kicad_sch"):
                self.assertIn(NOTICE, content)
                tree = sexpdata.loads(content)
                symbols.extend(children(tree, "symbol"))
        self.assertGreater(len(symbols), 0)
        self.assertEqual(len(symbols), len({children(s, "uuid")[0][1] for s in symbols}))

    def test_scope_and_wrapper_preservation(self):
        from ..electronics_interfaces.test_netlist_subboard import TestSubboardCircuit
        from ..electronics_interfaces.test_netlist_subboard_wrapper import TestWrapperCircuit
        from ..electronics_interfaces.test_netlist_subboard_array import TestArrayWrapperCircuit

        for design in (TestSubboardCircuit, TestWrapperCircuit, TestArrayWrapperCircuit):
            with self.subTest(design=design.__name__):
                compiled = ScalaCompiler.compile(design)
                compiled.append_values(RefdesRefinementPass().run(compiled))
                expected = NetlistTransform(compiled).run()
                bundle = KiCadSchematicExporter().export(compiled, SchematicExportOptions(design.__name__))
                roots = [n for n in bundle.files if n.endswith(".kicad_sch") and len(Path(n).stem.split("_")) == 2]
                self.assertEqual(len(roots), len(expected))
                actual_count = sum(
                    len(children(sexpdata.loads(content), "symbol"))
                    for name, content in bundle.files.items()
                    if name.endswith(".kicad_sch")
                )
                self.assertEqual(actual_count, sum(len(n.blocks) for n in expected.values()))

    def test_missing_python_placement_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing components"):
            KiCadSchematicExporter().export(
                self.compiled,
                SchematicExportOptions("Test", placements={"nonexistent": SchematicPlacement("Circuit", 60, 80)}),
            )

    def test_python_placement_rotation_and_reflection(self):
        options = SchematicExportOptions(
            "Hinted",
            placements={
                "source": SchematicPlacement("Circuit", 70, 90, 90, True),
                "sink": SchematicPlacement("Circuit", 140, 90, 270),
            },
        )
        result = KiCadSchematicExporter().export(self.compiled, options)
        physical = [
            symbol
            for name, content in result.files.items()
            if name.endswith(".kicad_sch")
            for symbol in children(sexpdata.loads(content), "symbol")
        ]
        self.assertEqual(len(physical), 2)
        if shutil.which("kicad-cli"):
            with tempfile.TemporaryDirectory() as directory:
                result.write(Path(directory))
                root = next(
                    name
                    for name in result.files
                    if name.endswith(".kicad_sch") and len(Path(name).stem.split("_")) == 2
                )
                output = Path(directory, "roundtrip.xml")
                subprocess.run(
                    [
                        "kicad-cli",
                        "sch",
                        "export",
                        "netlist",
                        "--format",
                        "kicadxml",
                        "-o",
                        str(output),
                        str(Path(directory, root)),
                    ],
                    check=True,
                    capture_output=True,
                    timeout=45,
                )
                verify_schematic_netlist(next(iter(NetlistTransform(self.compiled).run().values())), output)

    def test_physical_inventory_and_wires(self):
        bundle = KiCadSchematicExporter().export(self.compiled, SchematicExportOptions("Test"))
        expected = next(iter(NetlistTransform(self.compiled).run().values()))
        expected_pins = {
            b.refdes: set(v.split("=", 1)[0] for v in self.compiled.get_value(b.full_path.to_tuple() + ("fp_pinning",)))
            for b in expected.blocks
        }
        actual = {}
        wire_count = 0
        for name, content in bundle.files.items():
            if not name.endswith(".kicad_sch"):
                continue
            tree = sexpdata.loads(content)
            wire_count += len(children(tree, "wire"))
            for symbol in children(tree, "symbol"):
                props = {p[1]: p[2] for p in children(symbol, "property")}
                actual[props["Reference"]] = {p[1] for p in children(symbol, "pin")}
        self.assertEqual(actual, expected_pins)
        self.assertGreaterEqual(wire_count, sum(len(n.pins) for n in expected.nets))

    @unittest.skipUnless(shutil.which("kicad-cli"), "KiCad CLI not installed")
    def test_native_round_trip(self):
        bundle = KiCadSchematicExporter().export(self.compiled, SchematicExportOptions("Test"))
        with tempfile.TemporaryDirectory() as directory:
            bundle.write(Path(directory))
            root = next(
                name for name in bundle.files if name.endswith(".kicad_sch") and len(Path(name).stem.split("_")) == 2
            )
            output = Path(directory, "roundtrip.xml")
            subprocess.run(
                [
                    "kicad-cli",
                    "sch",
                    "export",
                    "netlist",
                    "--format",
                    "kicadxml",
                    "-o",
                    str(output),
                    str(Path(directory, root)),
                ],
                check=True,
                capture_output=True,
            )
            verify_schematic_netlist(next(iter(NetlistTransform(self.compiled).run().values())), output)

    def test_checker_rejects_merged_nets(self):
        expected = next(iter(NetlistTransform(self.compiled).run().values()))
        root = ET.Element("export")
        comps = ET.SubElement(root, "components")
        parts = ET.SubElement(root, "libparts")
        for block in expected.blocks:
            c = ET.SubElement(comps, "comp", ref=block.refdes)
            ET.SubElement(c, "footprint").text = block.footprint
            ET.SubElement(c, "libsource", lib="Test", part=block.refdes)
            part = ET.SubElement(parts, "libpart", lib="Test", part=block.refdes)
            pins = ET.SubElement(part, "pins")
            for pin in self.compiled.get_value(block.full_path.to_tuple() + ("fp_pinning",)):
                ET.SubElement(pins, "pin", num=pin.split("=", 1)[0])
        nets = ET.SubElement(root, "nets")
        refs = {str(b.full_path): b.refdes for b in expected.blocks}
        for net in expected.nets:
            n = ET.SubElement(nets, "net")
            for pin in net.pins:
                ET.SubElement(n, "node", ref=refs[str(pin.block_path)], pin=pin.pin_name)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory, "net.xml")
            ET.ElementTree(root).write(output)
            verify_schematic_netlist(expected, output)
            entries = list(nets)
            self.assertGreaterEqual(len(entries), 2)
            entries[0].extend(list(entries[1]))
            nets.remove(entries[1])
            ET.ElementTree(root).write(output)
            with self.assertRaises(ValueError):
                verify_schematic_netlist(expected, output)

    def test_compile_opt_in_and_generate_false(self):
        from ..BoardCompiler import compile_board

        with tempfile.TemporaryDirectory() as directory:
            target = (directory, "Test")
            compile_board(TestBasicCircuit, target)
            netlist = Path(directory, "Test.net").read_bytes()
            self.assertFalse(Path(directory, "Test.schematic").exists())
            compile_board(TestBasicCircuit, target, schematic=SchematicExportOptions("Test"))
            self.assertEqual(Path(directory, "Test.net").read_bytes(), netlist)
            self.assertTrue(Path(directory, "Test.schematic", "manifest.json").exists())
        result = compile_board(TestBasicCircuit, None, schematic=SchematicExportOptions("Test"))
        self.assertFalse(result.errors)

    def test_write_preserves_unowned_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "keep.txt").write_text("user")
            (root / "old.kicad_sch").write_text("old")
            (root / "manifest.json").write_text(json.dumps({"files": ["old.kicad_sch"]}))
            SchematicExport({"new.kicad_sch": "new", "manifest.json": '{"files": ["new.kicad_sch"]}'}, []).write(root)
            self.assertTrue((root / "keep.txt").exists())
            self.assertFalse((root / "old.kicad_sch").exists())

    def test_write_rolls_back_replacement_and_cleanup_failures(self):
        import os
        from unittest.mock import patch

        for failure in ("a.kicad_sch", "b.kicad_sch", "old.kicad_sch", "manifest.json"):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                original = {
                    "b.kicad_sch": b"old B",
                    "old.kicad_sch": b"obsolete sheet",
                    "keep.txt": b"user content",
                    "manifest.json": json.dumps({"files": ["b.kicad_sch", "old.kicad_sch"]}).encode(),
                }
                for name, content in original.items():
                    (root / name).write_bytes(content)
                bundle = SchematicExport({
                    "a.kicad_sch": "new A", "b.kicad_sch": "new B",
                    "manifest.json": json.dumps({"files": ["a.kicad_sch", "b.kicad_sch"]}),
                }, [])
                real_replace, real_unlink = os.replace, Path.unlink

                def replace(source, destination):
                    if Path(source).parent.name == "incoming" and Path(destination).name == failure:
                        raise OSError("injected replacement failure")
                    return real_replace(source, destination)

                def unlink(path, *args, **kwargs):
                    if path == root / failure and failure == "old.kicad_sch":
                        raise OSError("injected cleanup failure")
                    return real_unlink(path, *args, **kwargs)

                with patch("os.replace", replace), patch.object(Path, "unlink", unlink):
                    with self.assertRaisesRegex(OSError, "injected"):
                        bundle.write(root)
                self.assertEqual({p.name: p.read_bytes() for p in root.iterdir()}, original)
                # A retry must complete normally and retire only owned stale files.
                bundle.write(root)
                self.assertEqual((root / "keep.txt").read_bytes(), original["keep.txt"])
                self.assertFalse((root / "old.kicad_sch").exists())
                for name, content in bundle.files.items():
                    self.assertEqual((root / name).read_text(), content)

    def test_write_staging_failure_does_not_touch_existing_bundle(self):
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = {"a.kicad_sch": b"old A", "manifest.json": b'{"files": ["a.kicad_sch"]}'}
            for name, content in original.items():
                (root / name).write_bytes(content)
            real_write = Path.write_text

            def write(path, *args, **kwargs):
                if path.parent.name == "incoming" and path.name == "b.kicad_sch":
                    raise OSError("injected staging failure")
                return real_write(path, *args, **kwargs)

            with patch.object(Path, "write_text", write):
                with self.assertRaisesRegex(OSError, "injected staging failure"):
                    SchematicExport({"a.kicad_sch": "new A", "b.kicad_sch": "new B"}, []).write(root)
            self.assertEqual({p.name: p.read_bytes() for p in root.iterdir()}, original)

    def test_write_retains_backups_if_rollback_fails(self):
        import os
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "a.kicad_sch").write_text("old A")
            (root / "manifest.json").write_text('{"files": ["a.kicad_sch"]}')
            real_replace = os.replace

            def replace(source, destination):
                if Path(destination).name == "manifest.json" or Path(source).parent.name == "backup":
                    raise OSError("injected persistent failure")
                return real_replace(source, destination)

            with patch("os.replace", replace):
                with self.assertRaisesRegex(RuntimeError, "recovery files retained"):
                    SchematicExport({"a.kicad_sch": "new A", "manifest.json": "{}"}, []).write(root)
            recovery, = root.glob(".schematic-recovery-*")
            self.assertEqual((recovery / "backup" / "a.kicad_sch").read_text(), "old A")
            self.assertEqual((root / "manifest.json").read_text(), '{"files": ["a.kicad_sch"]}')

    def test_library_inheritance_and_mapping_validation(self):
        library = """(kicad_symbol_lib (version 20241209) (generator test)
          (symbol "Base" (symbol "Base_1_1"
            (pin passive line (at 0 0 0) (length 2.54) (name "A") (number "1"))))
          (symbol "Child" (extends "Base")))"""
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "Test.kicad_sym").write_text(library)
            component = PhysicalComponent(
                "test", "U1", "Test:FP", "test", {"7": "a"}, {"lib_id": "Test:Child", "pinning": {"1": "7"}}, "test"
            )
            resolver = SymbolResolver([directory])
            view = resolver.resolve(component)
            self.assertEqual(view.pins[0][0], "7")
            component.mapping["pinning"]["1"] = "8"
            with self.assertRaises(ValueError):
                resolver.resolve(component)


if __name__ == "__main__":
    unittest.main()
