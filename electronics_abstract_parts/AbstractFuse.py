from electronics_model import *
from .Categories import *


@abstract_block
class Fuse(DiscreteComponent, DiscreteApplication):
  @init_in_parent
  def __init__(self, trip_current: RangeLike = RangeExpr()) -> None:
    """Model-wise, equivalent to a ElectricalSource|Sink passthrough, with a trip rating."""
    super().__init__()

    self.trip_current = self.Parameter(RangeExpr(trip_current, constr=RangeSubset))

    self.pwr_in = self.Port(ElectricalSink(), [Input])  # TODO also allow Power tag?
    self.pwr_out = self.Port(ElectricalSource(), [Output])
    # TODO: GND port for voltage rating?

    self.constrain(self.pwr_in.current_draw == self.pwr_out.link().current_drawn)  # TODO dedup w/ ElectricalBridge?
    self.constrain(self.pwr_out.voltage_out == self.pwr_in.link().voltage)

    self.constrain(self.trip_current.upper() > self.pwr_out.link().current_drawn.lower(),
                   "expected current draw exceeds fuse trip rating")


@abstract_block
class PptcFuse(Fuse):
  """PPTC fuse that models PPTC-specific parameters.
  TODO: what other parameters?"""
  @init_in_parent
  def __init__(self, **kwargs) -> None:
    super().__init__(**kwargs)
