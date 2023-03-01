import unittest

from electronics_model import *
from .AbstractPowerConverters import LinearRegulator
from .Categories import IdealModel
from .DummyDevices import DummyVoltageSource, DummyVoltageSink


class IdealCircuitTestTop(Block):
  def __init__(self):
    super().__init__()
    self.gnd = self.Block(DummyVoltageSource(0*Volt(tol=0)))
    self.pwr = self.Block(DummyVoltageSource(5*Volt(tol=0)))
    with self.implicit_connect(
        ImplicitConnect(self.gnd.pwr, [Common]),
    ) as imp:
      self.reg = imp.Block(LinearRegulator(5*Volt(tol=0)))
      self.connect(self.reg.pwr_in, self.pwr.pwr)
      self.reg_draw = self.Block(DummyVoltageSink(current_draw=1*Amp(tol=0)))
      self.connect(self.reg_draw.pwr, self.reg.pwr_out)

    self.require(self.pwr.current_drawn == 1*Amp(tol=0))


class IdealCircuitTest(unittest.TestCase):
  def test_ideal_circuit(self) -> None:
    compiled = ScalaCompiler.compile(IdealCircuitTestTop, refinements=Refinements(
      class_values=[(IdealModel, ['allow_ideal'], True)]
    ))
