from typing import Optional, Any, Dict

from electronics_model import *
from . import PartsTableFootprint, PartsTableColumn, PartsTableRow
from .Categories import *
from .StandardPinningFootprint import StandardPinningFootprint


@abstract_block
class Fet(DiscreteSemiconductor):
  """Base class for untyped MOSFETs
  Drain voltage, drain current, and gate voltages are positive (absolute).

  MOSFET equations
  - https://inst.eecs.berkeley.edu/~ee105/fa05/handouts/discussions/Discussion5.pdf (cutoff/linear/saturation regions)

  Potentially useful references for selecting FETs:
  - Toshiba application_note_en_20180726, Power MOSFET Selecting MOSFFETs and Consideration for Circuit Design
  - https://www.vishay.com/docs/71933/71933.pdf, MOSFET figures of merit (which don't help in choosing devices), Rds,on * Qg
  - https://www.allaboutcircuits.com/technical-articles/choosing-the-right-transistor-understanding-low-frequency-mosfet-parameters/
  - https://www.allaboutcircuits.com/technical-articles/choosing-the-right-transistor-understanding-dynamic-mosfet-parameters/
  """
  def symbol_pinning(self, symbol_name: str) -> Dict[str, Port]:
    # TODO actually check that the device channel corresponds with the schematic?
    assert symbol_name.startswith('Device:Q_NMOS_') or symbol_name.startswith('Device:Q_PMOS_')
    assert symbol_name.removeprefix('Device:Q_NMOS_').removeprefix('Device:Q_PMOS_') in \
           ('DGS', 'DSG', 'GDS', 'GSD', 'SDG', 'SGD')
    return {'D': self.drain, 'G': self.gate, 'S': self.source}

  @staticmethod
  def NFet(*args, **kwargs) -> 'Fet':
    return Fet(*args, **kwargs, channel='N')

  @staticmethod
  def PFet(*args, **kwargs) -> 'Fet':
    return Fet(*args, **kwargs, channel='P')

  @init_in_parent
  def __init__(self, drain_voltage: RangeLike, drain_current: RangeLike, *,
               gate_voltage: RangeLike = Default(Range.all()), rds_on: RangeLike = Default(Range.all()),
               gate_charge: RangeLike = Default(Range.all()), power: RangeLike = Default(Range.exact(0)),
               channel: StringLike = StringExpr()) -> None:
    super().__init__()

    self.source = self.Port(Passive.empty())
    self.drain = self.Port(Passive.empty())
    self.gate = self.Port(Passive.empty())

    self.drain_voltage = self.ArgParameter(drain_voltage)
    self.drain_current = self.ArgParameter(drain_current)
    self.gate_voltage = self.ArgParameter(gate_voltage)
    self.rds_on = self.ArgParameter(rds_on)
    self.gate_charge = self.ArgParameter(gate_charge)
    self.power = self.ArgParameter(power)
    self.channel = self.ArgParameter(channel)

    self.actual_drain_voltage_rating = self.Parameter(RangeExpr())
    self.actual_drain_current_rating = self.Parameter(RangeExpr())
    self.actual_gate_voltage_rating = self.Parameter(RangeExpr())
    self.actual_gate_drive = self.Parameter(RangeExpr())
    self.actual_power_rating = self.Parameter(RangeExpr())
    self.actual_rds_on = self.Parameter(RangeExpr())
    self.actual_gate_charge = self.Parameter(RangeExpr())

    self.description = DescriptionString(
      "<b>Vds:</b> ", DescriptionString.FormatUnits(self.actual_drain_voltage_rating, "V"),
      " <b>of operating:</b> ", DescriptionString.FormatUnits(self.drain_voltage, "V"), "\n",
      "<b>Ids:</b> ", DescriptionString.FormatUnits(self.actual_drain_current_rating, "A"),
      " <b>of operating:</b> ", DescriptionString.FormatUnits(self.drain_current, "A"), "\n",
      "<b>Vgs,max:</b> ", DescriptionString.FormatUnits(self.actual_gate_voltage_rating, "V"),
      " <b>of operating:</b> ", DescriptionString.FormatUnits(self.gate_voltage, "V"), "\n",
      "<b>Vgs,th:</b> ", DescriptionString.FormatUnits(self.actual_gate_drive, "V"), "\n",
      "<b>Rds,on:</b> ", DescriptionString.FormatUnits(self.actual_rds_on, "Ω"),
      " <b>of spec:</b> ", DescriptionString.FormatUnits(self.rds_on, "Ω"), "\n"
      "<b>Pmax:</b> ", DescriptionString.FormatUnits(self.actual_power_rating, "W"),
      " <b>of operating:</b> ", DescriptionString.FormatUnits(self.power, "W")
    )


