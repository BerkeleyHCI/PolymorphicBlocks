import unittest

from edg_core import Range
from .ResistiveDivider import DividerValues
from .ESeriesUtil import ESeriesUtil, ESeriesRatioUtil


class ResistorDividerTest(unittest.TestCase):
  def test_resistor_divider(self) -> None:
    calculator = ESeriesRatioUtil(ESeriesUtil.SERIES[24], 0.01, DividerValues)

    self.assertEqual(
      calculator.find(DividerValues(Range(0, 1), Range(0.1, 1))),
      (1, 1))

    self.assertEqual(
      calculator.find(DividerValues(Range(0.48, 0.52), Range(0.1, 1))),  # test a tighter range
      (1, 1))

    self.assertEqual(
      calculator.find(DividerValues(Range(0.106, 0.111), Range(0.1, 1))),  # test E12
      (8.2, 1))

    self.assertEqual(
      calculator.find(DividerValues(Range(0.208, 0.215), Range(1, 10))),  # test E12
      (8.2, 2.2))

    self.assertEqual(
      calculator.find(DividerValues(Range(0.7241, 0.7321), Range(1, 10))),  # test E12
      (5.6, 15))

    self.assertEqual(
      calculator.find(DividerValues(Range(0, 1), Range(10, 100))),  # test impedance decade shift
      (100, 100))

    self.assertEqual(
      calculator.find(DividerValues(Range(0.106, 0.111), Range(11, 99))),  # test everything
      (820, 100))

  def test_impossible(self) -> None:
    e1_calculator = ESeriesRatioUtil(ESeriesUtil.SERIES[1], 0.01, DividerValues)

    with self.assertRaises(ESeriesRatioUtil.NoMatchException) as error:
      self.assertEqual(
        e1_calculator.find(DividerValues(Range(0.10, 0.4), Range(0.1, 10))),  # not possible with E1 series
        None)
    self.assertIn('with values (100.0, 10.0)', error.exception.args[0])

    with self.assertRaises(ESeriesRatioUtil.NoMatchException):
      self.assertEqual(
        e1_calculator.find(DividerValues(Range(0.5, 0.5), Range(0.1, 10))),  # tolerance too tight
        None)

    with self.assertRaises(ESeriesRatioUtil.NoMatchException):
      # this uses ratio = 0.1 - 0.9 for efficiency, otherwise the system searches keeps (fruitlessly)
      # searching through more extreme ratios until it hits decade limits
      self.assertEqual(
        e1_calculator.find(DividerValues(Range(0.1, 0.9), Range(1, 4))),  # can't meet the impedances
        None)
