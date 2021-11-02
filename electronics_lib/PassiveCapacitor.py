import csv
from functools import reduce
import math
import os

from electronics_abstract_parts import *
from electronics_abstract_parts.Categories import DummyDevice
from .ProductTableUtils import *


def generate_mlcc_table(TABLES: List[str]) -> ProductTable:
  tables = []
  for filename in TABLES:
    path = os.path.join(os.path.dirname(__file__), 'resources', filename)
    with open(path, newline='', encoding='utf-8') as csvfile:
      reader = csv.reader(csvfile)
      tables.append(ProductTable(next(reader), [row for row in reader]))
  table = reduce(lambda x, y: x+y, tables)

  # TODO maybe do voltage derating
  # TODO also consider minimum symmetric voltage
  return table.derived_column('capacitance',
                              RangeFromTolerance(ParseValue(Column('Capacitance'), 'F'), Column('Tolerance')),
                              missing='discard') \
    .derived_column('nominal_capacitance',
                    ParseValue(Column('Capacitance'), 'F'),
                    missing='discard') \
    .derived_column('voltage',
                    RangeFromUpper(ParseValue(Column('Voltage - Rated'), 'V'))) \
    .derived_column('footprint',
                    MapDict(Column('Package / Case'), {
                      '0603 (1608 Metric)': 'Capacitor_SMD:C_0603_1608Metric',
                      '0805 (2012 Metric)': 'Capacitor_SMD:C_0805_2012Metric',
                      '1206 (3216 Metric)': 'Capacitor_SMD:C_1206_3216Metric',
                    }), missing='discard')


