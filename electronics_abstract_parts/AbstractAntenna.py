from electronics_model import *
from .Categories import *


@abstract_block
class Antenna(Block):
  @init_in_parent
  def __init__(self, frequency: RangeLike, power: RangeLike = (0, 0*Watt)):
    super().__init__()

    self.frequency = self.ArgParameter(frequency)
    self.actual_frequency_rating = self.Parameter(RangeExpr())

    self.power = self.ArgParameter(power)
    self.actual_power_rating = self.Parameter(RangeExpr())

    self.a = self.Port(Passive.empty())
