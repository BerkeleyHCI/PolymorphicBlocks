from typing import Tuple
from math import pi

from ..abstract_parts import *
from .JlcPart import JlcPart


class Pe4259_Device(InternalSubcircuit, FootprintBlock, JlcPart):
    def __init__(self):
        super().__init__()

        self.gnd = self.Port(Ground())
        self.vdd = self.Port(Passive())  # modeled in container, series resistor recommended

        self.rf1 = self.Port(Passive())
        self.rf2 = self.Port(Passive())
        self.rfc = self.Port(Passive())

        self.ctrl = self.Port(Passive())  # modeled in container, series resistor recommended

    def contents(self):
        super().contents()

        self.footprint(
            'U', 'Package_TO_SOT_SMD:SOT-363_SC-70-6',
            {
                '1': self.rf1,
                '2': self.gnd,
                '3': self.rf2,
                '4': self.ctrl,
                '5': self.rfc,
                '6': self.vdd,
            },
            mfr='pSemi', part='PE4259',
            datasheet='https://www.psemi.com/pdf/datasheets/pe4259ds.pdf'
        )
        self.assign(self.lcsc_part, 'C470892')
        self.assign(self.actual_basic_part, False)


class Pe4259(Nonstrict3v3Compatible, Block):
    """RF switch between 10 MHz to 3000 MHz, 1.8-3.3v input.
    Requires all RF pins be held at 0v or are DC-blocked with a series cap.
    TODO: perhaps a RfSwitch base class? maybe some relation to AnalogSwitch? (though not valid at DC)
    """
    def __init__(self):
        super().__init__()
        self.ic = self.Block(Pe4259_Device())
        self.gnd = self.Export(self.ic.gnd, [Common])
        self.rf1 = self.Export(self.ic.rf1)  # connected when CTRL high
        self.rf2 = self.Export(self.ic.rf2)  # connected when CTRL low
        self.rfc = self.Export(self.ic.rfc)
        self.ctrl = self.Port(DigitalSink.empty())
        self.vdd = self.Port(VoltageSink.empty(), [Power])

    def contents(self):
        super().contents()

        self.vdd_res = self.Block(Resistor(1*kOhm(tol=0.05)))
        self.connect(self.vdd_res.b, self.ic.vdd)
        self.connect(self.vdd_res.a.adapt_to(VoltageSink.from_gnd(
                self.gnd,
                voltage_limits=self.nonstrict_3v3_compatible.then_else(
                    (1.8, 4.0)*Volt,
                    (1.8, 3.3)*Volt),
                current_draw=(9, 20)*uAmp,
        )), self.vdd)

        self.ctrl_res = self.Block(Resistor(1*kOhm(tol=0.05)))
        self.connect(self.ctrl_res.b, self.ic.ctrl)
        self.connect(self.ctrl_res.a.adapt_to(DigitalSink.from_supply(
            self.gnd, self.vdd,
            voltage_limit_tolerance=(-0.3, 0.3)*Volt,
            input_threshold_factor=(0.3, 0.7)
        )), self.ctrl)


class Sx1262BalunLike(InternalSubcircuit, GeneratorBlock):
    """'Balun' circuit with design methodology from ST AN5457 LNA matching methodology.
    This consists of a high-pass L impedance-matching network plus a capacitor to balance out the differential
    input voltages. The series cap then needs to be adjusted for the mismatch from the balancing cap.
    """
    @classmethod
    def _calculate_values(cls, freq: float, z_int: complex, z_ext: complex) -> Tuple[float, float, float]:
        """Calculate component values, returning the inductor, series cap, and parallel cap.
        The input cap to GND is DNP and omitted."""
        l_l, l_c = LHighPassFilter._calculate_values(freq, z_int, z_ext)
        # need the raw l (excluding the part canceling out internal reactance) to determine Cp
        l_raw, _ = LHighPassFilter._calculate_values(freq, complex(z_int.real, 0), z_ext)
        cp = PiLowPassFilter._reactance_to_capacitance(freq, -l_raw * 2 * pi * freq / 2)
        # since cp is in series with l_c (through l_l), we need to eliminate its effect from l_c
        l_c_new = (l_c * cp) / (cp - l_c)
        return l_l, l_c_new, cp

    @init_in_parent
    def __init__(self, frequency: FloatLike, src_resistance: FloatLike, src_reactance: FloatLike,
                 load_resistance: FloatLike, tolerance: FloatLike,
                 voltage: RangeLike, current: RangeLike):
        super().__init__()
        self.gnd = self.Port(Ground.empty(), [Common])
        self.input = self.Port(Passive.empty())
        self.rfi_n = self.Port(Passive.empty())
        self.rfi_p = self.Port(Passive.empty())

        self.frequency = self.ArgParameter(frequency)
        self.src_resistance = self.ArgParameter(src_resistance)
        self.src_reactance = self.ArgParameter(src_reactance)
        self.load_resistance = self.ArgParameter(load_resistance)
        self.voltage = self.ArgParameter(voltage)
        self.current = self.ArgParameter(current)
        self.tolerance = self.ArgParameter(tolerance)

        self.generator_param(self.frequency, self.src_resistance, self.src_reactance, self.load_resistance,
                             self.tolerance)

    def generate(self) -> None:
        super().generate()

        zs = complex(self.get(self.src_resistance), self.get(self.src_reactance))
        rl = complex(self.get(self.load_resistance), 0)

        l, c, c_p = self._calculate_values(self.get(self.frequency), zs, rl)
        tolerance = self.get(self.tolerance)

        self.l = self.Block(Inductor(inductance=l*Henry(tol=tolerance), current=self.current))
        self.c = self.Block(Capacitor(capacitance=c*Farad(tol=tolerance), voltage=self.voltage))
        self.c_p = self.Block(Capacitor(capacitance=c_p*Farad(tol=tolerance), voltage=self.voltage))

        self.connect(self.input, self.c.pos)
        self.connect(self.rfi_n, self.c.neg, self.l.a)
        self.connect(self.rfi_p, self.c_p.pos, self.l.b)
        self.connect(self.gnd, self.c_p.neg.adapt_to(Ground()))


