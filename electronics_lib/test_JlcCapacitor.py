import unittest
from .test_passive_common import *
from .JlcCapacitor import *

class JlcCapacitorTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(JlcCapacitor(
        capacitance=10 * nFarad(tol=0.1),
        voltage=(0, 3.3) * Volt
    ))
    (self.dummya, ), _ = self.chain(self.dut.pos, self.Block(PassiveDummy()))
    (self.dummyb, ), _ = self.chain(self.dut.neg, self.Block(PassiveDummy()))


class JlcBigCapacitorTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(JlcCapacitor(
        capacitance=(50, 1000) * uFarad,
        voltage=(0, 3.3) * Volt
    ))
    (self.dummya, ), _ = self.chain(self.dut.pos, self.Block(PassiveDummy()))
    (self.dummyb, ), _ = self.chain(self.dut.neg, self.Block(PassiveDummy()))


class CapacitorTestCase(unittest.TestCase):
  def test_capacitor(self) -> None:
    compiled = ScalaCompiler.compile(JlcCapacitorTestTop)
    self.assertEqual(compiled.get_value(['dut', 'fp_footprint']), 'Capacitor_SMD:C_0402_1005Metric')
    self.assertEqual(compiled.get_value(['dut', 'fp_part']), 'CL05B103KB5NNNC')
    self.assertEqual(compiled.get_value(['dut', 'lcsc_part']), 'C15195')

  def test_capacitor_part(self) -> None:
    compiled = ScalaCompiler.compile(JlcCapacitorTestTop, Refinements(
        instance_values=[(['dut', 'part'], 'CL21B103KBANNNC')]
    ))
    self.assertEqual(compiled.get_value(['dut', 'fp_footprint']), 'Capacitor_SMD:C_0805_2012Metric')
    self.assertEqual(compiled.get_value(['dut', 'fp_part']), 'CL21B103KBANNNC')

  def test_capacitor_min_package(self) -> None:
    compiled = ScalaCompiler.compile(JlcCapacitorTestTop, Refinements(
      instance_values=[(['dut', 'smd_min_package'], '0603')]
    ))
    self.assertEqual(compiled.get_value(['dut', 'fp_footprint']), 'Capacitor_SMD:C_0603_1608Metric')
    self.assertEqual(compiled.get_value(['dut', 'fp_part']), '0603B103K500NT')
    self.assertEqual(compiled.get_value(['dut', 'lcsc_part']), 'C57112')

  def test_capacitor_footprint(self) -> None:
    compiled = ScalaCompiler.compile(JlcCapacitorTestTop, Refinements(
        instance_values=[(['dut', 'footprint_spec'], 'Capacitor_SMD:C_0805_2012Metric')]
    ))
    self.assertEqual(compiled.get_value(['dut', 'fp_footprint']), 'Capacitor_SMD:C_0805_2012Metric')

  def test_multi_capacitor(self) -> None:
    """The example returns multiple capacitors due to accounting for ±10% tolerance.
    Minimal test to avoid flakiness from part table updates."""
    compiled = ScalaCompiler.compile(JlcBigCapacitorTestTop)
    self.assertNotEqual(compiled.get_value(['dut', 'c[0]', 'fp_footprint']), None)
    self.assertNotEqual(compiled.get_value(['dut', 'c[1]', 'fp_footprint']), None)
    # should not be more than 6
    self.assertEqual(compiled.get_value(['dut', 'c[6]', 'fp_footprint']), None)
