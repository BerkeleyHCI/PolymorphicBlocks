from typing import Optional, Dict, Any
from electronics_abstract_parts import *
from electronics_lib.DigikeyTable import DigikeyTablePart


class DigikeyMlcc(TableDeratingCapacitorNew, DigikeyTablePart, FootprintBlock):
  PACKAGE_FOOTPRINT_MAP = {
    '0603 (1608 Metric)': 'Capacitor_SMD:C_0603_1608Metric',
    '0805 (2012 Metric)': 'Capacitor_SMD:C_0805_2012Metric',
    '1206 (3216 Metric)': 'Capacitor_SMD:C_1206_3216Metric',
  }
  DERATE_VOLTCO_MAP = {  # in terms of %capacitance / V over 3.6
    'Capacitor_SMD:C_0603_1608Metric': float('inf'),  # not supported, should not generate below 1uF
    'Capacitor_SMD:C_0805_2012Metric': 0.08,
    'Capacitor_SMD:C_1206_3216Metric': 0.04,
  }

  @classmethod
  def _make_table(cls) -> PartsTable:
    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      new_cols: Dict[PartsTableColumn, Any] = {}
      try:
        footprint = cls.PACKAGE_FOOTPRINT_MAP[row[cls._PACKAGE_HEADER]]
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

        new_cols[cls.KICAD_FOOTPRINT] = footprint
        new_cols[cls.CAPACITANCE] = Range.from_tolerance(
          nominal_capacitance,
          PartsTableUtil.parse_tolerance(row['Tolerance'])
        )
        new_cols[cls.NOMINAL_CAPACITANCE] = nominal_capacitance
        new_cols[cls.VOLTAGE_RATING] = Range.zero_to_upper(
          PartsTableUtil.parse_value(row['Voltage - Rated'], 'V')
        )
        new_cols[cls.VOLTCO] = cls.DERATE_VOLTCO_MAP[footprint]

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
      lambda row: [row[cls.KICAD_FOOTPRINT], row[cls.COST]]  # prefer smaller first
    )

  def _make_footprint(self, part: PartsTableRow) -> None:
    self.footprint(
      'R', part[self.KICAD_FOOTPRINT],
      {
        '1': self.pos,
        '2': self.neg,
      },
      mfr=part[self.MANUFACTURER_HEADER], part=part[self.PART_NUMBER],
      value=part[self.DESCRIPTION_HEADER],
      datasheet=part[self.DATASHEET_HEADER]
    )

  def _make_parallel_footprints(self, part: PartsTableRow) -> None:
    assert part[self.PARALLEL_COUNT] < 10, f"too many parallel capacitors ({part[self.PARALLEL_COUNT]})"
    cap_model = DummyCapacitorFootprint(
      capacitance=part[self.NOMINAL_CAPACITANCE], voltage=self.voltage,
      footprint=part[self.KICAD_FOOTPRINT],
      manufacturer=part[self.MANUFACTURER_HEADER], part_number=part[self.PART_NUMBER],
      value=part[self.DESCRIPTION_HEADER])
    self.c = ElementDict[DummyCapacitorFootprint]()
    for i in range(part[self.PARALLEL_COUNT]):
      self.c[i] = self.Block(cap_model)
      self.connect(self.c[i].pos, self.pos)
      self.connect(self.c[i].neg, self.neg)
