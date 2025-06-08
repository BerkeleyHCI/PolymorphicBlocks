import unittest

from .AbstractPowerConverters import BuckConverterPowerPath, BoostConverterPowerPath
from ..core import Range


class BuckConverterCalculationTest(unittest.TestCase):
    def test_buck_converter(self):
        values = BuckConverterPowerPath.calculate_parameters(
            Range.exact(5), Range.exact(2.5), Range.exact(100e3), Range.exact(1),
            Range.exact(0.1), 0.01, 0.001,
            efficiency=Range.exact(1)
        )
        self.assertEqual(values.dutycycle, Range.exact(0.5))

    def test_boost_converter(self):
        values = BoostConverterPowerPath.calculate_parameters(
            Range.exact(5), Range.exact(10), Range.exact(100e3), Range.exact(1),
            Range.exact(0.1), 0.01, 0.001,
            efficiency=Range.exact(1)
        )
        self.assertEqual(values.dutycycle, Range.exact(0.5))