class Sx1262_Device(FootprintBlock):
    def __init__(self) -> None:
        super().__init__()
        self.gnd = self.Port(Ground(), [Common])
        self.vbat = self.Port(VoltageSink.from_gnd(
            self.gnd,  # include Vbat
            voltage_limits=(1.8, 3.7)*Volt,
            current_draw=(0.000160, 118)*mAmp))  # from IDDOFF to max TX
        self.vbat_io = self.Port(VoltageSink.from_gnd(
            self.gnd,
            voltage_limits=(1.8, 3.7)*Volt))  # no separate current draw given, lumped w/ Vbat

        self.vreg = self.Port(VoltageSource(  # may be a LDO output or DC-DC input
            voltage_out=1.55*Volt(tol=0)  # no tolerance specified
        ))
        self.dcc_sw = self.Port(Passive())

        self.xtal = self.Port(CrystalDriver())  # TODO loading caps not needed

        self.rfi_p = self.Port(Passive())
        self.rfi_n = self.Port(Passive())
        self.rfo = self.Port(Passive())
        self.vr_pa = self.Port(VoltageSource(
            voltage_out=(0, 3.1)*Volt  # from power supply scheme figure
        ))

        dio_model = DigitalBidir.from_supply(
            self.gnd, self.vbat_io,
            voltage_limit_tolerance=(-0.3, 0.3)*Volt,
            current_limits=(-0, 0)*mAmp,  # not specified
            input_threshold_factor=(0.3, 0.7)
        )
        self.dio1 = self.Port(dio_model, optional=True)  # generic IRQ
        self.dio2 = self.Port(dio_model, optional=True)  # generic IRQ, plus TX switch (1=Tx, 0=otherwise)
        self.dio3 = self.Port(dio_model, optional=True)  # generic IRQ, plus TXCO control
        self.spi = self.Port(SpiPeripheral(dio_model, frequency_limit=(0, 16)*MHertz))
        self.nss = self.Port(DigitalSink.from_bidir(dio_model))
        self.busy = self.Port(DigitalSource.from_bidir(dio_model), optional=True)

        self.nreset = self.Port(DigitalSink.from_supply(
            self.gnd, self.vbat_io,
            voltage_limit_tolerance=(-0.3, 0.3)*Volt,
            input_threshold_factor=(0.2, 0.7)
        ))

    def contents(self) -> None:
        self.footprint(
            'U', 'Package_DFN_QFN:QFN-24-1EP_4x4mm_P0.5mm_EP2.6x2.6mm',
            {
                '1': self.vbat,  # Vdd_in, internally connected to pin 10
                '2': self.gnd,
                '3': self.xtal.xtal_in,  # XTA
                '4': self.xtal.xtal_out,  # XTB
                '5': self.gnd,
                '6': self.dio3,
                '7': self.vreg,
                '8': self.gnd,
                '9': self.dcc_sw,
                '10': self.vbat,
                '11': self.vbat_io,
                '12': self.dio2,
                '13': self.dio1,
                '14': self.busy,
                '15': self.nreset,
                '16': self.spi.miso,
                '17': self.spi.mosi,
                '18': self.spi.sck,
                '19': self.nss,
                '20': self.gnd,
                '21': self.rfi_p,
                '22': self.rfi_n,
                '23': self.rfo,
                '24': self.vr_pa,
                '25': self.gnd,  # EP, labeled as pin 0 on datasheet
            },
            mfr='Semtech Corporation', part='SX1262',
            datasheet='https://semtech.my.salesforce.com/sfc/p/E0000000JelG/a/2R000000Un7F/yT.fKdAr9ZAo3cJLc4F2cBdUsMftpT2vsOICP7NmvMo'
        )


