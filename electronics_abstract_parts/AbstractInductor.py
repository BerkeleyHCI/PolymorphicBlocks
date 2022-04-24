from typing import Optional, cast

from electronics_model import *
from .PartsTable import PartsTableColumn
from .PartsTablePart import PartsTableFootprint
from .Categories import *


@abstract_block
class Inductor(PassiveComponent):
  @init_in_parent
  def __init__(self, inductance: RangeLike,
               current: RangeLike = Default(RangeExpr.ZERO),
               frequency: RangeLike = Default(RangeExpr.EMPTY_ZERO)) -> None:
    super().__init__()

    self.a = self.Port(Passive.empty())
    self.b = self.Port(Passive.empty())

    self.inductance = self.ArgParameter(inductance)
    self.current = self.ArgParameter(current)  # defined as operating current range, non-directioned
    self.frequency = self.ArgParameter(frequency)  # defined as operating frequency range
    # TODO: in the future, when we consider efficiency - for now, use current ratings
    # self.resistance_dc = self.Parameter(RangeExpr())
