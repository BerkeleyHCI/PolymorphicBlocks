import unittest

from . import *
from .IoController import IoController
from .AbstractPowerConverters import LinearRegulator, BoostConverter
from .Categories import IdealModel
from .DummyDevices import DummyVoltageSource, DummyVoltageSink, DummyDigitalSink


class IdealCircuitTestTop(Block):
  def __init__(self):
    super().__init__()
    self.gnd = self.Block(DummyGround())
    self.pwr = self.Block(DummyVoltageSource(5*Volt(tol=0)))
    with self.implicit_connect(
        ImplicitConnect(self.gnd.gnd, [Common]),
    ) as imp:
      self.reg = imp.Block(LinearRegulator(2*Volt(tol=0)))
      self.connect(self.reg.pwr_in, self.pwr.pwr)
      self.reg_draw = self.Block(DummyVoltageSink(current_draw=1*Amp(tol=0)))
      self.connect(self.reg_draw.pwr, self.reg.pwr_out)

      self.boost = imp.Block(BoostConverter(4*Volt(tol=0)))
      self.connect(self.boost.pwr_in, self.reg.pwr_out)
      self.boost_draw = self.Block(DummyVoltageSink(current_draw=1*Amp(tol=0)))
      self.connect(self.boost_draw.pwr, self.boost.pwr_out)  # draws 2A from reg

      self.mcu = imp.Block(IoController())
      self.connect(self.mcu.pwr, self.reg.pwr_out)
      self.mcu_io = self.Block(DummyDigitalSink())
      self.connect(self.mcu_io.io, self.mcu.gpio.request('test'))

    self.require(self.pwr.current_drawn == 3*Amp(tol=0))
    self.require(self.reg_draw.voltage == 2*Volt(tol=0))


class IdealCircuitTest(unittest.TestCase):
  def test_ideal_circuit(self) -> None:
    ScalaCompiler.compile(IdealCircuitTestTop, refinements=Refinements(
      class_values=[(IdealModel, ['allow_ideal'], True)]
    ))
