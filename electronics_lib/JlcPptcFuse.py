from typing import *
import re
from electronics_abstract_parts import *

from .JlcPart import JlcTablePart, DescriptionParser


class JlcPptcFuse(PptcFuse, TableFuse, JlcTablePart, FootprintBlock):
  PACKAGE_FOOTPRINT_MAP = {
    'F0603': 'Resistor_SMD:R_0603_1608Metric',
    '0603': 'Resistor_SMD:R_0603_1608Metric',
    'F0805': 'Resistor_SMD:R_0805_2012Metric',
    '0805': 'Resistor_SMD:R_0805_2012Metric',
    'F1206': 'Resistor_SMD:R_1206_3216Metric',
    '1206': 'Resistor_SMD:R_1206_3216Metric',
    '1210': 'Resistor_SMD:R_1210_3225Metric',
    'F1210': 'Resistor_SMD:R_1210_3225Metric',
    '1812': 'Resistor_SMD:R_1812_4532Metric',
    'F1812': 'Resistor_SMD:R_1812_4532Metric',
  }

  DESCRIPTION_PARSERS: List[DescriptionParser] = [
    (re.compile("(\S+V) (\S+A) (?:\S+A) (\S+A) .* Resettable Fuses.*"),
     lambda match: {
       TableFuse.VOLTAGE_RATING: Range.zero_to_upper(PartParserUtil.parse_value(match.group(1), 'V')),
       TableFuse.TRIP_CURRENT: Range.zero_to_upper(PartParserUtil.parse_value(match.group(2), 'A')),
       TableFuse.HOLD_CURRENT: Range.zero_to_upper(PartParserUtil.parse_value(match.group(3), 'A')),
     }),
  ]

  @classmethod
  def _make_table(cls) -> PartsTable:
    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      if not row['Second Category'] == 'Resettable Fuses':
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

  def _make_footprint(self, part: PartsTableRow) -> None:
    super()._make_footprint(part)
    self.assign(self.lcsc_part, part[self.LCSC_PART_HEADER])
    self.assign(self.actual_basic_part, part[self.BASIC_PART_HEADER] == self.BASIC_PART_VALUE)
