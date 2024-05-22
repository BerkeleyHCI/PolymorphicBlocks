from ..electronics_model import *
from .Categories import *


@abstract_block
class Battery(PowerSource):
  @init_in_parent
  def __init__(self, voltage: RangeLike,
               current: RangeLike = RangeExpr.ZERO, *,
               capacity: FloatLike = 0.0):
    super().__init__()

    self.pwr = self.Port(VoltageSource.empty())  # set by subclasses
    self.gnd = self.Port(GroundSource.empty())

    self.voltage = self.ArgParameter(voltage)
    self.capacity = self.ArgParameter(capacity)
    self.actual_capacity = self.Parameter(RangeExpr())

    self.require(self.pwr.voltage_out.within(voltage))
    self.require(self.pwr.current_limits.contains(current))
    self.require(self.actual_capacity.upper() >= capacity)
