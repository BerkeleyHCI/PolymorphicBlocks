"""The PB compile/export entry point must work without agentic-pcb installed."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class StandaloneSchematicTest(unittest.TestCase):
    def test_pb_cli_exports_without_agentic_pcb(self):
        # Use a fresh interpreter so an adapter already imported by another test
        # cannot conceal a reverse dependency. Block even optional imports.
        script = '''
import importlib.abc
import runpy
import sys

attempts = []

class NoAgenticPcb(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "agentic_pcb" or fullname.startswith("agentic_pcb."):
            attempts.append(fullname)
            raise AssertionError("PB export attempted to import its agent adapter: " + fullname)

assert not any(n == "agentic_pcb" or n.startswith("agentic_pcb.") for n in sys.modules)
sys.meta_path.insert(0, NoAgenticPcb())
sys.argv = ["examples.export_schematic", "--output", sys.argv[1]]
runpy.run_module("examples.export_schematic", run_name="__main__")
assert not attempts, "PB must not delegate export to its agent adapter: " + repr(attempts)
assert not any(n == "agentic_pcb" or n.startswith("agentic_pcb.") for n in sys.modules)
'''
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory, "export")
            result = subprocess.run(
                [sys.executable, "-c", script, str(output)],
                cwd=Path(__file__).resolve().parents[2],
                text=True, capture_output=True, timeout=120,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((output / "TestLed.net").is_file())
            bundle = output / "TestLed.schematic"
            manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["source"], "examples.test_blinky.TestLed")
            self.assertTrue(manifest["boards"])
            documents = [name for name in manifest["files"] if name.endswith(".kicad_sch")]
            self.assertTrue(documents)
            for name in documents:
                self.assertIn("SOURCE OF TRUTH", (bundle / name).read_text(encoding="utf-8"))
            for board in manifest["boards"]:
                self.assertIn(board["root"], documents)
            self.assertIn("symbol_coverage", manifest)
            for name in ("routing.json", "layout.json", "sheet-plan.json"):
                self.assertTrue((bundle / name).is_file())


if __name__ == "__main__":
    unittest.main()
