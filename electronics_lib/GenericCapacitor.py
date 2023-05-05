from typing import NamedTuple, Dict, Optional
import math

from electronics_abstract_parts import *


class GenericMlcc(Capacitor, FootprintBlock, SmdStandardPackage, GeneratorBlock):
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
  def __init__(self, *args, footprint_spec: StringLike = "", derating_coeff: FloatLike = 1.0, **kwargs):
    """
    footprint specifies an optional constraint on footprint
    derating_coeff specifies an optional derating coefficient (1.0 = no derating), that does not scale with package.
    """
    super().__init__(*args, **kwargs)

    self.capacitance_value = self.GeneratorParam(self.capacitance)
    self.voltage_value = self.GeneratorParam(self.voltage)
    self.footprint_spec = self.GeneratorParam(footprint_spec)
    self.smd_min_package_value = self.GeneratorParam(self.smd_min_package)
    self.derating_coeff = self.GeneratorParam(derating_coeff)

    # Output values
    self.selected_nominal_capacitance = self.Parameter(RangeExpr())

    self.assign(self.actual_capacitance, self.selected_nominal_capacitance)
    self.assign(self.actual_voltage_rating, self.voltage)  # TODO use package-based voltage rating


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

  def generate(self) -> None:
    """
    Selects a generic capacitor without using product tables

    :param capacitance: user-specified (derated) capacitance
    :param voltage: user-specified voltage
    :param single_nominal_capacitance: used when no single cap with requested capacitance, must generate multiple parallel caps,
                                       actually refers to max capacitance for a given part
    :param footprint_spec: user-specified package footprint
    :param derating_coeff: user-specified derating coefficient, if used then footprint_spec must be specified
    """
    super().generate()
    footprint = self.footprint_spec.get()

    def select_package(nominal_capacitance: float, voltage: Range) -> Optional[str]:
      minimum_invalid_footprints = SmdStandardPackage.get_smd_packages_below(
        self.smd_min_package_value.get(), TableDeratingCapacitor.SMD_FOOTPRINT_MAP)
      package_options = [spec for spec in self.PACKAGE_SPECS
                         if (not footprint or spec.name == footprint) and
                         (spec.name not in minimum_invalid_footprints)]

      for package in package_options:
        if package.max >= nominal_capacitance:
          for package_max_voltage, package_max_capacitance in package.vc_pairs.items():
            if package_max_voltage >= voltage.upper and package_max_capacitance >= nominal_capacitance:
              return package.name
      return None

    nominal_capacitance = self.capacitance_value.get() / self.derating_coeff.get()

    num_caps = math.ceil(nominal_capacitance.lower / self.SINGLE_CAP_MAX)
    if num_caps > 1:
      assert num_caps * self.SINGLE_CAP_MAX < nominal_capacitance.upper, "can't generate parallel caps within max capacitance limit"

      self.assign(self.selected_nominal_capacitance, num_caps * nominal_capacitance)

      if footprint == "":
        split_package = self.MAX_CAP_PACKAGE
      else:
        split_package = footprint

      cap_model = DummyCapacitorFootprint(
        capacitance=Range.exact(self.SINGLE_CAP_MAX), voltage=self.voltage_value.expr(),
        footprint=split_package,
        value=f'{UnitUtils.num_to_prefix(self.SINGLE_CAP_MAX, 3)}F')
      self.c = ElementDict[DummyCapacitorFootprint]()
      for i in range(num_caps):
        self.c[i] = self.Block(cap_model)
        self.connect(self.c[i].pos, self.pos)
        self.connect(self.c[i].neg, self.neg)
    else:
      value = ESeriesUtil.choose_preferred_number(nominal_capacitance, ESeriesUtil.SERIES[24], 0)
      assert value is not None, "cannot select a preferred number"
      valid_footprint = select_package(value, self.voltage_value.get())
      assert valid_footprint is not None, "cannot select a valid footprint"
      self.assign(self.selected_nominal_capacitance, value)

      self.footprint(
        'C', valid_footprint,
        {
          '1': self.pos,
          '2': self.neg,
        },
        value=f'{UnitUtils.num_to_prefix(value, 3)}F'
      )
