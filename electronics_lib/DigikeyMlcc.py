from typing import NamedTuple
from .DigikeyCapacitorTable import *


class MlccTable(DigikeyCapacitorTable):
  CAPACITANCE = PartsTableColumn(Range)
  NOMINAL_CAPACITANCE = PartsTableColumn(float)
  VOLTAGE_RATING = PartsTableColumn(Range)
  FOOTPRINT = PartsTableColumn(str)  # KiCad footprint name

  PACKAGE_FOOTPRINT_MAP = {
    '0603 (1608 Metric)': 'Capacitor_SMD:C_0603_1608Metric',
    '0805 (2012 Metric)': 'Capacitor_SMD:C_0805_2012Metric',
    '1206 (3216 Metric)': 'Capacitor_SMD:C_1206_3216Metric',
  }

  @classmethod
  def _generate_table(cls) -> PartsTable:
    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      new_cols: Dict[PartsTableColumn, Any] = {}
      try:
        footprint = cls.PACKAGE_FOOTPRINT_MAP[row['Package / Case']]
        nominal_capacitance = PartsTableUtil.parse_value(row['Capacitance'], 'F')

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
          PartsTableUtil.parse_tolerance(row['Tolerance'])
        )
        new_cols[cls.NOMINAL_CAPACITANCE] = nominal_capacitance
        new_cols[cls.VOLTAGE_RATING] = Range.zero_to_upper(
          PartsTableUtil.parse_value(row['Voltage - Rated'], 'V')
        )

        new_cols.update(cls._parse_digikey_common(row))

        return new_cols
      except (KeyError, PartsTableUtil.ParseError):
        return None

    raw_table = PartsTable.from_csv_files(PartsTableUtil.with_source_dir([
      'Digikey_MLCC_SamsungCl_1pF_E12.csv',
      'Digikey_MLCC_SamsungCl_1nF_E6.csv',
      'Digikey_MLCC_SamsungCl_1uF_E3.csv',
      'Digikey_MLCC_YageoCc_1pF_E12_1.csv',
      'Digikey_MLCC_YageoCc_1pF_E12_2.csv',
      'Digikey_MLCC_YageoCc_1nF_E6_1.csv',
      'Digikey_MLCC_YageoCc_1nF_E6_2.csv',
      'Digikey_MLCC_YageoCc_1uF_E3.csv',
    ], 'resources'), encoding='utf-8-sig')
    return raw_table.map_new_columns(parse_row).sort_by(
      lambda row: [row[cls.FOOTPRINT], row[cls.COST]]  # prefer smaller first
    )


class DigikeyMlcc(TableDeratingCapacitor):
  _TABLE = MlccTable

  @init_in_parent
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  def generate_parallel_capacitor(self, row: PartsTableRow,
                                  capacitance: Range, voltage: Range) -> None:
    super().generate_parallel_capacitor(row, capacitance, voltage)
    cap_model = DummyCapacitor(capacitance=row[self._TABLE.NOMINAL_CAPACITANCE],
                                  voltage=self.voltage,
                                  footprint=row[self._TABLE.FOOTPRINT],
                                  manufacturer=row[self._TABLE.MANUFACTURER], part_number=row[self._TABLE.PART_NUMBER],
                                  value=row[self._TABLE.DESCRIPTION])
    self.c = ElementDict[DummyCapacitor]()
    assert row[self.PARALLEL_COUNT] < 10, f"too many ({row[self.PARALLEL_COUNT]}) parallel capacitors to generate"
    for i in range(row[self.PARALLEL_COUNT]):
      self.c[i] = self.Block(cap_model)
      self.connect(self.c[i].pos, self.pos)
      self.connect(self.c[i].neg, self.neg)
