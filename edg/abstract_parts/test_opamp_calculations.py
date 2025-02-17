import unittest

from . import *
from .OpampCircuits import NoninvertingSummingAmplifier


class OpampCalculationsTest(unittest.TestCase):
  def test_noninverting_summing_amplifier(self) -> None:
    self.assertEquals(NoninvertingSummingAmplifier.calculate_ratio(
      [10*kOhm(tol=0), 10*kOhm(tol=0)]), [Range.exact(0.5), Range.exact(0.5)])
