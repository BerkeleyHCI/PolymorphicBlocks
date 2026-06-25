import unittest

from typing_extensions import override

from ..abstract_parts import *
from ..vendor_parts.generic import *
from .PowerCircuits import RampLimiter


class RampLimiterTestTop(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.dut = self.Block(RampLimiter())

        self.dummygnd = self.Block(DummyGround()).connected(self.dut.gnd)
        self.dummyin = self.Block(DummyVoltageSource(voltage=12 * Volt(tol=0))).connected(self.dut.pwr_in)
        self.dummyout = self.Block(DummyVoltageSink(current_draw=1 * Amp(tol=0))).connected(self.dut.pwr_out)
        self.dummyctl = self.Block(DummyDigitalSource(voltage=3.3 * Volt(tol=0))).connected(self.dut.control)

    @override
    def refinements(self) -> Refinements:
        return Refinements(
            class_refinements=[
                (Resistor, GenericChipResistor),
                (Capacitor, GenericMlcc),
                (Fet, CustomFet),
                (SwitchFet, CustomFet),
            ],
            instance_values=[
                (["dut", "drv", "footprint_spec"], "Package_TO_SOT_SMD:SOT-23"),
                (["dut", "ctl_fet", "footprint_spec"], "Package_TO_SOT_SMD:SOT-23"),
                (["dut", "drv", "actual_gate_drive"], Range(1.0, 12)),
            ],
        )


class RampLimiterTest(unittest.TestCase):
    def test_ramp_limiter(self) -> None:
        ScalaCompiler.compile(RampLimiterTestTop)
