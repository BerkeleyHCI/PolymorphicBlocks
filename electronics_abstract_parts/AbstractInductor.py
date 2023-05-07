from electronics_model import *
from .PartsTable import PartsTableColumn, PartsTableRow
from .PartsTablePart import PartsTableFootprintSelector
from .Categories import *
from .StandardFootprint import StandardFootprint


@abstract_block
class Inductor(PassiveComponent):
  @init_in_parent
  def __init__(self, inductance: RangeLike,
               current: RangeLike = Default(RangeExpr.ZERO),
               frequency: RangeLike = Default(RangeExpr.ZERO)) -> None:
    super().__init__()

    self.a = self.Port(Passive.empty())
    self.b = self.Port(Passive.empty())

    self.inductance = self.ArgParameter(inductance)
    self.current = self.ArgParameter(current)  # defined as operating current range, non-directioned
    self.frequency = self.ArgParameter(frequency)  # defined as operating frequency range
    # TODO: in the future, when we consider efficiency - for now, use current ratings
    # self.resistance_dc = self.Parameter(RangeExpr())

    self.actual_inductance = self.Parameter(RangeExpr())
    self.actual_current_rating = self.Parameter(RangeExpr())
    self.actual_frequency_rating = self.Parameter(RangeExpr())

  def contents(self):
    super().contents()

    self.description = DescriptionString(
      "<b>inductance:</b> ", DescriptionString.FormatUnits(self.actual_inductance, "H"),
      " <b>of spec:</b> ", DescriptionString.FormatUnits(self.inductance, "H"), "\n",
      "<b>current rating:</b> ", DescriptionString.FormatUnits(self.actual_current_rating, "A"),
      " <b>of operating:</b> ", DescriptionString.FormatUnits(self.current, "A"), "\n",
      "<b>frequency rating:</b> ", DescriptionString.FormatUnits(self.actual_frequency_rating, "Hz"),
      " <b>of operating:</b> ", DescriptionString.FormatUnits(self.frequency, "Hz")
    )


@non_library
class InductorStandardFootprint(Inductor, StandardFootprint[Inductor]):
  REFDES_PREFIX = 'L'

  FOOTPRINT_PINNING_MAP = {
    (
      'Inductor_SMD:L_0201_0603Metric',
      'Inductor_SMD:L_0402_1005Metric',
      'Inductor_SMD:L_0603_1608Metric',
      'Inductor_SMD:L_0805_2012Metric',
      'Inductor_SMD:L_1206_3216Metric',
      'Inductor_SMD:L_1210_3225Metric',
      'Inductor_SMD:L_1812_4532Metric',
      'Inductor_SMD:L_2010_5025Metric',
      'Inductor_SMD:L_2512_6332Metric',

      'Inductor_SMD:L_Bourns-SRR1005',
      'Inductor_SMD:L_Bourns_SRR1210A',
      'Inductor_SMD:L_Bourns_SRR1260',

      'Inductor_SMD:L_Taiyo-Yuden_NR-20xx',
      'Inductor_SMD:L_Taiyo-Yuden_NR-24xx',
      'Inductor_SMD:L_Taiyo-Yuden_NR-30xx',
      'Inductor_SMD:L_Taiyo-Yuden_NR-40xx',
      'Inductor_SMD:L_Taiyo-Yuden_NR-50xx',
      'Inductor_SMD:L_Taiyo-Yuden_NR-60xx',
      'Inductor_SMD:L_Taiyo-Yuden_NR-80xx',
    ): lambda block: {
      '1': block.a,
      '2': block.b,
    },
  }

  SMD_FOOTPRINT_MAP = {
    '01005': None,
    '0201': 'Inductor_SMD:L_0201_0603Metric',
    '0402': 'Inductor_SMD:L_0402_1005Metric',
    '0603': 'Inductor_SMD:L_0603_1608Metric',
    '0805': 'Inductor_SMD:L_0805_2012Metric',
    '1206': 'Inductor_SMD:L_1206_3216Metric',
    '1210': 'Inductor_SMD:L_1210_3225Metric',
    '1806': None,
    '1812': 'Inductor_SMD:L_1812_4532Metric',
    '2010': 'Inductor_SMD:L_2010_5025Metric',
    '2512': 'Inductor_SMD:L_2512_6332Metric',
  }


@non_library
class TableInductor(InductorStandardFootprint, PartsTableFootprintSelector):
  INDUCTANCE = PartsTableColumn(Range)  # actual inductance incl. tolerance
  FREQUENCY_RATING = PartsTableColumn(Range)  # tolerable frequencies
  CURRENT_RATING = PartsTableColumn(Range)  # tolerable current
  DC_RESISTANCE = PartsTableColumn(Range)  # actual DCR

  @init_in_parent
  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.generator_param(self.inductance, self.current, self.frequency)

  def _row_filter(self, row: PartsTableRow) -> bool:
    # TODO eliminate arbitrary DCR limit in favor of exposing max DCR to upper levels
    return super()._row_filter(row) and \
      row[self.INDUCTANCE].fuzzy_in(self.get(self.inductance)) and \
      self.get(self.current).fuzzy_in(row[self.CURRENT_RATING]) and \
      row[self.DC_RESISTANCE].fuzzy_in(Range.zero_to_upper(1.0)) and \
      self.get(self.frequency).fuzzy_in(row[self.FREQUENCY_RATING])

  def _row_generate(self, row: PartsTableRow) -> None:
    super()._row_generate(row)
    self.assign(self.actual_inductance, row[self.INDUCTANCE])
    self.assign(self.actual_current_rating, row[self.CURRENT_RATING])
    self.assign(self.actual_frequency_rating, row[self.FREQUENCY_RATING])