class SmtCeramicCapacitor(Capacitor, FootprintBlock, GeneratorBlock):
  @init_in_parent
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.footprint_spec = self.Parameter(StringExpr(""))

    # Default to be overridden on a per-device basis
    self.single_nominal_capacitance = self.Parameter(RangeExpr((0, (22e-6)*1.25)))  # maximum capacitance in a single part

    self.generator(self.select_capacitor, self.capacitance, self.voltage, self.single_nominal_capacitance,
                   self.part_spec, self.footprint_spec)

    # Output values
    self.selected_capacitance = self.Parameter(RangeExpr())
    self.selected_derated_capacitance = self.Parameter(RangeExpr())
    self.selected_voltage_rating = self.Parameter(RangeExpr())

  product_table = generate_mlcc_table([
    'Digikey_MLCC_SamsungCl_1pF_E12.csv',
    'Digikey_MLCC_SamsungCl_1nF_E6.csv',
    'Digikey_MLCC_SamsungCl_1uF_E3.csv',
    'Digikey_MLCC_YageoCc_1pF_E12_1.csv',
    'Digikey_MLCC_YageoCc_1pF_E12_2.csv',
    'Digikey_MLCC_YageoCc_1nF_E6_1.csv',
    'Digikey_MLCC_YageoCc_1nF_E6_2.csv',
    'Digikey_MLCC_YageoCc_1uF_E3.csv',
  ])

  DERATE_VOLTCO = {  # in terms of %capacitance / V over 3.6
    #  'Capacitor_SMD:C_0603_1608Metric'  # not supported, should not generate below 1uF
    'Capacitor_SMD:C_0805_2012Metric': 0.08,
    'Capacitor_SMD:C_1206_3216Metric': 0.04,
  }

  def select_capacitor(self, capacitance: Range, voltage: Range,
                       single_nominal_capacitance: Range,
                       part_spec: str, footprint_spec: str) -> None:
    def derated_capacitance(row: Dict[str, Any]) -> Tuple[float, float]:
      if voltage.upper < 3.6:  # x-intercept at 3.6v
        return row['capacitance']
      if (row['capacitance'][0] + row['capacitance'][1]) / 2 <= 1e-6:  # don't derate below 1uF
        return row['capacitance']
      if row['footprint'] not in self.DERATE_VOLTCO:
        return (0, 0)  # can't derate, generate obviously bogus and ignored value
      voltco = self.DERATE_VOLTCO[row['footprint']]
      return (
        row['capacitance'][0] * (1 - voltco * (voltage.upper - 3.6)),
        row['capacitance'][1] * (1 - voltco * (voltage.lower - 3.6))
      )

    single_cap_max = single_nominal_capacitance.upper

    parts = self.product_table \
      .filter(Implication(  # enforce minimum package size by capacitance
      RangeContains(
        Lit((1.1e-6, float('inf'))),
        RangeFromTolerance(ParseValue(Column('Capacitance'), 'F'), Lit('±0%'))),
      StringContains(Column('Package / Case'), [
        '0805 (2012 Metric)', '1206 (3216 Metric)',
      ]))) \
      .filter(Implication(
      RangeContains(
        Lit((11.0e-6, float('inf'))),
        RangeFromTolerance(ParseValue(Column('Capacitance'), 'F'), Lit('±0%'))),
      StringContains(Column('Package / Case'), [
        '1206 (3216 Metric)',
      ]))) \
      .filter(RangeContains(Column('voltage'), Lit(voltage))) \
      .filter(ContainsString(Column('Manufacturer Part Number'), part_spec or None)) \
      .filter(ContainsString(Column('footprint'), footprint_spec or None)) \
      .filter(RangeContains(RangeFromUpper(Lit(single_cap_max)), Column('capacitance'))) \
      .derived_column('derated_capacitance', derated_capacitance)

    capacitance_filtered_parts = parts.filter(RangeContains(Lit(capacitance), Column('derated_capacitance'))) \
      .sort(Column('Unit Price (USD)')) \
      .sort(Column('footprint'))  # this kind of gets at smaller first

    if len(capacitance_filtered_parts) > 0:  # available in single capacitor
      part = capacitance_filtered_parts.first(err=f"no single capacitors in ({capacitance}) F")

      self.assign(self.selected_voltage_rating, part['voltage'])
      self.assign(self.selected_capacitance, part['capacitance'])
      self.assign(self.selected_derated_capacitance, part['derated_capacitance'])

      self.footprint(
        'C', part['footprint'],
        {
          '1': self.pos,
          '2': self.neg,
        },
        mfr=part['Manufacturer'], part=part['Manufacturer Part Number'],
        value=f"{part['Capacitance']}, {part['Voltage - Rated']}",
        datasheet=part['Datasheets']
      )
    elif capacitance.upper >= single_cap_max:
      parts = parts.sort(Column('Unit Price (USD)')) \
        .sort(Column('footprint')) \
        .sort(Column('nominal_capacitance'), reverse=True)  # pick the largest capacitor available
      part = parts.first(err=f"no parallel capacitors in ({capacitance}) F")

      num_caps = math.ceil(capacitance.lower / part['derated_capacitance'][0])
      assert num_caps * part['derated_capacitance'][1] < capacitance.upper, "can't generate parallel caps within max capacitance limit"

      self.assign(self.selected_capacitance, (
        num_caps * part['capacitance'][0],
        num_caps * part['capacitance'][1],
      ))
      self.assign(self.selected_derated_capacitance, (
        num_caps * part['derated_capacitance'][0],
        num_caps * part['derated_capacitance'][1],
      ))

      cap_model = SmtCeramicCapacitor(capacitance=part['derated_capacitance'],
                                      voltage=self.voltage,
                                      part_spec=part['Manufacturer Part Number'])
      self.c = ElementDict[SmtCeramicCapacitor]()
      for i in range(num_caps):
        self.c[i] = self.Block(cap_model)
        self.connect(self.c[i].pos, self.pos)
        self.connect(self.c[i].neg, self.neg)

      # TODO CircuitBlocks probably shouldn't have hierarchy?
      self.assign(self.mfr, part['Manufacturer'])
      self.assign(self.part, part['Manufacturer Part Number'])
    else:
      raise ValueError(f"no single capacitors in ({capacitance}) F")


