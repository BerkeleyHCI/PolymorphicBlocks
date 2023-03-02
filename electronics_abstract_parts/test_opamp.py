import unittest

from electronics_abstract_parts import Resistor
from electronics_model import *
from .DummyDevices import DummyVoltageSource, DummyAnalogSink
from .AbstractOpamp import Opamp
from .OpampCircuits import Amplifier


class AnalogSourceDummy(Block):
  def __init__(self):
    super().__init__()
    self.port = self.Port(AnalogSource(), [InOut])


class TestOpamp(Opamp):
  def contents(self):
    self.pwr.init_from(VoltageSink())
    self.gnd.init_from(Ground())
    self.inp.init_from(AnalogSink())
    self.inn.init_from(AnalogSink())
    self.out.init_from(AnalogSource())


class TestResistor(Resistor):
  def contents(self):
    super().contents()
    self.assign(self.actual_resistance, self.resistance)


class AmplifierTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(Amplifier(
      amplification=Range.from_tolerance(2, 0.05)
    ))
    (self.dummyin, ), _ = self.chain(self.dut.input, self.Block(AnalogSourceDummy()))
    (self.dummyref, ), _ = self.chain(self.dut.reference, self.Block(AnalogSourceDummy()))
    (self.dummyout, ), _ = self.chain(self.dut.output, self.Block(DummyAnalogSink()))
    (self.dummypwr, ), _ = self.chain(self.dut.pwr, self.Block(DummyVoltageSource()))
    (self.dummygnd, ), _ = self.chain(self.dut.gnd, self.Block(DummyVoltageSource()))


class OpampCircuitTest(unittest.TestCase):
  def test_opamp_amplifier(self) -> None:
    compiled = ScalaCompiler.compile(AmplifierTestTop, refinements=Refinements(
      class_refinements=[
        (Opamp, TestOpamp),
        (Resistor, TestResistor),
      ]
    ))

    self.assertEqual(compiled.get_value(['dut', 'r1', 'resistance']), Range.from_tolerance(100e3, 0.01))
    self.assertEqual(compiled.get_value(['dut', 'r2', 'resistance']), Range.from_tolerance(100e3, 0.01))
