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

    self.pwr_in = self.Port(VoltageSink.empty(), [Input])
    self.pwr_out = self.Port(VoltageSource(
      voltage_out=self.pwr_in.link().voltage,
      current_limits=(0, self.actual_trip_current.lower())
    ), [Output])  # TODO: GND port for voltage rating?
    self.pwr_in.init_from(VoltageSink(
      voltage_limits=RangeExpr.ALL,
      current_draw=self.pwr_out.link().current_drawn
    ))

    self.require(self.actual_trip_current.within(self.trip_current),
                 "fuse rating not within specified rating")


@abstract_block
class PptcFuse(Fuse):
  """PPTC fuse that models PPTC-specific parameters.
  TODO: what other parameters?"""
