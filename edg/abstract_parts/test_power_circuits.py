import unittest

from . import *
from .DummyDevices import DummyVoltageSource
from .PowerCircuits import RampLimiter


class RampLimiterTestTop(DesignTop):
  def __init__(self) -> None:
    super().__init__()
    self.dut = self.Block(RampLimiter())

    (self.dummyin, ), _ = self.chain(self.dut.pwr_in, self.Block(DummyVoltageSource(voltage_out=12*Volt(tol=0))))
    (self.dummyout, ), _ = self.chain(self.dut.pwr_out, self.Block(DummyVoltageSink(current_draw=1*Amp(tol=0))))
    (self.dummyctl, ), _ = self.chain(self.dut.control, self.Block(DummyDigitalSource(voltage_out=3.3*Volt(tol=0))))
    (self.dummygnd, ), _ = self.chain(self.dut.gnd, self.Block(DummyGround()))

  def refinements(self) -> Refinements:
    return Refinements(
      class_refinements=[
        (Resistor, GenericChipResistor),
        (Capacitor, GenericMlcc),
        (Fet, CustomFet),
        (SwitchFet, CustomFet),
      ], instance_values=[
        (['dut', 'drv', 'footprint_spec'], 'Package_TO_SOT_SMD:SOT-23'),
        (['dut', 'ctl_fet', 'footprint_spec'], 'Package_TO_SOT_SMD:SOT-23'),
        (['dut', 'drv', 'actual_gate_drive'], Range(1.0, 12)),
      ]
    )


class RampLimiterTest(unittest.TestCase):
  def test_ramp_limiter(self) -> None:
    ScalaCompiler.compile(RampLimiterTestTop)
