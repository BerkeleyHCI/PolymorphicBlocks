from typing import *
import re
from electronics_abstract_parts import *

from .JlcPart import JlcTablePart, DescriptionParser


class JlcBaseDiode:
  PACKAGE_FOOTPRINT_MAP = {
    'LL-34': 'Diode_SMD:D_MiniMELF',
    'SOD-123': 'Diode_SMD:D_SOD-123',
    'SOD-323': 'Diode_SMD:D_SOD-323',
    'SMA,DO-214AC': 'Diode_SMD:D_SMA',
    'SMB,DO-214AA': 'Diode_SMD:D_SMB',
    'SMC,DO-214AB': 'Diode_SMD:D_SMC',
  }


class JlcDiode(TableDiode, JlcTablePart, JlcBaseDiode, FootprintBlock):
  DESCRIPTION_PARSERS: List[DescriptionParser] = [
    (re.compile("(\d+\.?\d*\w?V) (\d+\.?\d*\w?A) (\d+\.?\d*\w?V) @ (\d+\.?\d*\w?A) .* Schottky Barrier Diodes \(SBD\).*"),
     lambda match: {
       TableDiode.VOLTAGE_RATING: Range.zero_to_upper(PartsTableUtil.parse_value(match.group(1), 'V')),
       TableDiode.CURRENT_RATING: Range.zero_to_upper(PartsTableUtil.parse_value(match.group(2), 'A')),
       TableDiode.FORWARD_VOLTAGE: Range.zero_to_upper(PartsTableUtil.parse_value(match.group(3), 'V')),
       TableDiode.REVERSE_RECOVERY: Range.zero_to_upper(500e-9),  # arbitrary <500ns
     }),
  ]

  @classmethod
  def _make_table(cls) -> PartsTable:
    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      if row['Second Category'] not in [
        'Schottky Barrier Diodes (SBD)',
        # 'Switching Diode',  # inconsistent description format
        # 'Diodes - General Purpose', 'Diodes - Fast Recovery Rectifiers',
        # 'Diodes Rectifiers Fast Recovery'
      ]:
        return None
      footprint = cls.PACKAGE_FOOTPRINT_MAP.get(row[cls._PACKAGE_HEADER])
      if footprint is None:
        return None

      new_cols = cls.parse_full_description(row[cls.DESCRIPTION_HEADER], cls.DESCRIPTION_PARSERS)
      if new_cols is None:
        return None

      new_cols[cls.KICAD_FOOTPRINT] = footprint
      new_cols.update(cls._parse_jlcpcb_common(row))
      return new_cols

    return cls._jlc_table().map_new_columns(parse_row).sort_by(
      lambda row: [row[cls.BASIC_PART_HEADER], row[cls.KICAD_FOOTPRINT], row[cls.COST]]
    )

  def _make_footprint(self, part: PartsTableRow) -> None:
    self.footprint(
      'D', part[self.KICAD_FOOTPRINT],
      {
        '1': self.cathode,
        '2': self.anode,
      },
      mfr=part[self.MANUFACTURER_HEADER], part=part[self.PART_NUMBER],
      value=part[self.DESCRIPTION_HEADER],
      datasheet=part[self.DATASHEET_HEADER]
    )
    self.assign(self.lcsc_part, part[self.LCSC_PART_HEADER])
    self.assign(self.actual_basic_part, part[self.BASIC_PART_HEADER] == self.BASIC_PART_VALUE)


class JlcZenerDiode(TableZenerDiode, JlcTablePart, JlcBaseDiode, FootprintBlock):
  DESCRIPTION_PARSERS: List[DescriptionParser] = [
    (re.compile("(±\d+\.?\d*%) (\d+\.?\d*\w?V) (\d+\.?\d*\w?A) @ (\d+\.?\d*\w?V) (\d+\.?\d*\w?W).*"),
     lambda match: {
       TableZenerDiode.ZENER_VOLTAGE: Range.from_tolerance(PartsTableUtil.parse_value(match.group(2), 'V'),
                                                           PartsTableUtil.parse_tolerance(match.group(1)))
     }),
    (re.compile("(\d+\.?\d*\w?V)(\(Min\))?~(\d+\.?\d*\w?V)(\(Max\))? (\d+\.?\d*\w?A) @ (\d+\.?\d*\w?V) (\d+\.?\d*\w?W).*"),
     lambda match: {
       TableZenerDiode.ZENER_VOLTAGE: Range(PartsTableUtil.parse_value(match.group(1), 'V'),
                                            PartsTableUtil.parse_value(match.group(3), 'V'))
     }),
  ]

  @classmethod
  def _make_table(cls) -> PartsTable:
    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      if row['Second Category'] != 'Zener Diodes':
        return None
      footprint = cls.PACKAGE_FOOTPRINT_MAP.get(row[cls._PACKAGE_HEADER])
      if footprint is None:
        return None

      new_cols = cls.parse_full_description(row[cls.DESCRIPTION_HEADER], cls.DESCRIPTION_PARSERS)
      if new_cols is None:
        return None

      new_cols[cls.KICAD_FOOTPRINT] = footprint
      new_cols.update(cls._parse_jlcpcb_common(row))
      return new_cols

    return cls._jlc_table().map_new_columns(parse_row).sort_by(
      lambda row: [row[cls.BASIC_PART_HEADER], row[cls.KICAD_FOOTPRINT], row[cls.COST]]
    )

  def _make_footprint(self, part: PartsTableRow) -> None:
    self.footprint(
      'D', part[self.KICAD_FOOTPRINT],
      {
        '1': self.cathode,
        '2': self.anode,
      },
      mfr=part[self.MANUFACTURER_HEADER], part=part[self.PART_NUMBER],
      value=part[self.DESCRIPTION_HEADER],
      datasheet=part[self.DATASHEET_HEADER]
    )
    self.assign(self.lcsc_part, part[self.LCSC_PART_HEADER])
    self.assign(self.actual_basic_part, part[self.BASIC_PART_HEADER] == self.BASIC_PART_VALUE)
