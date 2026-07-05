import unittest
from typing_extensions import override

from .PowerConditioning import DiodePowerMerge
from ..vendor_parts.generic import *
from ..abstract_parts import *


class DiodeMergeTestTop(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.dut = self.Block(DiodePowerMerge(voltage_drop=(0, 1) * Volt))
        self.srca = self.Block(DummyVoltageSource(voltage=(12, 14) * Volt)).connected(self.dut.pwr_ins.request())
        self.srcb = self.Block(DummyVoltageSource(voltage=(4, 5) * Volt)).connected(self.dut.pwr_ins.request())
        self.sink = self.Block(DummyVoltageSink(current_draw=(0.5, 1.5) * Amp)).connected(self.dut.pwr_out)

    @override
    def refinements(self) -> Refinements:
        return Refinements(
            class_refinements=[
                (Diode, CustomDiode),
            ],
            class_values=[
                (CustomDiode, ["part_footprint"], "Diode_SMD:D_SOD-123"),
            ],
        )


class DiodeMergeTestCase(unittest.TestCase):
    def test_diode_merge(self) -> None:
        compiled = ScalaCompiler.compile(DiodeMergeTestTop)

        self.assertEqual(compiled.get_value(["dut", "pwr_out", "voltage"]), Range(3.0, 14.0))
        self.assertEqual(compiled.get_value(["dut", "pwr_ins", "0", "current_draw"]), Range(0.5, 1.5))
        self.assertEqual(compiled.get_value(["dut", "pwr_ins", "1", "current_draw"]), Range(0.5, 1.5))
        self.assertEqual(compiled.get_value(["dut", "diodes[0]", "fp_footprint"]), "Diode_SMD:D_SOD-123")
        self.assertEqual(compiled.get_value(["dut", "diodes[0]", "current"]), Range(0.5, 1.5))
        self.assertEqual(compiled.get_value(["dut", "diodes[0]", "reverse_voltage"]), Range(0, 2.0))
        self.assertEqual(compiled.get_value(["dut", "diodes[1]", "fp_footprint"]), "Diode_SMD:D_SOD-123")
        self.assertEqual(compiled.get_value(["dut", "diodes[1]", "current"]), Range(0.5, 1.5))
        self.assertEqual(compiled.get_value(["dut", "diodes[1]", "reverse_voltage"]), Range(0, 10.0))
        self.assertEqual(compiled.get_value(["dut", "diodes[2]", "fp_footprint"]), None)  # doesn't exist
