from electronics_abstract_parts import *
from .ProductTableUtils import *
from .DigikeyTable import *


class BaseFetTable(DigikeyTable):
  _TABLES: List[str]

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
    }[footprint]

  @classmethod
  def _generate_table(cls) -> PartsTable:
    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      new_rows: Dict[PartsTableColumn, Any] = {}
      try:
        new_rows[cls.FOOTPRINT] = cls.PACKAGE_FOOTPRINT_MAP.get(row['Package / Case'])

        new_rows[cls.VDS_RATING] = Range.zero_to_upper(
          PartsTableUtil.parse_value(row['Drain to Source Voltage (Vdss)'], 'V')
        )
        new_rows[cls.IDS_RATING] = Range.zero_to_upper(
          PartsTableUtil.parse_value(row['Current - Continuous Drain (Id) @ 25°C'].split('(')[0].strip(), 'A')
        )

        if row['Vgs (Max)'].startswith('±'):
          vgs_max = PartsTableUtil.parse_value(row['Vgs (Max)'][1:], 'V')
          new_rows[cls.VGS_RATING] = Range(-vgs_max, vgs_max)
        else:
          return None

        vgs_drive = PartsTableUtil.parse_value(row['Drive Voltage (Max Rds On,  Min Rds On)'].split(',')[0], 'V')
        if vgs_drive >= 0:
          new_rows[cls.VGS_DRIVE] = Range(vgs_drive, vgs_max)
        else:
          new_rows[cls.VGS_DRIVE] = Range(-vgs_max, vgs_drive)

        new_rows[cls.RDS_ON] = Range.zero_to_upper(
          PartsTableUtil.parse_value(PartsTableUtil.strip_parameter(row['Rds On (Max) @ Id, Vgs']), 'Ohm')
        )
        new_rows[cls.GATE_CHARGE] = Range.zero_to_upper(
          PartsTableUtil.parse_value(PartsTableUtil.strip_parameter(row['Gate Charge (Qg) (Max) @ Vgs']), 'C')
        )
        new_rows[cls.POWER_RATING] = Range.zero_to_upper(
          PartsTableUtil.parse_value(row['Power Dissipation (Max)'].split('(')[0].strip(), 'W')
        )

        new_rows.update(cls._parse_digikey_common(row))

        return new_rows
      except (KeyError, PartsTableUtil.ParseError):
        return None

    raw_table = PartsTable.from_csv_files(PartsTableUtil.with_source_dir(cls._TABLES, 'resources'),
                                          encoding='utf-8-sig')
    return raw_table.map_new_columns(parse_row).sort_by(
      lambda row: row[cls.COST]
    )


class NFetTable(BaseFetTable):
  _TABLES = ['Digikey_NFETs.csv']


class PFetTable(BaseFetTable):
  _TABLES = ['Digikey_PFETs.csv']


@abstract_block
class SmtFet(Fet, FootprintBlock, GeneratorBlock):
  TABLE: Type[BaseFetTable]

  @init_in_parent
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.selected_drain_voltage_rating = self.Parameter(RangeExpr())
    self.selected_drain_current_rating = self.Parameter(RangeExpr())
    self.selected_gate_drive = self.Parameter(RangeExpr())
    self.selected_power_rating = self.Parameter(RangeExpr())
    self.selected_rds_on = self.Parameter(RangeExpr())
    self.selected_gate_charge = self.Parameter(RangeExpr())

    self.generator(self.select_part,
                   self.drain_voltage, self.drain_current,
                   self.gate_voltage, self.rds_on, self.gate_charge, self.power)

  def select_part(self, drain_voltage: Range, drain_current: Range,
                  gate_voltage: Range, rds_on: Range, gate_charge: Range, power: Range) -> None:
    part = self.TABLE.table().filter(lambda row: (
        drain_voltage.fuzzy_in(row[self.TABLE.VDS_RATING]) and
        drain_current.fuzzy_in(row[self.TABLE.IDS_RATING]) and
        gate_voltage.fuzzy_in(row[self.TABLE.VGS_DRIVE]) and
        row[self.TABLE.RDS_ON].fuzzy_in(rds_on) and
        row[self.TABLE.GATE_CHARGE].fuzzy_in(gate_charge) and
        power.fuzzy_in(row[self.TABLE.POWER_RATING])
    )).first(f"no FETs in Vds={drain_voltage} V, Ids={drain_current} A, Vgs={gate_voltage} V")

    self.assign(self.selected_drain_voltage_rating, part[self.TABLE.VDS_RATING])
    self.assign(self.selected_drain_current_rating, part[self.TABLE.IDS_RATING])
    self.assign(self.selected_gate_drive, part[self.TABLE.VGS_DRIVE])
    self.assign(self.selected_rds_on, part[self.TABLE.RDS_ON])
    self.assign(self.selected_power_rating, part[self.TABLE.POWER_RATING])
    self.assign(self.selected_gate_charge, part[self.TABLE.GATE_CHARGE])

    self.footprint(
      'Q', part[self.TABLE.FOOTPRINT],
      self.TABLE.footprint_pinmap(part[self.TABLE.FOOTPRINT],
                                  self.gate, self.drain, self.source),
      mfr=part[self.TABLE.MANUFACTURER], part=part[self.TABLE.PART_NUMBER],
      value=f"Vds={part['Drain to Source Voltage (Vdss)']}, Ids={part['Current - Continuous Drain (Id) @ 25°C']}",
      datasheet=part[self.TABLE.DATASHEETS]
    )


