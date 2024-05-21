from typing import *
import re
from ..abstract_parts import *

from .JlcPart import DescriptionParser, JlcTableSelector


class JlcBaseDiode:
  PACKAGE_FOOTPRINT_MAP = {
    'LL-34': 'Diode_SMD:D_MiniMELF',
    'SOD-123': 'Diode_SMD:D_SOD-123',
    'SOD-323': 'Diode_SMD:D_SOD-323',
    'SMA,DO-214AC': 'Diode_SMD:D_SMA',
    'SMA': 'Diode_SMD:D_SMA',
    'SMAF': 'Diode_SMD:D_SMA',  # footprint compatible even if not the same package
    'SMB,DO-214AA': 'Diode_SMD:D_SMB',
    'SMC,DO-214AB': 'Diode_SMD:D_SMC',
  }


class JlcDiode(TableDiode, JlcTableSelector, JlcBaseDiode):
  DESCRIPTION_PARSERS: List[DescriptionParser] = [
    (re.compile("(\S+V) (\S+V)@\S+A (\S+A) .* Schottky Barrier Diodes \(SBD\).*"),
     lambda match: {
       TableDiode.VOLTAGE_RATING: Range.zero_to_upper(PartParserUtil.parse_value(match.group(1), 'V')),
       TableDiode.CURRENT_RATING: Range.zero_to_upper(PartParserUtil.parse_value(match.group(3), 'A')),
       TableDiode.FORWARD_VOLTAGE: Range.zero_to_upper(PartParserUtil.parse_value(match.group(2), 'V')),
       TableDiode.REVERSE_RECOVERY: Range.zero_to_upper(500e-9),  # arbitrary <500ns
     }),
    (re.compile("(\S+A) (?:Single )?\S+A@\S+V (\S+?V) (\S+V)@\S+A .* General Purpose.*"),
     lambda match: {
       TableDiode.VOLTAGE_RATING: Range.zero_to_upper(PartParserUtil.parse_value(match.group(2), 'V')),
       TableDiode.CURRENT_RATING: Range.zero_to_upper(PartParserUtil.parse_value(match.group(1), 'A')),
       TableDiode.FORWARD_VOLTAGE: Range.zero_to_upper(PartParserUtil.parse_value(match.group(3), 'V')),
       TableDiode.REVERSE_RECOVERY: Range.all(),
     }),
    (re.compile("(\S+V)@\S+A \S+A@\S+V (\S+s) (?:Single )?(\S+A) \S+ (\S+V) .* Diodes - Fast Recovery Rectifiers.*"),
     lambda match: {
       TableDiode.VOLTAGE_RATING: Range.zero_to_upper(PartParserUtil.parse_value(match.group(4), 'V')),
       TableDiode.CURRENT_RATING: Range.zero_to_upper(PartParserUtil.parse_value(match.group(3), 'A')),
       TableDiode.FORWARD_VOLTAGE: Range.zero_to_upper(PartParserUtil.parse_value(match.group(1), 'V')),
       TableDiode.REVERSE_RECOVERY: Range.zero_to_upper(PartParserUtil.parse_value(match.group(2), 's')),
     }),
    (re.compile("(\S+V) .*\S+W (?:Single )?(\S+V)@\S+A (\S+s) (?:\S+A@\S+V )?(\S+A) .* Switching Diode.*"),
     lambda match: {
       TableDiode.VOLTAGE_RATING: Range.zero_to_upper(PartParserUtil.parse_value(match.group(1), 'V')),
       TableDiode.CURRENT_RATING: Range.zero_to_upper(PartParserUtil.parse_value(match.group(4), 'A')),
       TableDiode.FORWARD_VOLTAGE: Range.zero_to_upper(PartParserUtil.parse_value(match.group(2), 'V')),
       TableDiode.REVERSE_RECOVERY: Range.zero_to_upper(PartParserUtil.parse_value(match.group(3), 's')),
     }),
  ]

  @classmethod
  def _make_table(cls) -> PartsTable:
    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      if row['Second Category'] not in [
        'Schottky Barrier Diodes (SBD)',
        'Diodes - General Purpose',
        'Diodes - Fast Recovery Rectifiers',
        'Switching Diode',
      ]:
        return None
      footprint = cls.PACKAGE_FOOTPRINT_MAP.get(row[cls._PACKAGE_HEADER])
      if footprint is None:
        return None

      new_cols = cls.parse_full_description(row[cls.DESCRIPTION_COL], cls.DESCRIPTION_PARSERS)
      if new_cols is None:
        return None

      new_cols[cls.KICAD_FOOTPRINT] = footprint
      new_cols.update(cls._parse_jlcpcb_common(row))
      return new_cols

    return cls._jlc_table().map_new_columns(parse_row).sort_by(
      lambda row: [row[cls.BASIC_PART_HEADER], row[cls.KICAD_FOOTPRINT], row[cls.COST]]
    )


class JlcZenerDiode(TableZenerDiode, JlcTableSelector, JlcBaseDiode):
  DESCRIPTION_PARSERS: List[DescriptionParser] = [
    (re.compile("\S+A@\S+V (±\S+%) \S+Ω (?:Single )?(\S+W) (\S+V).* Zener Diodes.*"),
     lambda match: {
       TableZenerDiode.ZENER_VOLTAGE: PartParserUtil.parse_abs_tolerance(
         match.group(1), PartParserUtil.parse_value(match.group(3), 'V'), 'V'),
       TableZenerDiode.POWER_RATING: Range.zero_to_upper(PartParserUtil.parse_value(match.group(2), 'W')),
     }),
    (re.compile("\S+A@\S+V \S+Ω (?:Single )?(\S+V)~(\S+V) (\S+W) \S+V .* Zener Diodes.*"),
     lambda match: {
       TableZenerDiode.ZENER_VOLTAGE: Range(PartParserUtil.parse_value(match.group(1), 'V'),
                                            PartParserUtil.parse_value(match.group(2), 'V')),
       TableZenerDiode.POWER_RATING: Range.zero_to_upper(PartParserUtil.parse_value(match.group(3), 'W')),
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

      new_cols = cls.parse_full_description(row[cls.DESCRIPTION_COL], cls.DESCRIPTION_PARSERS)
      if new_cols is None:
        return None

      new_cols[cls.KICAD_FOOTPRINT] = footprint
      new_cols.update(cls._parse_jlcpcb_common(row))
      return new_cols

    return cls._jlc_table().map_new_columns(parse_row).sort_by(
      lambda row: [row[cls.BASIC_PART_HEADER], row[cls.KICAD_FOOTPRINT], row[cls.COST]]
    )
