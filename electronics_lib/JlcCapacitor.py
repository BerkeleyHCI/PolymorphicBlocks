from .PassiveCapacitor import *
from .JlcFootprint import JlcFootprint


class JlcCapacitorTable(JlcTable):
  CAPACITANCE = PartsTableColumn(Range)
  NOMINAL_CAPACITANCE = PartsTableColumn(float)
  VOLTAGE_RATING = PartsTableColumn(Range)
  FOOTPRINT = PartsTableColumn(str)

  PACKAGE_FOOTPRINT_MAP = {
    '0603': 'Capacitor_SMD:C_0603_1608Metric',
    '0805': 'Capacitor_SMD:C_0805_2012Metric',
    '1206': 'Capacitor_SMD:C_1206_3216Metric',
  }

  @classmethod
  def _generate_table(cls) -> PartsTable:
    CAPACITOR_MATCHES = {
        'nominal_capacitance': "(^|\s)(\d+(?:\.\d*)?[GMkmunp]?F)($|\s)",
        'tolerance': "(^|\s)(([\u00B1]\d+(?:\.\d*)?%)|([\u00B1]\d+(?:\.\d*)?[GMkmunp]?F))($|\s)",
        'voltage': "(^|\s)(\d+(?:\.\d*)?V)($|\s)",
    }

    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      if (row['Library Type'] != 'Basic' or row['First Category'] != 'Capacitors'):
        return None

      new_cols: Dict[PartsTableColumn, Any] = {}
      try:
        # handle the footprint first since this is the most likely to filter
        footprint = cls.PACKAGE_FOOTPRINT_MAP[row['Package']]

        extracted_values = JlcTable.parse(row[JlcTable.DESCRIPTION], CAPACITOR_MATCHES)

        nominal_capacitance = PartsTableUtil.parse_value(extracted_values['nominal_capacitance'][1], 'F')

        # enforce minimum packages, note the cutoffs are exclusive
        if nominal_capacitance > 10e-6 and footprint not in [
          'Capacitor_SMD:C_1206_3216Metric',
        ]:
          return None
        elif nominal_capacitance > 1e-6 and footprint not in [
          'Capacitor_SMD:C_0805_2012Metric',
          'Capacitor_SMD:C_1206_3216Metric',
        ]:
          return None

        new_cols[cls.FOOTPRINT] = footprint
        new_cols[cls.CAPACITANCE] = Range.from_tolerance(
          nominal_capacitance,
          PartsTableUtil.parse_tolerance(extracted_values['tolerance'][1])
        )
        new_cols[cls.NOMINAL_CAPACITANCE] = nominal_capacitance
        new_cols[cls.VOLTAGE_RATING] = Range.zero_to_upper(
          PartsTableUtil.parse_value(extracted_values['voltage'][1], 'V')
        )

        new_cols.update(cls._parse_jlcpcb_common(row))

        return new_cols
      except (KeyError, PartsTableUtil.ParseError):
        return None

    raw_table = PartsTable.from_csv_files(PartsTableUtil.with_source_dir([
      'JLCPCB_SMT_Parts_Library.csv'
    ], 'resources'), encoding='gb2312')
    return raw_table.map_new_columns(parse_row).sort_by(
      lambda row: [row[cls.FOOTPRINT], row[cls.COST]]
    )


class JlcCapacitor(TableDeratingCapacitor, JlcFootprint):
  _TABLE = JlcCapacitorTable

  @init_in_parent
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  def generate_single_capacitor(self, row: PartsTableRow,
                                capacitance: Range, voltage: Range) -> None:
    super().generate_single_capacitor(row, capacitance, voltage)
    self.assign(self.lcsc_part, row[JlcTable.JLC_PART_NUMBER])


  def generate_parallel_capacitor(self, row: PartsTableRow,
                                  capacitance: Range, voltage: Range) -> None:
    super().generate_parallel_capacitor(row, capacitance, voltage)
    cap_model = JlcDummyCapacitor(capacitance=row[self._TABLE.NOMINAL_CAPACITANCE],
                                  voltage=self.voltage,
                                  lcsc_part=row[JlcTable.JLC_PART_NUMBER],
                                  footprint=row[self._TABLE.FOOTPRINT],
                                  manufacturer=row[self._TABLE.MANUFACTURER], part_number=row[self._TABLE.PART_NUMBER],
                                  value=row[self._TABLE.DESCRIPTION])
    self.c = ElementDict[JlcDummyCapacitor]()
    for i in range(row[self.PARALLEL_COUNT]):
      self.c[i] = self.Block(cap_model)
      self.connect(self.c[i].pos, self.pos)
      self.connect(self.c[i].neg, self.neg)
