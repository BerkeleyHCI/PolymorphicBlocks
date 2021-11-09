from typing import NamedTuple
import math

from electronics_abstract_parts import *
from electronics_abstract_parts.Categories import DummyDevice
from .DigikeyTable import *


class MlccTable(DigikeyTable):
  CAPACITANCE = PartsTableColumn(Range)
  NOMINAL_CAPACITANCE = PartsTableColumn(float)
  VOLTAGE_RATING = PartsTableColumn(Range)
  FOOTPRINT = PartsTableColumn(str)  # KiCad footprint name

  PACKAGE_FOOTPRINT_MAP = {
    '0603 (1608 Metric)': 'Capacitor_SMD:C_0603_1608Metric',
    '0805 (2012 Metric)': 'Capacitor_SMD:C_0805_2012Metric',
    '1206 (3216 Metric)': 'Capacitor_SMD:C_1206_3216Metric',
  }

  @classmethod
  def _generate_table(cls) -> PartsTable:
    def parse_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      new_cols: Dict[PartsTableColumn, Any] = {}
      try:
        footprint = cls.PACKAGE_FOOTPRINT_MAP[row['Package / Case']]
        nominal_capacitance = PartsTableUtil.parse_value(row['Capacitance'], 'F')

        # enforce minimum packages, note the cutoffs are exclusive
        if nominal_capacitance > 10e-6 and footprint not in [
          'Capacitor_SMD:C_1206_3216Metric',
        ]:
          return None
        elif nominal_capacitance > 1e-6 and footprint not in [
          'Capacitor_SMD:C_0805_2012Metric',
          'Capacitor_SMD:C_1206_3216Metric',
        ]:
          return None

        new_cols[cls.FOOTPRINT] = footprint
        new_cols[cls.CAPACITANCE] = Range.from_tolerance(
          nominal_capacitance,
          PartsTableUtil.parse_tolerance(row['Tolerance'])
        )
        new_cols[cls.NOMINAL_CAPACITANCE] = nominal_capacitance
        new_cols[cls.VOLTAGE_RATING] = Range.zero_to_upper(
          PartsTableUtil.parse_value(row['Voltage - Rated'], 'V')
        )

        new_cols.update(cls._parse_digikey_common(row))

        return new_cols
      except (KeyError, PartsTableUtil.ParseError):
        return None

    raw_table = PartsTable.from_csv_files(PartsTableUtil.with_source_dir([
      'Digikey_MLCC_SamsungCl_1pF_E12.csv',
      'Digikey_MLCC_SamsungCl_1nF_E6.csv',
      'Digikey_MLCC_SamsungCl_1uF_E3.csv',
      'Digikey_MLCC_YageoCc_1pF_E12_1.csv',
      'Digikey_MLCC_YageoCc_1pF_E12_2.csv',
      'Digikey_MLCC_YageoCc_1nF_E6_1.csv',
      'Digikey_MLCC_YageoCc_1nF_E6_2.csv',
      'Digikey_MLCC_YageoCc_1uF_E3.csv',
    ], 'resources'), encoding='utf-8-sig')
    return raw_table.map_new_columns(parse_row).sort_by(
      lambda row: [row[cls.FOOTPRINT], row[cls.COST]]  # prefer smaller first
    )


