from typing import Optional, Any, Dict
import re

from typing_extensions import override

from ..abstract_parts import *
from .JlcPart import JlcPart, JlcTableSelector


class JlcCapacitor(JlcTableSelector, PartsTableSelectorFootprint, TableDeratingCapacitor, CeramicCapacitor):
  PACKAGE_FOOTPRINT_MAP = {
    '0201': 'Capacitor_SMD:C_0201_0603Metric',
    '0402': 'Capacitor_SMD:C_0402_1005Metric',
    '0603': 'Capacitor_SMD:C_0603_1608Metric',
    '0805': 'Capacitor_SMD:C_0805_2012Metric',
    '1206': 'Capacitor_SMD:C_1206_3216Metric',
    '1210': 'Capacitor_SMD:C_1210_3225Metric',
    '1812': 'Capacitor_SMD:C_1812_4532Metric',

    'C0402': 'Capacitor_SMD:C_0402_1005Metric',
    'C0603': 'Capacitor_SMD:C_0603_1608Metric',
    'C0805': 'Capacitor_SMD:C_0805_2012Metric',
    'C1206': 'Capacitor_SMD:C_1206_3216Metric',
    'C1210': 'Capacitor_SMD:C_1210_3225Metric',
    'C1812': 'Capacitor_SMD:C_1812_4532Metric',
  }
  DERATE_VOLTCO_MAP = {  # in terms of %capacitance / V over 3.6
    'Capacitor_SMD:C_0201_0603Metric': float('inf'),  # not supported, should not generate below 1uF
    'Capacitor_SMD:C_0402_1005Metric': float('inf'),  # not supported, should not generate below 1uF
    'Capacitor_SMD:C_0603_1608Metric': float('inf'),  # not supported, should not generate below 1uF
    'Capacitor_SMD:C_0805_2012Metric': 0.08,
    'Capacitor_SMD:C_1206_3216Metric': 0.04,
    'Capacitor_SMD:C_1210_3225Metric': 0.04,
    'Capacitor_SMD:C_1812_4532Metric': 0.04,  # arbitrary, copy from 1206
  }

  def __init__(self, *args: Any, capacitance_minimum_size: BoolLike = True, **kwargs: Any) -> None:
    super().__init__(*args, **kwargs)
    self.capacitance_minimum_size = self.ArgParameter(capacitance_minimum_size)
    self.generator_param(self.capacitance_minimum_size)

  @classmethod
  @override
  def _make_table(cls) -> PartsTable:
    CAPACITOR_MATCHES = {
      'nominal_capacitance': re.compile(r"(^|\s)([^±]\S+F)($|\s)"),
      'tolerance': re.compile(r"(^|\s)(±\S+[%F])($|\s)"),
      'voltage': re.compile(r"(^|\s)(\d\S*V)($|\s)"),  # make sure not to catch 'Y5V'
      'tempco': re.compile(r"(^|\s)([CXYZ]\d[GPRSTUV])($|\s)"),
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

  @override
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
  @override
  def _row_sort_by(cls, row: PartsTableRow) -> Any:
    return [row[cls.PARALLEL_COUNT], super(JlcCapacitor, cls)._row_sort_by(row)]

  @override
  def _row_generate(self, row: PartsTableRow) -> None:
    # see comment in TableCapacitor._row_generate for why this needs to be here
    if row[self.PARALLEL_COUNT] == 1:
      super()._row_generate(row)  # creates the footprint
    else:
      TableCapacitor._row_generate(self, row)  # skips creating the footprint in PartsTableSelectorFootprint
      self.assign(self.actual_basic_part, True)  # dummy value
      self._make_parallel_footprints(row)

  @override
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


class JlcDummyCapacitor(JlcPart, DummyCapacitorFootprint):
  """Dummy capacitor that additionally has JLC part fields
  """
  def __init__(self, set_lcsc_part: StringLike = "", set_basic_part: BoolLike = False,
               footprint: StringLike = "", manufacturer: StringLike = "",
               part_number: StringLike = "", value: StringLike = "", *args: Any, **kwargs: Any) -> None:
    super().__init__(footprint=footprint, manufacturer=manufacturer, part_number=part_number,
                     value=value, *args, **kwargs)

    self.assign(self.lcsc_part, set_lcsc_part)
    self.assign(self.actual_basic_part, set_basic_part)


lambda: JlcCapacitor()  # ensure class is instantiable (non-abstract)