class SmtNFet(NFet, SmtFet):
  TABLE = NFetTable


class SmtPFet(PFet, SmtFet):
  TABLE = PFetTable


@abstract_block
class SmtSwitchFet(SwitchFet, FootprintBlock, GeneratorBlock):
  TABLE: Type[BaseFetTable]

  SWITCHING_POWER = PartsTableColumn(Range)
  STATIC_POWER = PartsTableColumn(Range)
  TOTAL_POWER = PartsTableColumn(Range)

  @init_in_parent
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.selected_drain_voltage_rating = self.Parameter(RangeExpr())
    self.selected_drain_current_rating = self.Parameter(RangeExpr())
    self.selected_gate_drive = self.Parameter(RangeExpr())
    self.selected_power_rating = self.Parameter(RangeExpr())
    self.selected_rds_on = self.Parameter(RangeExpr())
    self.selected_gate_charge = self.Parameter(RangeExpr())

    self.selected_static_power = self.Parameter(RangeExpr())
    self.selected_switching_power = self.Parameter(RangeExpr())
    self.selected_total_power = self.Parameter(RangeExpr())

    self.generator(self.select_part,
                   self.frequency, self.drive_current,
                   self.drain_voltage, self.drain_current,
                   self.gate_voltage, self.rds_on, self.gate_charge, self.power)

  def select_part(self, frequency: Range, drive_current: Range,
                  drain_voltage: Range, drain_current: Range,
                  gate_voltage: Range, rds_on: Range, gate_charge: Range, power: Range) -> None:
    # Pre-filter out by the static parameters
    prefiltered_parts = self.TABLE.table().filter(lambda row: (
        drain_voltage.fuzzy_in(row[self.TABLE.VDS_RATING]) and
        drain_current.fuzzy_in(row[self.TABLE.IDS_RATING]) and
        gate_voltage.fuzzy_in(row[self.TABLE.VGS_DRIVE]) and
        row[self.TABLE.RDS_ON].fuzzy_in(rds_on) and
        row[self.TABLE.GATE_CHARGE].fuzzy_in(gate_charge) and
        power.fuzzy_in(row[self.TABLE.POWER_RATING])
    ))

    # Then run the application-specific calculations and filter again by those
    gate_drive_rise, gate_drive_fall = drive_current.upper, -drive_current.lower
    assert gate_drive_rise > 0 and gate_drive_fall > 0, \
      f"got nonpositive gate currents rise={gate_drive_rise} A and fall={gate_drive_fall} A"
    def process_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      new_rows: Dict[PartsTableColumn, Any] = {}
      new_rows[self.STATIC_POWER] = drain_current * drain_current * row[self.TABLE.RDS_ON]

      rise_time = row[self.TABLE.GATE_CHARGE] / gate_drive_rise
      fall_time = row[self.TABLE.GATE_CHARGE] / gate_drive_fall
      new_rows[self.SWITCHING_POWER] = (rise_time + fall_time) * (drain_current * drain_voltage) * frequency

      new_rows[self.TOTAL_POWER] = new_rows[self.STATIC_POWER] + new_rows[self.SWITCHING_POWER]

      if new_rows[self.TOTAL_POWER].fuzzy_in(row[self.TABLE.POWER_RATING]):
        return new_rows
      else:
        return None

    part = prefiltered_parts.map_new_columns(
      process_row
    ).first(f"no FETs in Vds={drain_voltage} V, Ids={drain_current} A, Vgs={gate_voltage} V")

    self.assign(self.selected_drain_voltage_rating, part[self.TABLE.VDS_RATING])
    self.assign(self.selected_drain_current_rating, part[self.TABLE.IDS_RATING])
    self.assign(self.selected_gate_drive, part[self.TABLE.VGS_DRIVE])
    self.assign(self.selected_rds_on, part[self.TABLE.RDS_ON])
    self.assign(self.selected_power_rating, part[self.TABLE.POWER_RATING])
    self.assign(self.selected_gate_charge, part[self.TABLE.GATE_CHARGE])

    self.assign(self.selected_static_power, part[self.STATIC_POWER])
    self.assign(self.selected_switching_power, part[self.SWITCHING_POWER])
    self.assign(self.selected_total_power, part[self.TOTAL_POWER])

    self.footprint(
      'Q', part[self.TABLE.FOOTPRINT],
      self.TABLE.footprint_pinmap(part[self.TABLE.FOOTPRINT],
                                  self.gate, self.drain, self.source),
      mfr=part[self.TABLE.MANUFACTURER], part=part[self.TABLE.PART_NUMBER],
      value=f"Vds={part['Drain to Source Voltage (Vdss)']}, Ids={part['Current - Continuous Drain (Id) @ 25°C']}",
      datasheet=part[self.TABLE.DATASHEETS]
    )


class SmtSwitchNFet(SwitchNFet, SmtSwitchFet):
  TABLE = NFetTable


class SmtSwitchPFet(SwitchPFet, SmtSwitchFet):
  TABLE = PFetTable
