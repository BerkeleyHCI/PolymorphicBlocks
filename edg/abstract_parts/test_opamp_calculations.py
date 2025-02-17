import unittest

from . import *
from .OpampCircuits import SummingAmplifier


class OpampCalculationsTest(unittest.TestCase):
  def test_summing_amplifier(self) -> None:
    self.assertEqual(SummingAmplifier.calculate_ratio(
      [Range.exact(10e3), Range.exact(10e3)]), [Range.exact(0.5), Range.exact(0.5)])
