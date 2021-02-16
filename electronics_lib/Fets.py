import csv
from functools import reduce
import os

from electronics_abstract_parts import *
from .ProductTableUtils import *


def generate_fet_table(TABLES: List[str]) -> ProductTable:
  tables = []
  for filename in TABLES:
    path = os.path.join(os.path.dirname(__file__), 'resources', filename)
    with open(path, newline='', encoding='utf-8') as csvfile:
      reader = csv.reader(csvfile)
      tables.append(ProductTable(next(reader), [row for row in reader]))
  table = reduce(lambda x, y: x+y, tables)

  # TODO Current Drain: Delete Ta/Tc
  return table \
    .derived_column('Vds,max',
                    RangeFromUpper(ParseValue(Column('Drain to Source Voltage (Vdss)'), 'V')),
                    missing='discard') \
    .derived_column('Ids,max',
                    RangeFromUpper(ParseValue(Column('Current - Continuous Drain (Id) @ 25°C'), 'A')),
                    missing='discard') \
    .derived_column('Vgs',
                    Range(ParseValue(Column('Drive Voltage (Max Rds On,  Min Rds On)'), 'V'),
                          ParseValue(Column('Vgs (Max)'), 'V')),
                    missing='discard') \
    .derived_column('Rds,max',
                    RangeFromUpper(ParseValue(Column('Rds On (Max) @ Id, Vgs'), 'Ohm'), lower=0),
                    missing='discard') \
    .derived_column('P,max',
                    RangeFromUpper(ParseValue(Column('Power Dissipation (Max)'), 'W')),
                    missing='discard') \
    .derived_column('Qc',
                    RangeFromUpper(ParseValue(Column('Gate Charge (Qg) (Max) @ Vgs'), 'C'), lower=0),
                    missing='discard') \
    .derived_column('footprint',
                    MapDict(Column('Package / Case'), {
                      'TO-236-3, SC-59, SOT-23-3': 'Package_TO_SOT_SMD:SOT-23',
                      'TO-261-4, TO-261AA': 'Package_TO_SOT_SMD:SOT-223-3_TabPin2',
                      'TO-252-3, DPak (2 Leads + Tab), SC-63': 'Package_TO_SOT_SMD:TO-252-2',
                      'TO-263-3, D²Pak (2 Leads + Tab), TO-263AB': 'Package_TO_SOT_SMD:TO-263-2',
                    }), missing='discard')


@abstract_block
class SmtFet(Fet, CircuitBlock, GeneratorBlock):
  product_table: ProductTable

  @init_in_parent
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.drain_voltage_rating = self.Parameter(RangeExpr())
    self.drain_current_rating = self.Parameter(RangeExpr())
    self.gate_voltage_rating = self.Parameter(RangeExpr())
    self.power_rating = self.Parameter(RangeExpr())
    self.selected_rds_on = self.Parameter(RangeExpr())
    self.selected_gate_charge = self.Parameter(RangeExpr())

    self.generator(self.select_part,
                   self.drain_voltage, self.drain_current,
                   self.gate_voltage, self.rds_on, self.gate_charge, self.power)

  def select_part(self, drain_voltage: RangeVal, drain_current: RangeVal,
                  gate_voltage: RangeVal, rds_on: RangeVal, gate_charge: RangeVal, power: RangeVal) -> None:
    parts = self.product_table.filter(RangeContains(Column('Vds,max'), Lit(drain_voltage))) \
      .filter(RangeContains(Column('Ids,max'), Lit(drain_current))) \
      .filter(RangeContains(Column('Vgs'), Lit(gate_voltage))) \
      .filter(RangeContains(Lit(rds_on), Column('Rds,max'))) \
      .filter(RangeContains(Column('P,max'), Lit(power))) \
      .filter(RangeContains(Lit(gate_charge), Column('Qc'))) \
      .filter(ContainsString(Column('Manufacturer Part Number'), self.get_opt(self.part))) \
      .filter(ContainsString(Column('footprint'), self.get_opt(self.footprint_name))) \
      .sort(Column('Unit Price (USD)'))  # TODO actually make this into float
    part = parts.first(err=f"no FETs matching Vds={drain_voltage}, Ids={drain_current}, "
                           f"Vgs={gate_voltage}, Rds={rds_on}, "
                           f"Pmax={power}, Qc={gate_charge}")

    self.assign(self.drain_voltage_rating, part['Vds,max'])
    self.assign(self.drain_current_rating, part['Ids,max'])
    self.assign(self.gate_voltage_rating, part['Vgs'])  # TODO: confounded w/ gate drive voltage
    self.assign(self.selected_rds_on, part['Rds,max'])
    self.assign(self.power_rating, part['P,max'])
    self.assign(self.selected_gate_charge, part['Qc'])

    footprint_pinning = {
      'Package_TO_SOT_SMD:SOT-23': {
        '1': self.gate,
        '2': self.source,
        '3': self.drain,
      },
      'Package_TO_SOT_SMD:SOT-223-3_TabPin2': {
        '1': self.gate,
        '2': self.drain,
        '3': self.source,
      },
      'Package_TO_SOT_SMD:TO-252-2': {
        '1': self.gate,
        '2': self.drain,
        '3': self.source,
      },
      'Package_TO_SOT_SMD:TO-263-2': {
        '1': self.gate,
        '2': self.drain,
        '3': self.source,
      },
    }

    self.footprint(
      'Q', part['footprint'],
      footprint_pinning[part['footprint']],
      mfr=part['Manufacturer'], part=part['Manufacturer Part Number'],
      value=f"Vds={self.get(self.drain_voltage)} V, Ids={self.get(self.drain_current)} A",
      datasheet=part['Datasheets']
    )


