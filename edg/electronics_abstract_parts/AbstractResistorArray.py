from typing import List

from ...electronics_model import *
from .AbstractResistor import Resistor
from .PartsTable import PartsTableColumn, PartsTableRow
from .PartsTablePart import PartsTableFootprintSelector
from .Categories import *
from .StandardFootprint import StandardFootprint


class ResistorArrayElement(Resistor):  # to avoid an abstract part error
  def __init__(self):
    super().__init__(resistance=RangeExpr(), power=RangeExpr())


@abstract_block
class ResistorArray(PassiveComponent, MultipackBlock):
  """An n-element resistor array, where all resistors have the same resistance and power rating."""
  @init_in_parent
  def __init__(self, count: IntLike = 0) -> None:  # 0 means 'size automatically'
    super().__init__()

    self.count = self.ArgParameter(count)

    self.elements = self.PackedPart(PackedBlockArray(ResistorArrayElement()))
    self.a = self.PackedExport(self.elements.ports_array(lambda x: x.a))
    self.b = self.PackedExport(self.elements.ports_array(lambda x: x.b))
    self.resistances = self.PackedParameter(self.elements.params_array(lambda x: x.resistance))
    self.powers = self.PackedParameter(self.elements.params_array(lambda x: x.power))

    self.actual_count = self.Parameter(IntExpr())
    self.actual_resistance = self.Parameter(RangeExpr())
    self.actual_power_rating = self.Parameter(RangeExpr())  # per element

    self.unpacked_assign(self.elements.params(lambda x: x.actual_resistance), self.actual_resistance)
    self.unpacked_assign(self.elements.params(lambda x: x.actual_power_rating), self.actual_power_rating)

  def contents(self):
    super().contents()

    self.description = DescriptionString(  # TODO better support for array typed
      "<b>count:</b> ", DescriptionString.FormatUnits(self.actual_count, ""),  # TODO unitless
      " <b>of spec</b> ", DescriptionString.FormatUnits(self.count, ""), "\n",
      "<b>resistance:</b> ", DescriptionString.FormatUnits(self.actual_resistance, "Ω"),
      " <b>of specs</b> ", DescriptionString.FormatUnits(self.resistances, "Ω"), "\n",
      "<b>element power:</b> ", DescriptionString.FormatUnits(self.actual_power_rating, "W"),
      " <b>of operating:</b> ", DescriptionString.FormatUnits(self.powers, "W")
    )


@non_library
class ResistorArrayStandardFootprint(ResistorArray, StandardFootprint[ResistorArray]):
  REFDES_PREFIX = 'RN'

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


@non_library
class TableResistorArray(ResistorArrayStandardFootprint, PartsTableFootprintSelector):
  RESISTANCE = PartsTableColumn(Range)
  POWER_RATING = PartsTableColumn(Range)
  COUNT = PartsTableColumn(int)

  @init_in_parent
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.generator_param(self.count, self.a.requested(), self.b.requested(), self.resistances, self.powers)

  def _row_filter(self, row: PartsTableRow) -> bool:
    # TODO some kind of range intersect construct?
    resistances_min = max([resistance.lower for resistance in self.get(self.resistances)])
    resistances_max = min([resistance.upper for resistance in self.get(self.resistances)])
    assert resistances_min <= resistances_max, "resistances do not intersect"
    resistance_intersect = Range(resistances_min, resistances_max)

    powers_min = min([power.lower for power in self.get(self.powers)])
    powers_max = max([power.upper for power in self.get(self.powers)])
    powers_hull = Range(powers_min, powers_max)

    return super()._row_filter(row) and \
      (self.get(self.count) == 0 or self.get(self.count) == row[self.COUNT]) and \
      (row[self.COUNT] >= len(self.get(self.a.requested())) and \
       row[self.COUNT] >= len(self.get(self.b.requested()))) and \
      row[self.RESISTANCE].fuzzy_in(resistance_intersect) and \
      powers_hull.fuzzy_in(row[self.POWER_RATING])

  def _row_generate(self, row: PartsTableRow) -> None:
    for i in range(row[self.COUNT]):  # must generate ports before creating the footprint
      self.a.append_elt(Passive(), str(i))
      self.b.append_elt(Passive(), str(i))

    super()._row_generate(row)

    self.assign(self.actual_count, row[self.COUNT])
    self.assign(self.actual_resistance, row[self.RESISTANCE])
    self.assign(self.actual_power_rating, row[self.POWER_RATING])
