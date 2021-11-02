import unittest

from edg_core import Range
from .ESeriesUtil import ESeriesUtil

class PreferredNumberTestCase(unittest.TestCase):
  def test_zigzag_range(self) -> None:
    self.assertEqual(ESeriesUtil.zigzag_range(0, 1), [0])
    self.assertEqual(ESeriesUtil.zigzag_range(0, 2), [0, 1])
    self.assertEqual(ESeriesUtil.zigzag_range(0, 3), [1, 0, 2])
    self.assertEqual(ESeriesUtil.zigzag_range(0, 4), [1, 0, 2, 3])

  def test_preferred_number(self) -> None:
    # Test a few different powers
    self.assertEqual(ESeriesUtil.choose_preferred_number(Range(0.09, 0.11), 0.01, ESeriesUtil.E24_SERIES_ZIGZAG, 2),
                     0.1)
    self.assertEqual(ESeriesUtil.choose_preferred_number(Range(0.9, 1.1), 0.01, ESeriesUtil.E24_SERIES_ZIGZAG, 2),
                     1)
    self.assertEqual(ESeriesUtil.choose_preferred_number(Range(9, 11), 0.01, ESeriesUtil.E24_SERIES_ZIGZAG, 2),
                     10)
    self.assertEqual(ESeriesUtil.choose_preferred_number(Range(900, 1100), 0.01, ESeriesUtil.E24_SERIES_ZIGZAG, 2),
                     1000)

    # Test a few different numbers
    self.assertEqual(ESeriesUtil.choose_preferred_number(Range(8100, 8300), 0.01, ESeriesUtil.E24_SERIES_ZIGZAG, 2),
                     8200)
    self.assertEqual(ESeriesUtil.choose_preferred_number(Range(460, 480), 0.01, ESeriesUtil.E24_SERIES_ZIGZAG, 2),
                     470)

    # Test preference for lower E-series first
    self.assertEqual(ESeriesUtil.choose_preferred_number(Range(101, 9999), 0.01, ESeriesUtil.E24_SERIES_ZIGZAG, 2),
                     1000)
    self.assertEqual(ESeriesUtil.choose_preferred_number(Range(220, 820), 0.01, ESeriesUtil.E24_SERIES_ZIGZAG, 2),
                     470)

    # Test dynamic range edge cases
    self.assertEqual(ESeriesUtil.choose_preferred_number(Range(999, 1500), 0.01, ESeriesUtil.E24_SERIES_ZIGZAG, 2),
                     1200)
    self.assertEqual(ESeriesUtil.choose_preferred_number(Range(680, 1001), 0.01, ESeriesUtil.E24_SERIES_ZIGZAG, 2),
                     820)