class SmtNFet(PFet, SmtFet):
  product_table = generate_fet_table([
    'Digikey_NFETs.csv',
  ])


class SmtPFet(NFet, SmtFet):
  product_table = generate_fet_table([
    'Digikey_PFETs.csv',
  ])


@abstract_block
class SmtSwitchFet(SwitchFet, CircuitBlock, GeneratorBlock):  # TODO dedup w/ DefaultFet
  product_table: ProductTable

  @init_in_parent
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.drain_voltage_rating = self.Parameter(RangeExpr())
    self.drain_current_rating = self.Parameter(RangeExpr())
    self.gate_voltage_rating = self.Parameter(RangeExpr())
    self.power_rating = self.Parameter(RangeExpr())
    self.selected_rds_on = self.Parameter(RangeExpr())
    self.selected_gate_charge = self.Parameter(RangeExpr())

    self.static_power = self.Parameter(RangeExpr())
    self.switching_power = self.Parameter(RangeExpr())
    self.total_power = self.Parameter(RangeExpr())

    self.generator(self.select_part,
                   self.frequency, self.drive_current,
                   self.drain_voltage, self.drain_current,
                   self.gate_voltage, self.rds_on, self.gate_charge, self.power)

  def select_part(self, frequency: RangeVal, drive_current: RangeVal,
                  drain_voltage: RangeVal, drain_current: RangeVal,
                  gate_voltage: RangeVal, rds_on: RangeVal, gate_charge: RangeVal, power: RangeVal) -> None:
    i_max = drain_current[1]
    v_max = drain_voltage[1]
    gate_drive_rise, gate_drive_fall = drive_current[1], -drive_current[0]
    f_max = frequency[1]
    assert gate_drive_rise > 0 and gate_drive_fall > 0, \
      f"got nonpositive gate currents rise={gate_drive_rise} A and fall={gate_drive_fall} A"

    def static_power(row: Dict[str, Any]) -> Tuple[float, float]:
      r_max = cast(float, row['Rds,max'][1])
      return (0, (i_max ** 2) * r_max)

    def switching_power(row: Dict[str, Any]) -> Tuple[float, float]:
      qc_max = cast(float, row['Qc'][1])
      rise_time = qc_max / gate_drive_rise
      fall_time = qc_max / gate_drive_fall
      return (0, (rise_time + fall_time) * (i_max * v_max) * f_max)

    def total_power(row: Dict[str, Any]) -> Tuple[float, float]:
      return (0, row['static_power'][1] + row['switching_power'][1])

    parts = self.product_table.filter(RangeContains(Column('Vds,max'), Lit(drain_voltage))) \
      .filter(RangeContains(Column('Ids,max'), Lit(drain_current))) \
      .filter(RangeContains(Column('Vgs'), Lit(gate_voltage))) \
      .filter(RangeContains(Lit(rds_on), Column('Rds,max'))) \
      .filter(RangeContains(Column('P,max'), Lit(power))) \
      .filter(RangeContains(Lit(gate_charge), Column('Qc'))) \
      .filter(ContainsString(Column('Manufacturer Part Number'), self.get_opt(self.part))) \
      .filter(ContainsString(Column('footprint'), self.get_opt(self.footprint_name))) \
      .derived_column('static_power', static_power) \
      .derived_column('switching_power', switching_power) \
      .derived_column('total_power', total_power) \
      .filter(RangeContains(Column('P,max'), Column('total_power'))) \
      .sort(Column('Unit Price (USD)'))  # TODO actually make this into float
    part = parts.first(err=f"no FETs matching Vds={drain_voltage}, Ids={drain_current}, "
                           f"Vgs={gate_voltage}, Rds={rds_on}, "
                           f"Pmax={power}, Qc={gate_charge}")

    self.assign(self.drain_voltage_rating, part['Vds,max'])
    self.assign(self.drain_current_rating, part['Ids,max'])
    self.assign(self.gate_voltage_rating, part['Vgs'])  # TODO: confounded w/ gate drive voltage
    self.assign(self.selected_rds_on, part['Rds,max'])
    self.assign(self.power_rating, part['P,max'])
    self.assign(self.selected_gate_charge, part['Qc'])
    self.assign(self.static_power, part['static_power'])
    self.assign(self.switching_power, part['switching_power'])
    self.assign(self.total_power, part['total_power'])

    footprint_pinning = {
      'Package_TO_SOT_SMD:SOT-23': {
        '1': self.gate,
        '2': self.source,
        '3': self.drain,
      },
      'Package_TO_SOT_SMD:SOT-223-3_TabPin2': {
        '1': self.gate,
        '2': self.drain,
        '3': self.source,
      },
      'Package_TO_SOT_SMD:TO-252-2': {
        '1': self.gate,
        '2': self.drain,
        '3': self.source,
      },
      'Package_TO_SOT_SMD:TO-263-2': {
        '1': self.gate,
        '2': self.drain,
        '3': self.source,
      },
    }

    self.footprint(
      'Q', part['footprint'],
      footprint_pinning[part['footprint']],
      mfr=part['Manufacturer'], part=part['Manufacturer Part Number'],
      value=f"Vds={self.get(self.drain_voltage)} V, Ids={self.get(self.drain_current)} A",
      datasheet=part['Datasheets']
    )


class SmtSwitchNFet(SwitchNFet, SmtSwitchFet):
  product_table = generate_fet_table([
    'Digikey_NFETs.csv',
  ])


class SmtSwitchPFet(SwitchPFet, SmtSwitchFet):
  product_table = generate_fet_table([
    'Digikey_PFETs.csv',
  ])
