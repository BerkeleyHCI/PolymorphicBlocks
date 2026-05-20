import unittest

from .JlcDiode import *
from .. import DiodePowerMerge, BoardTop


class DiodeMergeTestTop(BoardTop):
    def __init__(self) -> None:
        super().__init__()
        self.dut = self.Block(DiodePowerMerge(voltage_drop=(0, 1) * Volt))
        (self.srca,), _ = self.chain(
            self.dut.pwr_ins.request(), self.Block(DummyVoltageSource(voltage_out=(12, 14) * Volt))
        )
        (self.srcb,), _ = self.chain(
            self.dut.pwr_ins.request(), self.Block(DummyVoltageSource(voltage_out=(4, 5) * Volt))
        )
        (self.sink,), _ = self.chain(self.dut.pwr_out, self.Block(DummyVoltageSink(current_draw=(0.5, 1.5) * Amp)))

    @override
    def refinements(self) -> Refinements:
        return Refinements(
            class_refinements=[
                (Diode, CustomDiode),
            ],
            class_values=[
                (CustomDiode, ["footprint_spec"], "Diode_SMD:D_SOD-123"),
            ],
        )


class DiodeMergeTestCase(unittest.TestCase):
    def test_diode_merge(self) -> None:
        compiled = ScalaCompiler.compile(DiodeMergeTestTop)

        self.assertEqual(compiled.get_value(["dut", "pwr_out", "voltage_out"]), Range(3.0, 14.0))
        self.assertEqual(compiled.get_value(["dut", "pwr_ins", "0", "current_draw"]), Range(0.5, 1.5))
        self.assertEqual(compiled.get_value(["dut", "pwr_ins", "1", "current_draw"]), Range(0.5, 1.5))
        self.assertEqual(compiled.get_value(["dut", "diodes[0]", "fp_footprint"]), "Diode_SMD:D_SOD-123")
        self.assertEqual(compiled.get_value(["dut", "diodes[1]", "fp_footprint"]), "Diode_SMD:D_SOD-123")
        self.assertEqual(compiled.get_value(["dut", "diodes[2]", "fp_footprint"]), None)  # doesn't exist
