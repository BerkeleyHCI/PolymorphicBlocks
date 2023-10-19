import unittest

from .RfNetworks import PiLowPassFilter


class PiLowPassFilterTest(unittest.TestCase):
    def test_low_pass_filter(self) -> None:
        # example 7.2 from https://www.silabs.com/documents/public/application-notes/an1275-imp-match-for-network-arch.pdf
        # note the results in the app note are NOT numerically accurate (and in some cases just flat out wrong)
        # overall result using https://www.eeweb.com/tools/pi-match/
        c1, c2, l, rv = PiLowPassFilter._calculate_values(2445e6, 2445/500, 50, complex(21, -1.15))
        self.assertAlmostEqual(rv, 2.007, delta=0.001)
        self.assertAlmostEqual(l, 1.0414e-9, delta=0.001e-9)
        self.assertAlmostEqual(c1, 6.366e-12, delta=0.001e-12)
        self.assertAlmostEqual(c2, 9.353e-12, delta=0.001e-12)

        # ESP32 example - NOTE this has excessively large Q
        c1, c2, l, rv = PiLowPassFilter._calculate_values(2443e6, 2443/82, complex(35, 10), 50)
        self.assertAlmostEqual(l, 0.204e-9, delta=0.001e-9)
        self.assertAlmostEqual(c1, 45.095e-12, delta=0.001e-12)
        self.assertAlmostEqual(c2, 38.82e-12, delta=0.01e-12)

    def test_calculate_l(self) -> None:
        # example 7.2 from https://www.silabs.com/documents/public/application-notes/an1275-imp-match-for-network-arch.pdf
        # note that its numerical results are wrong, but the equations are correct
        # RPload and XPload checked against https://www.w6ze.org/Calculators/Calc_SerParZ.html
        #   but its parallel component disagrees
        # stray capacitance checked against http://www.mathforengineers.com/AC-circuits-calculators/parallel-RC-circuit-Impedance.html
        # overall result checked against https://www.eeweb.com/tools/l-match/
        # l network 1
        l1, c1 = PiLowPassFilter._calculate_l_values(2445e6, 2.007, complex(50, 0))
        self.assertAlmostEqual(l1, 0.6389e-9, delta=0.0001e-9)
        self.assertAlmostEqual(c1, 6.366e-12, delta=0.001e-12)

        # l network 2
        l2, c2 = PiLowPassFilter._calculate_l_values(2445e6, 2.007, complex(21, -1.15))
        self.assertAlmostEqual(l2, 0.4026e-9, delta=0.0001e-9)
        self.assertAlmostEqual(c2, 9.354e-12, delta=0.001e-12)
