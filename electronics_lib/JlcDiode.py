from typing import *
import re
from electronics_abstract_parts import *

from .JlcFootprint import JlcTableFootprint


DescriptionParser = Tuple[re.Pattern,
                          Callable[[re.Match],
                                   Dict[PartsTableColumn, Any]]]

class JlcZenerDiode(TableZenerDiode, JlcTableFootprint, FootprintBlock):
  PACKAGE_FOOTPRINT_MAP = {
    'LL-34': 'Diode_SMD:D_MiniMELF',
    'SOD-123': 'Diode_SMD:D_SOD-123',
    'SOD-323': 'Diode_SMD:D_SOD-323',
    'SMA,DO-214AC': 'Diode_SMD:D_SMA',
    'SMB,DO-214AA': 'Diode_SMD:D_SMB',
    'SMC,DO-214AB': 'Diode_SMD:D_SMC',
  }

  DESCRIPTION_PARSERS: List[DescriptionParser] = [
    (re.compile("(±\d+\.?\d*%) (\d+\.?\d*V) (\d+\.?\d*\w?A) @ (\d+\.?\d*V) (\d+\.?\d*\w?W).*"),
     lambda match: {
       TableZenerDiode.ZENER_VOLTAGE: Range.from_tolerance(PartsTableUtil.parse_value(match.group(2), 'V'),
                                                           PartsTableUtil.parse_tolerance(match.group(1)))
     }),
    (re.compile("(\d+\.?\d*V)(\(Min\))?~(\d+\.?\d*V)(\(Max\))? (\d+\.?\d*\w?A) @ (\d+\.?\d*V) (\d+\.?\d*\w?W).*"),
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
      footprint = cls.PACKAGE_FOOTPRINT_MAP.get(row['Package'])
      if footprint is None:
        return None

      new_cols: Optional[Dict[PartsTableColumn, Any]] = None
      for parser, match_fn in cls.DESCRIPTION_PARSERS:
        parsed_values = parser.match(row[cls.DESCRIPTION_HEADER])
        if parsed_values:
          new_cols = match_fn(parsed_values)
          break

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
