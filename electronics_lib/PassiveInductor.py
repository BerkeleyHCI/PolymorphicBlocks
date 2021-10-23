import csv
import os
from functools import reduce

from electronics_abstract_parts import *
from .ProductTableUtils import *
from .PartsTable import *


class DigikeyInductorTable:
  @staticmethod
  def generate_table(csvs: List[str]) -> PartsTable:
    table = PartsTable.from_csv_files(csvs)
    return table


def generate_inductor_table(TABLES: List[str]) -> ProductTable:
  tables = []
  for filename in TABLES:
    path = os.path.join(os.path.dirname(__file__), 'resources', filename)
    with open(path, newline='', encoding='utf-8') as csvfile:
      reader = csv.reader(csvfile)
      tables.append(ProductTable(next(reader), [row for row in reader]))
  table = reduce(lambda x, y: x+y, tables)

  # TODO: take min of current rating and saturation current
  # TODO maybe 10x the frequency to be safe
  return table.derived_column('inductance',
                               RangeFromTolerance(ParseValue(Column('Inductance'), 'H'), Column('Tolerance'))) \
    .derived_column('frequency',
                    RangeFromUpper(ParseValue(Column('Frequency - Self Resonant'), 'Hz')),
                    missing='discard') \
    .derived_column('current',
                    RangeFromUpper(ParseValue(Column('Current Rating (Amps)'), 'A'))) \
    .derived_column('dc_resistance',
                    RangeFromUpper(ParseValue(Column('DC Resistance (DCR)'), 'Ohm')),
                    missing='discard') \
    .derived_column('footprint',
                    ChooseFirst(
                      MapDict(Column('Package / Case'), {
                        '0603 (1608 Metric)': 'Inductor_SMD:L_0603_1608Metric',
                        '0805 (2012 Metric)': 'Inductor_SMD:L_0805_2012Metric',
                        # Kicad does not have stock 1008 footprint
                      }),
                      MapDict(Column('Series'), {
                        'SRR1015': 'Inductor_SMD:L_Bourns-SRR1005',
                        'SRR1210': 'Inductor_SMD:L_Bourns_SRR1210A',
                        'SRR1210A': 'Inductor_SMD:L_Bourns_SRR1210A',
                        'SRR1260': 'Inductor_SMD:L_Bourns_SRR1260',
                        'SRR1260A': 'Inductor_SMD:L_Bourns_SRR1260',
                        # Kicad does not have stock 1008 footprint
                      }),
                      # parse of the form NR3015T100M
                      FormatRegex(Column('Manufacturer Part Number'), 'NR(\d\d).*', 'Inductor_SMD:L_Taiyo-Yuden_NR-{0}xx'),
                    ), missing='discard')


class SmtInductor(Inductor, FootprintBlock, GeneratorBlock):
  product_table = generate_inductor_table([
    'Digikey_Inductors_TdkMlz.csv',
    'Digikey_Inductors_MurataDfe.csv',
    'Digikey_Inductors_TaiyoYudenNr.csv',
    'Digikey_Inductors_Shielded_BournsSRR_1005_1210_1260.csv',
  ])

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
    # TODO eliminate arbitrary DCR limit in favor of exposing max DCR to upper levels
    parts = self.product_table.filter(RangeContains(Lit(inductance), Column('inductance'))) \
        .filter(RangeContains(Lit((-float('inf'), 1)), Column('dc_resistance'))) \
        .filter(RangeContains(Column('frequency'), Lit(frequency))) \
        .filter(RangeContains(Column('current'), Lit(current))) \
        .filter(ContainsString(Column('Manufacturer Part Number'), part_spec or None)) \
        .filter(ContainsString(Column('footprint'), footprint_spec or None)) \
        .sort(Column('footprint'))  \
        .sort(Column('Unit Price (USD)'))

    part = parts.first(err=f"no inductors in {inductance} H, {current} A, {frequency} Hz")

    self.assign(self.selected_inductance, part['inductance'])
    self.assign(self.selected_current_rating, part['current'])
    self.assign(self.selected_frequency_rating, part['frequency'])

    self.footprint(
      'L', part['footprint'],
      {
        '1': self.a,
        '2': self.b,
      },
      mfr=part['Manufacturer'], part=part['Manufacturer Part Number'],
      value=f"{part['Inductance']}, {part['Current Rating (Amps)']}",
      datasheet=part['Datasheets']
    )
