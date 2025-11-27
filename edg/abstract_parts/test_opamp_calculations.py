import unittest

from . import *
from .OpampCircuits import SummingAmplifier


class OpampCalculationsTest(unittest.TestCase):
  def test_summing_amplifier(self) -> None:
    self.assertEqual(SummingAmplifier.calculate_ratio(
      [Range.exact(10e3), Range.exact(10e3)]), [Range.exact(0.5), Range.exact(0.5)])
    self.assertEqual(SummingAmplifier.calculate_ratio(
      [Range.exact(10e3), Range.exact(10e3), Range.exact(20e3)]),
      [Range.exact(0.4), Range.exact(0.4), Range.exact(0.2)])
    self.assertEqual(SummingAmplifier.calculate_ratio(
      [Range.from_tolerance(10e3, 0.01), Range.from_tolerance(10e3, 0.01)]),
      [Range(0.495, 0.505), Range(0.495, 0.505)])
