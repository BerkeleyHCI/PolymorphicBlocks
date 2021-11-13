import unittest
from .JLC_Resistor import JLCPCB_Resistor, JLCPCB_ResistorTable
from .test_passive_common import *


class JLC_ResistorTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(JLCPCB_Resistor(
      resistance=750 * Ohm(tol=0.10),
      power=(0, 0.25) * Watt
    ))
    (self.dummya, ), _ = self.chain(self.dut.a, self.Block(PassiveDummy()))
    (self.dummyb, ), _ = self.chain(self.dut.b, self.Block(PassiveDummy()))


class JLC_ResistorTestCase(unittest.TestCase):
  def test_resistor(self) -> None:
    compiled = ScalaCompiler.compile(JLC_ResistorTestTop)

    self.assertEqual(compiled.get_value(['dut', 'footprint_name']), 'Resistor_SMD:R_1206_3216Metric')
    self.assertEqual(compiled.get_value(['dut', 'part']), '1206W4F7500T5E')
    self.assertEqual(compiled.get_value(['dut', 'value']), '0.25W ±1% 750Ω ±100ppm/℃ 1206 Chip Resistor - Surface Mount ROHS')



