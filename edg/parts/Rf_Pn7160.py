from typing import Tuple
from math import pi

from ..abstract_parts import *
from .JlcPart import JlcPart


# TODO some of these are pretty general RF building blocks and can be moved into shared libraries
# but until there are enough use cases they'll be buried here for now

class NfcAntenna(Block):
    """NFC antenna connector, also calculates the complex impedance from series-LRC parameters.
    In this model, the L and R are in series, and the C is in parallel with the LR stack.
    As in https://www.nxp.com/docs/en/application-note/AN13219.pdf
    """
    @classmethod
    def impedance_from_lrc(cls, freq: float, inductance: float, resistance: float, capacitance: float = 0.1e-9) -> complex:
        """Calculates the complex impedance of this antenna given the antenna L, R, C.
        A default C of 0.1pF
        From https://www.eetimes.eu/impedance-matching-for-nfc-applications/"""
        w = 2 * pi * freq
        realpart = resistance / ((1 - (w**2) * inductance * capacitance)**2 + (w * resistance * capacitance)**2)
        imagpart = (w * inductance - (w**3) * (inductance**2) * capacitance - w * (resistance**2) * capacitance) / \
                   ((1 - (w**2) * inductance * capacitance)**2 + (w * resistance * capacitance)**2)
        return complex(realpart, imagpart)

    def __init__(self):
        super().__init__()
        self.conn = self.Block(PassiveConnector(length=2))  # arbitrary

    def contents(self):
        super().contents()


class LcLowpassFilter(Block):
    @classmethod
    def _calculate_capacitance(cls, freq_cutoff: float, inductance: float) -> float:
        # from f = 1 / (2 pi sqrt(LC))
        return 1 / (inductance * (2*pi*freq_cutoff)**2)


class DifferentialLLowPassFilter:
    # TODO: implement as circuit generator

    @classmethod
    def _calculate_se_values(cls, freq: float, z1: complex, z2: complex) -> Tuple[float, float]:
        # calculate single-ended values from single-ended filter
        se_xs, se_xp = LLowPassFilter._calculate_impedance(z1, z2)
        se_cs = PiLowPassFilter._reactance_to_capacitance(freq, se_xs)
        se_cp = PiLowPassFilter._reactance_to_capacitance(freq, se_xp)
        return se_cs, se_cp


class Pn7160_Device(FootprintBlock, JlcPart):
    def __init__(self) -> None:
        super().__init__()
        self.vss = self.Port(Ground(), [Common])
        self.vbat = self.Port(VoltageSink.from_gnd(
            self.vss,
            voltage_limits=(2.5, 5.5)*Volt,
            current_draw=(0.0105, 290)*mAmp))  # hard power down to continuous transmit, limit of 330mA
        self.vddup = self.Port(VoltageSink.from_gnd(
            self.vss,
            voltage_limits=(2.8, 5.8)*Volt))
        self.vddpad = self.Port(VoltageSink.from_gnd(
            self.vss,
            voltage_limits=(3.0, 3.6)*Volt))  # also available in 1.8v nominal

        # internally generated supplies
        self.vdd = self.Port(VoltageSource(
            voltage_out=(1.7, 1.95)*Volt,  # Vddd pin characteristics
            current_limits=(0, 0)*Amp  # connect decap only
        ))
        self.vddmid = self.Port(VoltageSource(
            voltage_out=1.8*Volt(tol=0),  # assumed from external capacitor requirement
            current_limits=(0, 0)*Amp  # connect decap only
        ))
        self.vddtx = self.Port(VoltageSource(
            voltage_out=(self.vddup.link().voltage - 0.3*Volt).hull(2.5*Volt),  # up to 0.3v dropout
            current_limits=(0, 0)*Amp  # connect decap only
        ))

        self.xtal = self.Port(CrystalDriver(frequency_limits=27.12*MHertz(tol=50e-6)))

        # antenna interface
        self.tx1 = self.Port(Passive())
        self.tx2 = self.Port(Passive())
        self.rxp = self.Port(Passive())
        self.rxn = self.Port(Passive())

        # digital interfaces
        self.i2c = self.Port(I2cTarget(DigitalBidir.from_supply(
            self.vss, self.vddpad,
            input_threshold_factor=(0.3, 0.7)
        ), addresses=[0x28]))  # in ADR = (0, 0)

        self.irq = self.Port(DigitalSource.from_supply(
            self.vss, self.vddpad,
        ), optional=True)  # I2C can be polled, but IRQ is recommended
        self.ven = self.Port(DigitalSink.from_supply(  # reset
            self.vss, self.vbat,
            voltage_limit_tolerance=(0, 0),
            input_threshold_abs=(0.4, 1.1)*Volt
        ))

    def contents(self) -> None:
        self.footprint(
            'U', 'Package_DFN_QFN:HVQFN-40-1EP_6x6mm_P0.5mm_EP4.1x4.1mm',
            {
                '1': self.vss,  # self.i2c_adr0,
                # '2': DWL_REQ, firmware download control, leave open or ground if unused (internal pulldown)
                '3': self.vss,  # self.i2c_adr1,
                '4': self.vss,  # Vsspad
                '5': self.i2c.sda,
                '6': self.vddpad,
                '7': self.i2c.scl,
                '8': self.irq,
                '9': self.vss,  # VssA
                '10': self.ven,  # reset + hard power down
                # 11 internally connected, leave open
                '12': self.vbat,  # Vbat2
                '13': self.vddup,
                '14': self.vddtx,
                '15': self.rxn,
                '16': self.rxp,
                '17': self.vddmid,
                '18': self.vddtx,  # TVddIn
                '19': self.tx2,
                '20': self.vss,  # VssTx
                '21': self.tx1,
                '22': self.vddtx,  # TVddIn2
                # '23': self.ant1,  # ANT1/2, VddHF are for antenna connection for wake-up, not used
                # '24': self.ant2,
                # '25': self.vddhf,
                '26': self.vdd,  # AVdd
                '27': self.vdd,
                '28': self.vbat,
                '29': self.xtal.xtal_out,  # xtal2
                '30': self.xtal.xtal_in,  # nfc_clk_xtal1,
                '31': self.vdd,  # DVdd / Vddd
                # 32-36 NC
                # '37': self.dcdcen,  # for external DC-DC mode, connect to enable
                # 38 NC
                # '39': self.wkup_req,  # optional it seems, wake-up can be done via host interface
                # '40': self.clk_req,  # for clock-in, indicate when clock needs to be driven, unconnected if unused
                '41': self.vss,  # center pad
            },
            mfr='NXP', part='PN7160A1HN/C100Y',
            datasheet='https://www.nxp.com/docs/en/data-sheet/PN7160_PN7161.pdf'
        )
        self.assign(self.lcsc_part, 'C3303790')
        self.assign(self.actual_basic_part, False)


