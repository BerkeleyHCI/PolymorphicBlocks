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
    def __init__(self):
        super().__init__()
        self.ic = self.Block(Hdc1080_Device())
        self.vdd = self.Export(self.ic.vdd, [Power])
        self.gnd = self.Export(self.ic.gnd, [Common])
        self.i2c = self.Export(self.ic.i2c, [InOut])

    def contents(self):
        super().contents()
        # X7R capacitor recommended
        self.vdd_cap = self.Block(DecouplingCapacitor(0.1*uFarad(tol=0.2))).connected(self.gnd, self.ic.vdd)
