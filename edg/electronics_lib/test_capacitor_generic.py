import unittest

from .GenericCapacitor import *


class CapacitorGenericTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(GenericMlcc(
      capacitance=0.1 * uFarad(tol=0.2),
      voltage=(0, 3.3) * Volt
    ))
    (self.dummya, ), _ = self.chain(self.dut.pos, self.Block(DummyPassive()))
    (self.dummyb, ), _ = self.chain(self.dut.neg, self.Block(DummyPassive()))


class BigCapacitorGenericTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(GenericMlcc(
      capacitance=(50, 1000) * uFarad,
      voltage=(0, 5) * Volt
    ))
    (self.dummya, ), _ = self.chain(self.dut.pos, self.Block(DummyPassive()))
    (self.dummyb, ), _ = self.chain(self.dut.neg, self.Block(DummyPassive()))


class HighVoltageCapacitorGenericTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(GenericMlcc(
      capacitance=0.2 * uFarad(tol=0.2),
      voltage=(0, 20) * Volt
    ))
    (self.dummya, ), _ = self.chain(self.dut.pos, self.Block(DummyPassive()))
    (self.dummyb, ), _ = self.chain(self.dut.neg, self.Block(DummyPassive()))


class HighSingleCapacitorGenericTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(GenericMlcc(
      capacitance=22 * uFarad(tol=0.2),
      voltage=(0, 10) * Volt
    ))
    (self.dummya, ), _ = self.chain(self.dut.pos, self.Block(DummyPassive()))
    (self.dummyb, ), _ = self.chain(self.dut.neg, self.Block(DummyPassive()))


class MediumSingleCapacitorGenericTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(GenericMlcc(
      capacitance=2 * uFarad(tol=0.2),
      voltage=(0, 20) * Volt
    ))
    (self.dummya, ), _ = self.chain(self.dut.pos, self.Block(DummyPassive()))
    (self.dummyb, ), _ = self.chain(self.dut.neg, self.Block(DummyPassive()))

class DeratedCapacitorGenericTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(GenericMlcc(
      capacitance=1 * uFarad(tol=0.2),
      voltage=(0, 5) * Volt
    ))
    (self.dummya, ), _ = self.chain(self.dut.pos, self.Block(DummyPassive()))
    (self.dummyb, ), _ = self.chain(self.dut.neg, self.Block(DummyPassive()))

class BigMultiCapacitorGenericTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(GenericMlcc(
      capacitance=(50, 1000) * uFarad,
      voltage=(0, 5) * Volt
    ))
    (self.dummya, ), _ = self.chain(self.dut.pos, self.Block(DummyPassive()))
    (self.dummyb, ), _ = self.chain(self.dut.neg, self.Block(DummyPassive()))


