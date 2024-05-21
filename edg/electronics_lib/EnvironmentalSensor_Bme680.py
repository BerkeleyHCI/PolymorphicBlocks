from ..electronics_abstract_parts import *
from .JlcPart import JlcPart


class Bme680_Device(InternalSubcircuit, FootprintBlock, JlcPart):
    def __init__(self) -> None:
        super().__init__()
        self.vdd = self.Port(VoltageSink(
            voltage_limits=(1.71, 3.6)*Volt,
            current_draw=(0.15*uAmp, 18*mAmp)  # typ sleep to peak gas sensor supply
        ))
        self.vddio = self.Port(VoltageSink(
            voltage_limits=(1.2, 3.6)*Volt
        ))
        self.gnd = self.Port(Ground())

        dio_model = DigitalBidir.from_supply(
            self.gnd, self.vddio,
            voltage_limit_abs=(-0.3*Volt, self.vddio.voltage_limits.upper()+0.3),
            input_threshold_factor=(0.2, 0.8)
        )
        self.i2c = self.Port(I2cTarget(dio_model, [0x76]))

    def contents(self) -> None:
        self.footprint(
            'U', 'Package_LGA:Bosch_LGA-8_3x3mm_P0.8mm_ClockwisePinNumbering',
            {
                '1': self.gnd,
                '2': self.vddio,  # different in SPI mode
                '3': self.i2c.sda,
                '4': self.i2c.scl,
                '5': self.gnd,  # TODO address
                '6': self.vddio,
                '7': self.gnd,
                '8': self.vdd,
            },
            mfr='Bosch Sensortec', part='BME680',
            datasheet='https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme680-ds001.pdf'
        )
        self.assign(self.lcsc_part, 'C125972')
        self.assign(self.actual_basic_part, False)


class Bme680(EnvironmentalSensor, DefaultExportBlock):
    """Gas (indoor air quality), pressure, temperature, and humidity sensor.
    Humidity accuracy /-3% RH, pressure noise 0.12 Pa, temperature accuracy +/-0.5 C @ 25C"""
    def __init__(self):
        super().__init__()
        self.ic = self.Block(Bme680_Device())
        self.gnd = self.Export(self.ic.gnd, [Common])
        self.pwr = self.Export(self.ic.vdd, [Power])
        self.pwr_io = self.Export(self.ic.vddio, default=self.pwr, doc="IO supply voltage")
        self.i2c = self.Export(self.ic.i2c, [InOut])

    def contents(self):
        super().contents()  # capacitors from shuttle board example
        self.vdd_cap = self.Block(DecouplingCapacitor(100*nFarad(tol=0.2))).connected(self.gnd, self.ic.vdd)
        self.vddio_cap = self.Block(DecouplingCapacitor(100*nFarad(tol=0.2))).connected(self.gnd, self.ic.vddio)
