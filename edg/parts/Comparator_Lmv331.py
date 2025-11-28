from typing_extensions import override

from ..abstract_parts import *
from .JlcPart import JlcPart


class Lmv331_Device(InternalSubcircuit, FootprintBlock, JlcPart):
    def __init__(self) -> None:
        super().__init__()
        self.gnd = self.Port(Ground())
        self.vcc = self.Port(VoltageSink(
            voltage_limits=(2.7, 5.5)*Volt,
            current_draw=(40, 100)*uAmp  # Icc, typ to max
        ))

        in_model = AnalogSink.from_supply(
            self.gnd, self.vcc,
            voltage_limit_tolerance=(0, 0),
            impedance=(12.5, 200)*MOhm  # from input bias current @ 5v
        )
        self.inn = self.Port(in_model)
        self.inp = self.Port(in_model)
        out_model = DigitalSource.low_from_supply(self.gnd)
        self.out = self.Port(out_model)

    @override
    def contents(self) -> None:
        super().contents()
        self.footprint(
            'U','Package_TO_SOT_SMD:SOT-353_SC-70-5',
            {
                '1': self.inp,
                '2': self.gnd,
                '3': self.inn,
                '4': self.out,
                '5': self.vcc,
            },
            mfr='Texas Instruments', part='LMV331IDCKR',
            datasheet='https://www.ti.com/lit/ds/symlink/lmv331.pdf'
        )
        self.assign(self.lcsc_part, 'C7976')


class Lmv331(Comparator):
    """General purpose comparator"""
    @override
    def contents(self) -> None:
        super().contents()
        self.ic = self.Block(Lmv331_Device())
        self.connect(self.ic.vcc, self.pwr)
        self.connect(self.ic.gnd, self.gnd)
        self.connect(self.ic.inn, self.inn)
        self.connect(self.ic.inp, self.inp)
        self.connect(self.ic.out, self.out)

        self.vdd_cap = self.Block(DecouplingCapacitor(0.1*uFarad(tol=0.2))).connected(self.gnd, self.pwr)
