from abc import abstractmethod

from ..electronics_model import *
from . import PartsTableFootprint, PartsTableColumn, PartsTableRow, PartsTableSelector
from .Categories import *


@abstract_block
class Oscillator(DiscreteApplication):
  """Device that generates a digital clock signal given power."""
  @init_in_parent
  def __init__(self, frequency: RangeLike) -> None:
    super().__init__()

    self.frequency = self.ArgParameter(frequency)
    self.actual_frequency = self.Parameter(RangeExpr())

    self.gnd = self.Port(Ground.empty(), [Common])
    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.out = self.Port(DigitalSource.empty(), [Output])

  def contents(self):
    super().contents()

    self.description = DescriptionString(
      "<b>frequency:</b> ", DescriptionString.FormatUnits(self.actual_frequency, "Hz"),
      " <b>of spec:</b> ", DescriptionString.FormatUnits(self.frequency, "Hz"),
    )


@non_library
class TableOscillator(Oscillator, PartsTableSelector, PartsTableFootprint):
  """Provides basic part table matching functionality for oscillators, by frequency only.
  Unlike other table-based passive components, this should generate the full application circuit.
  No default footprints are provided since these may be non-standard."""
  FREQUENCY = PartsTableColumn(Range)

  @init_in_parent
  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.generator_param(self.frequency)

  def _row_filter(self, row: PartsTableRow) -> bool:
    return super()._row_filter(row) and \
      row[self.FREQUENCY] in self.get(self.frequency)

  def _row_generate(self, row: PartsTableRow) -> None:
    super()._row_generate(row)
    self.assign(self.actual_frequency, row[self.FREQUENCY])
