from typing import cast
from electronics_model import *
from .Categories import *


@abstract_block
class Crystal(DiscreteComponent):
  @init_in_parent
  def __init__(self, frequency: RangeLike) -> None:
    """Discrete crystal component."""
    super().__init__()

    self.frequency = cast(RangeExpr, frequency)

    self.crystal = self.Port(CrystalPort(
      frequency=self.frequency
    ), [InOut])
    self.gnd = self.Port(Ground(), [Common])
