from typing import Dict, Optional, Callable, Any
from electronics_abstract_parts import *
from .DigikeyTable import *


class FetTable(DigikeyTable):
  VDS_RATING = PartsTableColumn(Range)
  IDS_RATING = PartsTableColumn(Range)
  VGS_RATING = PartsTableColumn(Range)
  VGS_DRIVE = PartsTableColumn(Range)
  RDS_ON = PartsTableColumn(Range)
  POWER_RATING = PartsTableColumn(Range)
  GATE_CHARGE = PartsTableColumn(Range)

  FOOTPRINT = PartsTableColumn(str)  # KiCad footprint name

  PACKAGE_FOOTPRINT_MAP = {
    'TO-236-3, SC-59, SOT-23-3': 'Package_TO_SOT_SMD:SOT-23',
    'TO-261-4, TO-261AA': 'Package_TO_SOT_SMD:SOT-223-3_TabPin2',
    'TO-252-3, DPak (2 Leads + Tab), SC-63': 'Package_TO_SOT_SMD:TO-252-2',
    'TO-263-3, D²Pak (2 Leads + Tab), TO-263AB': 'Package_TO_SOT_SMD:TO-263-2',
    'PowerPAK® SO-8': 'Package_SO:PowerPAK_SO-8_Single',
  }

  @classmethod
  def footprint_pinmap(cls, footprint: str, gate: CircuitPort, drain: CircuitPort, source: CircuitPort):
    return {
      'Package_TO_SOT_SMD:SOT-23': {
        '1': gate,
        '2': source,
        '3': drain,
      },
      'Package_TO_SOT_SMD:SOT-223-3_TabPin2': {
        '1': gate,
        '2': drain,
        '3': source,
      },
      'Package_TO_SOT_SMD:TO-252-2': {
        '1': gate,
        '2': drain,
        '3': source,
      },
      'Package_TO_SOT_SMD:TO-263-2': {
        '1': gate,
        '2': drain,
        '3': source,
      },
      'Package_SO:PowerPAK_SO-8_Single': {
        '1': source,
        '2': source,
        '3': source,
        '4': gate,
        '5': drain,
      },
    }[footprint]

  @classmethod
  def _generate_table(cls) -> PartsTable:
    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      new_cols: Dict[PartsTableColumn, Any] = {}
      try:
        new_cols[cls.FOOTPRINT] = cls.PACKAGE_FOOTPRINT_MAP[row['Package / Case']]

        new_cols[cls.VDS_RATING] = Range.zero_to_upper(
          PartsTableUtil.parse_value(row['Drain to Source Voltage (Vdss)'], 'V')
        )
        new_cols[cls.IDS_RATING] = Range.zero_to_upper(
          PartsTableUtil.parse_value(row['Current - Continuous Drain (Id) @ 25°C'].split('(')[0].strip(), 'A')
        )

        if row['Vgs (Max)'].startswith('±'):
          vgs_max = PartsTableUtil.parse_value(row['Vgs (Max)'][1:], 'V')
          new_cols[cls.VGS_RATING] = Range(-vgs_max, vgs_max)
        else:
          return None

        vgs_drive = PartsTableUtil.parse_value(row['Drive Voltage (Max Rds On,  Min Rds On)'].split(',')[0], 'V')
        if vgs_drive >= 0:
          new_cols[cls.VGS_DRIVE] = Range(vgs_drive, vgs_max)
        else:
          new_cols[cls.VGS_DRIVE] = Range(-vgs_max, vgs_drive)

        new_cols[cls.RDS_ON] = Range.zero_to_upper(
          PartsTableUtil.parse_value(PartsTableUtil.strip_parameter(row['Rds On (Max) @ Id, Vgs']), 'Ohm')
        )
        new_cols[cls.GATE_CHARGE] = Range.zero_to_upper(
          PartsTableUtil.parse_value(PartsTableUtil.strip_parameter(row['Gate Charge (Qg) (Max) @ Vgs']), 'C')
        )
        new_cols[cls.POWER_RATING] = Range.zero_to_upper(
          PartsTableUtil.parse_value(row['Power Dissipation (Max)'].split('(')[0].strip(), 'W')
        )

        new_cols.update(cls._parse_digikey_common(row))

        return new_cols
      except (KeyError, PartsTableUtil.ParseError):
        return None

    raw_table = PartsTable.from_csv_files(PartsTableUtil.with_source_dir([
      'Digikey_NFETs.csv',
      'Digikey_PFETs.csv',
      'Digikey_FETs_SO8.csv',
    ], 'resources'), encoding='utf-8-sig')
    return raw_table.map_new_columns(parse_row).sort_by(
      lambda row: row[cls.COST]
    )

  @classmethod
  def n_fet_table(cls) -> PartsTable:
    # TODO maybe cache the results?
    return cls.table().filter(lambda row: (
        row['FET Type'] == 'N-Channel'
    ))

  @classmethod
  def p_fet_table(cls) -> PartsTable:
    # TODO maybe cache the results?
    return cls.table().filter(lambda row: (
        row['FET Type'] == 'P-Channel'
    ))

