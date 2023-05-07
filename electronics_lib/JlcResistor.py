import re
from typing import Optional, Dict, Any
from electronics_abstract_parts import *
from electronics_lib.JlcPart import JlcTableSelector


class JlcResistor(TableResistor, SmdStandardPackageSelector, JlcTableSelector):
  PACKAGE_FOOTPRINT_MAP = {
    # 0201 not in parts table, R_0201_0603Metric

    '0402': 'Resistor_SMD:R_0402_1005Metric',
    '0603': 'Resistor_SMD:R_0603_1608Metric',
    '0805': 'Resistor_SMD:R_0805_2012Metric',
    '1206': 'Resistor_SMD:R_1206_3216Metric',
    '2010': 'Resistor_SMD:R_2010_5025Metric',
    '2512': 'Resistor_SMD:R_2512_6332Metric',

    'R0402': 'Resistor_SMD:R_0402_1005Metric',
    'R0603': 'Resistor_SMD:R_0603_1608Metric',
    'R0805': 'Resistor_SMD:R_0805_2012Metric',
    'R1206': 'Resistor_SMD:R_1206_3216Metric',
    'R2010': 'Resistor_SMD:R_2010_5025Metric',
    'R2512': 'Resistor_SMD:R_2512_6332Metric',
  }

  RESISTOR_MATCHES = {
    'resistance': re.compile("(^|\s)(\S+Ω)($|\s)"),
    'tolerance': re.compile("(^|\s)(±\S+%)($|\s)"),
    'power': re.compile("(^|\s)(\S+W)($|\s)"),
    'voltage': re.compile("(^|\s)(\S+V)($|\s)"),
  }

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
          PartParserUtil.parse_value(extracted_values['resistance'][1], 'Ω'),
          PartParserUtil.parse_tolerance(extracted_values['tolerance'][1])
        )

        new_cols[cls.POWER_RATING] = Range.zero_to_upper(
          PartParserUtil.parse_value(extracted_values['power'][1], 'W'))

        new_cols[cls.VOLTAGE_RATING] = Range.zero_to_upper(
          PartParserUtil.parse_value(extracted_values['voltage'][1], 'V'))

        return new_cols
      except (KeyError, PartParserUtil.ParseError):
        return None

    return cls._jlc_table().map_new_columns(parse_row)
