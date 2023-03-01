import unittest

from .GenericResistor import *


class ResistorTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(GenericChipResistor(
      resistance=1 * kOhm(tol=0.1),
      power=(0, 0)*Watt
    ))
    (self.dummya, ), _ = self.chain(self.dut.a, self.Block(DummyPassive()))
    (self.dummyb, ), _ = self.chain(self.dut.b, self.Block(DummyPassive()))


class PowerResistorTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(GenericChipResistor(
      resistance=1 * kOhm(tol=0.1),
      power=(0, .24)*Watt
    ))
    (self.dummya, ), _ = self.chain(self.dut.a, self.Block(DummyPassive()))
    (self.dummyb, ), _ = self.chain(self.dut.b, self.Block(DummyPassive()))


class NonE12ResistorTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(GenericChipResistor(
      resistance=8.06 * kOhm(tol=0.01),
      power=(0, 0)*Watt
    ))
    (self.dummya, ), _ = self.chain(self.dut.a, self.Block(DummyPassive()))
    (self.dummyb, ), _ = self.chain(self.dut.b, self.Block(DummyPassive()))


class ResistorTestCase(unittest.TestCase):
  def test_basic_resistor(self) -> None:
    compiled = ScalaCompiler.compile(ResistorTestTop)
    self.assertEqual(compiled.get_value(['dut', 'fp_footprint']), 'Resistor_SMD:R_0201_0603Metric')
    self.assertEqual(compiled.get_value(['dut', 'fp_value']), '1k, 1%, 0.05 W')

  def test_power_resistor(self) -> None:
    compiled = ScalaCompiler.compile(PowerResistorTestTop)
    self.assertEqual(compiled.get_value(['dut', 'fp_footprint']), 'Resistor_SMD:R_1206_3216Metric')
    self.assertEqual(compiled.get_value(['dut', 'fp_value']), '1k, 1%, 0.25 W')

  def test_non_e12_resistor(self) -> None:
    compiled = ScalaCompiler.compile(NonE12ResistorTestTop, Refinements(
      instance_values=[(['dut', 'series'], 0)]
    ))
    self.assertEqual(compiled.get_value(['dut', 'fp_footprint']), 'Resistor_SMD:R_0201_0603Metric')
    self.assertEqual(compiled.get_value(['dut', 'fp_value']), '8.06k, 1%, 0.05 W')

  def test_min_package(self) -> None:
    compiled = ScalaCompiler.compile(ResistorTestTop, Refinements(
      instance_values=[(['dut', 'smd_min_package'], '0603')]
    ))
    self.assertEqual(compiled.get_value(['dut', 'fp_footprint']), 'Resistor_SMD:R_0603_1608Metric')
    self.assertEqual(compiled.get_value(['dut', 'fp_value']), '1k, 1%, 0.1 W')

  def test_footprint(self) -> None:
    compiled = ScalaCompiler.compile(ResistorTestTop, Refinements(
      instance_values=[(['dut', 'footprint_spec'], 'Resistor_SMD:R_1206_3216Metric')]
    ))
    self.assertEqual(compiled.get_value(['dut', 'fp_footprint']), 'Resistor_SMD:R_1206_3216Metric')
    self.assertEqual(compiled.get_value(['dut', 'fp_value']), '1k, 1%, 0.25 W')
