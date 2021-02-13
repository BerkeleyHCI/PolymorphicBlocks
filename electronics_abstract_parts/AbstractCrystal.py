from electronics_model import *
from .Categories import *


@abstract_block
class Crystal(DiscreteComponent):
  @init_in_parent
  def __init__(self, frequency: RangeLike = RangeExpr()) -> None:
    """Discrete crystal component."""
    super().__init__()

    self.frequency = self.Parameter(RangeExpr(frequency))

    self.crystal = self.Port(CrystalPort(), [InOut])
    self.gnd = self.Port(ElectricalSink(), [Common])
