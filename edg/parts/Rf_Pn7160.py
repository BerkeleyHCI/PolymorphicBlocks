from typing import Tuple
from math import pi

from ..abstract_parts import *
from .JlcPart import JlcPart


class Pn7160_Device(FootprintBlock, JlcPart):
    def __init__(self) -> None:
        super().__init__()
        self.gnd = self.Port(Ground(), [Common])
        self.vbat = self.Port(VoltageSink.from_gnd(
            self.gnd,
            voltage_limits=(2.5, 5.5)*Volt,
            current_draw=(0.0105, 290)*mAmp))  # hard power down to continuous transmit, limit of 330mA
        self.vddup = self.Port(VoltageSink.from_gnd(
            self.gnd,
            voltage_limits=(2.8, 5.8)*Volt))
        self.vddpad = self.Port(VoltageSink.from_gnd(
            self.gnd,
            voltage_limits=(3.0, 3.6)*Volt))  # also available in 1.8v nominal

        self.xtal = self.Port(CrystalDriver(frequency_limits=27.12*MHertz(tol=50e-6)))

        self.i2c = self.Port(I2cTarget(..., addresses=[0x28]))  # in ADR = (0, 0)

        self.irq = self.Port(..., optional=True)  # I2C can be polled, but IRQ is recommended

        # self.vbat_io = self.Port(VoltageSink.from_gnd(
        #     self.gnd,
        #     voltage_limits=(1.8, 3.7)*Volt))  # no separate current draw given, lumped w/ Vbat
        #
        # self.vreg = self.Port(VoltageSource(  # may be a LDO output or DC-DC input
        #     voltage_out=1.55*Volt(tol=0)  # no tolerance specified
        # ))
        # self.dcc_sw = self.Port(Passive())
        #
        # self.xtal = self.Port(CrystalDriver())  # TODO loading caps not needed
        #
        # self.rfi_p = self.Port(Passive())
        # self.rfi_n = self.Port(Passive())
        # self.rfo = self.Port(Passive())
        # self.vr_pa = self.Port(VoltageSource(
        #     voltage_out=(0, 3.1)*Volt  # from power supply scheme figure
        # ))
        #
        # dio_model = DigitalBidir.from_supply(
        #     self.gnd, self.vbat_io,
        #     voltage_limit_tolerance=(-0.3, 0.3)*Volt,
        #     current_limits=(-0, 0)*mAmp,  # not specified
        #     input_threshold_factor=(0.3, 0.7)
        # )
        # self.dio1 = self.Port(dio_model, optional=True)  # generic IRQ
        # self.dio2 = self.Port(dio_model, optional=True)  # generic IRQ, plus TX switch (1=Tx, 0=otherwise)
        # self.dio3 = self.Port(dio_model, optional=True)  # generic IRQ, plus TXCO control
        # self.spi = self.Port(SpiPeripheral(dio_model, frequency_limit=(0, 16)*MHertz))
        # self.nss = self.Port(DigitalSink.from_bidir(dio_model))
        # self.busy = self.Port(DigitalSource.from_bidir(dio_model), optional=True)
        #
        # self.nreset = self.Port(DigitalSink.from_supply(
        #     self.gnd, self.vbat_io,
        #     voltage_limit_tolerance=(-0.3, 0.3)*Volt,
        #     input_threshold_factor=(0.2, 0.7)
        # ))

    def contents(self) -> None:
        self.footprint(
            'U', 'Package_DFN_QFN:HVQFN-40-1EP_6x6mm_P0.5mm_EP4.1x4.1mm',
            {
                '1': self.vss,  # self.i2c_adr0,
                # '2': DWL_REQ, firmware download control, leave open or ground if unused (internal pulldown)
                '3': self.vss,  # self.i2c_adr1,
                '4': self.vss,
                '5': self.i2c.sda,
                '6': self.vdd,
                '7': self.i2c.scl,
                '8': self.irq,
                '9': self.vss,
                '10': self.ven,  # reset + hard power down
                # 11 internally connected, leave open
                '12': self.vbat,  # Vbat2
                '13': self.vddup,
                '14': self.vddtx,
                '15': self.rxn,
                '16': self.rxp,
                '17': self.vddvmin,
                '18': self.vddtx,  # TVddIn
                '19': self.tx2,
                '20': self.vssx,
                '21': self.tx1,
                '22': self.vddtx,  # TVddIn2
                '23': self.ant1,
                '24': self.ant2,
                '25': self.vddhf,
                '26': self.vdda,
                '27': self.vdd,
                '28': self.vbat,
                '29': self.xtal.xtal_out,  # xtal2
                '30': self.xtal.xtal_in,  # nfc_clk_xtal1,
                '31': self.vddd,
                # 32-36 NC
                # '37': self.dcdcen,  # for external DC-DC mode, connect to enable
                # 38 NC
                '39': self.wkup_req,
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
        # self.pwr = self.Export(self.ic.vbat, [Power])
        self.gnd = self.Export(self.ic.gnd, [Common])

    def contents(self):
        super().contents()

        # TODO technically only needed in RF active polling mode
        self.xtal = self.Block(OscillatorReference(27.12*MHertz(tol=50e-6)))
        self.connect(self.xtal.gnd, self.gnd)
        self.connect(self.ic.xtal, self.xtal.crystal)

