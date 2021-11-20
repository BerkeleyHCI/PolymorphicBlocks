from .JLcTable import *
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

          #Used in defining the footprint
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
  _TABLE = JLcCapacitorTable


