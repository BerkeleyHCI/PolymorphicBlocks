from typing import Optional, cast

from electronics_model import *
from .PartsTable import PartsTableColumn, PartsTableRow
from .PartsTablePart import PartsTableFootprint
from .Categories import *
from .StandardPinningFootprint import StandardPinningFootprint


@abstract_block
class ResistorArray(PassiveComponent, MultipackBlock):
  """An n-element resistor array, where all resistors have the same resistance and power rating."""
  @init_in_parent
  def __init__(self, count: IntLike = 0) -> None:  # 0 means 'size automatically'
    super().__init__()

    self.a = self.Port(Vector(Passive.empty()))
    self.b = self.Port(Vector(Passive.empty()))

    self.resistances = self.Parameter(ArrayRangeExpr())
    self.powers = self.Parameter(ArrayRangeExpr())  # operating power range
    self.actual_resistance = self.Parameter(RangeExpr())
    self.actual_power_rating = self.Parameter(RangeExpr())  # per element


@abstract_block
class ResistorArrayStandardPinning(ResistorArray, StandardPinningFootprint[ResistorArray]):
  # TODO some way to ensure the resistor count is sufficient?
  FOOTPRINT_PINNING_MAP = {  # these are all the footprints in KiCad as of 2022 05 31
    (
      'Resistor_SMD:R_Array_Concave_2x0603',
      'Resistor_SMD:R_Array_Convex_2x0402',
      'Resistor_SMD:R_Array_Convex_2x0603',
      'Resistor_SMD:R_Array_Convex_2x0606',
      'Resistor_SMD:R_Array_Convex_2x1206',
    ): lambda block: {
      '1': block.a['0'],
      '4': block.b['0'],
      '2': block.a['1'],
      '3': block.b['1'],
    },
    (
      'Resistor_SMD:R_Array_Concave_4x0402',
      'Resistor_SMD:R_Array_Concave_4x0603',
      'Resistor_SMD:R_Array_Convex_4x0402',
      'Resistor_SMD:R_Array_Convex_4x0603',
      'Resistor_SMD:R_Array_Convex_4x0612',
      'Resistor_SMD:R_Array_Convex_4x1206',
    ): lambda block: {
      '1': block.a['0'],
      '8': block.b['0'],
      '2': block.a['1'],
      '7': block.b['1'],
      '3': block.a['2'],
      '6': block.b['2'],
      '4': block.a['3'],
      '5': block.b['3'],
    },
  }


@abstract_block
class TableResistorArray(ResistorArrayStandardPinning, PartsTableFootprint, GeneratorBlock):
  RESISTANCE = PartsTableColumn(Range)
  POWER_RATING = PartsTableColumn(Range)

  @init_in_parent
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.generator(self.select_part, self.resistance, self.power, self.part, self.footprint_spec)

  def select_part(self, resistance: Range, power_dissipation: Range, part_spec: str, footprint_spec: str) -> None:
    parts = self._get_table().filter(lambda row: (
        (not part_spec or part_spec == row[self.PART_NUMBER_COL]) and
        (not footprint_spec or footprint_spec == row[self.KICAD_FOOTPRINT]) and
        row[self.RESISTANCE].fuzzy_in(resistance) and
        power_dissipation.fuzzy_in(row[self.POWER_RATING])
    ))
    part = parts.first(f"no resistors in {resistance} Ohm, {power_dissipation} W")

    self.assign(self.actual_part, part[self.PART_NUMBER_COL])
    self.assign(self.matching_parts, len(parts))
    self.assign(self.actual_resistance, part[self.RESISTANCE])
    self.assign(self.actual_power_rating, part[self.POWER_RATING])

    self._make_footprint(part)

  def _make_footprint(self, part: PartsTableRow) -> None:
    self.footprint(
      'R', part[self.KICAD_FOOTPRINT],
      self._make_pinning(part[self.KICAD_FOOTPRINT]),
      mfr=part[self.MANUFACTURER_COL], part=part[self.PART_NUMBER_COL],
      value=part[self.DESCRIPTION_COL],
      datasheet=part[self.DATASHEET_COL]
    )
