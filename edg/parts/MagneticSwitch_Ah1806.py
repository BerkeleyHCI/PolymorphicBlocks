from ..abstract_parts import *
from .JlcPart import JlcPart


class Ah1806_Device(InternalBlock, FootprintBlock, JlcPart):
    def __init__(self):
        super().__init__()
        self.gnd = self.Port(Ground())
        self.vdd = self.Port(VoltageSink.from_gnd(
            self.gnd,
            voltage_limits=(2.5, 5.5)*Volt,
            current_draw=(0, 40)*uAmp,  # average, up to 12mA when awake
        ))
        self.output = self.Port(DigitalSource.low_from_supply(
            self.gnd, current_limits=(-1, 0)*mAmp
        ))

    def contents(self):
        self.footprint(
            'U', 'Package_TO_SOT_SMD:SOT-23',
            {
                '1': self.vdd,  # note, kicad pin numbers differs from datasheet pin numbers
                '3': self.gnd,
                '2': self.output,
            },
            mfr="Diodes Incorporated", part='AH1806-W-7',
            datasheet='https://www.diodes.com/assets/Datasheets/AH1806.pdf')

        self.assign(self.lcsc_part, 'C126663')
        self.assign(self.actual_basic_part, False)


class Ah1806(MagneticSwitch, Block):
    """Micropower omnipolar hall-effect switch, open-drain (external pullup required)
    Typ. 30 gauss (15-45 tolerance range) operation (turn-on) point
    and 20 G (10-40 tolerance range) release point.
    0.1% duty cycle, period of 75ms (typ).
    Pin-compatible with some others in the AH18xx series and DRV5032, which have different trip characteristics"""
    def __init__(self):
        super().__init__()
        self.ic = self.Block(Ah1806_Device())
        self.gnd = self.Export(self.ic.gnd, [Common])
        self.pwr = self.Export(self.ic.vdd, [Power])
        self.out = self.Export(self.ic.output, [Output])

    def contents(self):
        super().contents()
        self.cin = self.Block(DecouplingCapacitor(100*nFarad(tol=0.2))).connected(self.gnd, self.pwr)
