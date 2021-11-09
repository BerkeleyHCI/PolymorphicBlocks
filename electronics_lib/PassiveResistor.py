from typing import List, Tuple
from electronics_abstract_parts import *


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
  def select_resistor(self, resistance: Range, power: Range, footprint_spec: str) -> None:
    value = ESeriesUtil.choose_preferred_number(resistance, self.TOLERANCE, ESeriesUtil.E24_SERIES[24], 2)

    if value is None:  # failed to find a preferred resistor, choose the center within tolerance
      center = resistance.center()
      min_tolerance = center * self.TOLERANCE
      if (center - resistance.lower) < min_tolerance or (resistance.upper - center < min_tolerance):
        # TODO should there be a better way of communicating generator failures?
        raise ValueError(f"Cannot generate 1% resistor within {resistance}")
      value = center

    # TODO we only need the first really so this is a bit inefficient
    suitable_packages = [(package_power, package) for package_power, package in self.PACKAGE_POWER
                         if package_power >= power.upper and (not footprint_spec or package == footprint_spec)]
    if not suitable_packages:
      raise ValueError(f"Cannot find suitable package for resistor needing {power.upper} W power")

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
