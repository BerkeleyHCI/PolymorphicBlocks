import unittest

from . import *


class UnitsTestCase(unittest.TestCase):
  def test_units(self):
    self.assertEqual(UnitUtils.num_to_prefix(1, 3), '1')
    self.assertEqual(UnitUtils.num_to_prefix(1000, 3), '1k')
    self.assertEqual(UnitUtils.num_to_prefix(0.001, 3), '1m')
    self.assertEqual(UnitUtils.num_to_prefix(4700, 3), '4.7k')
    self.assertEqual(UnitUtils.num_to_prefix(0.1e-6, 3), '100n')
