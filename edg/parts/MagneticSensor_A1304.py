from ..abstract_parts import *
from .JlcPart import JlcPart


class A1304_Device(InternalBlock, FootprintBlock, JlcPart):
    def __init__(self) -> None:
        super().__init__()
        self.gnd = self.Port(Ground())
        self.vcc = self.Port(VoltageSink.from_gnd(
            self.gnd,
            voltage_limits=(3, 3.6)*Volt,
            current_draw=(7.7, 9)*mAmp,  # typ to max
        ))
        self.vout = self.Port(AnalogSource.from_supply(
            self.gnd, self.vcc,
            signal_out_abs=(0.38, 2.87)  # output saturation limits @ Vcc=3.3v
        ))

    def contents(self):
        self.footprint(
            'U', 'Package_TO_SOT_SMD:SOT-23',
            {
                '1': self.vcc,
                '2': self.vout,
                '3': self.gnd,
            },
            mfr="Allegro MicroSystems", part='A1304ELHLX-T',
            datasheet='https://www.allegromicro.com/~/media/Files/Datasheets/A1304-Datasheet.ashx')

        self.assign(self.lcsc_part, 'C545185')
        self.assign(self.actual_basic_part, False)


class A1304(Magnetometer, Block):
    """Linear hall-effect sensor with analog output, sometimes used in game controllers as trigger detectors.
    Typ 4 mV / Gauss with full scale range of +/-375 Gauss."""
    def __init__(self) -> None:
        super().__init__()
        self.ic = self.Block(A1304_Device())
        self.gnd = self.Export(self.ic.gnd, [Common])
        self.pwr = self.Export(self.ic.vcc, [Power])
        self.out = self.Export(self.ic.vout, [Output])

    def contents(self):
        super().contents()
        self.cbyp = self.Block(DecouplingCapacitor(100*nFarad(tol=0.2))).connected(self.gnd, self.pwr)
