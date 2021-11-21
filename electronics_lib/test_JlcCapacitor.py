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
    self.assertEqual(compiled.get_value(['dut', 'footprint_name']), 'Capacitor_SMD:C_0603_1608Metric')
    self.assertEqual(compiled.get_value(['dut', 'part']), '0603B103K500NT')
    self.assertEqual(compiled.get_value(['dut', 'value']), 'X7R ±10% 50V 10nF 0603 Multilayer Ceramic Capacitors MLCC - SMD/SMT ROHS')

  def test_capacitor_part(self) -> None:
    compiled = ScalaCompiler.compile(JlcCapacitorTestTop, Refinements(
        instance_values=[(['dut', 'part_spec'], '0603B103K500NT')]
    ))
    self.assertEqual(compiled.get_value(['dut', 'footprint_name']), 'Capacitor_SMD:C_0603_1608Metric')
    self.assertEqual(compiled.get_value(['dut', 'part']), '0603B103K500NT')
    self.assertEqual(compiled.get_value(['dut', 'value']), 'X7R ±10% 50V 10nF 0603 Multilayer Ceramic Capacitors MLCC - SMD/SMT ROHS')

  def test_capacitor_footprint(self) -> None:
    compiled = ScalaCompiler.compile(JlcCapacitorTestTop, Refinements(
        instance_values=[(['dut', 'footprint_spec'], 'Capacitor_SMD:C_0603_1608Metric')]
    ))
    self.assertEqual(compiled.get_value(['dut', 'footprint_name']), 'Capacitor_SMD:C_0603_1608Metric')
    self.assertEqual(compiled.get_value(['dut', 'part']), '0603B103K500NT')
    self.assertEqual(compiled.get_value(['dut', 'value']), 'X7R ±10% 50V 10nF 0603 Multilayer Ceramic Capacitors MLCC - SMD/SMT ROHS')

  def test_multi_capacitor(self) -> None:
    compiled = ScalaCompiler.compile(JlcBigCapacitorTestTop)
    self.assertEqual(compiled.get_value(['dut', 'c[0]', 'footprint_name']), 'Capacitor_SMD:C_0805_2012Metric')
    self.assertEqual(compiled.get_value(['dut', 'c[0]', 'part']), 'CL21A106KAYNNNE')
    self.assertEqual(compiled.get_value(['dut', 'c[0]', 'value']), 'X5R 25V ±10% 10uF 0805 Multilayer Ceramic Capacitors MLCC - SMD/SMT ROHS')
    self.assertEqual(compiled.get_value(['dut', 'c[1]', 'footprint_name']), 'Capacitor_SMD:C_0805_2012Metric')
    self.assertEqual(compiled.get_value(['dut', 'c[1]', 'part']), 'CL21A106KAYNNNE')
    self.assertEqual(compiled.get_value(['dut', 'c[1]', 'value']), 'X5R 25V ±10% 10uF 0805 Multilayer Ceramic Capacitors MLCC - SMD/SMT ROHS')
    self.assertEqual(compiled.get_value(['dut', 'c[2]', 'footprint_name']), 'Capacitor_SMD:C_0805_2012Metric')
    self.assertEqual(compiled.get_value(['dut', 'c[2]', 'part']), 'CL21A106KAYNNNE')
    self.assertEqual(compiled.get_value(['dut', 'c[2]', 'value']), 'X5R 25V ±10% 10uF 0805 Multilayer Ceramic Capacitors MLCC - SMD/SMT ROHS')
    self.assertEqual(compiled.get_value(['dut', 'c[3]', 'footprint_name']), 'Capacitor_SMD:C_0805_2012Metric')
    self.assertEqual(compiled.get_value(['dut', 'c[3]', 'part']), 'CL21A106KAYNNNE')
    self.assertEqual(compiled.get_value(['dut', 'c[3]', 'value']), 'X5R 25V ±10% 10uF 0805 Multilayer Ceramic Capacitors MLCC - SMD/SMT ROHS')
    self.assertEqual(compiled.get_value(['dut', 'c[4]', 'footprint_name']), 'Capacitor_SMD:C_0805_2012Metric')
    self.assertEqual(compiled.get_value(['dut', 'c[4]', 'part']), 'CL21A106KAYNNNE')
    self.assertEqual(compiled.get_value(['dut', 'c[4]', 'value']), 'X5R 25V ±10% 10uF 0805 Multilayer Ceramic Capacitors MLCC - SMD/SMT ROHS')
    self.assertEqual(compiled.get_value(['dut', 'c[5]', 'footprint_name']), 'Capacitor_SMD:C_0805_2012Metric')
    self.assertEqual(compiled.get_value(['dut', 'c[5]', 'part']), 'CL21A106KAYNNNE')
    self.assertEqual(compiled.get_value(['dut', 'c[5]', 'value']), 'X5R 25V ±10% 10uF 0805 Multilayer Ceramic Capacitors MLCC - SMD/SMT ROHS')
    self.assertEqual(compiled.get_value(['dut', 'c[6]', 'footprint_name']), None)
