import unittest

from electronics_abstract_parts import *
import electronics_abstract_parts
import electronics_model
from . import *
from . import Passives
from .Passives import SmtCeramicCapacitorGeneric
from .test_passive_common import *


class CapacitorGenericTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(SmtCeramicCapacitorGeneric(
      capacitance=0.1 * uFarad(tol=0.2),
      voltage=(0, 3.3) * Volt
    ))
    (self.dummya, ), _ = self.chain(self.dut.pos, self.Block(PassiveDummy()))
    (self.dummyb, ), _ = self.chain(self.dut.neg, self.Block(PassiveDummy()))


class BigCapacitorGenericTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(SmtCeramicCapacitorGeneric(
      capacitance=(50, 1000) * uFarad,
      voltage=(0, 3.3) * Volt
    ))
    (self.dummya, ), _ = self.chain(self.dut.pos, self.Block(PassiveDummy()))
    (self.dummyb, ), _ = self.chain(self.dut.neg, self.Block(PassiveDummy()))


class HighVoltageCapacitorGenericTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(SmtCeramicCapacitorGeneric(
      capacitance=0.2 * uFarad(tol=0.2),
      voltage=(0, 20) * Volt
    ))
    (self.dummya, ), _ = self.chain(self.dut.pos, self.Block(PassiveDummy()))
    (self.dummyb, ), _ = self.chain(self.dut.neg, self.Block(PassiveDummy()))


class HighSingleCapacitorGenericTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(SmtCeramicCapacitorGeneric(
      capacitance=22 * uFarad(tol=0.2),
      voltage=(0, 10) * Volt
    ))
    (self.dummya, ), _ = self.chain(self.dut.pos, self.Block(PassiveDummy()))
    (self.dummyb, ), _ = self.chain(self.dut.neg, self.Block(PassiveDummy()))


class MediumSingleCapacitorGenericTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(SmtCeramicCapacitorGeneric(
      capacitance=2 * uFarad(tol=0.2),
      voltage=(0, 20) * Volt
    ))
    (self.dummya, ), _ = self.chain(self.dut.pos, self.Block(PassiveDummy()))
    (self.dummyb, ), _ = self.chain(self.dut.neg, self.Block(PassiveDummy()))

class DeratedCapacitorGenericTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(SmtCeramicCapacitorGeneric(
      capacitance=11 * uFarad(tol=0.2),
      voltage=(0, 5) * Volt
    ))
    (self.dummya, ), _ = self.chain(self.dut.pos, self.Block(PassiveDummy()))
    (self.dummyb, ), _ = self.chain(self.dut.neg, self.Block(PassiveDummy()))


class CapacitorTestCase(unittest.TestCase):
  def test_capacitor(self) -> None:
    compiled = ScalaCompiler.compile(CapacitorGenericTestTop)
    self.assertEqual(compiled.get_value(['dut', 'footprint_name']), 'Capacitor_SMD:C_0603_1608Metric')
    self.assertEqual(compiled.get_value(['dut', 'value']), '100nF')

  def test_capacitor_footprint(self) -> None:
    compiled = ScalaCompiler.compile(CapacitorGenericTestTop, Refinements(
      instance_values=[(['dut', 'footprint_spec'], 'Capacitor_SMD:C_1206_3216Metric')]
    ))
    self.assertEqual(compiled.get_value(['dut', 'footprint_name']), 'Capacitor_SMD:C_1206_3216Metric')
    self.assertEqual(compiled.get_value(['dut', 'value']), '100nF')

  def test_multi_capacitor(self) -> None:
    compiled = ScalaCompiler.compile(BigCapacitorGenericTestTop)
    self.assertEqual(compiled.get_value(['dut', 'c[0]', 'footprint_name']), 'Capacitor_SMD:C_1206_3216Metric')
    self.assertEqual(compiled.get_value(['dut', 'c[0]', 'value']), '22uF')
    self.assertEqual(compiled.get_value(['dut', 'c[1]', 'footprint_name']), 'Capacitor_SMD:C_1206_3216Metric')
    self.assertEqual(compiled.get_value(['dut', 'c[1]', 'value']), '22uF')
    self.assertEqual(compiled.get_value(['dut', 'c[2]', 'footprint_name']), 'Capacitor_SMD:C_1206_3216Metric')
    self.assertEqual(compiled.get_value(['dut', 'c[2]', 'value']), '22uF')
    self.assertEqual(compiled.get_value(['dut', 'c[3]', 'footprint_name']), None)

  def test_high_voltage_capacitor(self) -> None:
    compiled = ScalaCompiler.compile(HighVoltageCapacitorGenericTestTop)
    self.assertEqual(compiled.get_value(['dut', 'footprint_name']), 'Capacitor_SMD:C_0603_1608Metric')
    self.assertEqual(compiled.get_value(['dut', 'value']), '220nF')

  def test_high_single_capacitor(self) -> None:
    compiled = ScalaCompiler.compile(HighSingleCapacitorGenericTestTop)
    self.assertEqual(compiled.get_value(['dut', 'footprint_name']), 'Capacitor_SMD:C_1210_3225Metric')
    self.assertEqual(compiled.get_value(['dut', 'value']), '22uF')

  def test_medium_single_capacitor(self) -> None:
    compiled = ScalaCompiler.compile(MediumSingleCapacitorGenericTestTop)
    self.assertEqual(compiled.get_value(['dut', 'footprint_name']), 'Capacitor_SMD:C_0805_2012Metric')
    self.assertEqual(compiled.get_value(['dut', 'value']), '2.2uF')

  def test_derated_capacitor(self) -> None:
    compiled = ScalaCompiler.compile(DeratedCapacitorGenericTestTop, Refinements(
      instance_values=[(['dut', 'footprint_spec'], 'Capacitor_SMD:C_1206_3216Metric'),
                       (['dut', 'derating_coeff'], 0.04),]
    ))
    self.assertEqual(compiled.get_value(['dut', 'footprint_name']), 'Capacitor_SMD:C_1206_3216Metric')
    self.assertEqual(compiled.get_value(['dut', 'value']), '10uF')