import unittest
from .JLcResistor import JLcResistor, JLcResistorTable
from .test_passive_common import *


class JLcResistorTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(JLcResistor(
      resistance=750 * Ohm(tol=0.10),
      power=(0, 0.25) * Watt
    ))
    (self.dummya, ), _ = self.chain(self.dut.a, self.Block(PassiveDummy()))
    (self.dummyb, ), _ = self.chain(self.dut.b, self.Block(PassiveDummy()))


class JLcResistorTestCase(unittest.TestCase):
  def test_resistor(self) -> None:
    #test = JLcResistorTestTop
    compiled = ScalaCompiler.compile(JLcResistorTestTop)

    self.assertEqual(compiled.get_value(['dut', 'footprint_name']), 'Resistor_SMD:R_1206_3216Metric')
    self.assertEqual(compiled.get_value(['dut', 'part']), '1206W4F7500T5E')
    self.assertEqual(compiled.get_value(['dut', 'value']), '0.25W ±1% 750Ω ±100ppm/℃ 1206 Chip Resistor - Surface Mount ROHS')
