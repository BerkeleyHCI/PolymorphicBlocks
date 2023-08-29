from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Bh1750_Device(InternalSubcircuit, FootprintBlock, JlcPart):
    def __init__(self) -> None:
        super().__init__()
        self.vcc = self.Port(VoltageSink(
            voltage_limits=(2.4, 3.6)*Volt,
            current_draw=(0.01*uAmp, 190*uAmp)  # typ powerdown to max supply current
        ))
        self.dvi = self.Port(Passive())  # some kind of reset pin
        self.gnd = self.Port(Ground())

        dio_model = DigitalBidir.from_supply(
            self.gnd, self.vcc,
            input_threshold_factor=(0.3, 0.7)
        )
        self.i2c = self.Port(I2cTarget(dio_model, [0x23]))

    def contents(self) -> None:
        self.footprint(
            'U', 'Package_TO_SOT_SMD:HVSOF6',
            {
                '1': self.vcc,
                '2': self.gnd,  # TODO address support
                '3': self.gnd,
                '4': self.i2c.sda,
                '5': self.dvi,
                '6': self.i2c.scl,
            },
            mfr='Rohm Semiconductor', part='BH1750',
            datasheet='https://www.mouser.com/datasheet/2/348/bh1750fvi-e-186247.pdf'
        )
        self.assign(self.lcsc_part, 'C78960')
        self.assign(self.actual_basic_part, False)


class Bh1750(LightSensor, Block):
    def __init__(self):
        super().__init__()
        self.ic = self.Block(Bh1750_Device())
        self.pwr = self.Export(self.ic.vcc, [Power])
        self.gnd = self.Export(self.ic.gnd, [Common])
        self.i2c = self.Export(self.ic.i2c)

    def contents(self):
        super().contents()  # capacitors from shuttle board example
        self.vcc_cap = self.Block(DecouplingCapacitor(100*nFarad(tol=0.2))).connected(self.gnd, self.ic.vcc)
        self.dvi_res = self.Block(Resistor(1*kOhm(tol=0.05)))
        self.connect(self.dvi_res.a.adapt_to(VoltageSink()), self.pwr)
        self.connect(self.dvi_res.b, self.ic.dvi)
        self.dvi_cap = self.Block(Capacitor(1*uFarad(tol=0.2), self.pwr.link().voltage))
        self.connect(self.dvi_cap.pos, self.ic.dvi)
        self.connect(self.dvi_cap.neg.adapt_to(Ground()), self.gnd)
