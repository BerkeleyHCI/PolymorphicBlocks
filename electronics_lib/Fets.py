import csv
from functools import reduce
import os

from electronics_abstract_parts import *
from .ProductTableUtils import *
from .DigikeyTable import *


class BaseFetTable(DigikeyTable):
  VDS_RATING = PartsTableColumn(Range)
  IDS_RATING = PartsTableColumn(Range)
  VGS_RATING = PartsTableColumn(Range)
  VGS_DRIVE = PartsTableColumn(Range)
  RDS_ON = PartsTableColumn(Range)
  POWER_RATING = PartsTableColumn(Range)
  GATE_CHARGE = PartsTableColumn(Range)

  FOOTPRINT = PartsTableColumn(str)  # KiCad footprint name

  PACKAGE_FOOTPRINT_MAP = {
    'TO-236-3, SC-59, SOT-23-3': 'Package_TO_SOT_SMD:SOT-23',
    'TO-261-4, TO-261AA': 'Package_TO_SOT_SMD:SOT-223-3_TabPin2',
    'TO-252-3, DPak (2 Leads + Tab), SC-63': 'Package_TO_SOT_SMD:TO-252-2',
    'TO-263-3, D²Pak (2 Leads + Tab), TO-263AB': 'Package_TO_SOT_SMD:TO-263-2',
  }

  @classmethod
  def footprint_pinmap(cls, footprint: str, gate: CircuitPort, drain: CircuitPort, source: CircuitPort):
    return {
      'Package_TO_SOT_SMD:SOT-23': {
        '1': gate,
        '2': source,
        '3': drain,
      },
      'Package_TO_SOT_SMD:SOT-223-3_TabPin2': {
        '1': gate,
        '2': drain,
        '3': source,
      },
      'Package_TO_SOT_SMD:TO-252-2': {
        '1': gate,
        '2': drain,
        '3': source,
      },
      'Package_TO_SOT_SMD:TO-263-2': {
        '1': gate,
        '2': drain,
        '3': source,
      },
    }[footprint]

  @classmethod
  def parse_row(cls, row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
    new_rows: Dict[PartsTableColumn, Any] = {}
    try:
      new_rows[cls.FOOTPRINT] = cls.PACKAGE_FOOTPRINT_MAP.get(row['Package / Case'])

      new_rows[cls.VDS_RATING] = Range.zero_to_upper(
        PartsTableUtil.parse_value(row['Drain to Source Voltage (Vdss)'], 'V')
      )
      new_rows[cls.IDS_RATING] = Range.zero_to_upper(
        PartsTableUtil.parse_value(row['Current - Continuous Drain (Id) @ 25°C'].split('(')[0].strip(), 'A')
      )

      if row['Vgs (Max)'].startswith('±'):
        vgs_max = PartsTableUtil.parse_value(row['Vgs (Max)'][1:], 'V')
        new_rows[cls.VGS_RATING] = Range(-vgs_max, vgs_max)
      else:
        return None

      vgs_drive = PartsTableUtil.parse_value(row['Drive Voltage (Max Rds On,  Min Rds On)'].split(',')[0], 'V')
      if vgs_drive >= 0:
        new_rows[cls.VGS_DRIVE] = Range(vgs_drive, vgs_max)
      else:
        new_rows[cls.VGS_DRIVE] = Range(-vgs_max, vgs_drive)

      new_rows[cls.RDS_ON] = Range.zero_to_upper(
        PartsTableUtil.parse_value(PartsTableUtil.strip_parameter(row['Rds On (Max) @ Id, Vgs']), 'Ohm')
      )
      new_rows[cls.GATE_CHARGE] = Range.zero_to_upper(
        PartsTableUtil.parse_value(PartsTableUtil.strip_parameter(row['Gate Charge (Qg) (Max) @ Vgs']), 'C')
      )
      new_rows[cls.POWER_RATING] = Range.zero_to_upper(
        PartsTableUtil.parse_value(row['Power Dissipation (Max)'].split('(')[0].strip(), 'W')
      )

      new_rows.update(cls._parse_digikey_common(row))

      return new_rows
    except (KeyError, PartsTableUtil.ParseError):
      return None


class NFetTable(BaseFetTable):
  @classmethod
  def _generate_table(cls) -> PartsTable:
    raw_table = PartsTable.from_csv_files(PartsTableUtil.with_source_dir([
      'Digikey_NFETs.csv',
    ], 'resources'), encoding='utf-8-sig')
    return raw_table.map_new_columns(cls.parse_row)


class PFetTable(BaseFetTable):
  @classmethod
  def _generate_table(cls) -> PartsTable:
    raw_table = PartsTable.from_csv_files(PartsTableUtil.with_source_dir([
      'Digikey_PFETs.csv',
    ], 'resources'), encoding='utf-8-sig')
    return raw_table.map_new_columns(cls.parse_row)


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
                    MakeRange(ParseValue(Column('Drive Voltage (Max Rds On,  Min Rds On)'), 'V'),
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
class SmtFet(Fet, FootprintBlock, GeneratorBlock):
  TABLE: Type[BaseFetTable]

  @init_in_parent
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.selected_drain_voltage_rating = self.Parameter(RangeExpr())
    self.selected_drain_current_rating = self.Parameter(RangeExpr())
    self.selected_gate_drive = self.Parameter(RangeExpr())
    self.selected_power_rating = self.Parameter(RangeExpr())
    self.selected_rds_on = self.Parameter(RangeExpr())
    self.selected_gate_charge = self.Parameter(RangeExpr())

    self.generator(self.select_part,
                   self.drain_voltage, self.drain_current,
                   self.gate_voltage, self.rds_on, self.gate_charge, self.power)

  def select_part(self, drain_voltage: Range, drain_current: Range,
                  gate_voltage: Range, rds_on: Range, gate_charge: Range, power: Range) -> None:
    compatible_parts = self.TABLE.table().filter(lambda row: (
        drain_voltage.fuzzy_in(row[self.TABLE.VDS_RATING]) and
        drain_current.fuzzy_in(row[self.TABLE.IDS_RATING]) and
        gate_voltage.fuzzy_in(row[self.TABLE.VGS_DRIVE]) and
        row[self.TABLE.RDS_ON].fuzzy_in(rds_on) and
        row[self.TABLE.GATE_CHARGE].fuzzy_in(gate_charge) and
        power.fuzzy_in(row[self.TABLE.POWER_RATING])
    ))
    part = compatible_parts.sort_by(
      lambda row: row[self.TABLE.COST]
    ).first(f"{len(self.TABLE.table())}  no FETs diodes in Vds={drain_voltage} V, Ids={drain_current} A, Vgs={gate_voltage} V")

    self.assign(self.selected_drain_voltage_rating, part[self.TABLE.VDS_RATING])
    self.assign(self.selected_drain_current_rating, part[self.TABLE.IDS_RATING])
    self.assign(self.selected_gate_drive, part[self.TABLE.VGS_DRIVE])
    self.assign(self.selected_rds_on, part[self.TABLE.RDS_ON])
    self.assign(self.selected_power_rating, part[self.TABLE.POWER_RATING])
    self.assign(self.selected_gate_charge, part[self.TABLE.GATE_CHARGE])

    self.footprint(
      'Q', part[self.TABLE.FOOTPRINT],
      self.TABLE.footprint_pinmap(part[self.TABLE.FOOTPRINT],
                                  self.gate, self.drain, self.source),
      mfr=part[self.TABLE.MANUFACTURER], part=part[self.TABLE.PART_NUMBER],
      value=f"Vds={part['Drain to Source Voltage (Vdss)']}, Ids={part['Current - Continuous Drain (Id) @ 25°C']}",
      datasheet=part[self.TABLE.DATASHEETS]
    )


class SmtNFet(NFet, SmtFet):
  TABLE = NFetTable


class SmtPFet(PFet, SmtFet):
  TABLE = PFetTable


@abstract_block
class SmtSwitchFet(SwitchFet, FootprintBlock, GeneratorBlock):  # TODO dedup w/ DefaultFet
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

  def select_part(self, frequency: Range, drive_current: Range,
                  drain_voltage: Range, drain_current: Range,
                  gate_voltage: Range, rds_on: Range, gate_charge: Range, power: Range) -> None:
    i_max = drain_current.upper
    v_max = drain_voltage.upper
    gate_drive_rise, gate_drive_fall = drive_current.upper, -drive_current.lower
    f_max = frequency.upper
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
