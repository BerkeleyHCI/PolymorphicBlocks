import unittest

from .Rf_Pn7160 import NfcAntenna, LcLowpassFilter, DifferentialLLowPassFilter


class NfcAntennaTest(unittest.TestCase):
    def test_antenna(self) -> None:
        # from https://www.eetimes.eu/impedance-matching-for-nfc-applications-part-2/
        self.assertAlmostEqual(NfcAntenna.impedance_from_lrc(13.56e6, 0.7e-6, 1.7, 9.12e-12),
                               complex(1.87, 62.53), delta=0.01)

        # measured example from https://www.nxp.com/docs/en/application-note/AN13219.pdf
        # stray capacitance seems to have been lumped into the inductance
        self.assertAlmostEqual(NfcAntenna.impedance_from_lrc(13.56e6, 1.523773e-6, 1.372, 0e-12),
                               complex(1.372, 129.825), delta=0.001)

        # from https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/667/Impedance-matching-for-13.56-MHz-NFC-antennas-without-VNA.pdf
        self.assertAlmostEqual(NfcAntenna.impedance_from_lrc(13.56e6, 1.67e-6, 1.66, 0e-12),
                               complex(1.66, 142.28), delta=0.01)
        self.assertAlmostEqual(NfcAntenna.impedance_from_lrc(13.56e6, 1.03e-6, 0.51, 0e-12),
                               complex(0.51, 87.76), delta=0.01)

    def test_lc(self) -> None:
        # asymmetrical matching case from https://www.nxp.com/docs/en/application-note/AN13219.pdf
        self.assertAlmostEqual(LcLowpassFilter._calculate_capacitance(22e6, 160e-9),
                               327.1e-12, delta=0.1e-12)

    def test_l_match(self) -> None:
        # target impedance of 20 ohm - determines transmit power

        # asymmetrical matching case from https://www.nxp.com/docs/en/application-note/AN13219.pdf
        # cs (series) here is c1 in the example, cp (parallel) here is c2
        diff_cs, diff_cp = DifferentialLLowPassFilter._calculate_values(13.56e6, complex(20, 0), complex(1.372+2.54*2, 129.825))
        print(diff_cs, diff_cp)
        self.assertAlmostEqual(diff_cs, 65.3e-12, delta=0.1e-12)
        self.assertAlmostEqual(diff_cp, 107-12, delta=0.1e-12)
