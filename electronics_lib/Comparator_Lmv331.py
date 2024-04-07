from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Lmv331_Device(InternalSubcircuit, FootprintBlock, JlcPart):
    @init_in_parent
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
        out_model = DigitalSource.from_supply(
            self.gnd, self.vcc,
            current_limits=(-5, 5)*mAmp  # for Vcc=2.7V, increases with higher Vcc
        )
        self.out = self.Port(out_model)

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


class Lmv331(Interface, Block):
    """General purpose comparator

    TODO: should extend an abstract comparator interface, note output is open-drain"""
    @init_in_parent
    def __init__(self) -> None:
        super().__init__()
        self.ic = self.Block(Lmv331_Device())
        self.pwr = self.Export(self.ic.vcc, [Power])
        self.gnd = self.Export(self.ic.gnd, [Common])
        self.inn = self.Export(self.ic.inn)
        self.inp = self.Export(self.ic.inp)
        self.out = self.Export(self.ic.out)

    def contents(self) -> None:
        super().contents()
        self.vdd_cap = self.Block(DecouplingCapacitor(0.1*uFarad(tol=0.2))).connected(self.gnd, self.pwr)
