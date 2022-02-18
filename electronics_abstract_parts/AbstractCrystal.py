from electronics_model import *
from .Categories import *


@abstract_block
class Crystal(DiscreteComponent):
  @init_in_parent
  def __init__(self, frequency: RangeLike) -> None:
    """Discrete crystal component."""
    super().__init__()

    self.frequency = self.ArgParameter(frequency)

    # actual frequency to be fulled in by subclass
    self.crystal = self.Port(CrystalPort(frequency=RangeExpr()), [InOut])
    self.gnd = self.Port(Ground(), [Common])
