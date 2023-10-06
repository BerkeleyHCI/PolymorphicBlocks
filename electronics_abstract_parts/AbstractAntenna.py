from electronics_model import *
from .Categories import *
from .PartsTable import PartsTableColumn, PartsTableRow
from .PartsTablePart import PartsTableSelector


@abstract_block
class Antenna(Block):
  @init_in_parent
  def __init__(self, frequency: RangeLike, impedance: RangeLike=Range.all(), power: RangeLike = (0, 0*Watt)):
    super().__init__()

    self.frequency = self.ArgParameter(frequency)
    self.actual_frequency_rating = self.Parameter(RangeExpr())

    self.impedance = self.ArgParameter(impedance)
    self.actual_impedance = self.Parameter(RangeExpr())

    self.power = self.ArgParameter(power)
    self.actual_power_rating = self.Parameter(RangeExpr())

    self.a = self.Port(Passive.empty())


@non_library
class TableAntenna(Antenna, PartsTableSelector, GeneratorBlock):
  FREQUENCY_RATING = PartsTableColumn(Range)
  IMPEDANCE = PartsTableColumn(Range)
  POWER_RATING = PartsTableColumn(Range)

  @init_in_parent
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.generator_param(self.frequency, self.power, self.impedance)

  def _row_filter(self, row: PartsTableRow) -> bool:
    return super()._row_filter(row) and \
      self.get(self.frequency).fuzzy_in(row[self.FREQUENCY_RATING]) and \
      row[self.IMPEDANCE].fuzzy_in(self.get(self.impedance)) and\
      self.get(self.power).fuzzy_in(row[self.POWER_RATING])

  def _row_generate(self, row: PartsTableRow) -> None:
    super()._row_generate(row)
    self.assign(self.actual_frequency_rating, row[self.FREQUENCY_RATING])
    self.assign(self.actual_power_rating, row[self.POWER_RATING])
    self.assign(self.actual_impedance, row[self.IMPEDANCE])
