import unittest

from electronics_model import *
from .AbstractOpamp import Amplifier


class AmplifierTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(Amplifier(
      amplification=Range.from_tolerance(2, 0.05)
    ))
    # (self.dummya, ), _ = self.chain(self.dut.a, self.Block(PassiveDummy()))
    # (self.dummyb, ), _ = self.chain(self.dut.b, self.Block(PassiveDummy()))


class OpampCircuitTest(unittest.TestCase):
  def test_opamp_amplifier(self) -> None:
    compiled = ScalaCompiler.compile(AmplifierTestTop)

    self.assertEqual(compiled.get_value(['dut', 'r1', 'value']), 'Inductor_SMD:L_0805_2012Metric')
    self.assertEqual(compiled.get_value(['dut', 'r2', 'value']), 'Inductor_SMD:L_0805_2012Metric')