class SmtCeramicCapacitorGeneric(Capacitor, FootprintBlock, GeneratorBlock):
  """
  Generic SMT ceramic capacitor (MLCC) picker that chooses a common value (E-series) based on rules
  specifying what capacitances / voltage ratings are available in what packages.

  Chosen by a rough scan over available parts on Digikey
  at voltages 10v, 16v, 25v, 50v, 100v, 250v
  and capacitances 1.0, 2.2, 4.7

  For Class-1 dielectric (C0G/NP0), 20% tolerance
  0402: 50v/1nF
  0603: 100v/1nF, 50v/2.2nF ?
  0805: 100v/2.2nF, 50v/10nF
  1206: 100v/10nF

  For Class-2 dielectric (X**), 20% tolerance
  0402:                   50v /                0.1uF,     25v / 0.1uF,                      10v / 2.2uF
  0603:                   50v /                0.1uF,     25v /   1uF,     16v / 2.2uF,     10v /  10uF
  0805: 100v / 0.1uF,     50v / 0.1uF (maybe 0.22uF),     25v /  10uF
  1206: 100v / 0.1uF,     50v /                4.7uF,     25v /  10uF,                      10v /  22uF
  1210: 100v / 4.7uF,     50v /                 10uF,                      16v /  22uF,     10v /  47uF
  1812: 100v / 2.2uF,     50v /                  1uF,     25v /  10uF (though small sample size)

  Derating coefficients in terms of %capacitance / V over 3.6
  'Capacitor_SMD:C_0603_1608Metric'  # not supported, should not generate below 1uF
  """
  SINGLE_CAP_MAX = 22e-6 # maximum capacitance in a single part
  MAX_CAP_PACKAGE = 'Capacitor_SMD:C_1206_3216Metric' # default package for largest possible capacitor

  @init_in_parent
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.footprint_spec = self.Parameter(StringExpr(""))
    self.derating_coeff = self.Parameter(FloatExpr(1)) # simple multiplier for capacitance derating, does not scale with package or applied voltage

    self.generator(self.select_capacitor_no_prod_table, self.capacitance, self.voltage,
                   self.footprint_spec, self.derating_coeff)

    # Output values
    self.selected_nominal_capacitance = self.Parameter(RangeExpr())
    self.selected_voltage_rating = self.Parameter(RangeExpr())

  class SmtCeramicCapacitorGenericPackageSpecs(NamedTuple):
    name: str # package name
    max: float # maximum nominal capacitance
    derate: float # derating coefficient in terms of %capacitance / V over 3.6
    vc_pairs: Dict[float, float] # rough estimate of what the maximum nominal capacitance is at certain voltages

  # package specs in increasing order by size
  PACKAGE_SPECS = [
    SmtCeramicCapacitorGenericPackageSpecs(
      name='Capacitor_SMD:C_0402_1005Metric',
      max=1e-7,
      derate=0,
      vc_pairs={             50:   1e-7, 25: 1e-7,             10: 2.2e-6},
    ),
    SmtCeramicCapacitorGenericPackageSpecs(
      name='Capacitor_SMD:C_0603_1608Metric',
      max=1.1e-6,
      derate=0,
      vc_pairs={             50:   1e-7, 25: 1e-6, 16: 2.2e-6, 10:   1e-5},
    ),
    SmtCeramicCapacitorGenericPackageSpecs(
      name='Capacitor_SMD:C_0805_2012Metric',
      max=11e-6,
      derate=0.08,
      vc_pairs={100:   1e-7, 50:   1e-7, 25: 1e-5, },
    ),
    SmtCeramicCapacitorGenericPackageSpecs(
      name='Capacitor_SMD:C_1206_3216Metric',
      max=22e-6,
      derate=0.04,
      vc_pairs={100:   1e-7, 50: 4.7e-6, 25: 1e-5,             10: 2.2e-5},
    ),
    SmtCeramicCapacitorGenericPackageSpecs(
      name='Capacitor_SMD:C_1210_3225Metric',
      max=4.7e-5,
      derate=0,
      vc_pairs={100: 4.7e-6, 50:   1e-5,           16: 2.2e-5, 10: 4.7e-5},
    ),
    SmtCeramicCapacitorGenericPackageSpecs(
      name='Capacitor_SMD:C_1812_4532Metric',
      max=1e-4,
      derate=0,
      vc_pairs={100: 2.2e-6, 50:   1e-6, 25: 1e-5, },
    ),
  ]

  def select_capacitor_no_prod_table(self, capacitance: Range, voltage: Range,
                                     footprint_spec: str, derating_coeff: float) -> None:
    """
    Selects a generic capacitor without using product tables

    :param capacitance: user-specified (derated) capacitance
    :param voltage: user-specified voltage
    :param single_nominal_capacitance: used when no single cap with requested capacitance, must generate multiple parallel caps,
                                       actually refers to max capacitance for a given part
    :param footprint_spec: user-specified package footprint
    :param derating_coeff: user-specified derating coefficient, if used then footprint_spec must be specified
    """

    def select_package(nominal_capacitance: float, voltage: Range) -> Optional[str]:

      if footprint_spec == "":
        package_options = self.PACKAGE_SPECS
      else:
        package_options = [spec for spec in self.PACKAGE_SPECS if spec.name == footprint_spec]

      for package in package_options:
        if package.max >= nominal_capacitance:
          for package_max_voltage, package_max_capacitance in package.vc_pairs.items():
            if package_max_voltage >= voltage.upper and package_max_capacitance >= nominal_capacitance:
              return package.name
      return None

    nominal_capacitance = capacitance / derating_coeff

    num_caps = math.ceil(nominal_capacitance.lower / self.SINGLE_CAP_MAX)
    if num_caps > 1:
      assert num_caps * self.SINGLE_CAP_MAX < nominal_capacitance.upper, "can't generate parallel caps within max capacitance limit"

      self.assign(self.selected_nominal_capacitance, num_caps * nominal_capacitance)

      if footprint_spec == "":
        split_package = self.MAX_CAP_PACKAGE
      else:
        split_package = footprint_spec

      cap_model = DummyCapacitor(capacitance=(self.SINGLE_CAP_MAX, self.SINGLE_CAP_MAX),
                                 voltage=self.voltage, footprint_spec=split_package)
      self.c = ElementDict[DummyCapacitor]()
      for i in range(num_caps):
        self.c[i] = self.Block(cap_model)
        self.connect(self.c[i].pos, self.pos)
        self.connect(self.c[i].neg, self.neg)
    else:
      value = ESeriesUtil.choose_preferred_number(nominal_capacitance, 0, ESeriesUtil.E24_SERIES_ZIGZAG, 2)
      assert value is not None, "cannot generate a preferred number"
      valid_footprint_spec = select_package(value, voltage)
      assert valid_footprint_spec is not None, "cannot generate a valid footprint spec"
      self.assign(self.selected_nominal_capacitance, value)

      self.footprint(
        'C', valid_footprint_spec,
        {
          '1': self.pos,
          '2': self.neg,
        },
        value=f'{UnitUtils.num_to_prefix(value, 3)}F'
      )


class DummyCapacitor(DummyDevice, Capacitor, FootprintBlock, GeneratorBlock):
  """
  Capacitor that does not derate, used for splitting a generic capacitor into multiple when desired capacitance is too high
  """

  @init_in_parent
  def __init__(self, footprint_spec: StringLike = "", *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.footprint_spec = self.Parameter(StringExpr(footprint_spec))
    self.generator(self.select_capacitor, self.capacitance, self.footprint_spec)

  def select_capacitor(self, capacitance: Range, footprint_spec: str) -> None:
    self.footprint(
      'C', footprint_spec,
      {
        '1': self.pos,
        '2': self.neg,
      },
      value=f'{UnitUtils.num_to_prefix(capacitance.lower, 3)}F'
    )
