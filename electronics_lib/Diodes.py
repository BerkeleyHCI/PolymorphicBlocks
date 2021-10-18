import csv
from functools import reduce
import os

from electronics_abstract_parts import *
from .ProductTableUtils import *


def generate_diode_table(TABLES: List[str]) -> ProductTable:
  tables = []
  for filename in TABLES:
    path = os.path.join(os.path.dirname(__file__), 'resources', filename)
    with open(path, newline='', encoding='utf-8') as csvfile:
      reader = csv.reader(csvfile)
      tables.append(ProductTable(next(reader), [row for row in reader]))
  table = reduce(lambda x, y: x+y, tables)

  return table \
    .derived_column('Vr,max',
                    RangeFromUpper(ParseValue(Column('Voltage - DC Reverse (Vr) (Max)'), 'V'), lower=0),
                    missing='discard') \
    .derived_column('I,max',
                    RangeFromUpper(ParseValue(Column('Current - Average Rectified (Io)'), 'A'), lower=0),
                    missing='discard') \
    .derived_column('Vf,max',
                    RangeFromUpper(ParseValue(Column('Voltage - Forward (Vf) (Max) @ If'), 'V'), lower=0),
                    missing='discard') \
    .derived_column('trr',
                    ChooseFirst(
                      RangeFromUpper(ParseValue(Column('Reverse Recovery Time (trr)'), 's'), lower=0),
                      MapDict(Column('Speed'), {
                        'Fast Recovery =< 500ns, > 200mA (Io)': (0, 500e-9)
                      }),
                      Lit((0, float('inf')))
                    ),
                    missing='discard') \
    .derived_column('footprint',
                    MapDict(Column('Package / Case'), {
                      'DO-214AC, SMA': 'Diode_SMD:D_SMA',
                      'DO-214AA, SMB': 'Diode_SMD:D_SMB',
                      'DO-214AB, SMC': 'Diode_SMD:D_SMC',
                      'SOD-123': 'Diode_SMD:D_SOD-123',
                      'SOD-123F': 'Diode_SMD:D_SOD-123',
                      'SOD-123FL': 'Diode_SMD:D_SOD-123',
                      'SC-76, SOD-323': 'Diode_SMD:D_SOD-323',
                      'SC-90, SOD-323F': 'Diode_SMD:D_SOD-323',  # TODO should the FL use the more compact FL pattern?
                      'TO-252-3, DPak (2 Leads + Tab), SC-63': 'Package_TO_SOT_SMD:TO-252-2',
                      'TO-263-3, D²Pak (2 Leads + Tab), TO-263AB': 'Package_TO_SOT_SMD:TO-263-2',
                    }), missing='discard')


class SmtDiode(Diode, FootprintBlock, GeneratorBlock):
  product_table = generate_diode_table([
    'Digikey_Diodes_DO214.csv',
    'Digikey_Diodes_DPak_DDPak.csv',
    'Digikey_Diodes_SOD123_SOD323.csv',
  ])

  @init_in_parent
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.reverse_voltage_rating = self.Parameter(RangeExpr())
    self.current_rating = self.Parameter(RangeExpr())
    self.selected_voltage_drop = self.Parameter(RangeExpr())
    self.selected_reverse_recovery_time = self.Parameter(RangeExpr())

    self.generator(self.select_part, self.reverse_voltage, self.current, self.voltage_drop,
                   self.reverse_recovery_time)
    # TODO: also support optional part and footprint name

  def select_part(self, reverse_voltage: Range, current: Range, voltage_drop: Range,
                  reverse_recovery_time: Range) -> None:
    # TODO maybe apply ideal diode law / other simple static model to better bound Vf?
    parts = self.product_table.filter(RangeContains(Column('Vr,max'), Lit(reverse_voltage))) \
      .filter(RangeContains(Column('I,max'), Lit(current))) \
      .filter(RangeContains(Lit(voltage_drop), Column('Vf,max'))) \
      .filter(RangeContains(Lit(reverse_recovery_time), Column('trr'))) \
      .sort(Column('Unit Price (USD)'))  # TODO actually make this into float
    part = parts.first(err=f"no diodes matching Vr,max={reverse_voltage}, I={current}, "
                           f"Vf={voltage_drop}, trr={reverse_recovery_time}")

    self.assign(self.reverse_voltage_rating, part['Vr,max'])
    self.assign(self.current_rating, part['I,max'])
    self.assign(self.selected_voltage_drop, part['Vf,max'])
    self.assign(self.selected_reverse_recovery_time, part['trr'])

    footprint_pinning = {
      'Diode_SMD:D_SMA': {
        '1': self.cathode,
        '2': self.anode,
      },
      'Diode_SMD:D_SMB': {
        '1': self.cathode,
        '2': self.anode,
      },
      'Diode_SMD:D_SMC': {
        '1': self.cathode,
        '2': self.anode,
      },
      'Diode_SMD:D_SOD-123': {
        '1': self.cathode,
        '2': self.anode,
      },
      'Diode_SMD:D_SOD-323': {
        '1': self.cathode,
        '2': self.anode,
      },
      'Package_TO_SOT_SMD:TO-252-2': {
        '1': self.anode,
        '2': self.cathode,
        '3': self.anode,
      },
      'Package_TO_SOT_SMD:TO-263-2': {
        '1': self.anode,  # TODO sometimes NC
        '2': self.cathode,
        '3': self.anode,
      },
    }

    self.footprint(
      'D', part['footprint'],
      footprint_pinning[part['footprint']],
      mfr=part['Manufacturer'], part=part['Manufacturer Part Number'],
      value=f"Vr={self.get(self.reverse_voltage)} V, I={self.get(self.current)} A, Vd={self.get(self.voltage_drop)} V",
      datasheet=part['Datasheets']
    )


