from typing import *
import re

from typing_extensions import override

from ..abstract_parts import *

from .JlcPart import DescriptionParser, JlcTableSelector


@non_library
class FetFallbackGateCharge(PartsTableSelector, BaseTableFet):
  """A TableFet that allows a fallback gate charge if not specified in the table.
  Unspecified entries must be Range.all(), which will be substituted with the fallback
  value in per-Block post-processing."""
  def __init__(self, *args: Any, fallback_gate_charge: RangeLike = Range.from_tolerance(3000e-9, 0), **kwargs: Any) -> None:
    super().__init__(*args, **kwargs)
    # allow the user to specify a gate charge
    self.fallback_gate_charge = self.ArgParameter(fallback_gate_charge)
    self.generator_param(self.fallback_gate_charge)

  @override
  def _table_postprocess(self, table: PartsTable) -> PartsTable:
    fallback_gate_charge = self.get(self.fallback_gate_charge)
    def process_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      if row[TableFet.GATE_CHARGE] == Range.all():
        return {TableFet.GATE_CHARGE: fallback_gate_charge}
      else:
        return {TableFet.GATE_CHARGE: row[TableFet.GATE_CHARGE]}

    # must run before TableFet power calculations
    return super()._table_postprocess(table.map_new_columns(process_row, overwrite=True))


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
       TableFet.GATE_CHARGE: Range.all(),  # unspecified
     }),
    # some are more detailed
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
       TableFet.GATE_CHARGE: Range.exact(PartParserUtil.parse_value(match.group(8), 'C'))
     }),
    # many still don't have the gate charge
    (re.compile("(\S+V) (\S+A) (\S+Ω)@(\S+V),\S+A (\S+W) (\S+V)@\S+A.* ([PN]) Channel.* MOSFETs.*"),
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
       TableFet.GATE_CHARGE: Range.all(),  # unspecified
     }),
  ]

  SUPPLEMENTAL_QC = {  # mfr part number to typ Qc @ max Vgs (if multiple specified)
    # QFN-8 devices
    'IRFH7440TRPBF': 92e-9,  # @ Vgs=10
    'BSC028N06NSATMA1': 37e-9,  # @ Vgs=0...10V
    'BSC057N08NS3G': 42e-9,  # @ Vgs=0...10V
    'BSC093N04LSG': 18e-9,  # @ Vgs=0...10V
    'BSC160N10NS3G': 19e-9,  # @ Vgs=0...10V
    'SIR876ADP-T1-GE3': 32.8e-9,  # @ Vgs=10
    'SI7336ADP-T1-E3': 36e-9,  # @ Vgs=4.5
    'SIR470DP-T1-GE3': 102e-9,  # @ Vgs=10

    # SOIC-8 devices, top 5 stock in the static parts table
    'AO4406A': 14e-9,  # @ Vgs=10
    'IRF8313TRPBF': 6.0e-9,  # @ Vgs=4.5
    'AO4435': 18e-9,  # @ Vgs=-10
    'AO4419': 19e-9,  # @ Vgs=4.5
    'AO4264E': 14.5e-9,  # @ Vgs=10
    'AO4485': 42e-9,  # @ Vgs=10
    'AO4459': 9.2e-9,  # @ Vgs=10
    'AO4468': 15e-9,  # @ Vgs=10
    'IRF7458TRPBF': 39e-9,  # @ Vgs=10
    'AO4407A': 30e-9,  # @ Vgs=10

    # DPAK devices
    'IRLR024NTRPBF': 15e-9,  # @ Vgs=5
    'AOD413A': 16.2e-9,  # @ Vgs=-10
    'IRLR8726TRPBF': 15e-9,  # @ Vgs=4.5
    'IRLR8726TRLPBF': 15e-9,  # @ Vgs=4.5
    'IRFR5410TRPBF': 58e-9,  # @ Vgs=-10
    'KIA50N03BD': 25e-9,  # @ Vgs=10
  }

  @classmethod
  @override
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

      if new_cols[TableFet.GATE_CHARGE] == Range.all() and row[cls.PART_NUMBER_COL] in cls.SUPPLEMENTAL_QC:
        new_cols[TableFet.GATE_CHARGE] = Range.exact(cls.SUPPLEMENTAL_QC[row[cls.PART_NUMBER_COL]])

      new_cols[cls.KICAD_FOOTPRINT] = footprint
      new_cols.update(cls._parse_jlcpcb_common(row))
      return new_cols

    return cls._jlc_table().map_new_columns(parse_row)


class JlcFet(PartsTableSelectorFootprint, JlcBaseFet, FetFallbackGateCharge, TableFet):
  pass


class JlcSwitchFet(PartsTableSelectorFootprint, JlcBaseFet, FetFallbackGateCharge, TableSwitchFet):
  pass


lambda: (JlcFet(), JlcSwitchFet())  # ensure class is instantiable (non-abstract)
