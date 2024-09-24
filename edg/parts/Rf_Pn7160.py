from typing import Tuple
from math import pi

from ..abstract_parts import *
from .JlcPart import JlcPart


# TODO: some of these are pretty general RF building blocks and can be moved into shared libraries
# but until there are enough use cases they'll be buried here for now
# TODO: this is a bit of a structural mess right now, as with the other RF blocks, and needs refactoring
# TODO: maybe have a RfPort / DifferentialRfPort bidirectional type modeling impedances
# TODO: use actual component values in calculations, to account for tolerance stackup

class NfcAntenna(GeneratorBlock):
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

    @init_in_parent
    def __init__(self, freq: FloatLike, inductance: FloatLike, resistance: FloatLike, capacitance: FloatLike):
        super().__init__()
        self.conn = self.Block(PassiveConnector(length=2))  # arbitrary
        self.ant1 = self.Port(Passive())
        self.ant2 = self.Port(Passive())

        self.freq = self.ArgParameter(freq)
        self.inductance = self.ArgParameter(inductance)
        self.resistance = self.ArgParameter(resistance)
        self.capacitance = self.ArgParameter(capacitance)
        self.generator_param(self.freq, self.inductance, self.resistance, self.capacitance)
        self.z_real = self.Parameter(FloatExpr())
        self.z_imag = self.Parameter(FloatExpr())

    def generate(self):
        super().generate()

        self.connect(self.ant1, self.conn.pins.request('1'))
        self.connect(self.ant2, self.conn.pins.request('2'))

        impedance = NfcAntenna.impedance_from_lrc(self.get(self.freq), self.get(self.inductance),
                                                  self.get(self.resistance), self.get(self.capacitance))
        self.assign(self.z_real, impedance.real)
        self.assign(self.z_imag, impedance.imag)


class NfcAntennaDampening(GeneratorBlock):
    """Differential antenna dampening circuit, two inline resistors to achieve some target Q
    """
    @classmethod
    def damp_res_from_impedance(self, impedance: complex, target_q: float) -> float:
        """Calculates the single-ended damping resistance needed to achieve some target Q.
        For differential configuration, halve the result and split among the +/- terminals."""
        return impedance.imag / target_q - impedance.real

    @init_in_parent
    def __init__(self, target_q: FloatLike, ant_r: FloatLike, ant_x: FloatLike):
        super().__init__()
        self.in1 = self.Port(Passive())
        self.in2 = self.Port(Passive())
        self.ant1 = self.Port(Passive())
        self.ant2 = self.Port(Passive())

        self.target_q = self.ArgParameter(target_q)
        self.ant_r = self.ArgParameter(ant_r)
        self.ant_x = self.ArgParameter(ant_x)
        self.generator_param(self.target_q, self.ant_r, self.ant_x)
        self.z_real = self.Parameter(FloatExpr())
        self.z_imag = self.Parameter(FloatExpr())

    def generate(self):
        super().generate()

        res_value = self.damp_res_from_impedance(complex(self.get(self.ant_r), self.get(self.ant_x)),
                                                 self.get(self.target_q))
        res_model = Resistor((res_value / 2)*Ohm(tol=0.05))
        self.r1 = self.Block(res_model)
        self.r2 = self.Block(res_model)
        self.connect(self.in1, self.r1.a)
        self.connect(self.in2, self.r2.a)
        self.connect(self.r1.b, self.ant1)
        self.connect(self.r2.b, self.ant2)
        self.assign(self.z_real, self.ant_r + res_value * 2)
        self.assign(self.z_imag, self.ant_x)


class DifferentialLcLowpassFilter(GeneratorBlock):
    """Differential LC lowpass filter, commonly used as an EMC filter in the NFC analog frontend
    Input resistance is used to calculate the output impedance"""
    @classmethod
    def _calculate_capacitance(cls, freq_cutoff: float, inductance: float) -> float:
        return 1 / (inductance * (2*pi*freq_cutoff)**2)  # from f = 1 / (2 pi sqrt(LC))

    @init_in_parent
    def __init__(self, freq_cutoff: FloatLike, inductance: FloatLike, input_res: FloatLike,
                 freq: FloatLike, current: RangeExpr, voltage: RangeExpr):
        super().__init__()
        self.freq_cutoff = self.ArgParameter(freq_cutoff)
        self.inductance = self.ArgParameter(inductance)
        self.input_res = self.ArgParameter(input_res)
        self.freq = self.ArgParameter(freq)
        self.current = self.ArgParameter(current)
        self.voltage = self.ArgParameter(voltage)
        self.z_real = self.Parameter(FloatExpr())  # output impedance real part
        self.z_imag = self.Parameter(FloatExpr())

        self.generator_param(self.freq_cutoff, self.inductance, self.input_res, self.freq)

        self.in1 = self.Port(Passive())
        self.in2 = self.Port(Passive())
        self.out1 = self.Port(Passive())
        self.out2 = self.Port(Passive())
        self.gnd = self.Port(Ground.empty(), [Common])

    def generate(self):
        super().generate()

        inductor_model = Inductor(self.get(self.inductance)*Henry(tol=0.1),
                                  current=self.current, frequency=(0, self.freq_cutoff))
        self.l1 = self.Block(inductor_model)
        self.l2 = self.Block(inductor_model)
        capacitance = self._calculate_capacitance(self.get(self.freq_cutoff), self.get(self.inductance))
        cap_model = Capacitor(capacitance*Farad(tol=0.1), voltage=self.voltage)
        self.c1 = self.Block(cap_model)
        self.c2 = self.Block(cap_model)
        self.connect(self.in1, self.l1.a)
        self.connect(self.l1.b, self.c1.pos, self.out1)
        self.connect(self.in2, self.l2.a)
        self.connect(self.l2.b, self.c2.pos, self.out2)
        self.connect(self.c1.neg.adapt_to(Ground()), self.c2.neg.adapt_to(Ground()), self.gnd)

        impedance = NfcAntenna.impedance_from_lrc(self.get(self.freq), self.get(self.inductance),
                                                  self.get(self.input_res), capacitance)
        self.assign(self.z_real, impedance.real)
        self.assign(self.z_imag, impedance.imag)


