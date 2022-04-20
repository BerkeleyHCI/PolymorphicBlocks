from electronics_abstract_parts import *
from .DigikeyTable import *


class BaseDiodeTable(DigikeyTable):
  PACKAGE_FOOTPRINT_MAP = {
    'DO-214AC, SMA': 'Diode_SMD:D_SMA',
    'DO-214AA, SMB': 'Diode_SMD:D_SMB',
    'DO-214AB, SMC': 'Diode_SMD:D_SMC',
    'SOD-123': 'Diode_SMD:D_SOD-123',
    'SOD-123F': 'Diode_SMD:D_SOD-123',
    'SOD-123FL': 'Diode_SMD:D_SOD-123',
    'SC-76, SOD-323': 'Diode_SMD:D_SOD-323',
    'SC-90, SOD-323F': 'Diode_SMD:D_SOD-323',  # TODO should the FL use the more compact FL pattern?
    'TO-252-3, DPak (2 Leads + Tab), SC-63': 'Package_TO_SOT_SMD:TO-252-2',
    'TO-263-3, D²Pak (2 Leads + Tab), TO-263AB': 'Package_TO_SOT_SMD:TO-263-2',
  }

  @classmethod
  def footprint_pinmap(cls, footprint: str, anode: CircuitPort, cathode: CircuitPort):
    return {
      'Diode_SMD:D_SMA': {
        '1': cathode,
        '2': anode,
      },
      'Diode_SMD:D_SMB': {
        '1': cathode,
        '2': anode,
      },
      'Diode_SMD:D_SMC': {
        '1': cathode,
        '2': anode,
      },
      'Diode_SMD:D_SOD-123': {
        '1': cathode,
        '2': anode,
      },
      'Diode_SMD:D_SOD-323': {
        '1': cathode,
        '2': anode,
      },
      'Package_TO_SOT_SMD:TO-252-2': {
        '1': anode,
        '2': cathode,
        '3': anode,
      },
      'Package_TO_SOT_SMD:TO-263-2': {
        '1': anode,  # TODO sometimes NC
        '2': cathode,
        '3': anode,
      },
    }[footprint]


class DiodeTable(BaseDiodeTable):
  VOLTAGE_RATING = PartsTableColumn(Range)  # tolerable voltages, positive
  CURRENT_RATING = PartsTableColumn(Range)  # tolerable currents, average
  FORWARD_VOLTAGE = PartsTableColumn(Range)  # possible forward voltage range
  REVERSE_RECOVERY = PartsTableColumn(Range)  # possible reverse recovery time
  FOOTPRINT = PartsTableColumn(str)  # KiCad footprint name

  @classmethod
  def _generate_table(cls) -> PartsTable:
    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      new_cols: Dict[PartsTableColumn, Any] = {}
      try:
        new_cols[cls.FOOTPRINT] = cls.PACKAGE_FOOTPRINT_MAP[row['Package / Case']]

        new_cols[cls.VOLTAGE_RATING] = Range.zero_to_upper(
          PartsTableUtil.parse_value(row['Voltage - DC Reverse (Vr) (Max)'], 'V')
        )
        new_cols[cls.CURRENT_RATING] = Range.zero_to_upper(
          PartsTableUtil.parse_value(row['Current - Average Rectified (Io)'], 'A')
        )
        new_cols[cls.FORWARD_VOLTAGE] = Range.zero_to_upper(
          PartsTableUtil.parse_value(
            PartsTableUtil.strip_parameter(row['Voltage - Forward (Vf) (Max) @ If']),
            'V')
        )
        if row['Reverse Recovery Time (trr)'] and row['Reverse Recovery Time (trr)'] != '-':
          reverse_recovery = Range.zero_to_upper(
            PartsTableUtil.parse_value(row['Reverse Recovery Time (trr)'], 's')
          )
        elif row['Speed'] == 'Fast Recovery =< 500ns, > 200mA (Io)':
          reverse_recovery = Range.zero_to_upper(500e-9)
        else:
          reverse_recovery = Range.zero_to_upper(float('inf'))
        new_cols[cls.REVERSE_RECOVERY] = reverse_recovery

        new_cols.update(cls._parse_digikey_common(row))

        return new_cols
      except (KeyError, PartsTableUtil.ParseError):
        return None

    raw_table = PartsTable.from_csv_files(PartsTableUtil.with_source_dir([
      'Digikey_Diodes_DO214.csv',
      'Digikey_Diodes_DPak_DDPak.csv',
      'Digikey_Diodes_SOD123_SOD323.csv',
    ], 'resources'), encoding='utf-8-sig')
    return raw_table.map_new_columns(parse_row).sort_by(
      lambda row: row[cls.COST]
    )


