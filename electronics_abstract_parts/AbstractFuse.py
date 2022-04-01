from electronics_model import *
from .Categories import *


@abstract_block
class Fuse(DiscreteComponent, DiscreteApplication):
  @init_in_parent
  def __init__(self, trip_current: RangeLike) -> None:
    """Model-wise, equivalent to a VoltageSource|Sink passthrough, with a trip rating."""
    super().__init__()

    self.trip_current = self.ArgParameter(trip_current)
    self.actual_trip_current = self.Parameter(RangeExpr())

    self.pwr_in = self.Port(VoltageSink.empty(), [Input])  # TODO also allow Power tag?
    self.pwr_out = self.Port(VoltageSource.empty(), [Output])
    # TODO: GND port for voltage rating?

    self.assign(self.pwr_in.current_draw, self.pwr_out.link().current_drawn)  # TODO dedup w/ bridge?
    self.assign(self.pwr_out.voltage_out, self.pwr_in.link().voltage)

    self.require(self.trip_current.upper() > self.pwr_out.link().current_drawn.lower(),
                   "expected current draw exceeds fuse trip rating")


@abstract_block
class PptcFuse(Fuse):
  """PPTC fuse that models PPTC-specific parameters.
  TODO: what other parameters?"""
  @init_in_parent
  def __init__(self, **kwargs) -> None:
    super().__init__(**kwargs)
