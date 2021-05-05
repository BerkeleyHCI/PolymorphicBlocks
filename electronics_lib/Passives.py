import csv
from functools import reduce
import math
import os

from electronics_abstract_parts import *
from electronics_abstract_parts.Categories import DummyDevice
from .ProductTableUtils import *


def zigzag_range(start: int, end: int) -> Sequence[int]:
  if start >= end:
    return []

  center = int((start + end - 1) / 2)
  lower = list(range(start, center))
  upper = list(range(center + 1, end))
  output = [center]

  while lower or upper:
    if lower:
      output.append(lower.pop(0))
    if upper:
      output.append(upper.pop(0))

  return output

# from https://stackoverflow.com/questions/3410976/how-to-round-a-number-to-significant-figures-in-python
# TODO DEDUP w/ ResistiveDivider.py
def round_sig(x: float, sig: int) -> float:
  return round(x, sig-int(math.floor(math.log10(abs(x))))-1)

def choose_preferred_number(range: Tuple[float, float], tolerance: float, series: List[float], sig: int) ->\
    Optional[float]:
  lower_pow10 = math.floor(math.log10(range[0]))
  upper_pow10 = math.ceil(math.log10(range[1]))

  powers = zigzag_range(lower_pow10, upper_pow10)  # prefer the center power first, then zigzag away from it
  # TODO given the tolerance we can actually bound this further

  for value in series:
    for power in powers:
      pow10_mult = math.pow(10, power)
      value_mult = round_sig(value * pow10_mult, sig)  # this prevents floating point weirdness, eg 819.999
      value_tol = value_mult * tolerance
      if value_mult - value_tol >= range[0] and value_mult + value_tol <= range[1]:
        return value_mult

  return None


@abstract_block
class ESeriesResistor(Resistor, FootprintBlock, GeneratorBlock):
  TOLERANCE: float
  PACKAGE_POWER: List[Tuple[float, str]]

  @init_in_parent
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.footprint_spec = self.Parameter(StringExpr(""))
    self.generator(self.select_resistor, self.spec_resistance, self.power,
                   self.footprint_spec)

    # Output values
    self.selected_power_rating = self.Parameter(RangeExpr())

  """Default generator that automatically picks resistors.
  For value, preferentially picks the lowest-step E-series (E1 before E3 before E6 ...) value meeting the needs,
  at +/- 1% tolerance. If an E24 resistor at 1% cannot be found, tries to midpoint of the resistance range to pick an
  exact value at 1%.
  If below 1% tolerance is needed, fails. TODO: non-preferentially pick tolerances down to 0.1%, though pricey!
  Picks the minimum (down to 0603, up to 2512) SMD size for the power requirement. TODO: consider PTH types"""
  def select_resistor(self, resistance: RangeVal, power: RangeVal, footprint_spec: str) -> None:
    value = choose_preferred_number(resistance, self.TOLERANCE, self.E24_SERIES_ZIGZAG, 2)

    if value is None:  # failed to find a preferred resistor, choose the center within tolerance
      center = (resistance[0] + resistance[1]) / 2
      min_tolerance = center * self.TOLERANCE
      if (center - resistance[0]) < min_tolerance or (resistance[1] - center < min_tolerance):
        # TODO should there be a better way of communicating generator failures?
        raise ValueError(f"Cannot generate 1% resistor within {resistance}")
      value = center

    # TODO we only need the first really so this is a bit inefficient
    suitable_packages = [(package_power, package) for package_power, package in self.PACKAGE_POWER
                         if package_power >= power[1] and (not footprint_spec or package == footprint_spec)]
    if not suitable_packages:
      raise ValueError(f"Cannot find suitable package for resistor needing {power[1]} W power")

    self.assign(self.resistance, value * Ohm(tol=self.TOLERANCE))
    self.assign(self.selected_power_rating, suitable_packages[0][0])

    self.footprint(
      'R', suitable_packages[0][1],
      {
        '1': self.a,
        '2': self.b,
      },
      # TODO mfr and part number
      value=f'{UnitUtils.num_to_prefix(value, 3)}, {self.TOLERANCE * 100:0.3g}%, {suitable_packages[0][0]}W',
    )


