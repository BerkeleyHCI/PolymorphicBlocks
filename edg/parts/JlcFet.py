from typing import *
import re
from ..abstract_parts import *

from .JlcPart import DescriptionParser, JlcTableSelector


class JlcBaseFet(JlcTableSelector):
  PACKAGE_FOOTPRINT_MAP = {
    'SOT-23': 'Package_TO_SOT_SMD:SOT-23',
    'SOT23-3': 'Package_TO_SOT_SMD:SOT-23',
    'SOT-23-3': 'Package_TO_SOT_SMD:SOT-23',
    'SOT-23-3L': 'Package_TO_SOT_SMD:SOT-23',

    'SOT-323': 'Package_TO_SOT_SMD:SOT-323_SC-70',
    'SOT-323(SC-80)': 'Package_TO_SOT_SMD:SOT-323_SC-70',
    'SOT-323-3': 'Package_TO_SOT_SMD:SOT-323_SC-70',
    'SC-70-3': 'Package_TO_SOT_SMD:SOT-323_SC-70',

    'TO-252': 'Package_TO_SOT_SMD:TO-252-2',  # aka DPak
    'TO-252-2': 'Package_TO_SOT_SMD:TO-252-2',
    'TO-252(DPAK)': 'Package_TO_SOT_SMD:TO-252-2',
    'DPAK': 'Package_TO_SOT_SMD:TO-252-2',
    'TO-252-2(DPAK)': 'Package_TO_SOT_SMD:TO-252-2',
    'TO-263-2': 'Package_TO_SOT_SMD:TO-263-2',  # aka D2Pak
    'D2PAK': 'Package_TO_SOT_SMD:TO-263-2',

    'SOT-223': 'Package_TO_SOT_SMD:SOT-223-3_TabPin2',
    'SOT-223-3': 'Package_TO_SOT_SMD:SOT-223-3_TabPin2',

    'SO-8': 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',
    'SOIC-8': 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',
    'SOIC-8_3.9x4.9x1.27P': 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',
    'SOP-8': 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',
    'SOP-8_3.9x4.9x1.27P': 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',

    'PowerPAK SO-8_EP_5.2x6.2x1.27P': 'Package_DFN_QFN:PQFN-8-EP_6x5mm_P1.27mm_Generic',
    'POWERPAK-SO-8': 'Package_DFN_QFN:PQFN-8-EP_6x5mm_P1.27mm_Generic',
    'PowerPAK-SO-8': 'Package_DFN_QFN:PQFN-8-EP_6x5mm_P1.27mm_Generic',
    'PowerPAKSO-8L': 'Package_DFN_QFN:PQFN-8-EP_6x5mm_P1.27mm_Generic',
    'PowerPAKSO-8': 'Package_DFN_QFN:PQFN-8-EP_6x5mm_P1.27mm_Generic',
    'DFN5X6-8': 'Package_DFN_QFN:PQFN-8-EP_6x5mm_P1.27mm_Generic',
    'DFN5x6': 'Package_DFN_QFN:PQFN-8-EP_6x5mm_P1.27mm_Generic',
    'DFN-8_5x6x1.27P': 'Package_DFN_QFN:PQFN-8-EP_6x5mm_P1.27mm_Generic',
    'DFN-8(5x6)': 'Package_DFN_QFN:PQFN-8-EP_6x5mm_P1.27mm_Generic',
    'DFN5X6-8L': 'Package_DFN_QFN:PQFN-8-EP_6x5mm_P1.27mm_Generic',
    'PDFN5x6': 'Package_DFN_QFN:PQFN-8-EP_6x5mm_P1.27mm_Generic',
    'PDFN5x6-8': 'Package_DFN_QFN:PQFN-8-EP_6x5mm_P1.27mm_Generic',
    'PDFN5x6-8L': 'Package_DFN_QFN:PQFN-8-EP_6x5mm_P1.27mm_Generic',
    'PDFN5X6-8L': 'Package_DFN_QFN:PQFN-8-EP_6x5mm_P1.27mm_Generic',
    'PQFN 5X6': 'Package_DFN_QFN:PQFN-8-EP_6x5mm_P1.27mm_Generic',
    'PQFN5x6-8': 'Package_DFN_QFN:PQFN-8-EP_6x5mm_P1.27mm_Generic',
    'PQFN-8(4.9x5.8)': 'Package_DFN_QFN:PQFN-8-EP_6x5mm_P1.27mm_Generic',
    'PQFN-8(5x6)': 'Package_DFN_QFN:PQFN-8-EP_6x5mm_P1.27mm_Generic',
    'PRPAK5x6': 'Package_DFN_QFN:PQFN-8-EP_6x5mm_P1.27mm_Generic',
    'PRPAK5x6-8L': 'Package_DFN_QFN:PQFN-8-EP_6x5mm_P1.27mm_Generic',
    'PG-TDSON-8_EP_5.2x6.2x1.27P': 'Package_DFN_QFN:PQFN-8-EP_6x5mm_P1.27mm_Generic',

    'TDSON-8-EP(5x6)': 'Package_DFN_QFN:PQFN-8-EP_6x5mm_P1.27mm_Generic',
    'PDFN-8(5x6)': 'Package_DFN_QFN:PQFN-8-EP_6x5mm_P1.27mm_Generic',
    'DFN-8-EP(6.1x5.2)': 'Package_DFN_QFN:PQFN-8-EP_6x5mm_P1.27mm_Generic',
    'DFN-8(4.9x5.8)': 'Package_DFN_QFN:PQFN-8-EP_6x5mm_P1.27mm_Generic',
    'PDFN-8(5.8x4.9)': 'Package_DFN_QFN:PQFN-8-EP_6x5mm_P1.27mm_Generic',
  }

  DESCRIPTION_PARSERS: List[DescriptionParser] = [
    (re.compile("(\S+V) (\S+A) (\S+W) (\S+Ω)@(\S+V),\S+A (\S+V)@\S+A.* ([PN]) Channel.* MOSFETs.*"),
     lambda match: {
       TableFet.CHANNEL: match.group(7),
       TableFet.VDS_RATING: Range.zero_to_upper(PartParserUtil.parse_value(match.group(1), 'V')),
       TableFet.IDS_RATING: Range.zero_to_upper(PartParserUtil.parse_value(match.group(2), 'A')),
       # Vgs isn't specified, so the Ron@Vgs is used as a lower bound; assumed symmetric
       TableFet.VGS_RATING: Range.from_abs_tolerance(0,
                                                     PartParserUtil.parse_value(match.group(5), 'V')),
       TableFet.VGS_DRIVE: Range(PartParserUtil.parse_value(match.group(6), 'V'),
                                 PartParserUtil.parse_value(match.group(5), 'V')),
       TableFet.RDS_ON: Range.exact(PartParserUtil.parse_value(match.group(4), 'Ω')),
       TableFet.POWER_RATING: Range.zero_to_upper(PartParserUtil.parse_value(match.group(3), 'W')),
       TableFet.GATE_CHARGE: Range.all(),  # placeholder for unspecified
     }),
    # Some of them have the power entry later, for whatever reason
    (re.compile("(\S+V) (\S+A) (\S+Ω)@(\S+V),\S+A (\S+W) (\S+V)@\S+A.* ([PN]) Channel.* (\S+C)@\S+V.* MOSFETs.*"),
     lambda match: {
       TableFet.CHANNEL: match.group(7),
       TableFet.VDS_RATING: Range.zero_to_upper(PartParserUtil.parse_value(match.group(1), 'V')),
       TableFet.IDS_RATING: Range.zero_to_upper(PartParserUtil.parse_value(match.group(2), 'A')),
       # Vgs isn't specified, so the Ron@Vgs is used as a lower bound; assumed symmetric
       TableFet.VGS_RATING: Range.from_abs_tolerance(0,
                                                     PartParserUtil.parse_value(match.group(4), 'V')),
       TableFet.VGS_DRIVE: Range(PartParserUtil.parse_value(match.group(6), 'V'),
                                 PartParserUtil.parse_value(match.group(4), 'V')),
       TableFet.RDS_ON: Range.exact(PartParserUtil.parse_value(match.group(3), 'Ω')),
       TableFet.POWER_RATING: Range.zero_to_upper(PartParserUtil.parse_value(match.group(5), 'W')),
       TableFet.GATE_CHARGE: Range.exact(PartParserUtil.parse_value(match.group(8), 'C')),
     }),

  ]

  @classmethod
  def _make_table(cls) -> PartsTable:
    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      if row['Second Category'] != 'MOSFETs':
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

    return cls._jlc_table().map_new_columns(parse_row)

  @init_in_parent
  def __init__(self, *args, fallback_gate_charge: RangeLike = Range.from_tolerance(3000e-9, 0), **kwargs):
    super().__init__(*args, **kwargs)
    # allow the user to specify a gate charge
    self.fallback_gate_charge = self.ArgParameter(fallback_gate_charge)
    self.generator_param(self.fallback_gate_charge)

  def _table_postprocess(self, table: PartsTable) -> PartsTable:
    fallback_gate_charge = self.get(self.fallback_gate_charge)
    def process_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      if row[self.GATE_CHARGE] == Range.all():
        print("fallback gate charge for part", row[self.PART_NUMBER_COL])
        return {self.GATE_CHARGE: fallback_gate_charge}
      else:
        print(f"ok Qg part {row[self.PART_NUMBER_COL]} = {row[self.GATE_CHARGE]}")
        return None

    # must run before TableFet power calculations
    return super()._table_postprocess(table.map_new_columns(process_row, overwrite=True))


class JlcFet(PartsTableSelectorFootprint, JlcBaseFet, TableFet):
  pass


class JlcSwitchFet(PartsTableSelectorFootprint, JlcBaseFet, TableSwitchFet):
  pass


lambda: JlcFet, JlcSwitchFet()  # ensure class is instantiable (non-abstract)
