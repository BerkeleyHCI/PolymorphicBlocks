from typing import *
import re
from electronics_abstract_parts import *

from .JlcPart import DescriptionParser, JlcTableSelector


class JlcInductor(TableInductor, SmdStandardPackageSelector, JlcTableSelector):
  PACKAGE_FOOTPRINT_MAP = {
    '0402': 'Inductor_SMD:L_0402_1005Metric',
    '0603': 'Inductor_SMD:L_0603_1608Metric',
    '0805': 'Inductor_SMD:L_0805_2012Metric',
    '1206': 'Inductor_SMD:L_1206_3216Metric',
    '1210': 'Inductor_SMD:L_1210_3225Metric',
    '1812': 'Inductor_SMD:L_1812_4532Metric',

    'L0402': 'Inductor_SMD:L_0402_1005Metric',
    'L0603': 'Inductor_SMD:L_0603_1608Metric',
    'L0805': 'Inductor_SMD:L_0805_2012Metric',
    'L1206': 'Inductor_SMD:L_1206_3216Metric',
    'L1210': 'Inductor_SMD:L_1210_3225Metric',
    'L1812': 'Inductor_SMD:L_1812_4532Metric',
  }

  # a secondary parsing method if the package parser fails
  PART_FOOTPRINT_PARSERS: List[DescriptionParser] = [
    (re.compile("^NR(20|24|30|40|50|60|80).*$"),
     lambda match: {
       PartsTableFootprint.KICAD_FOOTPRINT: f'Inductor_SMD:L_Taiyo-Yuden_NR-{match.group(1)}xx'
     }),
    (re.compile("^SRR1015-.*$"),
     lambda match: {
       PartsTableFootprint.KICAD_FOOTPRINT: f'Inductor_SMD:L_Bourns-SRR1005'
     }),
    (re.compile("^SRR1210A?-.*$"),
     lambda match: {
       PartsTableFootprint.KICAD_FOOTPRINT: f'Inductor_SMD:L_Bourns_SRR1210A'
     }),
    (re.compile("^SRR1260A?-.*$"),
     lambda match: {
       PartsTableFootprint.KICAD_FOOTPRINT: f'Inductor_SMD:L_Bourns_SRR1260'
     }),
    # Kicad does not have stock 1008 footprint
  ]

  DESCRIPTION_PARSERS: List[DescriptionParser] = [
    (re.compile("(\S+A) (\S+H) (±\S+%) (\S+Ω) .* Inductors.*"),
     lambda match: {
       TableInductor.INDUCTANCE: Range.from_tolerance(PartParserUtil.parse_value(match.group(2), 'H'),
                                                      PartParserUtil.parse_tolerance(match.group(3))),
       TableInductor.FREQUENCY_RATING: Range.all(),  # ignored, checked elsewhere
       TableInductor.CURRENT_RATING: Range.zero_to_upper(PartParserUtil.parse_value(match.group(1), 'A')),
       TableInductor.DC_RESISTANCE: Range.zero_to_upper(PartParserUtil.parse_value(match.group(4), 'Ω')),
     }),
    (re.compile("(\S+A) (\S+H) ±(\S+H) (\S+Ω) .* Inductors.*"),
     lambda match: {
       TableInductor.INDUCTANCE: Range.from_abs_tolerance(PartParserUtil.parse_value(match.group(2), 'H'),
                                                          PartParserUtil.parse_value(match.group(3), 'H')),
       TableInductor.FREQUENCY_RATING: Range.all(),  # ignored, checked elsewhere
       TableInductor.CURRENT_RATING: Range.zero_to_upper(PartParserUtil.parse_value(match.group(1), 'A')),
       TableInductor.DC_RESISTANCE: Range.zero_to_upper(PartParserUtil.parse_value(match.group(4), 'Ω')),
     }),
  ]

  @init_in_parent
  def __init__(self, *args, ignore_frequency: BoolLike = False, **kwargs):
    super().__init__(*args, **kwargs)
    self.require(ignore_frequency | (self.frequency == Range.zero_to_upper(0)),
                 "JLC inductors do not have frequency data, frequency spec must be ignored")

  @classmethod
  def _make_table(cls) -> PartsTable:
    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      if row['Second Category'] not in ('Inductors (SMD)', 'Power Inductors'):
        return None

      new_cols = {}

      footprint = cls.PACKAGE_FOOTPRINT_MAP.get(row[cls._PACKAGE_HEADER])
      if footprint is not None:
        new_cols[cls.KICAD_FOOTPRINT] = footprint
      else:
        footprint_cols = cls.parse_full_description(row[cls.PART_NUMBER_COL], cls.PART_FOOTPRINT_PARSERS)
        if footprint_cols is not None:
          new_cols.update(footprint_cols)
        else:
          return None

      desc_cols = cls.parse_full_description(row[cls.DESCRIPTION_COL], cls.DESCRIPTION_PARSERS)
      if desc_cols is not None:
        new_cols.update(desc_cols)
      else:
        return None

      new_cols.update(cls._parse_jlcpcb_common(row))
      return new_cols

    return cls._jlc_table().map_new_columns(parse_row)

  @classmethod
  def _row_sort_by(cls, row: PartsTableRow) -> Any:
    return [row[cls.BASIC_PART_HEADER], row[cls.KICAD_FOOTPRINT], row[cls.COST]]
