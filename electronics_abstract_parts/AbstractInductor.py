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


@abstract_block
class TableInductor(Inductor, PartsTableFootprint, GeneratorBlock):
  INDUCTANCE = PartsTableColumn(Range)  # actual inductance incl. tolerance
  FREQUENCY_RATING = PartsTableColumn(Range)  # tolerable frequencies
  CURRENT_RATING = PartsTableColumn(Range)  # tolerable current
  DC_RESISTANCE = PartsTableColumn(Range)  # actual DCR

  @init_in_parent
  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.generator(self.select_part, self.inductance, self.current, self.frequency, self.part, self.footprint_spec)

    self.actual_inductance = self.Parameter(RangeExpr())
    self.actual_current_rating = self.Parameter(RangeExpr())
    self.actual_frequency_rating = self.Parameter(RangeExpr())

  def select_part(self, inductance: Range, current: Range, frequency: Range,
                  part_spec: str, footprint_spec: str) -> None:
    part = self._get_table().filter(lambda row: (
        (not part_spec or part_spec == row[self.PART_NUMBER]) and
        (not footprint_spec or footprint_spec == row[self.KICAD_FOOTPRINT]) and
        row[self.INDUCTANCE].fuzzy_in(inductance) and
        row[self.DC_RESISTANCE].fuzzy_in(Range.zero_to_upper(1.0)) and  # TODO eliminate arbitrary DCR limit in favor of exposing max DCR to upper levels
        frequency.fuzzy_in(row[self.FREQUENCY_RATING])
    )).first(f"no inductors in {inductance} H, {current} A, {frequency} Hz")

    self.assign(self.actual_inductance, part[self.INDUCTANCE])
    self.assign(self.actual_current_rating, part[self.CURRENT_RATING])
    self.assign(self.actual_frequency_rating, part[self.FREQUENCY_RATING])

    self._make_footprint(part)
