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
        # from https://www.eetimes.eu/impedance-matching-for-nfc-applications-part-2/
        # single-ended conversion
        source_z = NfcAntenna.impedance_from_lrc(13.56e6, 470e-9 * 2, 25 * 2, 247e-12 / 2)  # 25 ohm TX output assumed
        self.assertAlmostEqual(source_z, complex(165.82, -45.46), delta=0.01)
        diff_cs, diff_cp = DifferentialLLowPassFilter._calculate_values(13.56e6, source_z.conjugate(), complex(1.87, 62.53).conjugate())
        self.assertAlmostEqual(diff_cs * 2, -45e-12, delta=1e-12)  # TODO why is this negative
        self.assertAlmostEqual(diff_cp * 2, -337e-12, delta=1e-12)

        # target impedance of 20 ohm - determines transmit power

        # excel matching from https://www.nxp.com/docs/en/application-note/AN13219.pdf
        source_z = NfcAntenna.impedance_from_lrc(13.56e6, 160e-9 * 2, 20, 330e-12)
        source_z = complex(44, 24)
        # source_z = NfcAntenna.impedance_from_lrc(13.56e6, 0, 20, 0)
        sink_z = NfcAntenna.impedance_from_lrc(13.56e6, 1522e-9, 1.40, 0.1e-12) + 2.54*2
        print(source_z)
        print(sink_z)
        diff_cs, diff_cp = DifferentialLLowPassFilter._calculate_values(13.56e6, source_z.conjugate(), sink_z.conjugate())
        print(diff_cs*2, diff_cp*2)
        self.assertAlmostEqual(diff_cs * 2, 65.1e-12, delta=0.1e-12)
        self.assertAlmostEqual(diff_cp * 2, 111.0e-12, delta=0.1e-12)


        # asymmetrical matching case from https://www.nxp.com/docs/en/application-note/AN13219.pdf
        # cs (series) here is c1 in the example, cp (parallel) here is c2
        source_z = NfcAntenna.impedance_from_lrc(13.56e6, 160e-9 * 2, 0.9 * 2, 327.1e-12 / 2)
        sink_z = NfcAntenna.impedance_from_lrc(13.56e6, 1522e-9, 1.40, 2.0e-12) + 2.54*2
        diff_cs, diff_cp = DifferentialLLowPassFilter._calculate_values(13.56e6, source_z, sink_z)
        print(diff_cs, diff_cp)
        self.assertAlmostEqual(diff_cs * 2, 65.3e-12, delta=0.1e-12)
        self.assertAlmostEqual(diff_cp * 2, 107e-12, delta=0.1e-12)
