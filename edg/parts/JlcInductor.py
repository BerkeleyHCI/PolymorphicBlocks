from typing import *
import re
from ..abstract_parts import *

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
    (re.compile("^SRP12(45|65)A?-.*$"),
     lambda match: {
       PartsTableFootprint.KICAD_FOOTPRINT: f'Inductor_SMD:L_Bourns_SRP1245A'
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
    (re.compile("^SWPA(3010|3012|3015|4010|4012|4018|4020|4025|4030|5012|5020|5040|6020|6028|6040|6045|8040)S.*$"),
     lambda match: {
       PartsTableFootprint.KICAD_FOOTPRINT: f'Inductor_SMD:L_Sunlord_SWPA{match.group(1)}S'
     }),
    (re.compile("^SWRB(1204|1205|1207)S.*$"),
     lambda match: {
       PartsTableFootprint.KICAD_FOOTPRINT: f'Inductor_SMD:L_Sunlord_SWRB{match.group(1)}S'
     }),
    (re.compile("^SLF(6025|6028|6045|7032|7045|7055|10145|12555|12565|12575)T.*$"),
     lambda match: {
       PartsTableFootprint.KICAD_FOOTPRINT: f'Inductor_SMD:L_TDK_SLF{match.group(1)}'
     }),
    # Kicad does not have stock 1008 footprint
  ]

  DESCRIPTION_PARSERS: List[DescriptionParser] = [
    (re.compile("(\S+A) (\S+H) (±\S+%)(?: \S+A)? (\S+Ω) .* Inductors.*"),
     lambda match: {
       TableInductor.INDUCTANCE: PartParserUtil.parse_abs_tolerance(
           match.group(3), PartParserUtil.parse_value(match.group(2), 'H'), 'H'),
       TableInductor.FREQUENCY_RATING: Range.all(),  # ignored, checked elsewhere
       TableInductor.CURRENT_RATING: Range.zero_to_upper(PartParserUtil.parse_value(match.group(1), 'A')),
       TableInductor.DC_RESISTANCE: Range.zero_to_upper(PartParserUtil.parse_value(match.group(4), 'Ω')),
     }),
    (re.compile("(\S+A) (\S+H) ±(\S+H)(?: \S+A)? (\S+Ω) .* Inductors.*"),
     lambda match: {
       TableInductor.INDUCTANCE: Range.from_abs_tolerance(PartParserUtil.parse_value(match.group(2), 'H'),
                                                          PartParserUtil.parse_value(match.group(3), 'H')),
       TableInductor.FREQUENCY_RATING: Range.all(),  # ignored, checked elsewhere
       TableInductor.CURRENT_RATING: Range.zero_to_upper(PartParserUtil.parse_value(match.group(1), 'A')),
       TableInductor.DC_RESISTANCE: Range.zero_to_upper(PartParserUtil.parse_value(match.group(4), 'Ω')),
     }),
  ]

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # because the table does not have frequency specs, the table filter can't enforce frequency ratings
    # so the user must add the actual frequency rating in refinements
    self.manual_frequency_rating = self.Parameter(RangeExpr(Range.exact(0)))
    self.require(self.frequency.within(self.manual_frequency_rating))

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
