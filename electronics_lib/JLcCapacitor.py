from typing import Optional
from electronics_abstract_parts import *
from .JLcTable import *
from .TableDeratingCapacitor import TableDeratingCapacitor
from .PassiveCapacitor import *

class JLcCapacitorTable(JLcTable):
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
        'nominal_capacitance': "\s?(\d+(?:\.\d*)?[GMkmunp]?F)\s",
        'tolerance': "\s?([\u00B1]\d+(?:\.\d*)?%)\s",
        'voltage': "\s?(\d+(?:\.\d*)?V)\s",
    }

    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      if (row['Library Type'] == 'Basic' and row['First Category'] == 'Capacitors'):
        new_cols: Dict[PartsTableColumn, Any] = {}
        try:
          # handle the footprint first since this is the most likely to filter
          footprint = cls.PACKAGE_FOOTPRINT_MAP[row['Package']]
          new_cols[cls.FOOTPRINT] = footprint

          extracted_values = JLcTable.parse(row[JLcTable.DESCRIPTION], CAPACITOR_MATCHES)

          nominal_capacitance = PartsTableUtil.parse_value(extracted_values['nominal_capacitance'], 'F')

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

          new_cols['Capacitance'] = extracted_values['nominal_capacitance']
          new_cols['Voltage - Rated'] = extracted_values['voltage']

          new_cols[cls.FOOTPRINT] = footprint
          new_cols[cls.CAPACITANCE] = Range.from_tolerance(
            nominal_capacitance,
            PartsTableUtil.parse_tolerance(extracted_values['tolerance'])
          )
          new_cols[cls.NOMINAL_CAPACITANCE] = nominal_capacitance
          new_cols[cls.VOLTAGE_RATING] = Range.zero_to_upper(
            PartsTableUtil.parse_value(extracted_values['voltage'], 'V')
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

class JLcCapacitor(TableDeratingCapacitor, FootprintBlock, GeneratorBlock):

    @init_in_parent
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.part_spec = self.Parameter(StringExpr(""))
        self.footprint_spec = self.Parameter(StringExpr(""))

        # Default that can be overridden
        self.single_nominal_capacitance = self.Parameter(RangeExpr((0, 22)*uFarad))  # maximum capacitance in a single part

        self.generator(self.select_capacitor, self.capacitance, self.voltage, self.single_nominal_capacitance,
                       self.part_spec, self.footprint_spec)

        # Output values
        self.selected_capacitance = self.Parameter(RangeExpr())
        self.selected_derated_capacitance = self.Parameter(RangeExpr())
        self.selected_voltage_rating = self.Parameter(RangeExpr())

    def select_capacitor(self, capacitance: Range, voltage: Range,
                         single_nominal_capacitance: Range,
                         part_spec: str, footprint_spec: str) -> None:
        # Pre-filter out by the static parameters
        # Note that we can't filter out capacitance before derating
        prefiltered_parts = JLcCapacitorTable.table().filter(lambda row: (
            (not part_spec or part_spec == row[JLcCapacitorTable.PART_NUMBER]) and
            (not footprint_spec or footprint_spec == row[JLcCapacitorTable.FOOTPRINT]) and
            voltage.fuzzy_in(row[JLcCapacitorTable.VOLTAGE_RATING]) and
            Range.exact(row[JLcCapacitorTable.NOMINAL_CAPACITANCE]).fuzzy_in(single_nominal_capacitance)
        ))

        derated_parts = prefiltered_parts.map_new_columns(
            super().derate_row(JLcCapacitorTable)
        )
        derated_max_min_capacitance = max(derated_parts.map(lambda row: row[self.DERATED_CAPACITANCE].lower))

        if capacitance.lower <= derated_max_min_capacitance:
            part = derated_parts.filter(lambda row: (
                    row[self.DERATED_CAPACITANCE] in capacitance
            )).first(f"no single capacitor in {capacitance} F, {voltage} V")

            self.assign(self.selected_voltage_rating, part[JLcCapacitorTable.VOLTAGE_RATING])
            self.assign(self.selected_capacitance, part[JLcCapacitorTable.CAPACITANCE])
            self.assign(self.selected_derated_capacitance, part[self.DERATED_CAPACITANCE])

            self.footprint(
                'C', part[MlccTable.FOOTPRINT],
                {
                    '1': self.pos,
                    '2': self.neg,
                },
                mfr=part[JLcCapacitorTable.MANUFACTURER], part=part[JLcCapacitorTable.PART_NUMBER],
                value=f"{part[JLcCapacitorTable.DESCRIPTION]}",
                datasheet=part[JLcCapacitorTable.DATASHEETS]
            )
        else:
            part = derated_parts.map_new_columns(
                super().parallel_row(JLcCapacitorTable)
            ).sort_by(lambda row:
                (row[self.PARALLEL_COUNT], row[self.PARALLEL_COST])
            ).first(f"no parallel capacitor in {capacitance} F, {voltage} V")

            self.assign(self.selected_voltage_rating, part[JLcCapacitorTable.VOLTAGE_RATING])
            self.assign(self.selected_capacitance, part[self.PARALLEL_CAPACITANCE])
            self.assign(self.selected_derated_capacitance, part[self.PARALLEL_DERATED_CAPACITANCE])

            cap_model = DummyCapacitor(capacitance=part[JLcCapacitorTable.NOMINAL_CAPACITANCE],
                                       voltage=self.voltage,
                                       footprint=part[JLcCapacitorTable.FOOTPRINT],
                                       manufacturer=part[JLcCapacitorTable.MANUFACTURER], part_number=part[JLcCapacitorTable.PART_NUMBER],
                                       value=f"{part['Capacitance']}, {part['Voltage - Rated']}")
            self.c = ElementDict[DummyCapacitor]()
            for i in range(part[self.PARALLEL_COUNT]):
                self.c[i] = self.Block(cap_model)
                self.connect(self.c[i].pos, self.pos)
                self.connect(self.c[i].neg, self.neg)