def generate_zener_diode_table(TABLES: List[str]) -> ProductTable:
  tables = []
  for filename in TABLES:
    path = os.path.join(os.path.dirname(__file__), 'resources', filename)
    with open(path, newline='', encoding='utf-8') as csvfile:
      reader = csv.reader(csvfile)
      tables.append(ProductTable(next(reader), [row for row in reader]))
  table = reduce(lambda x, y: x+y, tables)

  return table \
    .derived_column('Vz',
                    RangeFromTolerance(ParseValue(Column('Voltage - Zener (Nom) (Vz)'), 'V'), Column('Tolerance')),
                    missing='discard') \
    .derived_column('Vf,max',
                    RangeFromUpper(ParseValue(Column('Voltage - Forward (Vf) (Max) @ If'), 'V'), lower=0),
                    missing='discard') \
    .derived_column('P,max',
                    RangeFromUpper(ParseValue(Column('Power - Max'), 'W'), lower=0),
                    missing='discard') \
    .derived_column('footprint',
                    MapDict(Column('Package / Case'), {
                      'DO-214AC, SMA': 'Diode_SMD:D_SMA',
                      'DO-214AA, SMB': 'Diode_SMD:D_SMB',
                      'DO-214AB, SMC': 'Diode_SMD:D_SMC',
                      'SOD-123': 'Diode_SMD:D_SOD-123',
                      'SOD-123F': 'Diode_SMD:D_SOD-123',
                      'SOD-123FL': 'Diode_SMD:D_SOD-123',
                      'SC-76, SOD-323': 'Diode_SMD:D_SOD-323',
                      'SC-90, SOD-323F': 'Diode_SMD:D_SOD-323',  # TODO should the FL use the more compact FL pattern?
                      'TO-252-3, DPak (2 Leads + Tab), SC-63': 'Package_TO_SOT_SMD:TO-252-2',
                      'TO-263-3, D²Pak (2 Leads + Tab), TO-263AB': 'Package_TO_SOT_SMD:TO-263-2',
                    }), missing='discard')


class SmtZenerDiode(ZenerDiode, FootprintBlock, GeneratorBlock):
  product_table = generate_zener_diode_table([
    'Digikey_ZenerDiodes_DO214.csv',
    'Digikey_ZenerDiodes_SOD123_SOD323.csv',
  ])

  @init_in_parent
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.power_rating = self.Parameter(RangeExpr())

    self.generator(self.select_part, self.zener_voltage, self.forward_voltage_drop)
    # TODO: also support optional part and footprint name

    self.selected_zener_voltage = self.Parameter(RangeExpr())
    self.selected_forward_voltage_drop = self.Parameter(RangeExpr())

  def select_part(self, zener_voltage: Range, forward_voltage_drop: Range) -> None:
    # TODO maybe apply ideal diode law / other simple static model to better bound Vf?
    parts = self.product_table.filter(RangeContains(Column('Vz'), Lit(zener_voltage))) \
      .filter(RangeContains(Lit(forward_voltage_drop), Column('Vf,max'))) \
      .sort(Column('Unit Price (USD)'))  # TODO actually make this into float
    part = parts.first(err=f"no zener diodes matching Vz={zener_voltage}")

    self.assign(self.selected_zener_voltage, part['Vz'])
    self.assign(self.selected_forward_voltage_drop, part['Vf,max'])
    self.assign(self.power_rating, part['P,max'])

    footprint_pinning = {
      'Diode_SMD:D_SMA': {
        '1': self.cathode,
        '2': self.anode,
      },
      'Diode_SMD:D_SMB': {
        '1': self.cathode,
        '2': self.anode,
      },
      'Diode_SMD:D_SMC': {
        '1': self.cathode,
        '2': self.anode,
      },
      'Diode_SMD:D_SOD-123': {
        '1': self.cathode,
        '2': self.anode,
      },
      'Diode_SMD:D_SOD-323': {
        '1': self.cathode,
        '2': self.anode,
      },
    }

    self.footprint(
      'D', part['footprint'],
      footprint_pinning[part['footprint']],
      mfr=part['Manufacturer'], part=part['Manufacturer Part Number'],
      value=f"Vz={self.get(self.zener_voltage)} V",
      datasheet=part['Datasheets']
    )
