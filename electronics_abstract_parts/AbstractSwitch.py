from typing import cast
from electronics_model import *
from .Categories import *


@abstract_block
class Switch(DiscreteComponent):
  @init_in_parent
  def __init__(self, current: RangeLike, voltage: RangeLike) -> None:
    super().__init__()

    self.a = self.Port(Passive())
    self.b = self.Port(Passive())

    self.current = cast(RangeExpr, current)
    self.voltage = cast(RangeExpr, voltage)


class DigitalSwitch(DiscreteApplication):
  def __init__(self) -> None:
    super().__init__()

    self.gnd = self.Port(Ground(), [Common])
    self.out = self.Port(DigitalSingleSource.low_from_supply(self.gnd), [Output])

  def contents(self):
    super().contents()
    self.package = self.Block(Switch(current=self.out.link().current_limits,
                                     voltage=self.out.link().voltage))

    self.connect(self.out, self.package.a.as_digital_single_source())
    self.connect(self.gnd, self.package.b.as_ground())
