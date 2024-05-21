from ..abstract_parts import *
from .JlcPart import JlcPart


class Sn74lvc1g74_Device(InternalSubcircuit, FootprintBlock, JlcPart):
    @init_in_parent
    def __init__(self) -> None:
        super().__init__()
        self.gnd = self.Port(Ground())
        self.vcc = self.Port(VoltageSink(
            voltage_limits=(1.65, 5.5)*Volt,
            current_draw=(0, 10)*uAmp  # Icc
        ))

        din_model = DigitalSink.from_supply(
            self.gnd, self.vcc,
            voltage_limit_abs=(-0.5, 6.5)*Volt,
            input_threshold_factor=(0.3, 0.7)  # tightest over operating range
        )
        self.clk = self.Port(din_model, optional=True)
        self.d = self.Port(din_model, optional=True)
        self.nclr = self.Port(din_model, optional=True)
        self.npre = self.Port(din_model, optional=True)
        self.require(self.d.is_connected() == self.clk.is_connected())
        self.require(self.d.is_connected() | self.clk.is_connected() |
                     self.nclr.is_connected() | self.npre.is_connected())
        dout_model = DigitalSource.from_supply(
            self.gnd, self.vcc,
            current_limits=(-4, 4)*mAmp  # for Vcc=1.65V, increases with higher Vcc
        )
        self.q = self.Port(dout_model, optional=True)
        self.nq = self.Port(dout_model, optional=True)
        self.require(self.q.is_connected() | self.nq.is_connected())

    def contents(self) -> None:
        super().contents()
        self.footprint(
            'U', 'Package_SO:VSSOP-8_2.4x2.1mm_P0.5mm',
            {
                '1': self.clk,
                '2': self.d,
                '3': self.nq,
                '4': self.gnd,
                '5': self.q,
                '6': self.nclr,
                '7': self.npre,
                '8': self.vcc,
            },
            mfr='Texas Instruments', part='SN74LVC1G74DCUR',
            datasheet='https://www.ti.com/lit/ds/symlink/sn74lvc1g74.pdf'
        )
        self.assign(self.lcsc_part, 'C70285')


class Sn74lvc1g74(Interface, Block):
    """D flip-flop with clear and preset

    TODO: should extend an abstract flip-lop interface, with async (n)set and (n)clear mixins"""
    @init_in_parent
    def __init__(self) -> None:
        super().__init__()
        self.ic = self.Block(Sn74lvc1g74_Device())
        self.pwr = self.Export(self.ic.vcc, [Power])
        self.gnd = self.Export(self.ic.gnd, [Common])
        self.clk = self.Export(self.ic.clk, optional=True)
        self.d = self.Export(self.ic.d, optional=True)
        self.nset = self.Export(self.ic.npre, optional=True)
        self.nclr = self.Export(self.ic.nclr, optional=True)
        self.q = self.Export(self.ic.q, optional=True)
        self.nq = self.Export(self.ic.nq, optional=True)

    def contents(self) -> None:
        super().contents()
        self.vdd_cap = self.Block(DecouplingCapacitor(0.1*uFarad(tol=0.2))).connected(self.gnd, self.pwr)
