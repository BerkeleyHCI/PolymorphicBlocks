from typing import Optional, Any, Dict
import re

from ..electronics_abstract_parts import *
from .JlcPart import JlcPart, JlcTableSelector


class JlcCapacitor(TableDeratingCapacitor, CeramicCapacitor, SmdStandardPackageSelector, JlcTableSelector):
  PACKAGE_FOOTPRINT_MAP = {
    # 0201 not in parts table, C_0201_0603Metric

    '0402': 'Capacitor_SMD:C_0402_1005Metric',
    '0603': 'Capacitor_SMD:C_0603_1608Metric',
    '0805': 'Capacitor_SMD:C_0805_2012Metric',
    '1206': 'Capacitor_SMD:C_1206_3216Metric',
    '1812': 'Capacitor_SMD:C_1812_4532Metric',

    'C0402': 'Capacitor_SMD:C_0402_1005Metric',
    'C0603': 'Capacitor_SMD:C_0603_1608Metric',
    'C0805': 'Capacitor_SMD:C_0805_2012Metric',
    'C1206': 'Capacitor_SMD:C_1206_3216Metric',
    'C1812': 'Capacitor_SMD:C_1812_4532Metric',
  }
  DERATE_VOLTCO_MAP = {  # in terms of %capacitance / V over 3.6
    'Capacitor_SMD:C_0402_1005Metric': float('inf'),  # not supported, should not generate below 1uF
    'Capacitor_SMD:C_0603_1608Metric': float('inf'),  # not supported, should not generate below 1uF
    'Capacitor_SMD:C_0805_2012Metric': 0.08,
    'Capacitor_SMD:C_1206_3216Metric': 0.04,
    'Capacitor_SMD:C_1812_4532Metric': 0.04,  # arbitrary, copy from 1206
  }

  @init_in_parent
  def __init__(self, *args, capacitance_minimum_size: BoolLike = True, **kwargs):
    super().__init__(*args, **kwargs)
    self.capacitance_minimum_size = self.ArgParameter(capacitance_minimum_size)
    self.generator_param(self.capacitance_minimum_size)

  @classmethod
  def _make_table(cls) -> PartsTable:
    CAPACITOR_MATCHES = {
      'nominal_capacitance': re.compile("(^|\s)([^±]\S+F)($|\s)"),
      'tolerance': re.compile("(^|\s)(±\S+[%F])($|\s)"),
      'voltage': re.compile("(^|\s)(\d\S*V)($|\s)"),  # make sure not to catch 'Y5V'
      'tempco': re.compile("(^|\s)([CXYZ]\d[GPRSTUV])($|\s)"),
    }

    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      if row['Second Category'] != 'Multilayer Ceramic Capacitors MLCC - SMD/SMT':
        return None

      new_cols: Dict[PartsTableColumn, Any] = {}
      try:
        # handle the footprint first since this is the most likely to filter
        footprint = cls.PACKAGE_FOOTPRINT_MAP[row[cls._PACKAGE_HEADER]]
        extracted_values = cls.parse(row[cls.DESCRIPTION_COL], CAPACITOR_MATCHES)

        tempco = extracted_values['tempco'][1]
        if tempco[0] not in ('X', 'C') or tempco[2] not in ('R', 'S', 'G'):
          return None

        nominal_capacitance = PartParserUtil.parse_value(extracted_values['nominal_capacitance'][1], 'F')

        new_cols[cls.KICAD_FOOTPRINT] = footprint
        new_cols[cls.CAPACITANCE] = PartParserUtil.parse_abs_tolerance(extracted_values['tolerance'][1],
                                                                       nominal_capacitance, 'F')
        new_cols[cls.NOMINAL_CAPACITANCE] = nominal_capacitance

        new_cols[cls.VOLTAGE_RATING] = Range.from_abs_tolerance(  # voltage rating for ceramic caps is bidirectional
          0, PartParserUtil.parse_value(extracted_values['voltage'][1], 'V'))
        new_cols[cls.VOLTCO] = cls.DERATE_VOLTCO_MAP[footprint]

        new_cols.update(cls._parse_jlcpcb_common(row))

        return new_cols
      except (KeyError, PartParserUtil.ParseError):
        return None

    return cls._jlc_table().map_new_columns(parse_row)

  def _table_postprocess(self, table: PartsTable) -> PartsTable:
    def filter_minimum_size(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      # enforce minimum packages, note the cutoffs are exclusive
      nominal_capacitance = row[self.NOMINAL_CAPACITANCE]
      footprint = row[self.KICAD_FOOTPRINT]
      if nominal_capacitance > 10e-6 and footprint not in [
          'Capacitor_SMD:C_1206_3216Metric',
        ]:
        return None
      elif nominal_capacitance > 1e-6 and footprint not in [
        'Capacitor_SMD:C_0805_2012Metric',
        'Capacitor_SMD:C_1206_3216Metric',
      ]:
        return None
      return {}
    table = super()._table_postprocess(table)
    if self.get(self.capacitance_minimum_size):
      table = table.map_new_columns(filter_minimum_size)
    return table

  @classmethod
  def _row_sort_by(cls, row: PartsTableRow) -> Any:
    return [row[cls.PARALLEL_COUNT], row[cls.BASIC_PART_HEADER], row[cls.KICAD_FOOTPRINT], row[cls.COST]]

  def _make_parallel_footprints(self, row: PartsTableRow) -> None:
    cap_model = JlcDummyCapacitor(set_lcsc_part=row[self.LCSC_PART_HEADER],
                                  set_basic_part=row[self.BASIC_PART_HEADER] == self.BASIC_PART_VALUE,
                                  footprint=row[self.KICAD_FOOTPRINT],
                                  manufacturer=row[self.MANUFACTURER_COL], part_number=row[self.PART_NUMBER_COL],
                                  value=row[self.DESCRIPTION_COL],
                                  capacitance=row[self.NOMINAL_CAPACITANCE],
                                  voltage=self.voltage)
    self.c = ElementDict[JlcDummyCapacitor]()
    for i in range(row[self.PARALLEL_COUNT]):
      self.c[i] = self.Block(cap_model)
      self.connect(self.c[i].pos, self.pos)
      self.connect(self.c[i].neg, self.neg)

    self.assign(self.lcsc_part, row[self.LCSC_PART_HEADER])
    self.assign(self.actual_basic_part, row[self.BASIC_PART_HEADER] == self.BASIC_PART_VALUE)


class JlcDummyCapacitor(DummyCapacitorFootprint, JlcPart):
  """Dummy capacitor that additionally has JLC part fields
  """
  @init_in_parent
  def __init__(self, set_lcsc_part: StringLike = "", set_basic_part: BoolLike = False,
               footprint: StringLike = "", manufacturer: StringLike = "",
               part_number: StringLike = "", value: StringLike = "", *args, **kwargs) -> None:
    super().__init__(footprint, manufacturer, part_number, value, *args, **kwargs)

    self.assign(self.lcsc_part, set_lcsc_part)
    self.assign(self.actual_basic_part, set_basic_part)