class DifferentialLLowPassFilter(GeneratorBlock):
    @classmethod
    def _calculate_se_values(cls, freq: float, z1: complex, z2: complex) -> Tuple[float, float]:
        # calculate single-ended values from single-ended filter
        se_xs, se_xp = LLowPassFilter._calculate_impedance(z1, z2)
        se_cs = PiLowPassFilter._reactance_to_capacitance(freq, se_xs)
        se_cp = PiLowPassFilter._reactance_to_capacitance(freq, se_xp)
        return se_cs, se_cp

    @init_in_parent
    def __init__(self, freq: FloatLike, src_r: FloatLike, src_x: FloatLike, snk_r: FloatLike, snk_x: FloatLike,
                 voltage: RangeLike):
        super().__init__()
        self.freq = self.ArgParameter(freq)
        self.src_r = self.ArgParameter(src_r)
        self.src_x = self.ArgParameter(src_x)
        self.snk_r = self.ArgParameter(snk_r)
        self.snk_x = self.ArgParameter(snk_x)
        self.voltage = self.ArgParameter(voltage)
        self.generator_param(self.freq, self.src_r, self.src_x, self.snk_r, self.snk_x)

        self.in1 = self.Port(Passive())
        self.in2 = self.Port(Passive())
        self.out1 = self.Port(Passive())
        self.out2 = self.Port(Passive())
        self.gnd = self.Port(Ground.empty(), [Common])

    def generate(self):
        super().generate()

        diff_cs, diff_cp = self._calculate_se_values(self.get(self.freq),
                                                     complex(self.get(self.src_r), self.get(self.src_x)),
                                                     complex(self.get(self.snk_r), self.get(self.snk_x)))
        cs_model = Capacitor(diff_cs*2*Farad(tol=0.1), voltage=self.voltage)
        self.cs1 = self.Block(cs_model)
        self.cs2 = self.Block(cs_model)
        cp_model = Capacitor(diff_cp*2*Farad(tol=0.1), voltage=self.voltage)
        self.cp1 = self.Block(cp_model)
        self.cp2 = self.Block(cp_model)
        self.connect(self.in1, self.cs1.pos)
        self.connect(self.cs1.neg, self.cp1.pos, self.out1)
        self.connect(self.in2, self.cs2.pos)
        self.connect(self.cs2.neg, self.cp2.pos, self.out2)
        self.connect(self.cp1.neg.adapt_to(Ground()), self.cp2.neg.adapt_to(Ground()), self.gnd)


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

            # for symmetrical tuning, 14.4-14.7MHz cutoff, for asymmetrical tuning, 20-22MHz cutoff
            # 20-ohm differential to TX1-TX2 is a recommendation from the datasheet
            # voltage and current are guesses, voltage is to spec a 50V NP0
            # while the reference design uses 160nH, this chooses 220nH to align with the E6 series
            SIGNAL_FREQ = 13.56*MHertz

            self.emc = imp.Block(DifferentialLcLowpassFilter(
                freq_cutoff=14.7*MHertz, inductance=220*nHenry, input_res=20*Ohm,
                freq=SIGNAL_FREQ, current=(0, 300)*mAmp, voltage=(0, 25)*Volt
            ))  # TODO should calculate impedance separately from the filter
            self.connect(self.ic.tx1, self.emc.in1)
            self.connect(self.ic.tx2, self.emc.in2)

            # ant specs from NXP AN13219 for 40x40mm PCB antemma
            self.ant = self.Block(NfcAntenna(freq=SIGNAL_FREQ, inductance=1522*nHenry,
                                             resistance=1.40*Ohm, capacitance=2.0*pFarad))
            self.damp = self.Block(NfcAntennaDampening(target_q=20, ant_r=self.ant.z_real, ant_x=self.ant.z_imag))
            self.connect(self.damp.ant1, self.ant.ant1)
            self.connect(self.damp.ant2, self.ant.ant2)

            self.match = imp.Block(DifferentialLLowPassFilter(  # complex conjugate both sides
                freq=SIGNAL_FREQ, src_r=self.emc.z_real, src_x=-self.emc.z_imag,
                snk_r=self.damp.z_real, snk_x=-self.damp.z_imag, voltage=(0, 25)*Volt
            ))
            self.connect(self.emc.out1, self.match.in1)
            self.connect(self.emc.out2, self.match.in2)

            self.connect(self.match.out1, self.damp.in1)
            self.connect(self.match.out2, self.damp.in2)
