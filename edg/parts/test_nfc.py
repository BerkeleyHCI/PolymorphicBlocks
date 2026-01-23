import unittest

from .Rf_Pn7160 import NfcAntenna, NfcAntennaDampening, DifferentialLcLowpassFilter, DifferentialLLowPassFilter


class NfcAntennaTest(unittest.TestCase):
    def test_antenna(self) -> None:
        # from https://www.eetimes.eu/impedance-matching-for-nfc-applications-part-2/
        self.assertAlmostEqual(
            NfcAntenna.impedance_from_lrc(13.56e6, 0.7e-6, 1.7, 9.12e-12), complex(1.87, 62.53), delta=0.01
        )

        # measured example from https://www.nxp.com/docs/en/application-note/AN13219.pdf
        # stray capacitance seems to have been lumped into the inductance
        self.assertAlmostEqual(
            NfcAntenna.impedance_from_lrc(13.56e6, 1.523773e-6, 1.372, 0e-12), complex(1.372, 129.825), delta=0.001
        )

        # from https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/667/Impedance-matching-for-13.56-MHz-NFC-antennas-without-VNA.pdf
        self.assertAlmostEqual(
            NfcAntenna.impedance_from_lrc(13.56e6, 1.67e-6, 1.66, 0e-12), complex(1.66, 142.28), delta=0.01
        )
        self.assertAlmostEqual(
            NfcAntenna.impedance_from_lrc(13.56e6, 1.03e-6, 0.51, 0e-12), complex(0.51, 87.76), delta=0.01
        )

    def test_damp_res(self) -> None:
        # excel matching from https://www.nxp.com/docs/en/application-note/AN13219.pdf
        ant_z = NfcAntenna.impedance_from_lrc(13.56e6, 1522e-9, 1.40, 0.1e-12)
        self.assertAlmostEqual(NfcAntennaDampening.damp_res_from_impedance(ant_z, 20), 2.54 * 2, delta=0.01)

    def test_lc(self) -> None:
        # asymmetrical matching case from https://www.nxp.com/docs/en/application-note/AN13219.pdf
        self.assertAlmostEqual(
            DifferentialLcLowpassFilter._calculate_capacitance(22e6, 160e-9), 327.1e-12, delta=0.1e-12
        )

    def test_l_match(self) -> None:
        # from https://www.eetimes.eu/impedance-matching-for-nfc-applications-part-2/
        # which is the same as https://www.we-online.com/components/media/o207264v410%20ANP084a%20EN.pdf
        # single-ended conversion
        source_z = NfcAntenna.impedance_from_lrc(13.56e6, 470e-9 * 2, 25 * 2, 247e-12 / 2)  # 25 ohm TX output assumed
        self.assertAlmostEqual(source_z, complex(165.82, -45.46), delta=0.01)
        ant_z = NfcAntenna.impedance_from_lrc(13.56e6, 0.7e-6, 1.7, 9.12e-12)
        self.assertAlmostEqual(ant_z, complex(1.87, 62.53), delta=0.01)
        diff_cs, diff_cp = DifferentialLLowPassFilter._calculate_se_values(
            13.56e6, source_z.conjugate(), ant_z.conjugate()
        )
        self.assertAlmostEqual(-diff_cs * 2, 45e-12, delta=1e-12)  # TODO why is this negative
        self.assertAlmostEqual(-diff_cp * 2, 337e-12, delta=1e-12)

        # from https://www.mroland.at/publications/2008-roland-csndsp/Roland_2008_CSNDSP08_AutomaticImpedanceMatching.pdf
        source_z = NfcAntenna.impedance_from_lrc(13.56e6, 560e-9 * 2, 50, 220e-12 / 2)  # common EMC filter
        ant_z = NfcAntenna.impedance_from_lrc(13.56e6, 3.12e-6, 4.93, 9.84e-12)
        diff_cs, diff_cp = DifferentialLLowPassFilter._calculate_se_values(
            13.56e6, source_z.conjugate(), ant_z.conjugate()
        )
        self.assertAlmostEqual(-diff_cs * 2, 14e-12, delta=1e-12)
        self.assertAlmostEqual(-diff_cp * 2, 55e-12, delta=1e-12)

        ant_z = NfcAntenna.impedance_from_lrc(13.56e6, 1.7e-6, 4.83, 6.99e-12)
        diff_cs, diff_cp = DifferentialLLowPassFilter._calculate_se_values(
            13.56e6, source_z.conjugate(), ant_z.conjugate()
        )
        self.assertAlmostEqual(-diff_cs * 2, 27e-12, delta=1e-12)
        self.assertAlmostEqual(-diff_cp * 2, 124e-12, delta=1e-12)

        # excel matching from https://www.nxp.com/docs/en/application-note/AN13219.pdf
        # source_z = NfcAntenna.impedance_from_lrc(13.56e6, 160e-9 * 2, 20, 330e-12)  # doesn't work
        source_z = complex(44, 24)  # this works, but unclear how this was obtained
        ant_z = NfcAntenna.impedance_from_lrc(13.56e6, 1522e-9, 1.40, 0.1e-12) + 2.54 * 2
        diff_cs, diff_cp = DifferentialLLowPassFilter._calculate_se_values(
            13.56e6, source_z.conjugate(), ant_z.conjugate()
        )
        self.assertAlmostEqual(-diff_cs * 2, 65.1e-12, delta=0.2e-12)
        self.assertAlmostEqual(-diff_cp * 2, 111.0e-12, delta=0.7e-12)