class SmtDiode(Diode, FootprintBlock, GeneratorBlock):
  @init_in_parent
  def __init__(self, *args, part: StringLike = Default(""), footprint: StringLike = Default(""), **kwargs):
    super().__init__(*args, **kwargs)
    self.actual_voltage_rating = self.Parameter(RangeExpr())
    self.actual_current_rating = self.Parameter(RangeExpr())
    self.actual_voltage_drop = self.Parameter(RangeExpr())
    self.actual_reverse_recovery_time = self.Parameter(RangeExpr())

    self.generator(self.select_part, self.reverse_voltage, self.current, self.voltage_drop,
                   self.reverse_recovery_time, part, footprint)

  def select_part(self, reverse_voltage: Range, current: Range, voltage_drop: Range,
                  reverse_recovery_time: Range, part_spec: str, footprint_spec: str) -> None:
    # TODO maybe apply ideal diode law / other simple static model to better bound Vf?
    part = DiodeTable.table().filter(lambda row: (
        (not part_spec or part_spec == row[DiodeTable.PART_NUMBER]) and
        (not footprint_spec or footprint_spec == row[DiodeTable.FOOTPRINT]) and
        reverse_voltage.fuzzy_in(row[DiodeTable.VOLTAGE_RATING]) and
        current.fuzzy_in(row[DiodeTable.CURRENT_RATING]) and
        row[DiodeTable.FORWARD_VOLTAGE].fuzzy_in(voltage_drop) and
        row[DiodeTable.REVERSE_RECOVERY].fuzzy_in(reverse_recovery_time)
    )).first(f"no diodes in Vr,max={reverse_voltage} V, I={current} A, Vf={voltage_drop} V, trr={reverse_recovery_time} s")

    self.assign(self.actual_voltage_rating, part[DiodeTable.VOLTAGE_RATING])
    self.assign(self.actual_current_rating, part[DiodeTable.CURRENT_RATING])
    self.assign(self.actual_voltage_drop, part[DiodeTable.FORWARD_VOLTAGE])
    self.assign(self.actual_reverse_recovery_time, part[DiodeTable.REVERSE_RECOVERY])

    self.footprint(
      'D', part[DiodeTable.FOOTPRINT],
      DiodeTable.footprint_pinmap(part[DiodeTable.FOOTPRINT],
                                  self.anode, self.cathode),
      mfr=part[DiodeTable.MANUFACTURER], part=part[DiodeTable.PART_NUMBER],
      value=f"Vr={part['Voltage - DC Reverse (Vr) (Max)']}, I={part['Current - Average Rectified (Io)']}",
      datasheet=part[DiodeTable.DATASHEETS]
    )


class ZenerTable(BaseDiodeTable):
  ZENER_VOLTAGE = PartsTableColumn(Range)  # actual zener voltage, positive
  FORWARD_VOLTAGE = PartsTableColumn(Range)  # possible forward voltage range
  POWER_RATING = PartsTableColumn(Range)  # tolerable power
  FOOTPRINT = PartsTableColumn(str)  # KiCad footprint name

  @classmethod
  def _generate_table(cls) -> PartsTable:
    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      new_cols: Dict[PartsTableColumn, Any] = {}
      try:
        new_cols[cls.FOOTPRINT] = cls.PACKAGE_FOOTPRINT_MAP[row['Package / Case']]

        new_cols[cls.ZENER_VOLTAGE] = Range.from_tolerance(
          PartsTableUtil.parse_value(row['Voltage - Zener (Nom) (Vz)'], 'V'),
          PartsTableUtil.parse_tolerance(row['Tolerance']),
        )
        new_cols[cls.FORWARD_VOLTAGE] = Range.zero_to_upper(
          PartsTableUtil.parse_value(
            PartsTableUtil.strip_parameter(row['Voltage - Forward (Vf) (Max) @ If']),
            'V')
        )
        new_cols[cls.POWER_RATING] = Range.zero_to_upper(
          PartsTableUtil.parse_value(row['Power - Max'], 'W')
        )

        new_cols.update(cls._parse_digikey_common(row))

        return new_cols
      except (KeyError, PartsTableUtil.ParseError):
        return None

    raw_table = PartsTable.from_csv_files(PartsTableUtil.with_source_dir([
      'Digikey_ZenerDiodes_DO214.csv',
      'Digikey_ZenerDiodes_SOD123_SOD323.csv',
    ], 'resources'), encoding='utf-8-sig')
    return raw_table.map_new_columns(parse_row).sort_by(
      lambda row: row[cls.COST]
    )


class SmtZenerDiode(ZenerDiode, FootprintBlock, GeneratorBlock):
  @init_in_parent
  def __init__(self, *args, part: StringLike = Default(""), footprint: StringLike = Default(""), **kwargs):
    super().__init__(*args, **kwargs)
    self.actual_zener_voltage = self.Parameter(RangeExpr())
    self.actual_forward_voltage_drop = self.Parameter(RangeExpr())

    self.generator(self.select_part, self.zener_voltage, self.forward_voltage_drop, part, footprint)

  def select_part(self, zener_voltage: Range, forward_voltage_drop: Range, part_spec: str, footprint_spec: str) -> None:
    part = ZenerTable.table().filter(lambda row: (
        (not part_spec or part_spec == row[ZenerTable.PART_NUMBER]) and
        (not footprint_spec or footprint_spec == row[ZenerTable.FOOTPRINT]) and
        row[ZenerTable.ZENER_VOLTAGE].fuzzy_in(zener_voltage) and
        row[ZenerTable.FORWARD_VOLTAGE].fuzzy_in(forward_voltage_drop)
    )).first(f"no zener diodes in Vz={zener_voltage} V, Vf={forward_voltage_drop} V")

    self.assign(self.actual_zener_voltage, part[ZenerTable.ZENER_VOLTAGE])
    self.assign(self.actual_forward_voltage_drop, part[ZenerTable.FORWARD_VOLTAGE])

    self.footprint(
      'D', part[ZenerTable.FOOTPRINT],
      ZenerTable.footprint_pinmap(part[ZenerTable.FOOTPRINT],
                                  self.anode, self.cathode),
      mfr=part[ZenerTable.MANUFACTURER], part=part[ZenerTable.PART_NUMBER],
      value=f"Vz={part['Voltage - Zener (Nom) (Vz)']}, I={part['Voltage - Forward (Vf) (Max) @ If']}",
      datasheet=part[ZenerTable.DATASHEETS]
    )