class SmtCeramicCapacitor(Capacitor, FootprintBlock, GeneratorBlock):
  DERATE_VOLTCO = {  # in terms of %capacitance / V over 3.6
    #  'Capacitor_SMD:C_0603_1608Metric'  # not supported, should not generate below 1uF
    'Capacitor_SMD:C_0805_2012Metric': 0.08,
    'Capacitor_SMD:C_1206_3216Metric': 0.04,
  }
  DERATE_MIN_VOLTAGE = 3.6  # voltage at which derating is zero
  DERATE_MIN_CAPACITANCE = 1.0e-6
  DERATED_CAPACITANCE = PartsTableColumn(Range)

  PARALLEL_COUNT = PartsTableColumn(int)
  PARALLEL_CAPACITANCE = PartsTableColumn(Range)
  PARALLEL_DERATED_CAPACITANCE = PartsTableColumn(Range)
  PARALLEL_COST = PartsTableColumn(float)

  @init_in_parent
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.part_spec = self.Parameter(StringExpr(""))
    self.footprint_spec = self.Parameter(StringExpr(""))

    # Default that can be overridden
    self.single_nominal_capacitance = self.Parameter(RangeExpr((0, 22)*uFarad))  # maximum capacitance in a single part

    self.generator(self.select_capacitor, self.capacitance, self.voltage, self.single_nominal_capacitance,
                   self.part_spec, self.footprint_spec)

    # Output values
    self.selected_capacitance = self.Parameter(RangeExpr())
    self.selected_derated_capacitance = self.Parameter(RangeExpr())
    self.selected_voltage_rating = self.Parameter(RangeExpr())

  def select_capacitor(self, capacitance: Range, voltage: Range,
                       single_nominal_capacitance: Range,
                       part_spec: str, footprint_spec: str) -> None:
    # Pre-filter out by the static parameters
    # Note that we can't filter out capacitance before derating
    prefiltered_parts = MlccTable.table().filter(lambda row: (
        (not part_spec or part_spec == row[MlccTable.PART_NUMBER]) and
        (not footprint_spec or footprint_spec == row[MlccTable.FOOTPRINT]) and
        voltage.fuzzy_in(row[MlccTable.VOLTAGE_RATING]) and
        Range.exact(row[MlccTable.NOMINAL_CAPACITANCE]).fuzzy_in(single_nominal_capacitance)
    ))

    def derate_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      if voltage.upper < self.DERATE_MIN_VOLTAGE:  # zero derating at low voltages
        derated = row[MlccTable.CAPACITANCE]
      elif row[MlccTable.NOMINAL_CAPACITANCE] <= self.DERATE_MIN_CAPACITANCE:  # don't derate below 1uF
        derated = row[MlccTable.CAPACITANCE]
      elif row[MlccTable.FOOTPRINT] not in self.DERATE_VOLTCO:  # should be rare, small capacitors should hit the above
        return None
      else:  # actually derate
        voltco = self.DERATE_VOLTCO[row[MlccTable.FOOTPRINT]]
        factor = 1 - voltco * (voltage.upper - 3.6)
        derated = row[MlccTable.CAPACITANCE] * Range(factor, 1)

      return {self.DERATED_CAPACITANCE: derated}

    # If the min required capacitance is above the highest post-derating minimum capacitance, use the parts table.
    # An empty parts table handles the case where it's below the minimum or does not match within a series.
    derated_parts = prefiltered_parts.map_new_columns(
      derate_row
    )
    derated_max_min_capacitance = max(derated_parts.map(lambda row: row[self.DERATED_CAPACITANCE].lower))

    if capacitance.lower <= derated_max_min_capacitance:
      part = derated_parts.filter(lambda row: (
          row[self.DERATED_CAPACITANCE] in capacitance
      )).first(f"no single capacitor in {capacitance} F, {voltage} V")

      self.assign(self.selected_voltage_rating, part[MlccTable.VOLTAGE_RATING])
      self.assign(self.selected_capacitance, part[MlccTable.CAPACITANCE])
      self.assign(self.selected_derated_capacitance, part[self.DERATED_CAPACITANCE])

      self.footprint(
        'C', part[MlccTable.FOOTPRINT],
        {
          '1': self.pos,
          '2': self.neg,
        },
        mfr=part[MlccTable.MANUFACTURER], part=part[MlccTable.PART_NUMBER],
        value=f"{part['Capacitance']}, {part['Voltage - Rated']}",
        datasheet=part[MlccTable.DATASHEETS]
      )
    else:  # Otherwise, generate multiple capacitors
      # Additionally annotate the table by total cost and count, sort by lower count then total cost
      def parallel_row(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
        new_cols: Dict[PartsTableColumn, Any] = {}
        count = math.ceil(capacitance.lower / row[self.DERATED_CAPACITANCE].lower)
        derated_parallel_capacitance = row[self.DERATED_CAPACITANCE] * count
        if not derated_parallel_capacitance.fuzzy_in(capacitance):  # not satisfying spec
          return None

        new_cols[self.PARALLEL_COUNT] = count
        new_cols[self.PARALLEL_DERATED_CAPACITANCE] = derated_parallel_capacitance
        new_cols[self.PARALLEL_CAPACITANCE] = row[MlccTable.CAPACITANCE] * count
        new_cols[self.PARALLEL_COST] = row[MlccTable.COST] * count

        return new_cols

      part = derated_parts.map_new_columns(
        parallel_row
      ).sort_by(lambda row:
        (row[self.PARALLEL_COUNT], row[self.PARALLEL_COST])
      ).first(f"no parallel capacitor in {capacitance} F, {voltage} V")

      self.assign(self.selected_voltage_rating, part[MlccTable.VOLTAGE_RATING])
      self.assign(self.selected_capacitance, part[self.PARALLEL_CAPACITANCE])
      self.assign(self.selected_derated_capacitance, part[self.PARALLEL_DERATED_CAPACITANCE])

      cap_model = DummyCapacitor(capacitance=part[MlccTable.NOMINAL_CAPACITANCE],
                                 voltage=self.voltage,
                                 footprint=part[MlccTable.FOOTPRINT],
                                 manufacturer=part[MlccTable.MANUFACTURER], part_number=part[MlccTable.PART_NUMBER],
                                 value=f"{part['Capacitance']}, {part['Voltage - Rated']}")
      self.c = ElementDict[DummyCapacitor]()
      for i in range(part[self.PARALLEL_COUNT]):
        self.c[i] = self.Block(cap_model)
        self.connect(self.c[i].pos, self.pos)
        self.connect(self.c[i].neg, self.neg)


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

      cap_model = DummyCapacitor(capacitance=Range.exact(self.SINGLE_CAP_MAX), voltage=voltage,
                                 footprint=split_package,
                                 value=f'{UnitUtils.num_to_prefix(self.SINGLE_CAP_MAX, 3)}F')
      self.c = ElementDict[DummyCapacitor]()
      for i in range(num_caps):
        self.c[i] = self.Block(cap_model)
        self.connect(self.c[i].pos, self.pos)
        self.connect(self.c[i].neg, self.neg)
    else:
      value = ESeriesUtil.choose_preferred_number(nominal_capacitance, 0, ESeriesUtil.E24_SERIES[24], 2)
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


class DummyCapacitor(DummyDevice, Capacitor, FootprintBlock):
  """
  Dummy capacitor that takes in all its parameters (footprint, value, etc) and does not do any computation.
  Used as the leaf block for generating parallel capacitors.
  """

  @init_in_parent
  def __init__(self, footprint: StringLike = "",
               manufacturer: StringLike = "", part_number: StringLike = "", value: StringLike = "",
               *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.footprint(
      'C', footprint,
      {
        '1': self.pos,
        '2': self.neg,
      },
      mfr=manufacturer, part=part_number,
      value=value
    )
