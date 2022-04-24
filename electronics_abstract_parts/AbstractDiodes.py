from electronics_model import *
from .Categories import *
from .PartsTable import PartsTableColumn, PartsTableRow
from .PartsTablePart import PartsTableFootprint
from .StandardPinningFootprint import StandardPinningFootprint


@abstract_block
class BaseDiode(DiscreteSemiconductor):
  """Base class for diodes, with anode and cathode pins, including a very wide range of devices.
  """

  @init_in_parent
  def __init__(self) -> None:
    super().__init__()

    self.anode = self.Port(Passive.empty())
    self.cathode = self.Port(Passive.empty())


@abstract_block
class BaseDiodeStandardPinning(BaseDiode, StandardPinningFootprint[BaseDiode]):
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
class Diode(BaseDiode):
  """Base class for untyped diodes

  TODO power? capacitance? leakage current?
  """
  @init_in_parent
  def __init__(self, reverse_voltage: RangeLike, current: RangeLike, *,
               voltage_drop: RangeLike = Default(Range.all()),
               reverse_recovery_time: RangeLike = Default(Range.all())) -> None:
    super().__init__()

    self.reverse_voltage = self.ArgParameter(reverse_voltage)
    self.current = self.ArgParameter(current)
    self.voltage_drop = self.ArgParameter(voltage_drop)
    self.reverse_recovery_time = self.ArgParameter(reverse_recovery_time)


@abstract_block
class TableDiode(Diode, BaseDiodeStandardPinning, PartsTableFootprint, GeneratorBlock):
  VOLTAGE_RATING = PartsTableColumn(Range)  # tolerable blocking voltages, positive
  CURRENT_RATING = PartsTableColumn(Range)  # tolerable currents, average
  FORWARD_VOLTAGE = PartsTableColumn(Range)  # possible forward voltage range
  REVERSE_RECOVERY = PartsTableColumn(Range)  # possible reverse recovery time

  @init_in_parent
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.generator(self.select_part, self.reverse_voltage, self.current, self.voltage_drop,
                   self.reverse_recovery_time, self.part, self.footprint_spec)

    self.actual_voltage_rating = self.Parameter(RangeExpr())
    self.actual_current_rating = self.Parameter(RangeExpr())
    self.actual_voltage_drop = self.Parameter(RangeExpr())
    self.actual_reverse_recovery_time = self.Parameter(RangeExpr())

  def select_part(self, reverse_voltage: Range, current: Range, voltage_drop: Range,
                  reverse_recovery_time: Range, part_spec: str, footprint_spec: str) -> None:
    parts = self._get_table().filter(lambda row: (
        (not part_spec or part_spec == row[self.PART_NUMBER_COL]) and
        (not footprint_spec or footprint_spec == row[self.KICAD_FOOTPRINT]) and
        reverse_voltage.fuzzy_in(row[self.VOLTAGE_RATING]) and
        current.fuzzy_in(row[self.CURRENT_RATING]) and
        row[self.FORWARD_VOLTAGE].fuzzy_in(voltage_drop) and
        row[self.REVERSE_RECOVERY].fuzzy_in(reverse_recovery_time)
    ))
    part = parts.first(f"no diodes in Vr,max={reverse_voltage} V, I={current} A, Vf={voltage_drop} V, trr={reverse_recovery_time} s")

    self.assign(self.actual_part, part[self.PART_NUMBER_COL])
    self.assign(self.matching_parts, len(parts))

    self.assign(self.actual_voltage_rating, part[self.VOLTAGE_RATING])
    self.assign(self.actual_current_rating, part[self.CURRENT_RATING])
    self.assign(self.actual_voltage_drop, part[self.FORWARD_VOLTAGE])
    self.assign(self.actual_reverse_recovery_time, part[self.REVERSE_RECOVERY])

    self._make_footprint(part)

  def _make_footprint(self, part: PartsTableRow) -> None:
    self.footprint(
      'D', part[self.KICAD_FOOTPRINT],
      self._make_pinning(part[self.KICAD_FOOTPRINT]),
      mfr=part[self.MANUFACTURER_COL], part=part[self.PART_NUMBER_COL],
      value=part[self.DESCRIPTION_COL],
      datasheet=part[self.DATASHEET_COL]
    )


@abstract_block
class ZenerDiode(BaseDiode, DiscreteSemiconductor):
  """Base class for untyped zeners

  TODO power? capacitance? leakage current?
  """
  @init_in_parent
  def __init__(self, zener_voltage: RangeLike) -> None:
    super().__init__()

    self.zener_voltage = self.ArgParameter(zener_voltage)


@abstract_block
class TableZenerDiode(ZenerDiode, BaseDiodeStandardPinning, PartsTableFootprint, GeneratorBlock):
  ZENER_VOLTAGE = PartsTableColumn(Range)
  POWER_RATING = PartsTableColumn(Range)  # tolerable power

  @init_in_parent
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.generator(self.select_part, self.zener_voltage, self.part, self.footprint_spec)

    self.actual_zener_voltage = self.Parameter(RangeExpr())
    self.actual_power_rating = self.Parameter(RangeExpr())

  def select_part(self, zener_voltage: Range, part_spec: str, footprint_spec: str) -> None:
    parts = self._get_table().filter(lambda row: (
        (not part_spec or part_spec == row[self.PART_NUMBER_COL]) and
        (not footprint_spec or footprint_spec == row[self.KICAD_FOOTPRINT]) and
        row[self.ZENER_VOLTAGE].fuzzy_in(zener_voltage)
    ))
    part = parts.first(f"no zener diodes in Vz={zener_voltage} V")

    self.assign(self.actual_part, part[self.PART_NUMBER_COL])
    self.assign(self.matching_parts, len(parts))

    self.assign(self.actual_zener_voltage, part[self.ZENER_VOLTAGE])
    self.assign(self.actual_power_rating, part[self.POWER_RATING])

    self._make_footprint(part)

  def _make_footprint(self, part: PartsTableRow) -> None:
    self.footprint(
      'D', part[self.KICAD_FOOTPRINT],
      self._make_pinning(part[self.KICAD_FOOTPRINT]),
      mfr=part[self.MANUFACTURER_COL], part=part[self.PART_NUMBER_COL],
      value=part[self.DESCRIPTION_COL],
      datasheet=part[self.DATASHEET_COL]
    )


class ProtectionZenerDiode(DiscreteApplication):
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
    self.connect(self.diode.cathode.as_voltage_sink(
      voltage_limits=(0, self.voltage.lower()),
      current_draw=(0, 0)*Amp  # TODO should be leakage current
    ), self.pwr)
    self.connect(self.diode.anode.as_voltage_sink(), self.gnd)
