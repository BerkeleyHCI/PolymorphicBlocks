from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Shtc3_Device(InternalSubcircuit, FootprintBlock, JlcPart):
    def __init__(self) -> None:
        super().__init__()
        self.vdd = self.Port(VoltageSink(
            voltage_limits=(1.62, 3.6)*Volt,
            current_draw=(0.3, 900)*uAmp  # typ sleep to max meas
        ))
        self.vss = self.Port(Ground())

        dio_model = DigitalBidir.from_supply(
            self.vss, self.vdd,
            input_threshold_factor=(0.42, 0.7)
        )
        self.i2c = self.Port(I2cTarget(dio_model, [0x70]))

    def contents(self) -> None:
        self.footprint(
            'U', 'Sensor_Humidity:Sensirion_DFN-4-1EP_2x2mm_P1mm_EP0.7x1.6mm',
            {
                '1': self.vdd,
                '2': self.i2c.scl,
                '3': self.i2c.sda,
                '4': self.vss,
                '5': self.vss,  # EP, recommended to be soldered for mechanical reasons (section 4)
            },
            mfr='Sensirion AG', part='SHTC3',
            datasheet='https://www.sensirion.com/media/documents/643F9C8E/63A5A436/Datasheet_SHTC3.pdf'
        )
        self.assign(self.lcsc_part, 'C194656')
        self.assign(self.actual_basic_part, False)


class Shtc3(EnvironmentalSensor, Block):
    def __init__(self):
        super().__init__()
        self.ic = self.Block(Shtc3_Device())
        self.vdd = self.Export(self.ic.vdd, [Power])
        self.gnd = self.Export(self.ic.vss, [Common])
        self.i2c = self.Export(self.ic.i2c)

    def contents(self):
        super().contents()  # capacitors from datasheet
        self.vdd_cap = self.Block(DecouplingCapacitor(100*nFarad(tol=0.2))).connected(self.gnd, self.ic.vdd)
