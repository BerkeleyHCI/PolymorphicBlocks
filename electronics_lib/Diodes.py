import csv
from functools import reduce
import os

from electronics_abstract_parts import *
from .ProductTableUtils import *
from .DigikeyTable import *


class BaseDiodeTable(DigikeyTable):
  PACKAGE_FOOTPRINT_MAP = {
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
  }

  @classmethod
  def footprint_pinmap(cls, footprint: str, anode: CircuitPort, cathode: CircuitPort):
    return {
      'Diode_SMD:D_SMA': {
        '1': cathode,
        '2': anode,
      },
      'Diode_SMD:D_SMB': {
        '1': cathode,
        '2': anode,
      },
      'Diode_SMD:D_SMC': {
        '1': cathode,
        '2': anode,
      },
      'Diode_SMD:D_SOD-123': {
        '1': cathode,
        '2': anode,
      },
      'Diode_SMD:D_SOD-323': {
        '1': cathode,
        '2': anode,
      },
      'Package_TO_SOT_SMD:TO-252-2': {
        '1': anode,
        '2': cathode,
        '3': anode,
      },
      'Package_TO_SOT_SMD:TO-263-2': {
        '1': anode,  # TODO sometimes NC
        '2': cathode,
        '3': anode,
      },
    }[footprint]

class DiodeTable(BaseDiodeTable):
  VOLTAGE_RATING = PartsTableColumn(Range)  # tolerable voltages, positive
  CURRENT_RATING = PartsTableColumn(Range)  # tolerable currents, average
  FORWARD_VOLTAGE = PartsTableColumn(Range)  # possible forward voltage range
  REVERSE_RECOVERY = PartsTableColumn(Range)  # possible reverse recovery time
  FOOTPRINT = PartsTableColumn(str)  # KiCad footprint name

  @classmethod
  def _generate_table(cls) -> PartsTable:
    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      new_rows: Dict[PartsTableColumn, Any] = {}
      try:
        new_rows[cls.FOOTPRINT] = cls.PACKAGE_FOOTPRINT_MAP.get(row['Package / Case'])

        new_rows[cls.VOLTAGE_RATING] = Range.zero_to_upper(
          PartsTableUtil.parse_value(row['Voltage - DC Reverse (Vr) (Max)'], 'V')
        )
        new_rows[cls.CURRENT_RATING] = Range.zero_to_upper(
          PartsTableUtil.parse_value(row['Current - Average Rectified (Io)'], 'A')
        )
        new_rows[cls.FORWARD_VOLTAGE] = Range.zero_to_upper(
          PartsTableUtil.parse_value(
            PartsTableUtil.strip_parameter(row['Voltage - Forward (Vf) (Max) @ If']),
            'V')
        )
        if row['Reverse Recovery Time (trr)'] and row['Reverse Recovery Time (trr)'] != '-':
          reverse_recovery = Range.zero_to_upper(
            PartsTableUtil.parse_value(row['Reverse Recovery Time (trr)'], 's')
          )
        elif row['Speed'] == 'Fast Recovery =< 500ns, > 200mA (Io)':
          reverse_recovery = Range.zero_to_upper(500e-9)
        else:
          reverse_recovery = Range.zero_to_upper(float('inf'))
        new_rows[cls.REVERSE_RECOVERY] = reverse_recovery

        new_rows.update(cls._parse_digikey_common(row))

        return new_rows
      except (KeyError, PartsTableUtil.ParseError):
        return None

    raw_table = PartsTable.from_csv_files(PartsTableUtil.with_source_dir([
      'Digikey_Diodes_DO214.csv',
      'Digikey_Diodes_DPak_DDPak.csv',
      'Digikey_Diodes_SOD123_SOD323.csv',
    ], 'resources'), encoding='utf-8-sig')
    return raw_table.map_new_columns(parse_row)


class SmtDiode(Diode, FootprintBlock, GeneratorBlock):
  @init_in_parent
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.selected_voltage_rating = self.Parameter(RangeExpr())
    self.selected_current_rating = self.Parameter(RangeExpr())
    self.selected_voltage_drop = self.Parameter(RangeExpr())
    self.selected_reverse_recovery_time = self.Parameter(RangeExpr())

    self.generator(self.select_part, self.reverse_voltage, self.current, self.voltage_drop,
                   self.reverse_recovery_time)
    # TODO: also support optional part and footprint name

  def select_part(self, reverse_voltage: Range, current: Range, voltage_drop: Range,
                  reverse_recovery_time: Range) -> None:
    # TODO maybe apply ideal diode law / other simple static model to better bound Vf?
    compatible_parts = DiodeTable.table().filter(lambda row: (
        reverse_voltage.fuzzy_in(row[DiodeTable.VOLTAGE_RATING]) and
        current.fuzzy_in(row[DiodeTable.CURRENT_RATING]) and
        row[DiodeTable.FORWARD_VOLTAGE].fuzzy_in(voltage_drop) and
        row[DiodeTable.REVERSE_RECOVERY].fuzzy_in(reverse_recovery_time)
    ))
    part = compatible_parts.sort_by(
      lambda row: row[DiodeTable.COST]
    ).first(f"no diodes in Vr,max={reverse_voltage} V, I={current} A, Vf={voltage_drop} V, trr={reverse_recovery_time} s")

    self.assign(self.selected_voltage_rating, part[DiodeTable.VOLTAGE_RATING])
    self.assign(self.selected_current_rating, part[DiodeTable.CURRENT_RATING])
    self.assign(self.selected_voltage_drop, part[DiodeTable.FORWARD_VOLTAGE])
    self.assign(self.selected_reverse_recovery_time, part[DiodeTable.REVERSE_RECOVERY])

    self.footprint(
      'D', part[DiodeTable.FOOTPRINT],
      DiodeTable.footprint_pinmap(part[DiodeTable.FOOTPRINT],
                                  self.anode, self.cathode),
      mfr=part[DiodeTable.MANUFACTURER], part=part[DiodeTable.PART_NUMBER],
      value=f"Vr={part['Voltage - DC Reverse (Vr) (Max)']}, I={part['Current - Average Rectified (Io)']}",
      datasheet=part[DiodeTable.DATASHEETS]
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
