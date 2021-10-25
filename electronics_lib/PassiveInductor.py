import csv
import os
from functools import reduce

from electronics_abstract_parts import *
from .ProductTableUtils import *
from .PartsTable import *


class InductorTable:
  INDUCTANCE = PartsTableColumn(Range)  # actual inductance incl. tolerance
  FREQUENCY_RATING = PartsTableColumn(Range)  # tolerable frequencies
  CURRENT_RATING = PartsTableColumn(Range)  # tolerable current
  DC_RESISTANCE = PartsTableColumn(Range)  # actual DCR
  FOOTPRINT = PartsTableColumn(str)  # KiCad footprint name
  COST = PartsTableColumn(float)

  PACKAGE_FOOTPRINT_MAP = {  # from Digikey Package / Case to KiCad footprint
    '0603 (1608 Metric)': 'Inductor_SMD:L_0603_1608Metric',
    '0805 (2012 Metric)': 'Inductor_SMD:L_0805_2012Metric',
  }
  SERIES_FOOTPRINT_MAP = {  # from part series to KiCad footprint
    'SRR1015': 'Inductor_SMD:L_Bourns-SRR1005',
    'SRR1210': 'Inductor_SMD:L_Bourns_SRR1210A',
    'SRR1210A': 'Inductor_SMD:L_Bourns_SRR1210A',
    'SRR1260': 'Inductor_SMD:L_Bourns_SRR1260',
    'SRR1260A': 'Inductor_SMD:L_Bourns_SRR1260',
    # Kicad does not have stock 1008 footprint
  }
  # from manufacturer part number to KiCad footprint w/ substitution
  MPN_NR_FOOTPRINT_REGEX = RegexRemapper(r'^NR(\d\d).*$', 'Inductor_SMD:L_Taiyo-Yuden_NR-{0}xx')

  @classmethod
  def table(cls) -> PartsTable:
    if not hasattr(cls, '_table'):
      cls._table = cls._generate_table()
    return cls._table

  @classmethod
  def _generate_table(cls) -> PartsTable:
    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      new_rows: Dict[PartsTableColumn, Any] = {}
      try:
        # handle the footprint first since this is the most likely to filter
        footprint = (cls.PACKAGE_FOOTPRINT_MAP.get(row['Package / Case'], None) or
                     cls.SERIES_FOOTPRINT_MAP.get(row['Series'], None) or
                     cls.MPN_NR_FOOTPRINT_REGEX.apply(row['Manufacturer Part Number']))
        if footprint is None:
          raise KeyError
        new_rows[cls.FOOTPRINT] = footprint

        new_rows[cls.INDUCTANCE] = Range.from_tolerance(
          PartsTableUtil.parse_value(row['Inductance'], 'H'),
          PartsTableUtil.parse_tolerance(row['Tolerance'])
        )
        current = PartsTableUtil.parse_value(row['Current Rating (Amps)'], 'A')
        new_rows[cls.CURRENT_RATING] = Range(-current, current)
        new_rows[cls.FREQUENCY_RATING] = Range.zero_to_upper(
          PartsTableUtil.parse_value(row['Frequency - Self Resonant'], 'Hz')
        )
        new_rows[cls.DC_RESISTANCE] = Range.exact(
          PartsTableUtil.parse_value(row['DC Resistance (DCR)'], 'Ohm', None) or
          PartsTableUtil.parse_value(row['DC Resistance (DCR)'], 'Ohm Max')
        )

        new_rows[cls.COST] = float(row['Unit Price (USD)'])

        return new_rows
      except (KeyError, PartsTableUtil.ParseError):
        return None

    raw_table = PartsTable.from_csv_files(PartsTableUtil.with_source_dir([
      'Digikey_Inductors_TdkMlz.csv',
      'Digikey_Inductors_MurataDfe.csv',
      'Digikey_Inductors_TaiyoYudenNr.csv',
      'Digikey_Inductors_Shielded_BournsSRR_1005_1210_1260.csv',
    ], 'resources'), encoding='utf-8-sig')
    return raw_table.map_new_columns(parse_row)


class SmtInductor(Inductor, FootprintBlock, GeneratorBlock):
  @init_in_parent
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.current_rating = self.Parameter(RangeExpr())
    self.frequency_rating = self.Parameter(RangeExpr())
    self.part_spec = self.Parameter(StringExpr(""))
    self.footprint_spec = self.Parameter(StringExpr(""))
    self.generator(self.select_inductor, self.inductance, self.current, self.frequency,
                   self.part_spec, self.footprint_spec)

    # Output values
    self.selected_inductance = self.Parameter(RangeExpr())
    self.selected_current_rating = self.Parameter(RangeExpr())
    self.selected_frequency_rating = self.Parameter(RangeExpr())

  def select_inductor(self, inductance: Range, current: Range, frequency: Range,
                      part_spec: str, footprint_spec: str) -> None:
    compatible_parts = InductorTable.table().filter(lambda row: (
        (not part_spec or part_spec == row['Manufacturer Part Number']) and
        (not footprint_spec or footprint_spec == row[InductorTable.FOOTPRINT]) and
        row[InductorTable.INDUCTANCE].fuzzy_in(inductance) and
        row[InductorTable.DC_RESISTANCE].fuzzy_in(Range.zero_to_upper(1.0)) and  # TODO eliminate arbitrary DCR limit in favor of exposing max DCR to upper levels
        frequency.fuzzy_in(row[InductorTable.FREQUENCY_RATING])
    ))
    part = compatible_parts.sort_by(
      lambda row: row[InductorTable.FOOTPRINT]
    ).sort_by(
      lambda row: row[InductorTable.COST]
    ).first(f"no inductors in {inductance} H, {current} A, {frequency} Hz  {[row.value['Manufacturer Part Number'] for row in InductorTable.table().rows]}")

    self.assign(self.selected_inductance, part[InductorTable.INDUCTANCE])
    self.assign(self.selected_current_rating, part[InductorTable.CURRENT_RATING])
    self.assign(self.selected_frequency_rating, part[InductorTable.FREQUENCY_RATING])

    self.footprint(
      'L', part[InductorTable.FOOTPRINT],
      {
        '1': self.a,
        '2': self.b,
      },
      mfr=part['Manufacturer'], part=part['Manufacturer Part Number'],
      value=f"{part['Inductance']}, {part['Current Rating (Amps)']}",
      datasheet=part['Datasheets']
    )
