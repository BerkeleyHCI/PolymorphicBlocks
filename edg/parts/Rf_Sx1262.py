from ..abstract_parts import *


class Sx1262_Device(FootprintBlock):
    def __init__(self) -> None:
        super().__init__()
        self.gnd = self.Port(Ground())
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
