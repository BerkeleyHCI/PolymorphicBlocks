from typing import Dict, Optional, Callable, Any
from electronics_abstract_parts import *
from .DigikeyTable import DigikeyTablePart


class DigikeyBaseFets(BaseTableFet, DigikeyTablePart, FootprintBlock):
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
  def _make_fet_table(cls) -> PartsTable:
    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      new_cols: Dict[PartsTableColumn, Any] = {}
      try:
        new_cols[cls.KICAD_FOOTPRINT] = cls.PACKAGE_FOOTPRINT_MAP[row[cls._PACKAGE_HEADER]]

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

  def _make_footprint(self, part: PartsTableRow) -> None:
    self.footprint(
      'Q', part[self.KICAD_FOOTPRINT],
      self.footprint_pinmap(part[self.KICAD_FOOTPRINT],
                            self.gate, self.drain, self.source),
      mfr=part[self.MANUFACTURER_HEADER], part=part[self.PART_NUMBER],
      value=f"Vds={part['Drain to Source Voltage (Vdss)']}, Ids={part['Current - Continuous Drain (Id) @ 25°C']}",
      datasheet=part[self.DATASHEET_HEADER]
    )


@abstract_block
class DigikeyFets(DigikeyBaseFets, TableFet):
  pass


class DigikeyNFet(NFet, DigikeyFets):
  @classmethod
  def _make_table(cls) -> PartsTable:
    return cls._make_fet_table().filter(lambda row: (
        row['FET Type'] == 'N-Channel'
    ))


class DigikeyPFet(PFet, DigikeyFets):
  @classmethod
  def _make_table(cls) -> PartsTable:
    return cls._make_fet_table().filter(lambda row: (
        row['FET Type'] == 'P-Channel'
    ))


@abstract_block
class DigikeySwitchFet(DigikeyBaseFets, TableSwitchFet):
  pass


class DigikeySwitchNFet(SwitchNFet, DigikeySwitchFet):
  @classmethod
  def _make_table(cls) -> PartsTable:
    return cls._make_fet_table().filter(lambda row: (
        row['FET Type'] == 'N-Channel'
    ))


class DigikeySwitchPFet(SwitchPFet, DigikeySwitchFet):
  @classmethod
  def _make_table(cls) -> PartsTable:
    return cls._make_fet_table().filter(lambda row: (
        row['FET Type'] == 'P-Channel'
    ))