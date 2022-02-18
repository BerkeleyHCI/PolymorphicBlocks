from electronics_model import *
from .Categories import *


@abstract_block
class Switch(DiscreteComponent):
  @init_in_parent
  def __init__(self, voltage: RangeLike, current: RangeLike = Default(0*Amp(tol=0))) -> None:
    super().__init__()

    self.a = self.Port(Passive())
    self.b = self.Port(Passive())

    self.current = self.ArgParameter(current)
    self.voltage = self.ArgParameter(voltage)


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
