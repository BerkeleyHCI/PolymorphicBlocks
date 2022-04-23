from typing import *
import re
from electronics_abstract_parts import *


from .JlcTable import JlcTable
from .JlcFootprint import JlcFootprint


DescriptionParser = Tuple[re.Pattern,
                          Callable[[re.Match],
                                   Dict[PartsTableColumn, Any]]]

class JlcZenerDiode(TableZenerDiode, JlcFootprint, FootprintBlock):
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
        parsed_values = parser.match(row[JlcTable.DESCRIPTION])
        if parsed_values:
          new_cols = match_fn(parsed_values)
          break

      if new_cols is None:
        return None

      new_cols[cls.KICAD_FOOTPRINT] = footprint
      new_cols.update(JlcTable._parse_jlcpcb_common(row))
      return new_cols

    return JlcTable._jlc_table().map_new_columns(parse_row).sort_by(
      lambda row: [row[cls.KICAD_FOOTPRINT], row[JlcTable.COST]]
    )

  def _make_footprint(self, part: PartsTableRow) -> None:
    self.footprint(
      'D', part[self.KICAD_FOOTPRINT],
      {
        '1': self.cathode,
        '2': self.anode,
      },
      mfr=part[JlcTable.MANUFACTURER], part=part[JlcTable.PART_NUMBER],
      value=part[JlcTable.DESCRIPTION],
      datasheet=part[JlcTable.DATASHEETS]
    )
    self.assign(self.lcsc_part, part[JlcTable.JLC_PART_NUMBER])
