import re
from typing import Optional, Dict, Any, List
from ..abstract_parts import *
from .JlcPart import DescriptionParser, JlcTableSelector


class JlcResistorArray(TableResistorArray, JlcTableSelector):
  SERIES_PACKAGE_FOOTPRINT_MAP = {
    ('4D03', '0603_x4'): 'Resistor_SMD:R_Array_Concave_4x0603',  # 1206 overall size
    ('4D03', 'RES-ARRAY-SMD'): 'Resistor_SMD:R_Array_Concave_4x0603',  # same as above, but inconsistent footprint field
    ('4D02', '0402_x4'): 'Resistor_SMD:R_Array_Concave_4x0402',  # 2x1mm overall size
    ('RC-M', '0402_x4'): 'Resistor_SMD:R_Array_Convex_4x0402',  # 2x1mm overall size
  }

  DESCRIPTION_PARSERS: List[DescriptionParser] = [
    (re.compile("(\S+) (±\S+%) \S+ (\S+Ω) (\S+W) ±\S+ \S+ Resistor Networks & Arrays.*"),
     lambda match: {
       TableResistorArray.RESISTANCE: PartParserUtil.parse_abs_tolerance(
         match.group(2), PartParserUtil.parse_value(match.group(3), 'Ω'), 'Ω'),
       TableResistorArray.POWER_RATING: Range.zero_to_upper(PartParserUtil.parse_value(match.group(4), 'W')),
       TableResistorArray.COUNT: int(match.group(1)),
     }),
  ]

  @classmethod
  def _make_table(cls) -> PartsTable:
    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      if row['Second Category'] != 'Resistor Networks & Arrays':
        return None

      footprint = None
      for (series, package), map_footprint in cls.SERIES_PACKAGE_FOOTPRINT_MAP.items():
        if row[cls.PART_NUMBER_COL].startswith(series) and row[cls._PACKAGE_HEADER] == package:
          assert footprint is None, f"multiple footprint rules match {row[cls.PART_NUMBER_COL]}"
          footprint = map_footprint
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
