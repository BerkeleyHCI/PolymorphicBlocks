import unittest

from . import *
from .test_passive_common import *


class JLC_ResistorTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(JLCPCB_Resistor(
      resistancece=750 * Ohm(tol=0.01),
      power_dissipation=0.25 * W
    ))
    (self.dummya, ), _ = self.chain(self.dut.a, self.Block(PassiveDummy()))
    (self.dummyb, ), _ = self.chain(self.dut.b, self.Block(PassiveDummy()))


class JLC_ResistorTestCase(unittest.TestCase):
  def test_resistor(self) -> None:
    compiled = ScalaCompiler.compile(JLC_ResistorTestTop)

    #self.assertEqual(compiled.get_value(['dut', 'footprint_name']), '1206W4F7500T5E')
    self.assertEqual(compiled.get_value(['dut', 'part']), '1206W4F7500T5E')
    self.assertEqual(compiled.get_value(['dut', 'value']), '750Ohm, 0.25W')
    
test = JLC_ResistorTestCase()
if (test.test_resistor()):
    print("Success!")
