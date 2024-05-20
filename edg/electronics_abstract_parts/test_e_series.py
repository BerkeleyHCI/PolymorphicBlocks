import unittest
from typing import List, Tuple

from edg_core import Range
from .ESeriesUtil import ESeriesUtil, ESeriesRatioUtil


class PreferredNumberTestCase(unittest.TestCase):
  def test_zigzag_range(self) -> None:
    self.assertEqual(ESeriesUtil.zigzag_range(0, 1), [0])
    self.assertEqual(ESeriesUtil.zigzag_range(0, 2), [0, 1])
    self.assertEqual(ESeriesUtil.zigzag_range(0, 3), [1, 0, 2])
    self.assertEqual(ESeriesUtil.zigzag_range(0, 4), [1, 0, 2, 3])

  def test_preferred_number(self) -> None:
    # Test a few different powers
    self.assertEqual(ESeriesUtil.choose_preferred_number(Range(0.09, 0.11), ESeriesUtil.SERIES[24], 0.01),
                     0.1)
    self.assertEqual(ESeriesUtil.choose_preferred_number(Range(0.9, 1.1), ESeriesUtil.SERIES[24], 0.01),
                     1)
    self.assertEqual(ESeriesUtil.choose_preferred_number(Range(9, 11), ESeriesUtil.SERIES[24], 0.01),
                     10)
    self.assertEqual(ESeriesUtil.choose_preferred_number(Range(900, 1100), ESeriesUtil.SERIES[24], 0.01),
                     1000)

    # Test higher series
    self.assertEqual(
      ESeriesUtil.choose_preferred_number(Range.from_tolerance(965, 0.01), ESeriesUtil.SERIES[24], 0.01),
      None)
    self.assertEqual(
      ESeriesUtil.choose_preferred_number(Range.from_tolerance(965, 0.01), ESeriesUtil.SERIES[192], 0.01),
      965)

    # Test a few different numbers
    self.assertEqual(ESeriesUtil.choose_preferred_number(Range(8100, 8300), ESeriesUtil.SERIES[24], 0.01),
                     8200)
    self.assertEqual(ESeriesUtil.choose_preferred_number(Range(460, 480), ESeriesUtil.SERIES[24], 0.01),
                     470)

    # Test preference for lower E-series first
    self.assertEqual(ESeriesUtil.choose_preferred_number(Range(101, 9999), ESeriesUtil.SERIES[24], 0.01),
                     1000)
    self.assertEqual(ESeriesUtil.choose_preferred_number(Range(220, 820), ESeriesUtil.SERIES[24], 0.01),
                     470)
    self.assertEqual(ESeriesUtil.choose_preferred_number(Range(220, 820), ESeriesUtil.SERIES[24192], 0.01),
                     470)

    # Test dynamic range edge cases
    self.assertEqual(ESeriesUtil.choose_preferred_number(Range(999, 1500), ESeriesUtil.SERIES[24], 0.01),
                     1200)
    self.assertEqual(ESeriesUtil.choose_preferred_number(Range(680, 1001), ESeriesUtil.SERIES[24], 0.01),
                     820)


class RatioTestCase(unittest.TestCase):
  def test_ratio_product(self):
    self.assertEqual(ESeriesRatioUtil._generate_e_series_product([1, 2, 3, 4], 0, 0),
                     [(1, 1),
                      (2, 1), (1, 2), (2, 2),
                      (3, 1), (1, 3), (3, 2), (2, 3), (3, 3),
                      (4, 1), (1, 4), (4, 2), (2, 4), (4, 3), (3, 4), (4, 4)])
