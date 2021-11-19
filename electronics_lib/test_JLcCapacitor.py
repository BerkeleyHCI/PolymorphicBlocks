import unittest
from .JLcCapacitor import JLcCapacitor
from .test_passive_common import *
from .JLcCapacitor import *

class JLcCapacitorTestTop(Block):
  def __init__(self):
    super().__init__()
    #X7R ±10% 50V 10nF 0805 Multilayer Ceramic Capacitors MLCC - SMD/SMT ROHS
    self.dut = self.Block(JLcCapacitor(
        capacitance=10 * nFarad(tol=0.1),
        voltage=(0, 3.3) * Volt
    ))
    (self.dummya, ), _ = self.chain(self.dut.pos, self.Block(PassiveDummy()))
    (self.dummyb, ), _ = self.chain(self.dut.neg, self.Block(PassiveDummy()))


class JLcBigCapacitorTestTop(Block):
    def __init__(self):
        super().__init__()
        self.dut = self.Block(JLcCapacitor(
            capacitance=(50, 1000) * uFarad,
            voltage=(0, 3.3) * Volt
        ))
        (self.dummya, ), _ = self.chain(self.dut.pos, self.Block(PassiveDummy()))
        (self.dummyb, ), _ = self.chain(self.dut.neg, self.Block(PassiveDummy()))


class CapacitorTestCase(unittest.TestCase):
  def test_capacitor(self) -> None:
    test = JLcCapacitorTable()
    print("Test begins:\n", test.table())
    #compiled = ScalaCompiler.compile(JLcCapacitor)
    #self.assertEqual(compiled.get_value(['dut', 'footprint_name']), 'Capacitor_SMD:C_0805_2012Metric')
    #self.assertEqual(compiled.get_value(['dut', 'part']), 'CL21B103KBANNNC')
    #self.assertEqual(compiled.get_value(['dut', 'value']), '10nF, 50V')

  def test_capacitor_part(self) -> None:
    #X7R ±10% 50V 10nF 0603 Multilayer Ceramic Capacitors MLCC - SMD/SMT ROHS
    compiled = ScalaCompiler.compile(JLcCapacitorTestTop, Refinements(
        instance_values=[(['dut', 'part_spec'], '0603B103K500NT')]
    ))
    self.assertEqual(compiled.get_value(['dut', 'footprint_name']), 'Capacitor_SMD:C_0603_1608Metric')
    self.assertEqual(compiled.get_value(['dut', 'part']), '0603B103K500NT')
    self.assertEqual(compiled.get_value(['dut', 'value']), '10nF, 50V')

  def test_capacitor_footprint(self) -> None:
    compiled = ScalaCompiler.compile(JLcCapacitorTestTop, Refinements(
        instance_values=[(['dut', 'footprint_spec'], 'Capacitor_SMD:C_0603_1608Metric')]
    ))
    self.assertEqual(compiled.get_value(['dut', 'footprint_name']), 'Capacitor_SMD:C_0603_1608Metric')
    self.assertEqual(compiled.get_value(['dut', 'part']), '0603B103K500NT')
    self.assertEqual(compiled.get_value(['dut', 'value']), '10nF, 50V')

  def test_multi_capacitor(self) -> None:
    #X5R 6.3V ±20% 22uF 0603 Multilayer Ceramic Capacitors MLCC - SMD/SMT ROHS
    compiled = ScalaCompiler.compile(JLcBigCapacitorTestTop)
    self.assertEqual(compiled.get_value(['dut', 'c[0]', 'footprint_name']), 'Capacitor_SMD:C_0603_1608Metric')
    self.assertEqual(compiled.get_value(['dut', 'c[0]', 'part']), 'CL10A226MQ8NRNC')
    self.assertEqual(compiled.get_value(['dut', 'c[0]', 'value']), '22µF, 6.3V')
    self.assertEqual(compiled.get_value(['dut', 'c[1]', 'footprint_name']), 'Capacitor_SMD:C_0603_1608Metric')
    self.assertEqual(compiled.get_value(['dut', 'c[1]', 'part']), 'CL10A226MQ8NRNC')
    self.assertEqual(compiled.get_value(['dut', 'c[1]', 'value']), '22µF, 6.3V')
    self.assertEqual(compiled.get_value(['dut', 'c[2]', 'footprint_name']), 'Capacitor_SMD:C_0603_1608Metric')
    self.assertEqual(compiled.get_value(['dut', 'c[2]', 'part']), 'CL10A226MQ8NRNC')
    self.assertEqual(compiled.get_value(['dut', 'c[2]', 'value']), '22µF, 6.3V')
    #self.assertEqual(compiled.get_value(['dut', 'c[3]', 'footprint_name']), None)
