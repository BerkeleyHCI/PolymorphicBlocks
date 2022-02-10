from typing import cast
from electronics_model import *
from .Categories import *


@abstract_block
class Battery(DiscreteApplication):
  @init_in_parent
  def __init__(self, voltage: RangeLike,
               current: RangeLike = Default(RangeExpr.ZERO),
               capacity: FloatLike = Default(0.0)):
    super().__init__()

    self.pwr = self.Port(VoltageSource(
      voltage_out=RangeExpr(), current_limits=RangeExpr()))  # set by subclasses
    self.gnd = self.Port(GroundSource())

    self.capacity = cast(RangeExpr, capacity)
    self.voltage = cast(RangeExpr, voltage)

    self.require(self.pwr.voltage_out.within(voltage))
    self.require(self.pwr.current_limits.contains(current))
    self.require(self.capacity.lower() >= capacity)

    self.assign(self.pwr.voltage_out, self.voltage)