class ChipResistor(ESeriesResistor):
  TOLERANCE = 0.01
  PACKAGE_POWER = [  # sorted by order of preference (lowest power to highest power)
    # picked based on the most common power rating for a size at 100ohm on Digikey
    # (1.0/32, '01005'),  # KiCad doesn't seem to have a default footprint this small
    # (1.0/20, 'Resistor_SMD:R_0201_0603Metric'),
    # (1.0/16, 'Resistor_SMD:R_0402_1005Metric'),
    (1.0/10, 'Resistor_SMD:R_0603_1608Metric'),
    (1.0/8, 'Resistor_SMD:R_0805_2012Metric'),
    (1.0/4, 'Resistor_SMD:R_1206_3216Metric'),
    # (1.0/2, 'Resistor_SMD:R_1210_3225Metric'),  # actually not that common
    # (3.0/4, 'Resistor_SMD:R_2010_5025Metric'),  # actually not that common
    (1.0, 'Resistor_SMD:R_2512_6332Metric'),  # a good portion are also rated for 2W
  ]


class AxialResistor(ESeriesResistor):
  TOLERANCE = 0.01
  PACKAGE_POWER = [  # sorted by order of preference (lowest power to highest power)
    # picked based on the most common power rating for a size at 100ohm on Digikey
    (1.0/8, 'Resistor_THT:R_Axial_DIN0204_L3.6mm_D1.6mm_P5.08mm_Horizontal'),
    (1.0/4, 'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal'),
    (1.0/2, 'Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal'),
    (1.0, 'Resistor_THT:R_Axial_DIN0411_L9.9mm_D3.6mm_P12.70mm_Horizontal'),
    (2.0, 'Resistor_THT:R_Axial_DIN0414_L11.9mm_D4.5mm_P15.24mm_Horizontal'),
  ]


