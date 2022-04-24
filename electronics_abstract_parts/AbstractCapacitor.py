from typing import Optional, cast

from electronics_model import *
from .PartsTable import PartsTableColumn
from .PartsTablePart import PartsTableFootprint
from .Categories import *


@abstract_block
class UnpolarizedCapacitor(PassiveComponent):
  """Base type for a capacitor, that defines its parameters and without ports (since capacitors can be polarized)"""
  @init_in_parent
  def __init__(self, capacitance: RangeLike, voltage: RangeLike) -> None:
    super().__init__()

    self.capacitance = self.ArgParameter(capacitance)
    self.voltage = self.ArgParameter(voltage)  # defined as operating voltage range


@abstract_block
class Capacitor(UnpolarizedCapacitor):
  """Polarized capacitor, which we assume will be the default"""
  @init_in_parent
  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)

    self.pos = self.Port(Passive.empty())
    self.neg = self.Port(Passive.empty())


class DecouplingCapacitor(DiscreteApplication):
  """Optionally polarized capacitor used for DC decoupling, with VoltageSink connections with voltage inference.
  Implemented as a shim block."""
  @init_in_parent
  def __init__(self, capacitance: RangeLike) -> None:
    super().__init__()

    self.cap = self.Block(Capacitor(capacitance, voltage=RangeExpr()))
    self.gnd = self.Export(self.cap.neg.as_voltage_sink(), [Common])
    self.pwr = self.Export(self.cap.pos.as_voltage_sink(), [Power])

    self.assign(self.cap.voltage, self.pwr.link().voltage - self.gnd.link().voltage)

  def connected(self, gnd: Optional[Port[VoltageLink]] = None, pwr: Optional[Port[VoltageLink]] = None) -> \
      'DecouplingCapacitor':
    """Convenience function to connect both ports, returning this object so it can still be given a name."""
    if gnd is not None:
      cast(Block, builder.get_enclosing_block()).connect(gnd, self.gnd)
    if pwr is not None:
      cast(Block, builder.get_enclosing_block()).connect(pwr, self.pwr)
    return self
