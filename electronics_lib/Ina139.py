from edg import *  # Importing all from the 'edg' library for electronics design

class Ina139_Device(FootprintBlock):

    def __init__(self) -> None:
        super().__init__()
        self.vin_plus = self.Port(AnalogSink(voltage_limits=(2.7, 40)*Volt,))
        self.vin_minus = self.Port(AnalogSink(voltage_limits=(2.7, 40)*Volt))
        self.vout = self.Port(AnalogSource())
        self.vplus = self.Port(VoltageSink(voltage_limits=(2.7, 40)*Volt, ))
        self.gnd = self.Port(Ground())

    def contents(self) -> None:
        super().contents()
        self.footprint(
            'U', 'Custom:SOT95P280X145-5N',
            {
                '1': self.vout,
                '2': self.gnd,
                '3': self.vin_plus,
                '4': self.vin_minus,
                '5': self.vplus,
            },
            mfr='Texas Instruments', part='INA139',
            datasheet='https://www.ti.com/product/INA139'
        )

class Ina139(Sensor, Block):
    def __init__(self, resistor_shunt: RangeLike, gain: FloatLike) -> None:
        super().__init__()
        # Instantiate the INA139 device
        self.ic = self.Block(Ina139_Device())
        self.Rs = self.Block(CurrentSenseResistor(value=resistor_shunt) )# 0.001Ohm -> 35A, 0.1Ohm -> 3.5A, 1Ohm -> 0.35A
        self.Rl = self.Block(Resistor(value=gain*kOhm(tol=0.05)))
        self.opa = self.Block(Opamp())


        self.vin_plus = self.Export(self.Rs.pwr_in)
        self.vin_minus = self.Export(self.Rs.pwr_out)


        self.vplus = self.Export(self.ic.vplus, [Power])
        self.gnd = self.Export(self.ic.gnd, [Common])
        self.vout = self.Export(self.opa.out)

    def contents(self):
        self.connect(self.ic.vin_plus, self.Rs.sense_in)
        self.connect(self.ic.vin_minus, self.Rs.sense_out)

        self.connect(self.Rl.a, self.vout)
        self.connect(self.Rl.b, self.gnd)

        self.connect(self.opa.pwr, self.ic.vplus)
        self.connect(self.opa.gnd, self.ic.gnd)
        self.connect(self.opa.inp, self.Rl.a)
        self.connect(self.opa.inn, self.gnd)

