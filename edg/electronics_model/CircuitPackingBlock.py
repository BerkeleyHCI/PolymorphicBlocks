from __future__ import annotations

from ..core import *
from .PassivePort import Passive
from .GroundPort import Ground, GroundReference
from .VoltagePorts import VoltageSource, VoltageSink


@abstract_block
class NetPackingBlock(InternalBlock, Block):
  def packed(self, elts: BasePort, merged: BasePort) -> None:
    """Asserts that elts are all connected to the same net, and connects them to merged."""
    self.nets_packed = self.Metadata({
      'src': self._ports.name_of(elts),
      'dst': self._ports.name_of(merged)
    })


class PackedPassive(NetPackingBlock, GeneratorBlock):
  def __init__(self):
    super().__init__()
    self.elts = self.Port(Vector(Passive.empty()))
    self.merged = self.Port(Passive.empty())
    self.generator_param(self.elts.requested())
    self.packed(self.elts, self.merged)

  def generate(self):
    super().generate()
    self.elts.defined()
    for request in self.get(self.elts.requested()):
      self.elts.append_elt(Passive(), request)


class PackedGround(NetPackingBlock, GeneratorBlock):
  """Takes in several Ground connections that are of the same net (asserted in netlister),
  and provides a single Ground."""
  def __init__(self):
    super().__init__()
    self.gnd_ins = self.Port(Vector(Ground.empty()))
    self.gnd_out = self.Port(GroundReference(
      voltage_out=RangeExpr(),
    ))
    self.generator_param(self.gnd_ins.requested())
    self.packed(self.gnd_ins, self.gnd_out)

  def generate(self):
    super().generate()
    self.gnd_ins.defined()
    for in_request in self.get(self.gnd_ins.requested()):
      self.gnd_ins.append_elt(Ground(), in_request)

    self.assign(self.gnd_out.voltage_out,
                self.gnd_ins.hull(lambda x: x.link().voltage))


class PackedVoltageSource(NetPackingBlock, GeneratorBlock):
  """Takes in several VoltageSink connections that are of the same net (asserted in netlister),
  and provides a single VoltageSource. Distributes the current draw from the VoltageSource
  equally among the inputs."""
  def __init__(self):
    super().__init__()
    self.pwr_ins = self.Port(Vector(VoltageSink.empty()))
    self.pwr_out = self.Port(VoltageSource(
      voltage_out=RangeExpr(),
      current_limits=RangeExpr.ALL
    ))
    self.generator_param(self.pwr_ins.requested())
    self.packed(self.pwr_ins, self.pwr_out)

  def generate(self):
    super().generate()
    self.pwr_ins.defined()
    for in_request in self.get(self.pwr_ins.requested()):
      self.pwr_ins.append_elt(VoltageSink(
        voltage_limits=RangeExpr.ALL,
        current_draw=self.pwr_out.link().current_drawn / len(self.get(self.pwr_ins.requested()))
      ), in_request)

    self.assign(self.pwr_out.voltage_out,
                self.pwr_ins.hull(lambda x: x.link().voltage))
