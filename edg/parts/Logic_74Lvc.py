from ..abstract_parts import *
from .JlcPart import JlcPart


class Sn74lvc1g74_Device(InternalSubcircuit, FootprintBlock, JlcPart):
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


class Sn74lvc2g02_Device(InternalSubcircuit, FootprintBlock, JlcPart):
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
        self.in1a = self.Port(din_model, optional=True)
        self.in1b = self.Port(din_model, optional=True)
        self.in2a = self.Port(din_model, optional=True)
        self.in2b = self.Port(din_model, optional=True)

        dout_model = DigitalSource.from_supply(
            self.gnd, self.vcc,
            current_limits=(-4, 4)*mAmp  # for Vcc=1.65V, increases with higher Vcc
        )
        self.out1 = self.Port(dout_model, optional=True)
        self.out2 = self.Port(dout_model, optional=True)

        self.require((self.out1.is_connected() == self.in1a.is_connected()) &
                     (self.out1.is_connected() == self.in1b.is_connected()))
        self.require((self.out2.is_connected() == self.in2a.is_connected()) &
                     (self.out2.is_connected() == self.in2b.is_connected()))

    def contents(self) -> None:
        super().contents()
        self.footprint(
            'U', 'Package_SO:VSSOP-8_2.3x2mm_P0.5mm',
            {
                '1': self.in1a,
                '2': self.in1b,
                '3': self.out2,
                '4': self.gnd,
                '5': self.in2a,
                '6': self.in2b,
                '7': self.out1,
                '8': self.vcc,
            },
            mfr='Texas Instruments', part='SN74LVC2G02DCUT',
            datasheet='https://www.ti.com/lit/ds/symlink/sn74lvc2g02.pdf'
        )
        self.assign(self.lcsc_part, 'C2867561')


class Sn74lvc2g02(Interface, Block):
    """2-input positive NOR gate
    TODO: support multipacking"""
    @init_in_parent
    def __init__(self) -> None:
        super().__init__()
        self.ic = self.Block(Sn74lvc2g02_Device())
        self.pwr = self.Export(self.ic.vcc, [Power])
        self.gnd = self.Export(self.ic.gnd, [Common])
        self.in1a = self.Export(self.ic.in1a, optional=True)
        self.in1b = self.Export(self.ic.in1b, optional=True)
        self.in2a = self.Export(self.ic.in2a, optional=True)
        self.in2b = self.Export(self.ic.in2b, optional=True)
        self.out1 = self.Export(self.ic.out1, optional=True)
        self.out2 = self.Export(self.ic.out2, optional=True)

    def contents(self) -> None:
        super().contents()
        self.vdd_cap = self.Block(DecouplingCapacitor(0.1*uFarad(tol=0.2))).connected(self.gnd, self.pwr)
