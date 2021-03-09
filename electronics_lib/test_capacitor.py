import unittest

from electronics_abstract_parts import *
import electronics_abstract_parts
import electronics_model
from . import *
from . import Passives
from .test_passive_common import *


class CapacitorTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(SmtCeramicCapacitor(
      capacitance=0.1 * uFarad(tol=0.2),
      voltage=(0, 3.3) * Volt
    ))
    (self.dummya, ), _ = self.chain(self.dut.pos, self.Block(PassiveDummy()))
    (self.dummyb, ), _ = self.chain(self.dut.neg, self.Block(PassiveDummy()))


class BigCapacitorTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(SmtCeramicCapacitor(
      capacitance=(50, 1000) * uFarad,
      voltage=(0, 3.3) * Volt
    ))
    (self.dummya, ), _ = self.chain(self.dut.pos, self.Block(PassiveDummy()))
    (self.dummyb, ), _ = self.chain(self.dut.neg, self.Block(PassiveDummy()))


class CapacitorTestCase(unittest.TestCase):
  def test_capacitor(self) -> None:
    compiled = ScalaCompiler.compile(CapacitorTestTop)
    self.assertEqual(compiled.get_value(['dut', 'footprint_name']), 'Capacitor_SMD:C_0603_1608Metric')
    self.assertEqual(compiled.get_value(['dut', 'part']), 'CL10B104KB8NNNC')
    self.assertEqual(compiled.get_value(['dut', 'value']), '0.1µF, 50V')

  def test_capacitor_part(self) -> None:
    compiled = ScalaCompiler.compile(CapacitorTestTop, Refinements(
      instance_values=[(['dut', 'part_spec'], 'CL31B104KBCNNNC')]
    ))
    self.assertEqual(compiled.get_value(['dut', 'footprint_name']), 'Capacitor_SMD:C_1206_3216Metric')
    self.assertEqual(compiled.get_value(['dut', 'part']), 'CL31B104KBCNNNC')
    self.assertEqual(compiled.get_value(['dut', 'value']), '0.1µF, 50V')

  def test_capacitor_footprint(self) -> None:
    compiled = ScalaCompiler.compile(CapacitorTestTop, Refinements(
      instance_values=[(['dut', 'footprint_spec'], 'Capacitor_SMD:C_1206_3216Metric')]
    ))
    self.assertEqual(compiled.get_value(['dut', 'footprint_name']), 'Capacitor_SMD:C_1206_3216Metric')
    self.assertEqual(compiled.get_value(['dut', 'part']), 'CL31B104KBCNNNC')
    self.assertEqual(compiled.get_value(['dut', 'value']), '0.1µF, 50V')

  def test_multi_capacitor(self) -> None:
    compiled = ScalaCompiler.compile(BigCapacitorTestTop)
    self.assertEqual(compiled.get_value(['dut', 'c[0]', 'footprint_name']), 'Capacitor_SMD:C_1206_3216Metric')
    self.assertEqual(compiled.get_value(['dut', 'c[0]', 'part']), 'CL31A226MQHNNNE')
    self.assertEqual(compiled.get_value(['dut', 'c[0]', 'value']), '22µF, 6.3V')
    self.assertEqual(compiled.get_value(['dut', 'c[1]', 'footprint_name']), 'Capacitor_SMD:C_1206_3216Metric')
    self.assertEqual(compiled.get_value(['dut', 'c[1]', 'part']), 'CL31A226MQHNNNE')
    self.assertEqual(compiled.get_value(['dut', 'c[1]', 'value']), '22µF, 6.3V')
    self.assertEqual(compiled.get_value(['dut', 'c[2]', 'footprint_name']), 'Capacitor_SMD:C_1206_3216Metric')
    self.assertEqual(compiled.get_value(['dut', 'c[2]', 'part']), 'CL31A226MQHNNNE')
    self.assertEqual(compiled.get_value(['dut', 'c[2]', 'value']), '22µF, 6.3V')
    self.assertEqual(compiled.get_value(['dut', 'c[3]', 'footprint_name']), None)