class Pn7160(Resettable, Block):
    """Multi-protocol NFC controller, up to 1.3W output power, in I2C ('A' suffix)
    """
    def __init__(self):
        super().__init__()
        self.ic = self.Block(Pn7160_Device())
        self.gnd = self.Export(self.ic.vss, [Common])
        self.pwr = self.Export(self.ic.vbat)
        self.pwr_io = self.Export(self.ic.vddpad)
        self.i2c = self.Export(self.ic.i2c)

    def contents(self):
        super().contents()

        self.connect(self.reset, self.ic.ven)
        self.connect(self.ic.vbat, self.ic.vddup)  # CFG1, VddUp and Vbat from same supply

        with self.implicit_connect(
                ImplicitConnect(self.gnd, [Common]),
        ) as imp:
            # caps table from hardware design guide, 10% or better tolerance recommended
            self.cvddup = imp.Block(DecouplingCapacitor(capacitance=4.7*uFarad(tol=0.1))).connected(pwr=self.ic.vddup)
            self.cvbat = imp.Block(DecouplingCapacitor(capacitance=4.7*uFarad(tol=0.1))).connected(pwr=self.ic.vbat)
            self.cvbat1 = imp.Block(DecouplingCapacitor(capacitance=100*nFarad(tol=0.1))).connected(pwr=self.ic.vbat)
            self.cvdd1 = imp.Block(DecouplingCapacitor(capacitance=2.2*uFarad(tol=0.1))).connected(pwr=self.ic.vdd)
            self.cvdd2 = imp.Block(DecouplingCapacitor(capacitance=2.2*uFarad(tol=0.1))).connected(pwr=self.ic.vdd)
            self.ctvdd1 = imp.Block(DecouplingCapacitor(capacitance=2.2*uFarad(tol=0.1))).connected(pwr=self.ic.vddtx)
            self.ctvdd2 = imp.Block(DecouplingCapacitor(capacitance=2.2*uFarad(tol=0.1))).connected(pwr=self.ic.vddtx)
            self.cvddpad = imp.Block(DecouplingCapacitor(capacitance=1*uFarad(tol=0.1))).connected(pwr=self.ic.vddpad)
            self.cvddmid = imp.Block(DecouplingCapacitor(capacitance=100*nFarad(tol=0.1))).connected(pwr=self.ic.vddmid)

            self.xtal = imp.Block(OscillatorReference(27.12*MHertz(tol=50e-6)))  # TODO only needed in RF polling mode
            self.connect(self.ic.xtal, self.xtal.crystal)

            # TODO antenna and RF filter / match generation
            # LC filter cutoff must be at least 14.4MHz (center + 848kHz sub carrier)
            # recommended asymmetrical cutoff is 22MHz, 160nH

            # matching circuit
