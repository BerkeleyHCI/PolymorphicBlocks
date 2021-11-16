import unittest

from electronics_abstract_parts import Resistor
from electronics_model import *
from .AbstractOpamp import Amplifier, Opamp


# TODO DEDUP w/ one from test_passive_common
class AnalogSourceDummy(Block):
  def __init__(self):
    super().__init__()
    self.port = self.Port(AnalogSource(), [InOut])


class AnalogSinkDummy(Block):
  def __init__(self):
    super().__init__()
    self.port = self.Port(AnalogSink(), [InOut])


class VoltageDummy(Block):
  def __init__(self):
    super().__init__()
    self.port = self.Port(VoltageSource(), [InOut])


class TestOpamp(Opamp):
  pass


class TestResistor(Resistor):
  def contents(self):
    super().contents()
    self.assign(self.resistance, self.spec_resistance)


class AmplifierTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(Amplifier(
      amplification=Range.from_tolerance(2, 0.05)
    ))
    (self.dummyin, ), _ = self.chain(self.dut.input, self.Block(AnalogSourceDummy()))
    (self.dummyout, ), _ = self.chain(self.dut.output, self.Block(AnalogSinkDummy()))
    (self.dummypwr, ), _ = self.chain(self.dut.pwr, self.Block(VoltageDummy()))
    (self.dummygnd, ), _ = self.chain(self.dut.gnd, self.Block(VoltageDummy()))


class OpampCircuitTest(unittest.TestCase):
  def test_opamp_amplifier(self) -> None:
    compiled = ScalaCompiler.compile(AmplifierTestTop, refinements=Refinements(
      class_refinements=[
        (Opamp, TestOpamp),
        (Resistor, TestResistor),
      ]
    ))

    self.assertEqual(compiled.get_value(['dut', 'r1', 'spec_resistance']), Range.from_tolerance(100e3, 0.01))
    self.assertEqual(compiled.get_value(['dut', 'r2', 'spec_resistance']), Range.from_tolerance(100e3, 0.01))
