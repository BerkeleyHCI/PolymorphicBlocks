from typing import Optional, cast

from edg_core.Blocks import DescriptionString
from electronics_model import *
from .PartsTable import PartsTableColumn, PartsTableRow
from .PartsTablePart import PartsTableFootprint
from .Categories import *
from .StandardPinningFootprint import StandardPinningFootprint


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

    self.description = DescriptionString(
      "<b>spec inductance:</b> ", DescriptionString.FormatUnits(self.inductance, "H"),
      "\n<b>spec current:</b> ", DescriptionString.FormatUnits(self.current, "A"),
      "\n<b>spec frequency:</b> ", DescriptionString.FormatUnits(self.frequency, "Hz"))


@abstract_block
class InductorStandardPinning(Inductor, StandardPinningFootprint[Inductor]):
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


@abstract_block
class TableInductor(InductorStandardPinning, PartsTableFootprint, GeneratorBlock):
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

    self.description = DescriptionString(
      "<b>inductance:</b> ", DescriptionString.FormatUnits(self.actual_inductance, "H"),
      " <b>of spec</b> ", DescriptionString.FormatUnits(self.inductance, "H"),
      "\n<b>current rating:</b> ", DescriptionString.FormatUnits(self.actual_current_rating, "A"),
      " <b>of spec:</b> ", DescriptionString.FormatUnits(self.current, "A"),
      "\n<b>frequency rating:</b> ", DescriptionString.FormatUnits(self.actual_frequency_rating, "Hz"),
      " <b>of spec:</b> ", DescriptionString.FormatUnits(self.frequency, "Hz"))

  def select_part(self, inductance: Range, current: Range, frequency: Range,
                  part_spec: str, footprint_spec: str) -> None:
    parts = self._get_table().filter(lambda row: (
        (not part_spec or part_spec == row[self.PART_NUMBER_COL]) and
        (not footprint_spec or footprint_spec == row[self.KICAD_FOOTPRINT]) and
        row[self.INDUCTANCE].fuzzy_in(inductance) and
        current.fuzzy_in(row[self.CURRENT_RATING]) and
        row[self.DC_RESISTANCE].fuzzy_in(Range.zero_to_upper(1.0)) and  # TODO eliminate arbitrary DCR limit in favor of exposing max DCR to upper levels
        frequency.fuzzy_in(row[self.FREQUENCY_RATING])
    ))
    part = parts.first(f"no inductors in {inductance} H, {current} A, {frequency} Hz")

    self.assign(self.actual_part, part[self.PART_NUMBER_COL])
    self.assign(self.matching_parts, len(parts))

    self.assign(self.actual_inductance, part[self.INDUCTANCE])
    self.assign(self.actual_current_rating, part[self.CURRENT_RATING])
    self.assign(self.actual_frequency_rating, part[self.FREQUENCY_RATING])

    self._make_footprint(part)

  def _make_footprint(self, part: PartsTableRow) -> None:
    self.footprint(
      'L', part[self.KICAD_FOOTPRINT],
      self._make_pinning(part[self.KICAD_FOOTPRINT]),
      mfr=part[self.MANUFACTURER_COL], part=part[self.PART_NUMBER_COL],
      value=part[self.DESCRIPTION_COL],
      datasheet=part[self.DATASHEET_COL]
    )
