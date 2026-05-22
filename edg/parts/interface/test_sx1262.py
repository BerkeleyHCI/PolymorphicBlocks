import unittest

from .Rf_Sx1262 import Sx1262BalunLike


class Sx1262BalunLikeTest(unittest.TestCase):
    def test_values(self) -> None:
        # examples from ST AN5457
        l, c, cp = Sx1262BalunLike._calculate_values(915e6, complex(62, -112), complex(50, 0))
        self.assertAlmostEqual(l, 11.86e-9, delta=0.01e-9)
        self.assertAlmostEqual(c, 4.322e-12, delta=0.001e-12)  # 4.45 in the datasheet, but not numerically precise
        self.assertAlmostEqual(cp, 2.7e-12, delta=0.1e-12)