@abstract_block
class DigikeyFets(Fet, FootprintBlock, GeneratorBlock):
  TABLE_FN: Callable[[Any], PartsTable]

  @init_in_parent
  def __init__(self, *args, part: StringLike = Default(""), footprint: StringLike = Default(""),
               **kwargs):
    super().__init__(*args, **kwargs)

    self.generator(self.select_part, self.drain_voltage, self.drain_current,
                   self.gate_voltage, self.rds_on, self.gate_charge, self.power,
                   part, footprint)

  def select_part(self, drain_voltage: Range, drain_current: Range,
                  gate_voltage: Range, rds_on: Range, gate_charge: Range, power: Range,
                  part_spec: str, footprint_spec: str,) -> None:
    part = self.TABLE_FN().filter(lambda row: (
        (not part_spec or part_spec == row[FetTable.PART_NUMBER]) and
        (not footprint_spec or footprint_spec == row[FetTable.FOOTPRINT]) and
        drain_voltage.fuzzy_in(row[FetTable.VDS_RATING]) and
        drain_current.fuzzy_in(row[FetTable.IDS_RATING]) and
        gate_voltage.fuzzy_in(row[FetTable.VGS_RATING]) and
        row[FetTable.RDS_ON].fuzzy_in(rds_on) and
        row[FetTable.GATE_CHARGE].fuzzy_in(gate_charge) and
        power.fuzzy_in(row[FetTable.POWER_RATING])
    )).first(f"no FETs in Vds={drain_voltage} V, Ids={drain_current} A, Vgs={gate_voltage} V")

    self.assign(self.actual_drain_voltage_rating, part[FetTable.VDS_RATING])
    self.assign(self.actual_drain_current_rating, part[FetTable.IDS_RATING])
    self.assign(self.actual_gate_drive, part[FetTable.VGS_DRIVE])
    self.assign(self.actual_rds_on, part[FetTable.RDS_ON])
    self.assign(self.actual_power_rating, part[FetTable.POWER_RATING])
    self.assign(self.actual_gate_charge, part[FetTable.GATE_CHARGE])

    self.footprint(
      'Q', part[FetTable.FOOTPRINT],
      FetTable.footprint_pinmap(part[FetTable.FOOTPRINT],
                                self.gate, self.drain, self.source),
      mfr=part[FetTable.MANUFACTURER], part=part[FetTable.PART_NUMBER],
      value=f"Vds={part['Drain to Source Voltage (Vdss)']}, Ids={part['Current - Continuous Drain (Id) @ 25°C']}",
      datasheet=part[FetTable.DATASHEETS]
    )


class DigikeyNFet(NFet, DigikeyFets):
  TABLE_FN = FetTable.n_fet_table


class DigikeyPFet(PFet, DigikeyFets):
  TABLE_FN = FetTable.p_fet_table


