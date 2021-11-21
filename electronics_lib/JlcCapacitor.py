from .JlcTable import *
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
      #print(row[JlcTable.DESCRIPTION])
      new_cols: Dict[PartsTableColumn, Any] = {}
      try:
        # handle the footprint first since this is the most likely to filter
        footprint = cls.PACKAGE_FOOTPRINT_MAP[row['Package']]
        new_cols[cls.FOOTPRINT] = footprint

        extracted_values = JlcTable.parse(row[JlcTable.DESCRIPTION], CAPACITOR_MATCHES)

        #print(extracted_values)
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

        #Used in defining the footprint

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

  def select_capacitor(self, capacitance: Range, voltage: Range,
                       single_nominal_capacitance: Range,
                       part_spec: str, footprint_spec: str) -> None:
    # Pre-filter out by the static parameters
    # Note that we can't filter out capacitance before derating
    prefiltered_parts = self.filter_capacitor(voltage, single_nominal_capacitance, part_spec, footprint_spec)

    # If the min required capacitance is above the highest post-derating minimum capacitance, use the parts table.
    # An empty parts table handles the case where it's below the minimum or does not match within a series.
    derated_parts = self.derate_parts(voltage, prefiltered_parts)

    derated_max_min_capacitance = max(derated_parts.map(lambda row: row[self.DERATED_CAPACITANCE].lower))

    if capacitance.lower <= derated_max_min_capacitance:
      part = derated_parts.filter(lambda row: (
          row[self.DERATED_CAPACITANCE] in capacitance
      )).first(f"no single capacitor in {capacitance} F, {voltage} V")

      self.assign(self.selected_voltage_rating, part[self._TABLE.VOLTAGE_RATING])
      self.assign(self.selected_capacitance, part[self._TABLE.CAPACITANCE])
      self.assign(self.selected_derated_capacitance, part[self.DERATED_CAPACITANCE])
      self.assign(self.lcsc_part, part[JlcTable.JLC_PART_NUMBER])
      #TODO add a DISTRIBUTER PART NUMBER
      #Ex: JLC_PART_NUMBER

      self.footprint(
        'C', part[self._TABLE.FOOTPRINT],
        {
          '1': self.pos,
          '2': self.neg,
        },
        mfr=part[self._TABLE.MANUFACTURER], part=part[self._TABLE.PART_NUMBER],
        value=part[self._TABLE.DESCRIPTION],
        datasheet=part[self._TABLE.DATASHEETS]
      )
    else:  # Otherwise, generate multiple capacitors
      # Additionally annotate the table by total cost and count, sort by lower count then total cost
      def parallel_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
        new_cols: Dict[PartsTableColumn, Any] = {}
        count = math.ceil(capacitance.lower / row[self.DERATED_CAPACITANCE].lower)
        derated_parallel_capacitance = row[self.DERATED_CAPACITANCE] * count
        if not derated_parallel_capacitance.fuzzy_in(capacitance):  # not satisfying spec
          return None

        new_cols[self.PARALLEL_COUNT] = count
        new_cols[self.PARALLEL_DERATED_CAPACITANCE] = derated_parallel_capacitance
        new_cols[self.PARALLEL_CAPACITANCE] = row[self._TABLE.CAPACITANCE] * count
        new_cols[self.PARALLEL_COST] = row[self._TABLE.COST] * count

        return new_cols

      part = self.parallel_parts(derated_parts, capacitance, voltage)

      self.assign(self.selected_voltage_rating, part[self._TABLE.VOLTAGE_RATING])
      self.assign(self.selected_capacitance, part[self.PARALLEL_CAPACITANCE])
      self.assign(self.selected_derated_capacitance, part[self.PARALLEL_DERATED_CAPACITANCE])
      self.assign(self.lcsc_part, part[JlcTable.JLC_PART_NUMBER])
      #TODO add a DISTRIBUTER PART NUMBER
      #Ex: JLC_PART_NUMBER

      cap_model = DummyCapacitor(capacitance=part[self._TABLE.NOMINAL_CAPACITANCE],
                                 voltage=self.voltage,
                                 footprint=part[self._TABLE.FOOTPRINT],
                                 manufacturer=part[self._TABLE.MANUFACTURER], part_number=part[self._TABLE.PART_NUMBER],
                                 value=part[self._TABLE.DESCRIPTION])
      self.c = ElementDict[DummyCapacitor]()
      for i in range(part[self.PARALLEL_COUNT]):
        self.c[i] = self.Block(cap_model)
        self.connect(self.c[i].pos, self.pos)
        self.connect(self.c[i].neg, self.neg)

