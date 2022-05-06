from typing import Any, Dict, Optional
from electronics_abstract_parts import *
from .DigikeyPart import DigikeyTablePart


class DigikeyBaseDiode:
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


class DigikeySmtDiode(TableDiode, DigikeyTablePart, DigikeyBaseDiode, FootprintBlock):
  @classmethod
  def _make_table(cls) -> PartsTable:
    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      new_cols: Dict[PartsTableColumn, Any] = {}
      try:
        new_cols[cls.KICAD_FOOTPRINT] = cls.PACKAGE_FOOTPRINT_MAP[row[cls._PACKAGE_HEADER]]

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


class DigikeySmtZenerDiode(TableZenerDiode, DigikeyTablePart, DigikeyBaseDiode, FootprintBlock):
  @classmethod
  def _make_table(cls) -> PartsTable:
    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      new_cols: Dict[PartsTableColumn, Any] = {}
      try:
        new_cols[cls.KICAD_FOOTPRINT] = cls.PACKAGE_FOOTPRINT_MAP[row[cls._PACKAGE_HEADER]]

        new_cols[cls.ZENER_VOLTAGE] = Range.from_tolerance(
          PartsTableUtil.parse_value(row['Voltage - Zener (Nom) (Vz)'], 'V'),
          PartsTableUtil.parse_tolerance(row['Tolerance']),
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