@abstract_block
class DigikeySwitchFet(SwitchFet, FootprintBlock, GeneratorBlock):
  TABLE_FN: Callable[[Any], PartsTable]

  SWITCHING_POWER = PartsTableColumn(Range)
  STATIC_POWER = PartsTableColumn(Range)
  TOTAL_POWER = PartsTableColumn(Range)

  @init_in_parent
  def __init__(self, *args, part: StringLike = Default(""), footprint: StringLike = Default(""),
               **kwargs):
    super().__init__(*args, **kwargs)

    self.actual_static_power = self.Parameter(RangeExpr())
    self.actual_switching_power = self.Parameter(RangeExpr())
    self.actual_total_power = self.Parameter(RangeExpr())

    self.generator(self.select_part, self.frequency, self.drive_current,
                   self.drain_voltage, self.drain_current,
                   self.gate_voltage, self.rds_on, self.gate_charge, self.power,
                   part, footprint)

  def select_part(self, frequency: Range, drive_current: Range,
                  drain_voltage: Range, drain_current: Range,
                  gate_voltage: Range, rds_on: Range, gate_charge: Range, power: Range,
                  part_spec: str, footprint_spec: str) -> None:
    # Pre-filter out by the static parameters
    prefiltered_parts = self.TABLE_FN().filter(lambda row: (
        (not part_spec or part_spec == row[FetTable.PART_NUMBER]) and
        (not footprint_spec or footprint_spec == row[FetTable.FOOTPRINT]) and
        drain_voltage.fuzzy_in(row[FetTable.VDS_RATING]) and
        drain_current.fuzzy_in(row[FetTable.IDS_RATING]) and
        gate_voltage.fuzzy_in(row[FetTable.VGS_DRIVE]) and
        row[FetTable.RDS_ON].fuzzy_in(rds_on) and
        row[FetTable.GATE_CHARGE].fuzzy_in(gate_charge) and
        power.fuzzy_in(row[FetTable.POWER_RATING])
    ))

    # Then run the application-specific calculations and filter again by those
    gate_drive_rise, gate_drive_fall = drive_current.upper, -drive_current.lower
    assert gate_drive_rise > 0 and gate_drive_fall > 0, \
      f"got nonpositive gate currents rise={gate_drive_rise} A and fall={gate_drive_fall} A"
    def process_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      new_cols: Dict[PartsTableColumn, Any] = {}
      new_cols[self.STATIC_POWER] = drain_current * drain_current * row[FetTable.RDS_ON]

      rise_time = row[FetTable.GATE_CHARGE] / gate_drive_rise
      fall_time = row[FetTable.GATE_CHARGE] / gate_drive_fall
      new_cols[self.SWITCHING_POWER] = (rise_time + fall_time) * (drain_current * drain_voltage) * frequency

      new_cols[self.TOTAL_POWER] = new_cols[self.STATIC_POWER] + new_cols[self.SWITCHING_POWER]

      if new_cols[self.TOTAL_POWER].fuzzy_in(row[FetTable.POWER_RATING]):
        return new_cols
      else:
        return None

    part = prefiltered_parts.map_new_columns(
      process_row
    ).first(f"no FETs in Vds={drain_voltage} V, Ids={drain_current} A, Vgs={gate_voltage} V")

    self.assign(self.actual_drain_voltage_rating, part[FetTable.VDS_RATING])
    self.assign(self.actual_drain_current_rating, part[FetTable.IDS_RATING])
    self.assign(self.actual_gate_drive, part[FetTable.VGS_DRIVE])
    self.assign(self.actual_rds_on, part[FetTable.RDS_ON])
    self.assign(self.actual_power_rating, part[FetTable.POWER_RATING])
    self.assign(self.actual_gate_charge, part[FetTable.GATE_CHARGE])

    self.assign(self.actual_static_power, part[self.STATIC_POWER])
    self.assign(self.actual_switching_power, part[self.SWITCHING_POWER])
    self.assign(self.actual_total_power, part[self.TOTAL_POWER])

    self.footprint(
      'Q', part[FetTable.FOOTPRINT],
      FetTable.footprint_pinmap(part[FetTable.FOOTPRINT],
                                self.gate, self.drain, self.source),
      mfr=part[FetTable.MANUFACTURER], part=part[FetTable.PART_NUMBER],
      value=f"Vds={part['Drain to Source Voltage (Vdss)']}, Ids={part['Current - Continuous Drain (Id) @ 25°C']}",
      datasheet=part[FetTable.DATASHEETS]
    )


class DigikeySwitchNFet(SwitchNFet, DigikeySwitchFet):
  TABLE_FN = FetTable.n_fet_table


class DigikeySwitchPFet(SwitchPFet, DigikeySwitchFet):
  TABLE_FN = FetTable.p_fet_table
