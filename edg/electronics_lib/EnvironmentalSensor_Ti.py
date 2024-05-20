from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Hdc1080_Device(InternalSubcircuit, FootprintBlock, JlcPart):
    def __init__(self) -> None:
        super().__init__()
        self.gnd = self.Port(Ground())
        self.vdd = self.Port(VoltageSink(
            voltage_limits=(2.7, 5.5)*Volt,
            current_draw=(0.1, 300)*uAmp  # sleep to startup average
        ))

        dio_model = DigitalBidir.from_supply(
            self.gnd, self.vdd,
            input_threshold_factor=(0.3, 0.7)
        )
        self.i2c = self.Port(I2cTarget(dio_model, [0x40]))

    def contents(self) -> None:
        super().contents()
        self.footprint(
            'U', 'Package_SON:WSON-6-1EP_3x3mm_P0.95mm',
            {
                '1': self.i2c.sda,
                '2': self.gnd,
                # 3, 4 are NC
                '5': self.vdd,
                '6': self.i2c.scl,
                # EP explicitly should be left floating
            },
            mfr='Texas Instruments', part='HDC1080',
            datasheet='https://www.ti.com/lit/ds/symlink/hdc1080.pdf'
        )
        self.assign(self.lcsc_part, 'C82227')
        self.assign(self.actual_basic_part, False)


class Hdc1080(EnvironmentalSensor, Block):
    """Temperature and humidity sensor with +/- 0.2C and +/- 2% RH typical accuracy"""
    def __init__(self):
        super().__init__()
        self.ic = self.Block(Hdc1080_Device())
        self.pwr = self.Export(self.ic.vdd, [Power])
        self.gnd = self.Export(self.ic.gnd, [Common])
        self.i2c = self.Export(self.ic.i2c, [InOut])

    def contents(self):
        super().contents()
        # X7R capacitor recommended
        self.vdd_cap = self.Block(DecouplingCapacitor(0.1*uFarad(tol=0.2))).connected(self.gnd, self.ic.vdd)


class Tmp1075n_Device(InternalSubcircuit, FootprintBlock, JlcPart, GeneratorBlock):
    @init_in_parent
    def __init__(self, addr_lsb: IntLike) -> None:
        super().__init__()
        self.gnd = self.Port(Ground())
        self.vdd = self.Port(VoltageSink(
            voltage_limits=(1.62, 3.6)*Volt,
            current_draw=(0.5, 85)*uAmp  # shutdown to serial active
        ))

        dio_model = DigitalBidir.from_supply(
            self.gnd, self.vdd,
            input_threshold_factor=(0.3, 0.7)
        )
        self.i2c = self.Port(I2cTarget(dio_model, addresses=ArrayIntExpr()))
        self.alert = self.Port(DigitalSingleSource.low_from_supply(self.gnd), optional=True)

        self.addr_lsb = self.ArgParameter(addr_lsb)
        self.generator_param(self.addr_lsb)

    def generate(self) -> None:
        super().generate()
        addr_lsb = self.get(self.addr_lsb)
        self.require((addr_lsb < 4) & (addr_lsb >= 0), f"addr_lsb={addr_lsb} must be within [0, 4)")
        self.require((addr_lsb < 2), f"TODO: support A0=SDA/SCL")
        self.assign(self.i2c.addresses, [0x48 | addr_lsb])

        self.footprint(
            'U', 'Package_TO_SOT_SMD:SOT-563',
            {
                '1': self.i2c.scl,
                '2': self.gnd,
                '3': self.alert,
                '4': self.vdd if addr_lsb & 1 else self.gnd,  # A0
                '5': self.vdd,
                '6': self.i2c.sda,
            },
            mfr='Texas Instruments', part='TMP1075N',
            datasheet='https://www.ti.com/lit/ds/symlink/tmp1075.pdf'
        )
        self.assign(self.lcsc_part, 'C3663690')
        self.assign(self.actual_basic_part, False)


class Tmp1075n(EnvironmentalSensor, Block):
    """Temperature sensor with 0.25C typical accuracy"""
    @init_in_parent
    def __init__(self, addr_lsb: IntLike = 0):
        super().__init__()
        self.ic = self.Block(Tmp1075n_Device(addr_lsb))
        self.gnd = self.Export(self.ic.gnd, [Common])
        self.pwr = self.Export(self.ic.vdd, [Power])

        self.i2c = self.Export(self.ic.i2c, [InOut])
        self.alert = self.Export(self.ic.alert, optional=True, doc="Overtemperature SMBus alert")

    def contents(self):
        super().contents()
        self.vdd_cap = self.Block(DecouplingCapacitor(0.01*uFarad(tol=0.2))).connected(self.gnd, self.ic.vdd)
