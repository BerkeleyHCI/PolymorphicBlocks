import unittest

from . import *
from .test_passive_common import *


class JlcInductorTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(JlcInductor(
      inductance=2.2 * uHenry(tol=0.2),
      current=(0, 500) * mAmp,
      # no frequency spec since JLC doesn't allow it
    ))
    (self.dummya, ), _ = self.chain(self.dut.a, self.Block(PassiveDummy()))
    (self.dummyb, ), _ = self.chain(self.dut.b, self.Block(PassiveDummy()))


class InductorTestCase(unittest.TestCase):
  def test_inductor(self) -> None:
    compiled = ScalaCompiler.compile(JlcInductorTestTop)

    self.assertEqual(compiled.get_value(['dut', 'fp_footprint']), 'Inductor_SMD:L_0603_1608Metric')
    self.assertEqual(compiled.get_value(['dut', 'fp_part']), 'CMH160808B2R2MT')
