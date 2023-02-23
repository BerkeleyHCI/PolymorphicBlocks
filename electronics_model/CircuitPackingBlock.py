from __future__ import annotations

from typing import *
from edg_core import *

from .VoltagePorts import VoltageSource, VoltageSink


@abstract_block
class NetPackingBlock(InternalBlock, Block):
  def packed(self, source: BasePort, dst: BasePort) -> None:
    """Asserts that sources are all connected to the same net, and connects all of dsts to that net."""
    self.nets_packed = self.Metadata({
      'src': self._ports.name_of(source),
      'dst': self._ports.name_of(dst)
    })


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
    self.generator(self.generate, self.pwr_ins.requested())
    self.packed(self.pwr_ins, self.pwr_out)

  def generate(self, in_requests: List[str]):
    self.pwr_ins.defined()
    for in_request in in_requests:
      self.pwr_ins.append_elt(VoltageSink(
        voltage_limits=RangeExpr.ALL,
        current_draw=self.pwr_out.link().current_drawn / len(in_requests)
      ), in_request)

    self.assign(self.pwr_out.voltage_out,
                self.pwr_ins.hull(lambda x: x.link().voltage))