class CapacitorTestCase(unittest.TestCase):
  def test_capacitor(self) -> None:
    compiled = ScalaCompiler.compile(CapacitorGenericTestTop)
    self.assertEqual(compiled.get_value(['dut', 'fp_footprint']), 'Capacitor_SMD:C_0402_1005Metric')
    self.assertEqual(compiled.get_value(['dut', 'fp_value']), '100nF')

  def test_capacitor_footprint(self) -> None:
    compiled = ScalaCompiler.compile(CapacitorGenericTestTop, Refinements(
      instance_values=[(['dut', 'footprint_spec'], 'Capacitor_SMD:C_1206_3216Metric')]
    ))
    self.assertEqual(compiled.get_value(['dut', 'fp_footprint']), 'Capacitor_SMD:C_1206_3216Metric')
    self.assertEqual(compiled.get_value(['dut', 'fp_value']), '100nF')

  def test_multi_capacitor(self) -> None:
    compiled = ScalaCompiler.compile(BigCapacitorGenericTestTop)
    self.assertEqual(compiled.get_value(['dut', 'c[0]', 'fp_footprint']), 'Capacitor_SMD:C_1206_3216Metric')
    self.assertEqual(compiled.get_value(['dut', 'c[0]', 'fp_value']), '22uF')
    self.assertEqual(compiled.get_value(['dut', 'c[1]', 'fp_footprint']), 'Capacitor_SMD:C_1206_3216Metric')
    self.assertEqual(compiled.get_value(['dut', 'c[1]', 'fp_value']), '22uF')
    self.assertEqual(compiled.get_value(['dut', 'c[2]', 'fp_footprint']), 'Capacitor_SMD:C_1206_3216Metric')
    self.assertEqual(compiled.get_value(['dut', 'c[2]', 'fp_value']), '22uF')
    self.assertEqual(compiled.get_value(['dut', 'c[3]', 'fp_footprint']), None)

  def test_high_voltage_capacitor(self) -> None:
    compiled = ScalaCompiler.compile(HighVoltageCapacitorGenericTestTop)
    self.assertEqual(compiled.get_value(['dut', 'fp_footprint']), 'Capacitor_SMD:C_0603_1608Metric')
    self.assertEqual(compiled.get_value(['dut', 'fp_value']), '220nF')

  def test_high_single_capacitor(self) -> None:
    compiled = ScalaCompiler.compile(HighSingleCapacitorGenericTestTop)
    self.assertEqual(compiled.get_value(['dut', 'fp_footprint']), 'Capacitor_SMD:C_1206_3216Metric')
    self.assertEqual(compiled.get_value(['dut', 'fp_value']), '22uF')

  def test_medium_single_capacitor(self) -> None:
    compiled = ScalaCompiler.compile(MediumSingleCapacitorGenericTestTop)
    self.assertEqual(compiled.get_value(['dut', 'fp_footprint']), 'Capacitor_SMD:C_0805_2012Metric')
    self.assertEqual(compiled.get_value(['dut', 'fp_value']), '2.2uF')

  def test_derated_capacitor(self) -> None:
    compiled = ScalaCompiler.compile(DeratedCapacitorGenericTestTop, Refinements(
      instance_values=[(['dut', 'footprint_spec'], 'Capacitor_SMD:C_1206_3216Metric'),
                       (['dut', 'derating_coeff'], 0.5),]
    ))
    self.assertEqual(compiled.get_value(['dut', 'fp_footprint']), 'Capacitor_SMD:C_1206_3216Metric')
    self.assertEqual(compiled.get_value(['dut', 'fp_value']), '2.2uF')

  def test_derated_multi_capacitor(self) -> None:
    compiled = ScalaCompiler.compile(BigMultiCapacitorGenericTestTop, Refinements(
      instance_values=[(['dut', 'footprint_spec'], 'Capacitor_SMD:C_1206_3216Metric'),
                       (['dut', 'derating_coeff'], 0.5),]
    ))
    self.assertEqual(compiled.get_value(['dut', 'c[0]', 'fp_footprint']), 'Capacitor_SMD:C_1206_3216Metric')
    self.assertEqual(compiled.get_value(['dut', 'c[0]', 'fp_value']), '22uF')
    self.assertEqual(compiled.get_value(['dut', 'c[1]', 'fp_footprint']), 'Capacitor_SMD:C_1206_3216Metric')
    self.assertEqual(compiled.get_value(['dut', 'c[1]', 'fp_value']), '22uF')
    self.assertEqual(compiled.get_value(['dut', 'c[2]', 'fp_footprint']), 'Capacitor_SMD:C_1206_3216Metric')
    self.assertEqual(compiled.get_value(['dut', 'c[2]', 'fp_value']), '22uF')
    self.assertEqual(compiled.get_value(['dut', 'c[3]', 'fp_footprint']), 'Capacitor_SMD:C_1206_3216Metric')
    self.assertEqual(compiled.get_value(['dut', 'c[3]', 'fp_value']), '22uF')
    self.assertEqual(compiled.get_value(['dut', 'c[4]', 'fp_footprint']), 'Capacitor_SMD:C_1206_3216Metric')
    self.assertEqual(compiled.get_value(['dut', 'c[4]', 'fp_value']), '22uF')
    self.assertEqual(compiled.get_value(['dut', 'c[5]', 'fp_footprint']), None)
