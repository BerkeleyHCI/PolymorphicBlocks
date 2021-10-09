import unittest

from . import Range

class RangeTestCase(unittest.TestCase):
  def test_range_contains(self) -> None:
    self.assertTrue(Range(0, 1).contains(0.5))
    self.assertTrue(Range(0, 1).contains(Range(0, 1)))

    self.assertFalse(Range(0, 1).contains(Range(0, 1.1)))

  def test_range_tolerance(self) -> None:
    self.assertEqual(Range.from_tolerance(100, 0.05).upper, 105)
    self.assertEqual(Range.from_tolerance(100, 0.05).lower, 95)
    self.assertEqual(Range.from_tolerance(1000, (-0.1, 0.05)).lower, 900)
    self.assertEqual(Range.from_tolerance(1000, (-0.1, 0.05)).upper, 1050)

  def test_from(self) -> None:
    self.assertEqual(Range.from_lower(500).upper, float('inf'))
    self.assertEqual(Range.from_lower(500).lower, 500)
    self.assertTrue(Range.from_lower(500).contains(500))
    self.assertTrue(Range.from_lower(500).contains(1e12))
    self.assertFalse(Range.from_lower(500).contains(499))
    self.assertFalse(Range.from_lower(500).contains(0))
    self.assertFalse(Range.from_lower(500).contains(float('-inf')))

    self.assertEqual(Range.from_upper(500).upper, 500)
    self.assertEqual(Range.from_upper(500).lower, float('-inf'))
    self.assertTrue(Range.from_upper(500).contains(0))
    self.assertTrue(Range.from_upper(500).contains(-1e12))
    self.assertFalse(Range.from_upper(500).contains(1000))
    self.assertFalse(Range.from_upper(500).contains(float('inf')))
