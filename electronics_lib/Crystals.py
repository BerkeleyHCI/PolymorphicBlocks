import csv
from functools import reduce
import os

from electronics_abstract_parts import *
from .ProductTableUtils import *


def generate_crystal_table(TABLES: List[str]) -> ProductTable:
  tables = []
  for filename in TABLES:
    path = os.path.join(os.path.dirname(__file__), 'resources', filename)
    with open(path, newline='', encoding='utf-8') as csvfile:
      reader = csv.reader(csvfile)
      tables.append(ProductTable(next(reader), [row for row in reader]))
  table = reduce(lambda x, y: x+y, tables)

  return table \
    .derived_column('frequency',
                    RangeFromTolerance(ParseValue(Column('Frequency'), 'Hz'), Column('Frequency Tolerance')),
                    missing='discard') \
    .derived_column('capacitance',
                    ParseValue(Column('Load Capacitance'), 'F'),
                    missing='discard') \
    .filter(ContainsString(Column('Operating Mode'), 'Fundamental')) \
    .filter(ContainsString(Column('Size / Dimension'), '0.126" L x 0.098" W (3.20mm x 2.50mm)')) \
    .derived_column('footprint',
                    MapDict(Column('Package / Case'), {
                      '4-SMD, No Lead': 'Oscillator:Oscillator_SMD_Abracon_ASE-4Pin_3.2x2.5mm',  # TODO needs to be both Package/Case and Size/Dimension
                    }), missing='discard')


class SmdCrystal(Crystal, CircuitBlock):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self._in_mfr = self.Parameter(StringExpr())
    self._in_part = self.Parameter(StringExpr())
    self._in_value = self.Parameter(StringExpr())
    self._in_datasheet = self.Parameter(StringExpr())

  def contents(self):
    super().contents()
    self.footprint(
      'X', 'Oscillator:Oscillator_SMD_Abracon_ASE-4Pin_3.2x2.5mm',
      {
        '1': self.crystal.a,
        '2': self.gnd,
        '3': self.crystal.b,
        '4': self.gnd,
      },
      mfr=self._in_mfr, part=self._in_part, value=self._in_value, datasheet=self._in_datasheet
    )


class OscillatorCrystal(DiscreteApplication, GeneratorBlock):  # TODO rename to disambiguate from part?
  product_table = generate_crystal_table([
    'Digikey_Crystals_3.2x2.5_1.csv',
    'Digikey_Crystals_3.2x2.5_2.csv',
  ])
  PARASITIC_CAPACITANCE = 5e-12

  @init_in_parent
  def __init__(self, frequency: RangeLike = RangeExpr()) -> None:
    """Crystal and supporting circuitry to connect it to an oscillator driver.
    Should include load capacitors."""
    super().__init__()

    self.frequency = self.Parameter(RangeExpr(frequency))

    self.crystal = self.Port(CrystalPort(), [InOut])
    self.gnd = self.Port(Ground(), [Common])

    self.generator(self.select_part, self.frequency,
                   targets=[self.crystal, self.gnd])

    # Output values
    self.selected_frequency = self.Parameter(RangeExpr())

  def select_part(self, frequency: RangeVal):
    # TODO this should be part of the crystal block, but that needs a post-generate elaborate
    parts = self.product_table.filter(RangeContains(Lit(frequency), Column('frequency'))) \
      .sort(Column('Unit Price (USD)'))  # TODO actually make this into float
    part = parts.first(err=f"no crystal matching f={frequency}")

    self.package = self.Block(SmdCrystal(frequency=self.selected_frequency))

    self.assign(self.package._in_mfr, part['Manufacturer'])
    self.assign(self.package._in_part, part['Manufacturer Part Number'])
    self.assign(self.selected_frequency, part['frequency'])
    self.assign(self.package._in_value, f"{part['Frequency']}, {part['Load Capacitance']}")
    self.assign(self.package._in_datasheet, part['Datasheets'])

    self.connect(self.crystal, self.package.crystal)
    self.connect(self.gnd, self.package.gnd)

    crystal_capacitance = part['capacitance']
    load_capacitance = (crystal_capacitance - self.PARASITIC_CAPACITANCE) * 2

    # Tolerance selected using table 32 in https://www.nxp.com/docs/en/data-sheet/LPC15XX.pdf, which gives suggested
    # load cap values 18pF, 39pF, 57pF. Assume any capacitance in the center could round either way - 22pF goes to 18pF
    # or 39pF, which gives a 28% tolerance.
    # Calculation: for tolerance y and series multiplicative factor a, we need (1+y) = a(1-y)
    # which solves to y=(a-1)/(a+1)
    # Then stack an additive 10% tolerance for the capacitor tolerance.
    # TODO this should be formalized better.

    cap_model = Capacitor(
      capacitance=load_capacitance*Farad(tol=0.38),  # arbitrary tolerance given load capacitors from https://www.nxp.com/docs/en/data-sheet/LPC15XX.pdf
      voltage=self.crystal.link().drive_voltage
    )
    self.cap_a = self.Block(cap_model)
    self.cap_b = self.Block(cap_model)
    self.connect(self.cap_a.pos, self.crystal.a)
    self.connect(self.cap_b.pos, self.crystal.b)
    self.connect(self.cap_a.neg.as_voltage_sink(), self.cap_b.neg.as_voltage_sink(), self.gnd)