class Sx1262(Resettable, Block):
    """Sub-GHZ (150-960MHz) RF transceiver with LoRa support, with discrete RF frontend and parameterized by frequency.
    Up to 62.5kb/s in LoRa mode and 300kb/s in FSK mode.
    TODO: RF frequency parameterization
    """
    def __init__(self):
        super().__init__()
        self.ic = self.Block(Sx1262_Device())
        self.pwr = self.Export(self.ic.vbat, [Power])
        self.gnd = self.Export(self.ic.gnd, [Common])

        self.spi = self.Export(self.ic.spi)
        self.cs = self.Export(self.ic.nss)
        self.require(self.reset.is_connected())  # TODO allow hard tie?
        self.connect(self.reset, self.ic.nreset)
        self.dio1 = self.Export(self.ic.dio1, optional=True)

    def contents(self) -> None:
        super().contents()
        self.connect(self.ic.vbat_io, self.pwr)

        with self.implicit_connect(
                ImplicitConnect(self.gnd, [Common])
        ) as imp:
            self.xtal = imp.Block(Crystal(30*MHertz(tol=30e-6)))  # 30ppm for LoRaWAN systems
            self.connect(self.xtal.crystal, self.ic.xtal)

            self.vreg_cap = imp.Block(DecouplingCapacitor(470*nFarad(tol=0.2))).connected(pwr=self.ic.vreg)
            self.vbat_cap = imp.Block(DecouplingCapacitor(100*nFarad(tol=0.2))).connected(pwr=self.ic.vbat)
            self.vdd_cap = imp.Block(DecouplingCapacitor(1*uFarad(tol=0.2))).connected(pwr=self.ic.vbat)
            self.vrpa_cap0 = imp.Block(DecouplingCapacitor(47*pFarad(tol=0.05))).connected(pwr=self.ic.vr_pa)
            self.vrpa_cap1 = imp.Block(DecouplingCapacitor(47*nFarad(tol=0.05))).connected(pwr=self.ic.vr_pa)

            self.dcc_l = self.Block(Inductor(  # from datasheet 5.1.5
                15*uHenry(tol=0.2), current=(0, 100)*mAmp, frequency=20*MHertz(tol=0), resistance_dc=(0, 2)*Ohm))
            self.connect(self.dcc_l.a, self.ic.dcc_sw)
            self.connect(self.dcc_l.b.adapt_to(VoltageSink()), self.ic.vreg)  # actually the source, but ic assumes ldo

            # RF signal chain
            # switch
            rf_voltage = (0, 10)*Volt  # assumed, wild guess
            rf_current = (0, 100)*mAmp  # assumed, wild guess
            dcblock_model = Capacitor(47*pFarad(tol=0.05), voltage=rf_voltage)
            self.rf_sw = imp.Block(Pe4259())
            self.connect(self.rf_sw.vdd, self.pwr)
            self.connect(self.rf_sw.ctrl, self.ic.dio2)
            self.tx_dcblock = self.Block(dcblock_model)
            self.connect(self.tx_dcblock.pos, self.rf_sw.rf1)
            self.rfc_dcblock = self.Block(dcblock_model)
            self.connect(self.rfc_dcblock.neg, self.rf_sw.rfc)

            # transmit filter chain
            self.vrpa_choke = self.Block(Inductor(47*nHenry(tol=0.05)))  # see ST AN5457 for other frequencies
            self.connect(self.vrpa_choke.a.adapt_to(VoltageSink()), self.ic.vr_pa)
            self.connect(self.ic.rfo, self.vrpa_choke.b)

            (self.tx_l, self.tx_pi), _ = self.chain(
                self.ic.rfo,
                imp.Block(LLowPassFilterWith2HNotch(915*MHertz, 11.7*Ohm, -4.8*Ohm, 50*Ohm, 0.1,
                                                    rf_voltage, rf_current)),
                imp.Block(PiLowPassFilter((915-915/2, 915+915/2)*MHertz, 50*Ohm, 0, 50*Ohm, 0.1,  # Q=1
                                          rf_voltage, rf_current)),
                self.tx_dcblock.neg
            )

            # receive filter chain
            self.balun = imp.Block(Sx1262BalunLike(915*MHertz, 74*Ohm, -134*Ohm, 50*Ohm, 0.1,
                                                    rf_voltage, rf_current))
            self.connect(self.balun.input, self.rf_sw.rf2)
            self.connect(self.balun.rfi_n, self.ic.rfi_n)
            self.connect(self.balun.rfi_p, self.ic.rfi_p)

            # antenna
            (self.ant_pi, self.ant), _ = self.chain(
                self.rfc_dcblock.pos,
                imp.Block(PiLowPassFilter((915-915/2, 915+915/2)*MHertz, 50*Ohm, 0, 50*Ohm, 0.1,  # Q=1
                                          rf_voltage, rf_current)),
                imp.Block(Antenna(frequency=(915-0.5, 915+0.5)*MHertz,  # up to 500kHz bandwidth in LoRa mode
                                  impedance=50*Ohm(tol=0.1), power=(0, 0.159)*Watt)))    # +22dBm