@abstract_block
class FetStandardPinning(Fet, StandardPinningFootprint[Fet]):
  FOOTPRINT_PINNING_MAP = {
    'Package_TO_SOT_SMD:SOT-23': lambda block: {
      '1': block.gate,
      '2': block.source,
      '3': block.drain,
    },
    (
      'Package_TO_SOT_SMD:SOT-223-3_TabPin2',
      'Package_TO_SOT_SMD:TO-252-2',
      'Package_TO_SOT_SMD:TO-263-2'
    ): lambda block: {
      '1': block.gate,
      '2': block.drain,
      '3': block.source,
    },
    'Package_SO:PowerPAK_SO-8_Single': lambda block: {
      '1': block.source,
      '2': block.source,
      '3': block.source,
      '4': block.gate,
      '5': block.drain,
    },
  }


class BaseTableFet(Fet):
  """Shared table columns for both TableFet and TableSwitchFet"""
  VDS_RATING = PartsTableColumn(Range)
  IDS_RATING = PartsTableColumn(Range)
  VGS_RATING = PartsTableColumn(Range)
  VGS_DRIVE = PartsTableColumn(Range)
  RDS_ON = PartsTableColumn(Range)
  POWER_RATING = PartsTableColumn(Range)
  GATE_CHARGE = PartsTableColumn(Range)  # units of C
  CHANNEL = PartsTableColumn(str)  # either 'P' or 'N'


@abstract_block
class TableFet(FetStandardPinning, BaseTableFet, PartsTableFootprint, GeneratorBlock):
  @init_in_parent
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.generator(self.select_part, self.drain_voltage, self.drain_current,
                   self.gate_voltage, self.rds_on, self.gate_charge, self.power, self.channel,
                   self.part, self.footprint_spec)

  def select_part(self, drain_voltage: Range, drain_current: Range,
                  gate_voltage: Range, rds_on: Range, gate_charge: Range, power: Range, channel: str,
                  part_spec: str, footprint_spec: str) -> None:
    parts = self._get_table().filter(lambda row: (
        (not part_spec or part_spec == row[self.PART_NUMBER_COL]) and
        (not footprint_spec or footprint_spec == row[self.KICAD_FOOTPRINT]) and
        row[self.CHANNEL] == channel and
        drain_voltage.fuzzy_in(row[self.VDS_RATING]) and
        drain_current.fuzzy_in(row[self.IDS_RATING]) and
        gate_voltage.fuzzy_in(row[self.VGS_RATING]) and
        row[self.RDS_ON].fuzzy_in(rds_on) and
        row[self.GATE_CHARGE].fuzzy_in(gate_charge) and
        power.fuzzy_in(row[self.POWER_RATING])
    ))
    part = parts.first(f"no FETs in Vds={drain_voltage} V, Ids={drain_current} A, Vgs={gate_voltage} V")

    self.assign(self.actual_part, part[self.PART_NUMBER_COL])
    self.assign(self.matching_parts, parts.map(lambda row: row[self.PART_NUMBER_COL]))

    self.assign(self.actual_drain_voltage_rating, part[self.VDS_RATING])
    self.assign(self.actual_drain_current_rating, part[self.IDS_RATING])
    self.assign(self.actual_gate_voltage_rating, part[self.VGS_RATING])
    self.assign(self.actual_gate_drive, part[self.VGS_DRIVE])
    self.assign(self.actual_rds_on, part[self.RDS_ON])
    self.assign(self.actual_power_rating, part[self.POWER_RATING])
    self.assign(self.actual_gate_charge, part[self.GATE_CHARGE])

    self._make_footprint(part)

  def _make_footprint(self, part: PartsTableRow) -> None:
    self.footprint(
      'Q', part[self.KICAD_FOOTPRINT],
      self._make_pinning(part[self.KICAD_FOOTPRINT]),
      mfr=part[self.MANUFACTURER_COL], part=part[self.PART_NUMBER_COL],
      value=part[self.DESCRIPTION_COL],
      datasheet=part[self.DATASHEET_COL]
    )


@abstract_block
class SwitchFet(Fet):
  """FET that switches between an off state and on state, not operating in the linear region except for rise/fall time.
  Ports remain untyped. TODO: are these limitations enough to type the ports? maybe except for the output?
  Models static and switching power dissipation. Gate charge and power parameters are optional, they will be the
  stricter of the explicit input or model-derived parameters."""
  # TODO ideally this would just instantaite a Fet internally, but the parts selection becomes more complex b/c
  # parameters are cross-dependent
  @staticmethod
  def NFet(*args, **kwargs):
    return SwitchFet(*args, **kwargs, channel='N')

  @staticmethod
  def PFet(*args, **kwargs):
    return SwitchFet(*args, **kwargs, channel='P')


  @init_in_parent
  def __init__(self, frequency: RangeLike, drive_current: RangeLike, **kwargs) -> None:
    super().__init__(**kwargs)

    self.frequency = self.ArgParameter(frequency)
    self.drive_current = self.ArgParameter(drive_current)  # positive is turn-on drive, negative is turn-off drive


