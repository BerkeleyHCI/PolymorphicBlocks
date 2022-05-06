import re
from typing import Optional, Dict, Any
from electronics_abstract_parts import *
from .JlcPart import JlcTablePart


class JlcResistor(TableResistor, JlcTablePart, FootprintBlock):
  PACKAGE_FOOTPRINT_MAP = {
    '0603': 'Resistor_SMD:R_0603_1608Metric',
    '0805': 'Resistor_SMD:R_0805_2012Metric',
    '1206': 'Resistor_SMD:R_1206_3216Metric',
  }

  RESISTOR_MATCHES = {
    'resistance': re.compile("(^|\s)(\S+Ω)($|\s)"),
    'tolerance': re.compile("(^|\s)(±\S+%)($|\s)"),
    'power': re.compile("(^|\s)(\S+W)($|\s)"),
  }
  RESISTOR_POWER_DIV_MATCH = re.compile("(\d+)/(\d+)W")

  @classmethod
  def _make_table(cls) -> PartsTable:
    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      if row['First Category'] != 'Resistors':
        return None

      new_cols: Dict[PartsTableColumn, Any] = {}
      try:
        # handle the footprint first since this is the most likely to filter
        new_cols[cls.KICAD_FOOTPRINT] = cls.PACKAGE_FOOTPRINT_MAP[row[cls._PACKAGE_HEADER]]
        new_cols.update(cls._parse_jlcpcb_common(row))

        extracted_values = cls.parse(row[cls.DESCRIPTION_COL], cls.RESISTOR_MATCHES)

        new_cols[cls.RESISTANCE] = Range.from_tolerance(
          PartsTableUtil.parse_value(extracted_values['resistance'][1], 'Ω'),
          PartsTableUtil.parse_tolerance(extracted_values['tolerance'][1])
        )

        power_value = extracted_values['power'][1]
        power_div_match = cls.RESISTOR_POWER_DIV_MATCH.match(power_value)
        if power_div_match:
          power_rating = float(power_div_match.group(1)) / float(power_div_match.group(2))
        else:
          power_rating = PartsTableUtil.parse_value(power_value, 'W')
        new_cols[cls.POWER_RATING] = Range.zero_to_upper(power_rating)

        return new_cols
      except (KeyError, PartsTableUtil.ParseError):
        return None

    return cls._jlc_table().map_new_columns(parse_row).sort_by(
      lambda row: [row[cls.BASIC_PART_HEADER], row[cls.KICAD_FOOTPRINT], row[cls.COST]]
    )

  def _make_footprint(self, part: PartsTableRow) -> None:
    super()._make_footprint(part)
    self.assign(self.lcsc_part, part[self.LCSC_PART_HEADER])
    self.assign(self.actual_basic_part, part[self.BASIC_PART_HEADER] == self.BASIC_PART_VALUE)
