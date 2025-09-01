import unittest

from . import *
from .DummyDevices import DummyVoltageSource
from .PowerCircuits import RampLimiter


class RampLimiterTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(RampLimiter())

    (self.dummyin, ), _ = self.chain(self.dut.pwr_in, self.Block(DummyVoltageSource(voltage_out=12*Volt(tol=0))))
    (self.dummyout, ), _ = self.chain(self.dut.pwr_out, self.Block(DummyVoltageSink(current_draw=1*Amp(tol=0))))
    (self.dummygnd, ), _ = self.chain(self.dut.gnd, self.Block(DummyGround()))


class RampLimiterTest(unittest.TestCase):
  def test_opamp_amplifier(self) -> None:
    compiled = ScalaCompiler.compile(RampLimiterTestTop, refinements=Refinements(
      class_refinements=[
      ]
    ))
