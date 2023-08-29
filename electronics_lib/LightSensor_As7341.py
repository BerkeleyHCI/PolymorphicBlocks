from electronics_abstract_parts import *
from .JlcPart import JlcPart


class As7341_Device(InternalSubcircuit, FootprintBlock, JlcPart):
    def __init__(self) -> None:
        super().__init__()
        self.vdd = self.Port(VoltageSink(
            voltage_limits=(1.7, 2.0)*Volt,
            current_draw=(0.7, 300)*uAmp  # typ sleep to max active
        ))
        self.gnd = self.Port(Ground())

        dio_model = DigitalBidir.from_supply(
            self.gnd, self.vdd,
            voltage_limit_abs=(-0.3, 3.6)*Volt,
            input_threshold_abs=(0.54, 1.26)*Volt,
            output_threshold_abs=(0, float('inf'))*Volt # reflects pulldown
        )
        self.i2c = self.Port(I2cTarget(dio_model, [0x39]))

    def contents(self) -> None:
        self.footprint(
            'U', 'Package_LGA:AMS_OLGA-8_2x3.1mm_P0.8mm',
            {
                '1': self.vdd,
                '2': self.i2c.scl,
                '3': self.gnd,
                # '4': self.ldr,
                '5': self.gnd,  # PGND
                # '6': self.gpio,
                # '7': self.int,
                '8': self.i2c.sda,
            },
            mfr='ams', part='AS7341-DLGT',
            datasheet='https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/324/AS7341_DS.pdf'
        )
        self.assign(self.lcsc_part, 'C2655145')
        self.assign(self.actual_basic_part, False)


class As7341(LightSensor, Block):
    def __init__(self):
        super().__init__()
        self.ic = self.Block(As7341_Device())
        self.pwr = self.Export(self.ic.vdd, [Power])
        self.gnd = self.Export(self.ic.gnd, [Common])
        self.i2c = self.Export(self.ic.i2c)

    def contents(self):
        super().contents()
        # capacitance value assumed, same value as on Adafruit's breakout
        self.vdd_cap = self.Block(DecouplingCapacitor(100*nFarad(tol=0.2))).connected(self.gnd, self.ic.vdd)