@abstract_block
class TableSwitchFet(SwitchFet, FetStandardPinning, BaseTableFet, PartsTableFootprint, GeneratorBlock):
  SWITCHING_POWER = PartsTableColumn(Range)
  STATIC_POWER = PartsTableColumn(Range)
  TOTAL_POWER = PartsTableColumn(Range)

  @init_in_parent
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.generator(self.select_part, self.frequency, self.drive_current,
                   self.drain_voltage, self.drain_current,
                   self.gate_voltage, self.rds_on, self.gate_charge, self.power, self.channel,
                   self.part, self.footprint_spec)  # type: ignore

    self.actual_static_power = self.Parameter(RangeExpr())
    self.actual_switching_power = self.Parameter(RangeExpr())
    self.actual_total_power = self.Parameter(RangeExpr())

  def select_part(self, frequency: Range, drive_current: Range,
                  drain_voltage: Range, drain_current: Range,
                  gate_voltage: Range, rds_on: Range, gate_charge: Range, power: Range, channel: str,
                  part_spec: str, footprint_spec: str) -> None:
    # Pre-filter out by the static parameters
    prefiltered_parts = self._get_table().filter(lambda row: (
        (not part_spec or part_spec == row[self.PART_NUMBER_COL]) and
        (not footprint_spec or footprint_spec == row[self.KICAD_FOOTPRINT]) and
        row[self.CHANNEL] == channel and
        drain_voltage.fuzzy_in(row[self.VDS_RATING]) and
        drain_current.fuzzy_in(row[self.IDS_RATING]) and
        gate_voltage.fuzzy_in(row[self.VGS_DRIVE]) and
        row[self.RDS_ON].fuzzy_in(rds_on) and
        row[self.GATE_CHARGE].fuzzy_in(gate_charge) and
        power.fuzzy_in(row[self.POWER_RATING])
    ))

    # Then run the application-specific calculations and filter again by those
    gate_drive_rise, gate_drive_fall = drive_current.upper, -drive_current.lower
    assert gate_drive_rise > 0 and gate_drive_fall > 0, \
      f"got nonpositive gate currents rise={gate_drive_rise} A and fall={gate_drive_fall} A"
    def process_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      new_cols: Dict[PartsTableColumn, Any] = {}
      new_cols[self.STATIC_POWER] = drain_current * drain_current * row[self.RDS_ON]

      rise_time = row[self.GATE_CHARGE] / gate_drive_rise
      fall_time = row[self.GATE_CHARGE] / gate_drive_fall
      new_cols[self.SWITCHING_POWER] = (rise_time + fall_time) * (drain_current * drain_voltage) * frequency

      new_cols[self.TOTAL_POWER] = new_cols[self.STATIC_POWER] + new_cols[self.SWITCHING_POWER]

      if new_cols[self.TOTAL_POWER].fuzzy_in(row[self.POWER_RATING]):
        return new_cols
      else:
        return None

    parts = prefiltered_parts.map_new_columns(process_row)
    part = parts.first(f"no FETs in Vds={drain_voltage} V, Ids={drain_current} A, Vgs={gate_voltage} V")

    self.assign(self.actual_part, part[self.PART_NUMBER_COL])
    self.assign(self.matching_parts, parts.map(lambda row: row[self.PART_NUMBER_COL]))

    self.assign(self.actual_drain_voltage_rating, part[self.VDS_RATING])
    self.assign(self.actual_drain_current_rating, part[self.IDS_RATING])
    self.assign(self.actual_gate_voltage_rating, part[self.VGS_RATING])
    self.assign(self.actual_gate_drive, part[self.VGS_DRIVE])
    self.assign(self.actual_rds_on, part[self.RDS_ON])
    self.assign(self.actual_power_rating, part[self.POWER_RATING])
    self.assign(self.actual_gate_charge, part[self.GATE_CHARGE])

    self.assign(self.actual_static_power, part[self.STATIC_POWER])
    self.assign(self.actual_switching_power, part[self.SWITCHING_POWER])
    self.assign(self.actual_total_power, part[self.TOTAL_POWER])

    self._make_footprint(part)

  def _make_footprint(self, part: PartsTableRow) -> None:
    self.footprint(
      'Q', part[self.KICAD_FOOTPRINT],
      self._make_pinning(part[self.KICAD_FOOTPRINT]),
      mfr=part[self.MANUFACTURER_COL], part=part[self.PART_NUMBER_COL],
      value=part[self.DESCRIPTION_COL],
      datasheet=part[self.DATASHEET_COL]
    )
