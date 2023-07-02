from typing import Dict

from electronics_model import *
from .Categories import *
from .PartsTable import PartsTableColumn, PartsTableRow
from .PartsTablePart import PartsTableFootprintSelector
from .StandardFootprint import StandardFootprint


@non_library
class BaseDiode(DiscreteSemiconductor):
  """Base class for diodes, with anode and cathode pins, including a very wide range of devices.
  """
  @init_in_parent
  def __init__(self) -> None:
    super().__init__()

    self.anode = self.Port(Passive.empty())
    self.cathode = self.Port(Passive.empty())


@non_library
class BaseDiodeStandardFootprint(BaseDiode, StandardFootprint[BaseDiode]):
  REFDES_PREFIX = 'D'

  FOOTPRINT_PINNING_MAP = {
    (
      'Diode_SMD:D_MiniMELF',
      'Diode_SMD:D_SOD-123',
      'Diode_SMD:D_SOD-323',
      'Diode_SMD:D_SMA',
      'Diode_SMD:D_SMB',
      'Diode_SMD:D_SMC',
    ): lambda block: {
      '1': block.cathode,
      '2': block.anode,
    },
    (  # TODO are these standard?
      'Package_TO_SOT_SMD:TO-252-2',
      'Package_TO_SOT_SMD:TO-263-2',
    ): lambda block: {
      '1': block.anode,  # sometimes NC
      '2': block.cathode,
      '3': block.anode,
    },
  }


@abstract_block
class Diode(KiCadImportableBlock, BaseDiode):
  """Base class for untyped diodes

  TODO power? capacitance? leakage current?
  """
  def symbol_pinning(self, symbol_name: str) -> Dict[str, BasePort]:
    assert symbol_name in ('Device:D', 'Device:D_Small')
    return {'A': self.anode, 'K': self.cathode}

  @init_in_parent
  def __init__(self, reverse_voltage: RangeLike, current: RangeLike, *,
               voltage_drop: RangeLike = Range.all(),
               reverse_recovery_time: RangeLike = Range.all()) -> None:
    super().__init__()

    self.reverse_voltage = self.ArgParameter(reverse_voltage)
    self.current = self.ArgParameter(current)
    self.voltage_drop = self.ArgParameter(voltage_drop)
    self.reverse_recovery_time = self.ArgParameter(reverse_recovery_time)

    self.actual_voltage_rating = self.Parameter(RangeExpr())
    self.actual_current_rating = self.Parameter(RangeExpr())
    self.actual_voltage_drop = self.Parameter(RangeExpr())
    self.actual_reverse_recovery_time = self.Parameter(RangeExpr())

  def contents(self):
    super().contents()

    self.description = DescriptionString(
      "<b>Vr:</b> ", DescriptionString.FormatUnits(self.actual_voltage_rating, "V"),
      " <b>of operating:</b> ", DescriptionString.FormatUnits(self.reverse_voltage, "V"), "\n",
      "<b>If:</b> ", DescriptionString.FormatUnits(self.actual_current_rating, "A"),
      " <b>of operating:</b> ", DescriptionString.FormatUnits(self.current, "A"), "\n",
      "<b>Vf:</b> ", DescriptionString.FormatUnits(self.actual_voltage_drop, "V"),
      " <b>of spec:</b> ", DescriptionString.FormatUnits(self.voltage_drop, "V")
    )


@non_library
class TableDiode(Diode, BaseDiodeStandardFootprint, PartsTableFootprintSelector, GeneratorBlock):
  VOLTAGE_RATING = PartsTableColumn(Range)  # tolerable blocking voltages, positive
  CURRENT_RATING = PartsTableColumn(Range)  # tolerable currents, average
  FORWARD_VOLTAGE = PartsTableColumn(Range)  # possible forward voltage range
  REVERSE_RECOVERY = PartsTableColumn(Range)  # possible reverse recovery time

  @init_in_parent
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.generator_param(self.reverse_voltage, self.current, self.voltage_drop, self.reverse_recovery_time)

  def _row_filter(self, row: PartsTableRow) -> bool:
    return super()._row_filter(row) and \
      self.get(self.reverse_voltage).fuzzy_in(row[self.VOLTAGE_RATING]) and \
      self.get(self.current).fuzzy_in(row[self.CURRENT_RATING]) and \
      row[self.FORWARD_VOLTAGE].fuzzy_in(self.get(self.voltage_drop)) and \
      row[self.REVERSE_RECOVERY].fuzzy_in(self.get(self.reverse_recovery_time))

  def _row_generate(self, row: PartsTableRow) -> None:
    super()._row_generate(row)
    self.assign(self.actual_voltage_rating, row[self.VOLTAGE_RATING])
    self.assign(self.actual_current_rating, row[self.CURRENT_RATING])
    self.assign(self.actual_voltage_drop, row[self.FORWARD_VOLTAGE])
    self.assign(self.actual_reverse_recovery_time, row[self.REVERSE_RECOVERY])


@abstract_block
class ZenerDiode(BaseDiode, DiscreteSemiconductor):
  """Base class for untyped zeners

  TODO power? capacitance? leakage current?
  """
  @init_in_parent
  def __init__(self, zener_voltage: RangeLike) -> None:
    super().__init__()

    self.zener_voltage = self.ArgParameter(zener_voltage)

    self.actual_zener_voltage = self.Parameter(RangeExpr())
    self.actual_power_rating = self.Parameter(RangeExpr())

  def contents(self):
    super().contents()

    self.description = DescriptionString(
      "zener voltage=", DescriptionString.FormatUnits(self.actual_zener_voltage, "V"),
      " <b>of spec:</b>", DescriptionString.FormatUnits(self.zener_voltage, "V"), "\n",
      "power=", DescriptionString.FormatUnits(self.actual_power_rating, "W")
    )


@non_library
class TableZenerDiode(ZenerDiode, BaseDiodeStandardFootprint, PartsTableFootprintSelector, GeneratorBlock):
  ZENER_VOLTAGE = PartsTableColumn(Range)
  POWER_RATING = PartsTableColumn(Range)  # tolerable power

  @init_in_parent
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.generator_param(self.zener_voltage)

  def _row_filter(self, row: PartsTableRow) -> bool:
    return super()._row_filter(row) and \
      row[self.ZENER_VOLTAGE].fuzzy_in(self.get(self.zener_voltage))

  def _row_generate(self, row: PartsTableRow) -> None:
    super()._row_generate(row)
    self.assign(self.actual_zener_voltage, row[self.ZENER_VOLTAGE])
    self.assign(self.actual_power_rating, row[self.POWER_RATING])


class ProtectionZenerDiode(Protection):
  """Zener diode reversed across a power rail to provide transient overvoltage protection (and become an incandescent
  indicator on a reverse voltage)"""
  @init_in_parent
  def __init__(self, voltage: RangeLike):
    super().__init__()

    self.pwr = self.Port(VoltageSink.empty(), [Power, InOut])
    self.gnd = self.Port(Ground.empty(), [Common])

    self.voltage = self.ArgParameter(voltage)

  def contents(self):
    super().contents()
    self.diode = self.Block(ZenerDiode(zener_voltage=self.voltage))
    self.connect(self.diode.cathode.adapt_to(VoltageSink(
      voltage_limits=(0, self.diode.actual_zener_voltage.lower()),
      current_draw=(0, 0)*Amp  # TODO should be leakage current
    )), self.pwr)
    self.connect(self.diode.anode.adapt_to(Ground()), self.gnd)
