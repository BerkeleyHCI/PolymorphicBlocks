from abc import abstractmethod

from electronics_model import *
from . import PartsTableFootprint, PartsTableColumn, PartsTableRow
from .Categories import *


@abstract_block
class Oscillator(DiscreteComponent):
  """Device that generates a digital clock signal given power."""
  @init_in_parent
  def __init__(self, frequency: RangeLike) -> None:
    super().__init__()

    self.frequency = self.ArgParameter(frequency)
    self.actual_frequency = self.Parameter(RangeExpr())

    self.gnd = self.Port(Ground.empty(), [Common])
    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.clock = self.Port(DigitalSource.empty(), [Output])

    self.description = DescriptionString(
      "<b>frequency:</b> ", DescriptionString.FormatUnits(self.actual_frequency, "Hz"),
      " <b>of spec:</b> ", DescriptionString.FormatUnits(self.frequency, "Hz"),
    )


@abstract_block
class TableOscillator(Oscillator, PartsTableFootprint, GeneratorBlock):
  """Provides basic part table matching functionality for oscillators, by frequency only.
  Unlike other table-based passive components, additional pin modeling is required.
  No default footprints are provided since these may be non-standard."""
  FREQUENCY = PartsTableColumn(Range)

  @init_in_parent
  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.generator(self.select_part, self.frequency, self.part, self.footprint_spec)

  def select_part(self, frequency: Range, part_spec: str, footprint_spec: str) -> None:
    parts = self._get_table().filter(lambda row: (
        (not part_spec or part_spec == row[self.PART_NUMBER_COL]) and
        (not footprint_spec or footprint_spec == row[self.KICAD_FOOTPRINT]) and
        row[self.FREQUENCY] in frequency
    ))
    part = parts.first(f"no oscillator matching f={frequency} Hz")

    self.assign(self.actual_part, part[self.PART_NUMBER_COL])
    self.assign(self.matching_parts, parts.map(lambda row: row[self.PART_NUMBER_COL]))
    self.assign(self.actual_frequency, part[self.FREQUENCY])

    self._implementation(part)

  @abstractmethod
  def _implementation(self, part: PartsTableRow) -> None:
    """Implement me. This defines the implementation given the selected part.
    Unlike passives, this doesn't necessarily create a footprint, since it may need a supporting capacitor."""
    ...
