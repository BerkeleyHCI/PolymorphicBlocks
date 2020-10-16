from electronics_model import *
from .Categories import *


@abstract_block
class Battery(DiscreteApplication):
  @init_in_parent
  def __init__(self, voltage: RangeLike = RangeExpr(), current: RangeLike = RangeExpr(), capacity: RangeLike = RangeExpr()):
    super().__init__()

    self.pwr = self.Port(ElectricalSource(voltage_out=voltage, current_limits=current))
    self.gnd = self.Port(GroundSource())

    self.capacity = self.Parameter(RangeExpr(capacity))
