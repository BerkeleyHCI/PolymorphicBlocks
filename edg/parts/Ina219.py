from edg import *
from edg.parts.JlcPart import JlcPart


class Ina219_Device(InternalSubcircuit, JlcPart, FootprintBlock, Block):
    @init_in_parent
    def __init__(self):
        super().__init__()

        self.vs = self.Port(VoltageSink(
            voltage_limits=(3, 5.5) * Volt,
            current_draw=(6 * uAmp, 1 * mAmp)
        ))
        self.gnd = self.Port(Ground())

        dio_model = DigitalBidir.from_supply(
            self.gnd, self.vs,
            voltage_limit_tolerance=(-0.3, 0.3) * Volt,
            input_threshold_factor=(0.3, 0.7)
        )
        dio_sda_model = DigitalBidir.from_supply(
            self.gnd, self.vs,
            voltage_limit_abs=(-0.3 * Volt, 6.0 * Volt),
            input_threshold_factor=(0.3, 0.7)
        )

        self.i2c = self.Port(I2cTarget(DigitalBidir.empty(), addresses=[0x40]))
        self.i2c.sda.init_from(dio_sda_model)
        self.i2c.scl.init_from(DigitalSink.from_bidir(dio_model))

        self.in_pos = self.Port(AnalogSink(voltage_limits=(-0.3, 26) * Volt))
        self.in_neg = self.Port(AnalogSink(voltage_limits=(-0.3, 26) * Volt))

    def contents(self):
        super().contents()
        self.footprint(
            'U', 'Package_TO_SOT_SMD:SOT-23-8',
            {
                '1': self.in_pos,
                '2': self.in_neg,
                '3': self.gnd,
                '4': self.vs,
                '5': self.i2c.scl,
                '6': self.i2c.sda,
                '7': self.gnd,  # TODO: make this address selectable, sa0 pin
                '8': self.gnd  # TODO: make this address selectable, sa1 pin
            },
            mfr='Texas Instruments', part='INA219AIDCNR',
            datasheet='https://www.ti.com/lit/ds/symlink/ina219.pdf'
        )
        self.assign(self.lcsc_part, "C87469")


class Ina219(CurrentSensor, Block):
    """Current/voltage/power monitor with I2C interface"""

    @init_in_parent
    def __init__(self, shunt_resistor: RangeLike = 2.0 * mOhm(tol=0.05)):
        super().__init__()
        self.ic = self.Block(Ina219_Device())
        self.pwr = self.Export(self.ic.vs, [Power])
        self.gnd = self.Export(self.ic.gnd, [Common])
        self.i2c = self.Export(self.ic.i2c)

        self.vs_cap = self.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2))).connected(self.gnd, self.pwr)

        self.Rs = self.Block(CurrentSenseResistor(
            resistance=shunt_resistor,
        ))

        self.sense_pos = self.Export(self.Rs.pwr_in)
        self.sense_neg = self.Export(self.Rs.pwr_out)

    def contents(self):
        super().contents()
        self.connect(self.Rs.sense_in, self.ic.in_pos)
        self.connect(self.Rs.sense_out, self.ic.in_neg)
