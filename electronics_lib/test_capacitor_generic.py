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
    self.assertEqual(compiled.get_value(['dut', 'c_0', 'footprint_name']), 'Capacitor_SMD:C_1206_3216Metric')
    self.assertEqual(compiled.get_value(['dut', 'c_0', 'value']), '22uF')
    self.assertEqual(compiled.get_value(['dut', 'c_1', 'footprint_name']), 'Capacitor_SMD:C_1206_3216Metric')
    self.assertEqual(compiled.get_value(['dut', 'c_1', 'value']), '22uF')
    self.assertEqual(compiled.get_value(['dut', 'c_2', 'footprint_name']), 'Capacitor_SMD:C_1206_3216Metric')
    self.assertEqual(compiled.get_value(['dut', 'c_2', 'value']), '22uF')
    self.assertEqual(compiled.get_value(['dut', 'c_3', 'footprint_name']), None)