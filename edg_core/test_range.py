import math
import unittest

from . import Range

class RangeTestCase(unittest.TestCase):
  def test_range_contains(self) -> None:
    self.assertTrue(0.5 in Range(0, 1))
    self.assertTrue(Range(0, 1) in Range(0, 1))

    self.assertFalse(Range(0, 1.1) in Range(0, 1))

  def test_range_tolerance(self) -> None:
    self.assertEqual(Range.from_tolerance(100, 0.05).upper, 105)
    self.assertEqual(Range.from_tolerance(100, 0.05).lower, 95)
    self.assertEqual(Range.from_tolerance(1000, (-0.1, 0.05)).lower, 900)
    self.assertEqual(Range.from_tolerance(1000, (-0.1, 0.05)).upper, 1050)

  def test_from(self) -> None:
    self.assertEqual(Range.from_lower(500).upper, float('inf'))
    self.assertEqual(Range.from_lower(500).lower, 500)
    self.assertTrue(500 in Range.from_lower(500))
    self.assertTrue(1e12 in Range.from_lower(500))
    self.assertFalse(499 in Range.from_lower(500))
    self.assertFalse(0 in Range.from_lower(500))
    self.assertFalse(float('-inf') in Range.from_lower(500))

    self.assertEqual(Range.from_upper(500).upper, 500)
    self.assertEqual(Range.from_upper(500).lower, float('-inf'))
    self.assertTrue(0 in Range.from_upper(500))
    self.assertTrue(-1e12 in Range.from_upper(500))
    self.assertFalse(1000 in Range.from_upper(500))
    self.assertFalse(float('inf') in Range.from_upper(500))

  def test_all(self) -> None:
    self.assertTrue(Range.all() in Range.all())
    self.assertTrue(0 in Range.all())
    self.assertTrue(1e12 in Range.all())

  def test_ops(self) -> None:
    self.assertTrue(Range(1.1, 5) == Range(1.1, 5))
    self.assertTrue(Range(1.1, 5) != Range(1.2, 5))
    self.assertTrue(Range.all() == Range.all())
    self.assertTrue(Range.all() != Range(1.2, 5))

    self.assertEqual(Range(1.1, 5) * 2, Range(2.2, 10))

    self.assertEqual(Range(1, 5).center(), 3)

  def test_intersect(self) -> None:
    self.assertTrue(Range(-1, 2).intersects(Range(2, 3)))
    self.assertTrue(Range(-1, 2).intersects(Range(0, 3)))
    self.assertTrue(Range(-1, 2).intersects(Range(-2, -1)))
    self.assertTrue(Range(-1, 2).intersects(Range(-2, 0)))
    self.assertTrue(Range(-1, 2).intersects(Range(0, 1)))
    self.assertFalse(Range(-1, 2).intersects(Range(3, 4)))
    self.assertFalse(Range(-1, 2).intersects(Range(-3, -2)))

  def test_cancel_property(self) -> None:
    range1 = Range(10, 20)
    self.assertEqual(Range.cancel_multiply(range1, 1/range1), Range(1, 1))

  def test_frequency(self) -> None:
    """Tests (back-)calculating C from target w and R - so tolerancing flows from R and C to w
    instead of w and R to C."""
    R = Range(90, 110)
    C = Range.from_tolerance(1e-6, 0.05)
    w = 1 / (2 * math.pi * R * C)
    solved = Range.cancel_multiply(1/(2*math.pi * R), 1/w)
    self.assertTrue(math.isclose(C.lower, solved.lower))
    self.assertTrue(math.isclose(C.upper, solved.upper))

  def test_bound(self) -> None:
    """Tests (back-)calculating C from target w and R - so tolerancing flows from R and C to w
    instead of w and R to C."""
    self.assertEqual(Range(0, 1).bound_to(Range(0.5, 1.5)),
                     Range(0.5, 1))
    self.assertEqual(Range(0, 1).bound_to(Range(-0.5, 0.5)),
                     Range(0, 0.5))

    self.assertEqual(Range(0, 1).bound_to(Range(10, 20)),
                     Range(10, 10))
    self.assertEqual(Range(0, 1).bound_to(Range(-20, -10)),
                     Range(-10, -10))
