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


class Pe4259(Block, Nonstrict3v3Compatible):
    """RF switch between 10 MHz to 3000 MHz, 1.8-3.3v input.
    Requires all RF pins be held at 0v or are DC-blocked with a series cap.
    TODO: perhaps a RfSwitch base class? maybe some relation to AnalogSwitch? (though not valid at DC)
    """
    def __init__(self):
        super().__init__()
        self.ic = self.Block(Pe4259_Device())
        self.gnd = self.Export(self.ic.gnd, [Common])
        self.rf1 = self.Export(self.ic.rf1)
        self.rf2 = self.Export(self.ic.rf2)
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
        self.dio1 = self.Port(dio_model)
        self.dio2 = self.Port(dio_model)
        self.dio3 = self.Port(dio_model)
        self.spi = self.Port(SpiPeripheral(dio_model, frequency_limit=(0, 16)*MHertz))
        self.nss = self.Port(DigitalSink.from_bidir(dio_model))
        self.busy = self.Port(DigitalSource.from_bidir(dio_model))

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


class Sx1262(Block):
    """Sub-GHZ (150-960MHz) RF transceiver with LoRa support, with discrete RF frontend and parameterized by frequency.
    Up to 62.5kb/s in LoRa mode and 300kb/s in FSK mode."""
    def __init__(self):
        super().__init__()
        self.ic = self.Block(Sx1262_Device())
        self.pwr = self.Export(self.ic.vbat, [Power])
        self.gnd = self.Export(self.ic.gnd, [Common])

    def contents(self) -> None:
        super().contents()
        self.connect(self.ic.vbat_io, self.pwr)

        with self.implicit_connect(
                ImplicitConnect(self.gnd, [Common])
        ) as imp:
            self.xtal = self.Block(Crystal(30*MHertz(tol=30e-6)))  # 30ppm for LoRaWAN systems
            self.connect(self.xtal.crystal, self.ic.xtal)

            self.vreg_cap = self.Block(DecouplingCapacitor(470*nFarad(tol=0.2))).connected(pwr=self.ic.vreg)
            self.vbat_cap = self.Block(DecouplingCapacitor(100*nFarad(tol=0.2))).connected(pwr=self.ic.vbat)
            self.vdd_cap = self.Block(DecouplingCapacitor(1*uFarad(tol=0.2))).connected(pwr=self.ic.vbat)
            self.vrpa_cap0 = self.Block(DecouplingCapacitor(47*pFarad(tol=0.05))).connected(pwr=self.ic.vr_pa)
            self.vrpa_cap1 = self.Block(DecouplingCapacitor(47*nFarad(tol=0.05))).connected(pwr=self.ic.vr_pa)

            self.dcc_l = self.Block(Inductor(  # from datasheet 5.1.5
                15*uHenry(tol=0.2), current=(0, 100)*mAmp, frequency=20*MHertz(tol=0), resistance_dc=(0, 2)*Ohm))
            self.connect(self.dcc_l.a, self.ic.dcc_sw)
            self.connect(self.dcc_l.b.adapt_to(VoltageSink()), self.ic.vreg)  # actually the source, but ic assumes ldo

            # RF signal chain
            self.ant = self.Block(Antenna(frequency=(2402, 2484)*MHertz, impedance=50*Ohm(tol=0.1), power=(0, 0.126)*Watt))

            # transmit filter chain
            self.vrpa_choke = self.Block(Inductor(47*nHenry(tol=0.05)))  # see ST AN5457 for values for other frequencies

            # receive filter chain

            # switch
            dcblock_model = Capacitor(47*pFarad(tol=0.05))
            self.rf_sw = self.Block(Pe4259())
            self.tx_dcblock = self.Block(dcblock_model)
            # self.connect(self.tx_dcblock.neg, ...)
            self.connect(self.tx_dcblock.pos, self.rf_sw.rf1)
            self.rfc_dcblock = self.Block(dcblock_model)
            self.connect(self.rfc_dcblock.neg, self.rf_sw.rfc)

            # antenna
            (self.ant_pi, ), _ = self.chain(
                self.rfc_dcblock.pos,
                # imp.Block(PiLowPassFilter((2402-200, 2484+200)*MHertz, 35*Ohm, 10*Ohm, 50*Ohm,
                #                           0.10, self.pwr.link().voltage, (0, 0.1)*Amp)),
                self.ant.a)
