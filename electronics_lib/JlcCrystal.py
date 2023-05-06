import re
from typing import Optional, Dict, Any, List
from electronics_abstract_parts import *
from .JlcPart import JlcTableSelector, DescriptionParser


class JlcCrystal(TableCrystal, JlcTableSelector, FootprintBlock):
  SERIES_PACKAGE_FOOTPRINT_MAP = {
    ('X3225', 'SMD-3225_4P'): 'Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm',
  }

  DESCRIPTION_PARSERS: List[DescriptionParser] = [
    (re.compile("(\S+Hz) SMD Crystal Resonator (\S+F) (±\S+) .* Crystals .*"),
     lambda match: {
       TableCrystal.FREQUENCY: Range.from_tolerance(PartParserUtil.parse_value(match.group(1), 'Hz'),
                                                    PartParserUtil.parse_tolerance(match.group(3))),
       TableCrystal.CAPACITANCE: PartParserUtil.parse_value(match.group(2), 'F'),
     }),
  ]

  @classmethod
  def _make_table(cls) -> PartsTable:
    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      if row['Second Category'] != 'Crystals':
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