class AxialVerticalResistor(ESeriesResistor):
  TOLERANCE = 0.01
  PACKAGE_POWER = [  # sorted by order of preference (lowest power to highest power)
    # picked based on the most common power rating for a size at 100ohm on Digikey
    (1.0/8, 'Resistor_THT:R_Axial_DIN0204_L3.6mm_D1.6mm_P1.90mm_Vertical'),
    (1.0/4, 'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical'),
    (1.0/2, 'Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P2.54mm_Vertical'),
    (1.0, 'Resistor_THT:R_Axial_DIN0411_L9.9mm_D3.6mm_P5.08mm_Vertical'),
    (2.0, 'Resistor_THT:R_Axial_DIN0414_L11.9mm_D4.5mm_P5.08mm_Vertical'),
  ]


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
                    }), missing='discard') \


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

  def select_capacitor(self, capacitance: RangeVal, voltage: RangeVal,
                       single_nominal_capacitance: RangeVal,
                       part_spec: str, footprint_spec: str) -> None:
    def derated_capacitance(row: Dict[str, Any]) -> Tuple[float, float]:
      if voltage[1] < 3.6:  # x-intercept at 3.6v
        return row['capacitance']
      if (row['capacitance'][0] + row['capacitance'][1]) / 2 <= 1e-6:  # don't derate below 1uF
        return row['capacitance']
      if row['footprint'] not in self.DERATE_VOLTCO:
        return (0, 0)  # can't derate, generate obviously bogus and ignored value
      voltco = self.DERATE_VOLTCO[row['footprint']]
      return (
        row['capacitance'][0] * (1 - voltco * (voltage[1] - 3.6)),
        row['capacitance'][1] * (1 - voltco * (voltage[0] - 3.6))
      )

    single_cap_max = single_nominal_capacitance[1]

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
    elif capacitance[1] >= single_cap_max:
      parts = parts.sort(Column('Unit Price (USD)')) \
        .sort(Column('footprint')) \
        .sort(Column('nominal_capacitance'), reverse=True)  # pick the largest capacitor available
      part = parts.first(err=f"no parallel capacitors in ({capacitance}) F")

      num_caps = math.ceil(capacitance[0] / part['derated_capacitance'][0])
      assert num_caps * part['derated_capacitance'][1] < capacitance[1], "can't generate parallel caps within max capacitance limit"

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
  @init_in_parent
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.footprint_spec = self.Parameter(StringExpr(""))

    # Default to be overridden on a per-device basis
    self.single_cap_max = 22e-6
    self.single_nominal_capacitance = self.Parameter(RangeExpr((0, self.single_cap_max * 1.25)))  # maximum capacitance in a single part

    self.generator(self.select_capacitor_no_prod_table, self.capacitance, self.voltage, self.single_nominal_capacitance,
                   self.part_spec, self.footprint_spec)

    # Output values
    self.selected_capacitance = self.Parameter(RangeExpr())
    self.selected_derated_capacitance = self.Parameter(RangeExpr())
    self.selected_voltage_rating = self.Parameter(RangeExpr())

  # Chosen by a rough scan over available parts on Digikey
  # at voltages 10v, 16v, 25v, 50v, 100v, 250v
  # and capacitances 1.0, 2.2, 4.7
  #
  # For Class-1 dielectric (C0G/NP0), 20% tolerance
  # 0402: 50v/1nF
  # 0603: 100v/1nF, 50v/2.2nF ?
  # 0805: 100v/2.2nF, 50v/10nF
  # 1206: 100v/10nF
  #
  # For Class-2 dielectric (X**), 20% tolerance
  # 0402:                   50v /                0.1uF,     25v / 0.1uF,                      10v / 2.2uF
  # 0603:                   50v /                0.1uF,     25v /   1uF,     16v / 2.2uF,     10v /  10uF
  # 0805: 100v / 0.1uF,     50v / 0.1uF (maybe 0.22uF),     25v /  10uF
  # 1206: 100v / 0.1uF,     50v /                4.7uF,     25v /  10uF,                      10v /  22uF
  # 1210: 100v / 4.7uF,     50v /                 10uF,                      16v /  22uF,     10v /  47uF
  # 1812: 100v / 2.2uF,     50v /                  1uF,     25v /  10uF (though small sample size)

  # derating coefficients in terms of %capacitance / V over 3.6
  # 'Capacitor_SMD:C_0603_1608Metric'  # not supported, should not generate below 1uF

  PACKAGE_SPECS = {
    402: {
      'name'    : 'Capacitor_SMD:C_0402_1105Metric',
      'max'     :  1e-7,
      'derate'  : 0,
      'vc_pairs': {             50:   1e-7, 25: 1e-7,             10: 2.2e-6},
    },
    603: {
      'name'    : 'Capacitor_SMD:C_0603_1608Metric',
      'max'     : 1.1e-6,
      'derate'  : 0,
      'vc_pairs': {             50:   1e-7, 25: 1e-6, 16: 2.2e-6, 10:   1e-5},
    },
    805:{
      'name'    : 'Capacitor_SMD:C_0805_2012Metric',
      'max'     : 11e-6,
      'derate'  : 0.08,
      'vc_pairs': {100:   1e-7, 50:   1e-7, 25: 1e-5, },
    },
    1206: {
      'name'    : 'Capacitor_SMD:C_1206_3216Metric',
      'max'     : float('inf'),
      'derate'  : 0.04,
      'vc_pairs': {100:   1e-7, 50: 4.7e-6, 25: 1e-5,             10: 2.2e-5},
    },
    1210: {
      'name'    : 'Capacitor_SMD:C_1210_3225Metric',
      'max'     : float('inf'),
      'derate'  : 0,
      'vc_pairs': {100: 4.7e-6, 50:   1e-5,           16: 2.2e-5, 10: 4.7e-5},
    },
    1812: {
      'name'    : 'Capacitor_SMD:C_1812_4532Metric',
      'max'     : float('inf'),
      'derate'  : 0,
      'vc_pairs': {100: 2.2e-6, 50:   1e-6, 25: 1e-5, },
    },
  }

  def select_capacitor_no_prod_table(self, capacitance: RangeVal, voltage: RangeVal,
                                     single_nominal_capacitance: RangeVal,
                                     part_spec: str, footprint_spec: str) -> None:

    # capacitance: user-specified capacitance
    # single nominal capacitance: no single cap with requested capacitance, must generate multiple parallel caps
    # nominal capacitance: selected part's capacitance

    def valid_package_min_nominal_capacitance(package: int, capacitance: RangeVal, voltage: RangeVal) -> Tuple[float, float]:
      """
      Calculates if the package is a valid choice for the given capacitance and voltage.
      If the package is a valid choice, the function returns the minimum nominal capacitance
      for the specs. If the package is not valid, the function returns False.
      """
      avg_cap = (capacitance[0] + capacitance[1]) / 2
      avg_volt = (voltage[0] + voltage[1]) / 2

      # Calculate derated capacitance for the package
      if (avg_volt <= 3.6) or (avg_cap <= 1e-6):
        min_nominal_capacitance = capacitance
      else:
        voltco = self.PACKAGE_SPECS[package]['derate']
        min_nominal_capacitance = (
          capacitance[0] / (1 - voltco * (voltage[1] - 3.6)),
          capacitance[1] / (1 - voltco * (voltage[0] - 3.6))
        )

      # Check if package is still valid for the derated capacitance
      if self.PACKAGE_SPECS[package]['max'] >= avg_cap:
        for v, c in self.PACKAGE_SPECS[package]['vc_pairs'].items():
          if v >= voltage[1] and c >= min_nominal_capacitance[1]:
            return min_nominal_capacitance
      return False

    def select_package(capacitance: RangeVal, voltage: RangeVal) -> Tuple[float, float]:

      if footprint_spec == "":
        for package in sorted(self.PACKAGE_SPECS.keys()):
          package_derated_capacitance = valid_package_min_nominal_capacitance(package, capacitance, voltage)
          if package_derated_capacitance:
            return (self.PACKAGE_SPECS[package]['name'], package_derated_capacitance)
        return ("", (0, 0))
      else:
        package = int(footprint_spec.split('_')[2])
        package_derated_capacitance = valid_package_min_nominal_capacitance(package, capacitance, voltage)
        if package_derated_capacitance:
          return (footprint_spec, package_derated_capacitance)
      return (footprint_spec, (0, 0))

    value = choose_preferred_number(capacitance, 0, self.E24_SERIES_ZIGZAG, 2)
    valid_footprint_spec, min_nominal_capacitance = select_package(capacitance, voltage)

    if capacitance[1] > single_nominal_capacitance[1] or valid_footprint_spec == "":
      num_caps = math.ceil(capacitance[0] / self.single_cap_max)
      assert num_caps * self.single_cap_max < capacitance[1], "can't generate parallel caps within max capacitance limit"

      self.assign(self.selected_derated_capacitance, (
        num_caps * capacitance[0],
        num_caps * capacitance[1],
      ))
      self.assign(self.selected_capacitance, (
        num_caps * min_nominal_capacitance[0],
        num_caps * min_nominal_capacitance[1],
      ))

      cap_model = DummyCapacitor(capacitance=(self.single_cap_max, self.single_cap_max),
                                      voltage=self.voltage)
      self.c = ElementDict[DummyCapacitor]()
      for i in range(num_caps):
        self.c[i] = self.Block(cap_model)
        self.connect(self.c[i].pos, self.pos)
        self.connect(self.c[i].neg, self.neg)
    else:
      self.assign(self.selected_derated_capacitance, capacitance)
      self.assign(self.selected_capacitance, min_nominal_capacitance)

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

  PACKAGE_MIN_CAP = {
    'Capacitor_SMD:C_0603_1608Metric': 1e-7,
    'Capacitor_SMD:C_0805_2012Metric': 1.1e-6,
    'Capacitor_SMD:C_1206_3216Metric': 11e-6
  }

  def select_capacitor(self, capacitance: RangeVal, voltage: RangeVal,
                       single_nominal_capacitance: RangeVal,
                       part_spec: str, footprint_spec: str) -> None:

    # avg_cap = (capacitance[0] + capacitance[1]) / 2
    # for package_name in sorted(self.PACKAGE_MIN_CAP.keys())[::-1]:
    #   if avg_cap > self.PACKAGE_MIN_CAP[package_name]:
    #     self.calculated_package_size = package_name
    #     break

    # if not (footprint_spec == ""):
    #   self.calculated_package_size = footprint_spec

    self.assign(self.selected_capacitance, capacitance)
    self.assign(self.selected_derated_capacitance, capacitance)

    self.footprint(
      'C', sorted(self.PACKAGE_MIN_CAP.keys())[-1], # TODO fix to a parameter footprint
      {
        '1': self.pos,
        '2': self.neg,
      },
      value=f'{UnitUtils.num_to_prefix(capacitance[0], 3)}F'
    )

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
                    ), missing='discard') \


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

  def select_inductor(self, inductance: RangeVal, current: RangeVal, frequency: RangeVal,
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
