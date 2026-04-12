from __future__ import annotations

from deprecated import deprecated
from typing_extensions import override

from ..core import *
from .PassivePort import Passive
from .GroundPort import Ground, GroundReference
from .VoltagePorts import VoltageSource, VoltageSink


@deprecated("Use PackedPassive with compositional passive")
@abstract_block
class NetPackingBlock(InternalBlock, Block):
    def packed(self, elts: BasePort, merged: BasePort) -> None:
        self.nets_packed = self.Metadata({"src": self._ports.name_of(elts), "dst": self._ports.name_of(merged)})


class PackedPassive(GeneratorBlock):
    """A pseudoblock that asserts all elts are connected to the same net, then connects them to merged."""

    def __init__(self) -> None:
        super().__init__()
        self.elts = self.Port(Vector(Passive.empty()))
        self.merged = self.Port(Passive.empty())
        self.generator_param(self.elts.requested())

    @override
    def generate(self) -> None:
        super().generate()
        self.elts.defined()
        for request in self.get(self.elts.requested()):
            self.elts.append_elt(Passive(), request)

        self.nets_packed = self.Metadata(
            {"src": self._ports.name_of(self.elts), "dst": self._ports.name_of(self.merged)}
        )


class PackedGround(GeneratorBlock):
    """Takes in several Ground connections that are of the same net (asserted in netlister),
    and provides a single Ground."""

    def __init__(self) -> None:
        super().__init__()
        self.gnd_ins = self.Port(Vector(Ground.empty()))
        self.gnd_out = self.Port(GroundReference(voltage_out=RangeExpr()))
        self.generator_param(self.gnd_ins.requested())

    @override
    def generate(self) -> None:
        super().generate()
        self.packed = self.Block(PackedPassive())

        self.gnd_ins.defined()
        for in_request in self.get(self.gnd_ins.requested()):
            in_port = self.gnd_ins.append_elt(Ground(), in_request)
            self.connect(in_port.net, self.packed.elts.request(in_request))
        self.connect(self.packed.merged, self.gnd_out.net)
        self.assign(self.gnd_out.voltage_out, self.gnd_ins.hull(lambda x: x.link().voltage))


class PackedVoltageSource(GeneratorBlock):
    """Takes in several VoltageSink connections that are of the same net (asserted in netlister),
    and provides a single VoltageSource. Distributes the current draw from the VoltageSource
    equally among the inputs."""

    def __init__(self) -> None:
        super().__init__()
        self.pwr_ins = self.Port(Vector(VoltageSink.empty()))
        self.pwr_out = self.Port(VoltageSource(voltage_out=RangeExpr()))
        self.generator_param(self.pwr_ins.requested())

    @override
    def generate(self) -> None:
        super().generate()
        self.packed = self.Block(PackedPassive())

        self.pwr_ins.defined()
        for in_request in self.get(self.pwr_ins.requested()):
            in_port = self.pwr_ins.append_elt(
                VoltageSink(current_draw=self.pwr_out.link().current_drawn / len(self.get(self.pwr_ins.requested()))),
                in_request,
            )
            self.connect(in_port.net, self.packed.elts.request(in_request))
        self.connect(self.packed.merged, self.pwr_out.net)
        self.assign(self.pwr_out.voltage_out, self.pwr_ins.hull(lambda x: x.link().voltage))
