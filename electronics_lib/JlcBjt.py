from typing import *
import re
from electronics_abstract_parts import *

from .JlcPart import DescriptionParser, JlcTableSelector


class JlcBjt(TableBjt, JlcTableSelector):
  PACKAGE_FOOTPRINT_MAP = {
    'SOT-23': 'Package_TO_SOT_SMD:SOT-23',
    'SOT-23-3': 'Package_TO_SOT_SMD:SOT-23',

    'SOT-323': 'Package_TO_SOT_SMD:SOT-323_SC-70',
    'SOT-323-3': 'Package_TO_SOT_SMD:SOT-323_SC-70',
    'SC-70': 'Package_TO_SOT_SMD:SOT-323_SC-70',
    'SC-70-3': 'Package_TO_SOT_SMD:SOT-323_SC-70',

    'SOT-89': 'Package_TO_SOT_SMD:SOT-89-3',
    'SOT-89-3': 'Package_TO_SOT_SMD:SOT-89-3',
  }

  DESCRIPTION_PARSERS: List[DescriptionParser] = [
    # the included table is differently formatted than the latest JLC description format
    (re.compile("(\S+V) (\S+W) (\S+A) (\S+)@(?:\S+A,\S+V) .*(NPN|PNP).* Bipolar Transistors.*"),
     lambda match: {
       TableBjt.CHANNEL: match.group(5),
       TableBjt.VCE_RATING: Range.zero_to_upper(PartParserUtil.parse_value(match.group(1), 'V')),
       TableBjt.ICE_RATING: Range.zero_to_upper(PartParserUtil.parse_value(match.group(3), 'A')),
       TableBjt.GAIN: Range.exact(PartParserUtil.parse_value(match.group(4), '')),
       TableBjt.POWER_RATING: Range.zero_to_upper(PartParserUtil.parse_value(match.group(2), 'W')),
     }),
  ]

  @classmethod
  def _make_table(cls) -> PartsTable:
    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      if row['Second Category'] != 'Bipolar Transistors - BJT':
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
