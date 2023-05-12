from typing import Dict

from electronics_model import *
from .Categories import *
from .PartsTable import PartsTableColumn, PartsTableRow
from .PartsTablePart import PartsTableFootprintSelector
from .StandardFootprint import StandardFootprint


@abstract_block
class Bjt(KiCadImportableBlock, DiscreteSemiconductor):
  """Base class for untyped BJTs
  """
  def symbol_pinning(self, symbol_name: str) -> Dict[str, BasePort]:
    # TODO actually check that the device channel corresponds with the schematic?
    assert symbol_name.startswith('Device:Q_NPN_') or symbol_name.startswith('Device:Q_PNP_')
    assert symbol_name.removeprefix('Device:Q_NPN_').removeprefix('Device:Q_PNP_') in \
           ('BCE', 'BEC', 'CBE', 'CEB', 'EBC', 'ECB')
    return {'B': self.base, 'C': self.collector, 'E': self.emitter}

  @staticmethod
  def Npn(*args, **kwargs) -> 'Bjt':
    return Bjt(*args, **kwargs, channel='NPN')

  @staticmethod
  def Pnp(*args, **kwargs) -> 'Bjt':
    return Bjt(*args, **kwargs, channel='PNP')

  @init_in_parent
  def __init__(self, collector_voltage: RangeLike, collector_current: RangeLike, *,
               gain: RangeLike = Default(Range.all()), power: RangeLike = Default(Range.exact(0)),
               channel: StringLike = StringExpr()) -> None:
    super().__init__()

    self.base = self.Port(Passive.empty())
    self.collector = self.Port(Passive.empty())
    self.emitter = self.Port(Passive.empty())

    self.collector_voltage = self.ArgParameter(collector_voltage)
    self.collector_current = self.ArgParameter(collector_current)
    self.gain = self.ArgParameter(gain)
    self.power = self.ArgParameter(power)
    self.channel = self.ArgParameter(channel)

    self.actual_collector_voltage_rating = self.Parameter(RangeExpr())
    self.actual_collector_current_rating = self.Parameter(RangeExpr())
    self.actual_power_rating = self.Parameter(RangeExpr())
    self.actual_gain = self.Parameter(RangeExpr())

  def contents(self):
    super().contents()

    self.description = DescriptionString(
      "<b>Vce:</b> ", DescriptionString.FormatUnits(self.actual_collector_voltage_rating, "V"),
      " <b>of operating:</b> ", DescriptionString.FormatUnits(self.collector_voltage, "V"), "\n",
      "<b>Ice:</b> ", DescriptionString.FormatUnits(self.actual_collector_current_rating, "A"),
      " <b>of operating:</b> ", DescriptionString.FormatUnits(self.collector_current, "A"), "\n",
      "<b>Gain:</b> ", DescriptionString.FormatUnits(self.actual_gain, ""),
      " <b>of spec:</b> ", DescriptionString.FormatUnits(self.gain, ""), "\n",
      "<b>Pmax:</b> ", DescriptionString.FormatUnits(self.actual_power_rating, "W"),
      " <b>of operating:</b> ", DescriptionString.FormatUnits(self.power, "W")
    )


@non_library
class BjtStandardFootprint(Bjt, StandardFootprint[Bjt]):
  REFDES_PREFIX = 'Q'

  FOOTPRINT_PINNING_MAP = {
    'Package_TO_SOT_SMD:SOT-23': lambda block: {
      '1': block.base,
      '2': block.emitter,
      '3': block.collector,
    },
  }


class TableBjt(BjtStandardFootprint, PartsTableFootprintSelector):
  VCE_RATING = PartsTableColumn(Range)
  ICE_RATING = PartsTableColumn(Range)
  GAIN = PartsTableColumn(Range)
  POWER_RATING = PartsTableColumn(Range)
  CHANNEL = PartsTableColumn(str)  # either 'PNP' or 'NPN'

  @init_in_parent
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.generator_param(self.collector_voltage, self.collector_current, self.gain, self.power, self.channel)

  def _row_filter(self, row: PartsTableRow) -> bool:
    return super()._row_filter(row) and \
      row[self.CHANNEL] == self.get(self.channel) and \
      self.get(self.collector_voltage).fuzzy_in(row[self.VCE_RATING]) and \
      self.get(self.collector_current).fuzzy_in(row[self.ICE_RATING]) and \
      self.get(self.gain).fuzzy_in(row[self.GAIN]) and \
      self.get(self.power).fuzzy_in(row[self.POWER_RATING])

  def _row_generate(self, row: PartsTableRow) -> None:
    super()._row_generate(row)
    self.assign(self.actual_collector_voltage_rating, row[self.VCE_RATING])
    self.assign(self.actual_collector_current_rating, row[self.ICE_RATING])
    self.assign(self.actual_gain, row[self.GAIN])
    self.assign(self.actual_power_rating, row[self.POWER_RATING])
