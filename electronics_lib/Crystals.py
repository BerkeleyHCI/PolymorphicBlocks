from electronics_abstract_parts import *
from .ProductTableUtils import *
from .DigikeyTable import *


class CrystalTable(DigikeyTable):
  FREQUENCY = PartsTableColumn(Range)
  CAPACITANCE = PartsTableColumn(float)
  FOOTPRINT = PartsTableColumn(str)  # KiCad footprint name

  SIZE_PACKAGE_FOOTPRINT_MAP = {
    ('0.126" L x 0.098" W (3.20mm x 2.50mm)', '4-SMD, No Lead'):
      'Oscillator:Oscillator_SMD_Abracon_ASE-4Pin_3.2x2.5mm',
  }

  @classmethod
  def _generate_table(cls) -> PartsTable:
    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      new_rows: Dict[PartsTableColumn, Any] = {}
      try:
        # handle the footprint first since this is the most likely to filter
        new_rows[cls.FOOTPRINT] = cls.SIZE_PACKAGE_FOOTPRINT_MAP[
          (row['Size / Dimension'], row['Package / Case'])
        ]

        if row['Operating Mode'] != 'Fundamental':
          return None

        new_rows[cls.FREQUENCY] = Range.from_tolerance(
          PartsTableUtil.parse_value(row['Frequency'], 'Hz'),
          PartsTableUtil.parse_tolerance(row['Frequency Tolerance'])
        )
        new_rows[cls.CAPACITANCE] = PartsTableUtil.parse_value(row['Load Capacitance'], 'F')

        new_rows.update(cls._parse_digikey_common(row))

        return new_rows
      except (KeyError, PartsTableUtil.ParseError):
        return None

    raw_table = PartsTable.from_csv_files(PartsTableUtil.with_source_dir([
      'Digikey_Crystals_3.2x2.5_1.csv',
      'Digikey_Crystals_3.2x2.5_2.csv',
    ], 'resources'), encoding='utf-8-sig')
    return raw_table.map_new_columns(parse_row)


class SmdCrystal(Crystal, FootprintBlock, GeneratorBlock):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)

    self.selected_capacitance = self.Parameter(FloatExpr())

    self.generator(self.select_part, self.frequency,
                   targets=[self.crystal])

  def select_part(self, frequency: Range):
    compatible_parts = CrystalTable.table().filter(lambda row: (
      row[CrystalTable.FREQUENCY] in frequency
    ))
    part = compatible_parts.sort_by(
      lambda row: row[CrystalTable.COST]
    ).first(f"no crystal matching f={frequency} Hz")

    self.assign(self.selected_capacitance, part[CrystalTable.CAPACITANCE])
    self.assign(self.crystal.frequency, part[CrystalTable.FREQUENCY])

    self.footprint(
      'X', 'Oscillator:Oscillator_SMD_Abracon_ASE-4Pin_3.2x2.5mm',
      {
        '1': self.crystal.a,
        '2': self.gnd,
        '3': self.crystal.b,
        '4': self.gnd,
      },
      mfr=part[CrystalTable.MANUFACTURER], part=part[CrystalTable.PART_NUMBER],
      value=f"{part['Frequency']}, {part['Load Capacitance']}",
      datasheet=part[CrystalTable.DATASHEETS]
    )


class OscillatorCrystal(DiscreteApplication):  # TODO rename to disambiguate from part?
  PARASITIC_CAPACITANCE = 5e-12

  # Tolerance selected using table 32 in https://www.nxp.com/docs/en/data-sheet/LPC15XX.pdf, which gives suggested
  # load cap values 18pF, 39pF, 57pF. Assume any capacitance in the center could round either way - 22pF goes to 18pF
  # or 39pF, which gives a 28% tolerance.
  # Calculation: for tolerance y and series multiplicative factor a, we need (1+y) = a(1-y)
  # which solves to y=(a-1)/(a+1)
  # Then stack an additive 10% tolerance for the capacitor tolerance, for a total 0.38 tolerance.
  # TODO this should be formalized better.
  CAPACITOR_TOLERANCE = 0.38

  @init_in_parent
  def __init__(self, frequency: RangeLike = RangeExpr()) -> None:
    """Crystal and supporting circuitry to connect it to an oscillator driver.
    Should include load capacitors."""
    super().__init__()

    self.package = self.Block(SmdCrystal(frequency=frequency))
    self.crystal = self.Export(self.package.crystal, [InOut])
    self.gnd = self.Export(self.package.gnd, [Common])

    cap_model = Capacitor(
      capacitance=(
          (self.package.selected_capacitance - self.PARASITIC_CAPACITANCE) * 2 * (1 - self.CAPACITOR_TOLERANCE),
          (self.package.selected_capacitance - self.PARASITIC_CAPACITANCE) * 2 * (1 + self.CAPACITOR_TOLERANCE)),
      voltage=self.crystal.link().drive_voltage
    )
    self.cap_a = self.Block(cap_model)
    self.cap_b = self.Block(cap_model)
    self.connect(self.cap_a.pos, self.crystal.a)
    self.connect(self.cap_b.pos, self.crystal.b)
    self.connect(self.gnd, self.cap_a.neg.as_ground(), self.cap_b.neg.as_ground())
