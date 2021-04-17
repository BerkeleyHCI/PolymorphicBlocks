from typing import *
import unittest

from electronics_abstract_parts import *
import electronics_model
import electronics_abstract_parts
from .test_passive_common import *
from . import *


class ResistorTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(ChipResistor(
      resistance=1 * kOhm(tol=0.1),
      power=(0, 0)*Watt
    ))
    (self.dummya, ), _ = self.chain(self.dut.a, self.Block(PassiveDummy()))
    (self.dummyb, ), _ = self.chain(self.dut.b, self.Block(PassiveDummy()))


class PowerResistorTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(ChipResistor(
      resistance=1 * kOhm(tol=0.1),
      power=(0, .24)*Watt
    ))
    (self.dummya, ), _ = self.chain(self.dut.a, self.Block(PassiveDummy()))
    (self.dummyb, ), _ = self.chain(self.dut.b, self.Block(PassiveDummy()))


class NonE12ResistorTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(ChipResistor(
      resistance=8.06 * kOhm(tol=0.01),
      power=(0, 0)*Watt
    ))
    (self.dummya, ), _ = self.chain(self.dut.a, self.Block(PassiveDummy()))
    (self.dummyb, ), _ = self.chain(self.dut.b, self.Block(PassiveDummy()))


class ResistorTestCase(unittest.TestCase):
  def test_basic_resistor(self) -> None:
    compiled = ScalaCompiler.compile(ResistorTestTop)
    self.assertEqual(compiled.get_value(['dut', 'footprint_name']), 'Resistor_SMD:R_0603_1608Metric')
    self.assertEqual(compiled.get_value(['dut', 'value']), '1k, 1%, 0.1W')

  def test_power_resistor(self) -> None:
    compiled = ScalaCompiler.compile(PowerResistorTestTop)
    self.assertEqual(compiled.get_value(['dut', 'footprint_name']), 'Resistor_SMD:R_1206_3216Metric')
    self.assertEqual(compiled.get_value(['dut', 'value']), '1k, 1%, 0.25W')

  def test_non_e12_resistor(self) -> None:
    compiled = ScalaCompiler.compile(NonE12ResistorTestTop)
    self.assertEqual(compiled.get_value(['dut', 'footprint_name']), 'Resistor_SMD:R_0603_1608Metric')
    self.assertEqual(compiled.get_value(['dut', 'value']), '8.06k, 1%, 0.1W')

  def test_footprint(self) -> None:
    compiled = ScalaCompiler.compile(ResistorTestTop, Refinements(
      instance_values=[(['dut', 'footprint_spec'], 'Resistor_SMD:R_1206_3216Metric')]
    ))
    self.assertEqual(compiled.get_value(['dut', 'footprint_name']), 'Resistor_SMD:R_1206_3216Metric')
    self.assertEqual(compiled.get_value(['dut', 'value']), '1k, 1%, 0.25W')
