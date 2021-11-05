import unittest

from . import *
from .test_passive_common import *


class InductorTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(SmtInductor(
      inductance=2.2 * uHenry(tol=0.2),
      frequency=(0, 1) * MHertz,
      current=(0, 500) * mAmp
    ))
    (self.dummya, ), _ = self.chain(self.dut.a, self.Block(PassiveDummy()))
    (self.dummyb, ), _ = self.chain(self.dut.b, self.Block(PassiveDummy()))


class InductorTestCase(unittest.TestCase):
  def test_inductor(self) -> None:
    compiled = ScalaCompiler.compile(InductorTestTop)

    self.assertEqual(compiled.get_value(['dut', 'footprint_name']), 'Inductor_SMD:L_0805_2012Metric')
    self.assertEqual(compiled.get_value(['dut', 'part']), 'MLZ2012N2R2LT000')
    self.assertEqual(compiled.get_value(['dut', 'value']), '2.2µH, 800mA')
