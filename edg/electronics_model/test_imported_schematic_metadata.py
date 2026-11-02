"""Imported symbol meaning survives compilation without changing physical connectivity."""

import json
import unittest

from ..core import Block, ScalaCompiler
from .CircuitBlock import FootprintBlock
from .KiCadSchematicBlock import KiCadBlackbox
from .PassivePort import Passive


class ImportedMetadataBoard(Block):
    def contents(self):
        super().contents()
        self.imported = self.Block(
            KiCadBlackbox(
                ["1", "2", "3"],
                "U",
                "Test:Package",
                "Test:Amplifier",
                "Part",
                "",
                kicad_pin_names=["1=IN+", "2=OUT", "3=GND"],
            )
        )
        self.graphic = self.Block(KiCadBlackbox([], "SYM", "Test:Graphic", "Graphic:Logo", "Logo", ""))


class ImportedSchematicMetadataTest(unittest.TestCase):
    def test_blackbox_metadata_and_physical_inventory(self):
        compiled = ScalaCompiler.compile(ImportedMetadataBoard)
        metadata = json.loads(compiled.get_value(("imported", "sch_symbol")))
        self.assertEqual(
            metadata,
            {
                "lib_id": "Test:Amplifier",
                "pinning": {"1": "1", "2": "2", "3": "3"},
                "pin_names": {"1": "IN+", "2": "OUT", "3": "GND"},
            },
        )
        self.assertEqual(
            compiled.get_value(("imported", "fp_pinning")),
            ["1=ports.1", "2=ports.2", "3=ports.3"],
        )
        self.assertFalse(compiled.get_value(("graphic", "sch_symbol")))

    def test_real_import_keeps_hx711_pin_meaning(self):
        from examples.test_blinky import TestBlinkyWithModeledSchematicImport

        compiled = ScalaCompiler.compile(TestBlinkyWithModeledSchematicImport)
        metadata = json.loads(compiled.get_value(("sense", "U1", "sch_symbol")))
        self.assertEqual(metadata["lib_id"], "Analog_ADC:HX711")
        self.assertEqual(set(metadata["pinning"]), {str(i) for i in range(1, 17)})
        self.assertIn("DOUT", metadata["pin_names"].values())
        self.assertIn("INA+", metadata["pin_names"].values())
        self.assertIn("INA-", metadata["pin_names"].values())

    def test_invalid_physical_pin_names_rejected(self):
        block = FootprintBlock()
        with self.assertRaisesRegex(ValueError, "mapped physical pads"):
            block.schematic_symbol("Device:R", {"1": "3", "2": "4"}, pin_names={"1": "a"})
        with self.assertRaisesRegex(ValueError, "string pin numbers"):
            block.schematic_symbol("Device:R", {1: "3"})


if __name__ == "__main__":
    unittest.main()
