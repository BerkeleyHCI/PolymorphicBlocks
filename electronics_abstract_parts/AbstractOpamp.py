from math import ceil, log10
from typing import NamedTuple, List, Tuple

from electronics_abstract_parts import Resistor
from electronics_model import *
from .Categories import *
from .ESeriesUtil import ESeriesRatioUtil, ESeriesUtil


@abstract_block
class Opamp(Block):
  """Base class for opamps. Parameters need to be more restricted in subclasses.
  """

  @init_in_parent
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink(), [Power])
    self.gnd = self.Port(Ground(), [Common])

    self.inp = self.Port(AnalogSink())
    self.inn = self.Port(AnalogSink())
    self.out = self.Port(AnalogSource())


class OpampFollower(AnalogFilter):
  """Opamp follower circuit, outputs the same signal as the input (but probably stronger)."""
  def __init__(self):
    super().__init__()

    self.amp = self.Block(Opamp())

    self.pwr = self.Export(self.amp.pwr, [Power])
    self.gnd = self.Export(self.amp.gnd, [Common])

    self.input = self.Export(self.amp.inp, [Input])
    self.output = self.Export(self.amp.out, [Output])
    self.connect(self.amp.out, self.amp.inn)


class AmplifierValues(NamedTuple):
  amplification: Range  # amplification factor from in to out
  parallel_impedance: Range  # parallel impedance into the opamp negative pin

  @staticmethod
  def from_resistors(rhigh: Range, rlow: Range) -> 'AmplifierValues':
    """Calculates range of outputs given range of resistors.
    rlow is the low-side resistor (Vin- to GND) and rhigh is the high-side resistor (Vin- to Vout)."""
    return AmplifierValues(
      (rhigh / rlow) + 1,
      1 / (1 / rhigh + 1 / rlow)
    )

  def distance_to(self, spec: 'AmplifierValues') -> List[float]:
    """Returns a distance vector to the spec, or the empty list if satisfying the spec"""
    if self.amplification in spec.amplification and self.parallel_impedance in spec.parallel_impedance:
      return []
    else:
      return [
        abs(self.amplification.center() - spec.amplification.center()),
        abs(self.parallel_impedance.center() - spec.parallel_impedance.center())
      ]

  def intersects(self, spec: 'AmplifierValues') -> bool:
    """Return whether this intersects with some spec - whether some subset of the resistors
    can potentially satisfy some spec"""
    return self.amplification.intersects(spec.amplification) and \
           self.parallel_impedance.intersects(
             spec.parallel_impedance)

class ResistorCalculator(ESeriesRatioUtil[AmplifierValues]):
  class NoMatchException(Exception):
    pass

  def __init__(self, series: List[float], tolerance: float):
    super().__init__(series)  # TODO custom range series
    self.tolerance = tolerance

  def _calculate_output(self, r1: float, r2: float) -> AmplifierValues:
    """This uses resistive divider conventions: R1 is output-side and R2 is ground-side
    """
    return AmplifierValues.from_resistors(
      Range.from_tolerance(r1, self.tolerance),
      Range.from_tolerance(r2, self.tolerance))

  def _get_distance(self, proposed: AmplifierValues, target: AmplifierValues) -> List[float]:
    return proposed.distance_to(target)

  def _no_result_error(self, best_values: Tuple[float, float], best: AmplifierValues,
                       target: AmplifierValues) -> Exception:
    return ResistorCalculator.NoMatchException(
      f"No resistive divider found for target amplification={target.amplification}, impedance={target.parallel_impedance}, "
      f"best: {best_values} with amplification={best.amplification}, impedance={best.parallel_impedance}"
    )

  def _get_initial_decades(self, target: AmplifierValues) -> List[Tuple[int, int]]:
    # TODO: adjust initial ratio to intersect? - see issues with ResistiveDividerCalculator
    decade = ceil(log10(target.parallel_impedance.upper))
    return [(decade, decade)]

  def _get_next_decades(self, decade: Tuple[int, int], target: AmplifierValues) -> \
      List[Tuple[int, int]]:
    def range_of_decade(range_decade: int) -> Range:
      """Given a decade, return the range of possible values - for example, decade 0
      would mean 1.0, 2.2, 4.7 and would return a range of (1, 10)."""
      return Range(10 ** range_decade, 10 ** (range_decade + 1))

    test_decades = [
      # adjustments shifting both decades in the same direction (changes impedance)
      (decade[0] - 1, decade[1] - 1),
      (decade[0] + 1, decade[1] + 1),
      # adjustments shifting decades independently (changes ratio)
      (decade[0] - 1, decade[1]),
      (decade[0], decade[1] + 1),
      (decade[0] + 1, decade[1]),
      (decade[0], decade[1] - 1),
    ]

    new_decades = [decade for decade in test_decades
                   if AmplifierValues.from_resistors(
                       range_of_decade(decade[0]), range_of_decade(decade[1])
                   ).intersects(target)
                   ]

    return new_decades


class Amplifier(AnalogFilter, GeneratorBlock):
  """Opamp non-inverting amplifier, outputs a scaled-up version of the input signal.

  From https://en.wikipedia.org/wiki/Operational_amplifier_applications#Non-inverting_amplifier:
  Vout = Vin (1 + R1/R2)

  The input and output impedances given are a bit more complex, so this simplifies it to
  the opamp's specified pin impedances - TODO: is this correct(ish)?
  """
  def __init__(self, amplification: RangeLike = RangeExpr(), impedance: RangeLike = (10, 100)*kOhm):
    super().__init__()

    self.amp = self.Block(Opamp())

    self.pwr = self.Export(self.amp.pwr, [Power])
    self.gnd = self.Export(self.amp.gnd, [Common])

    self.input = self.Export(self.amp.inp, [Input])
    self.output = self.Export(self.amp.out, [Output])

    self.amplification = self.Parameter(RangeExpr(amplification))
    self.impedance = self.Parameter(RangeExpr(impedance))

    self.series = self.Parameter(IntExpr(24))  # can be overridden by refinements
    self.tolerance = self.Parameter(FloatExpr(0.01))  # can be overridden by refinements

    self.generator(self.generate_resistors, self.amplification, self.impedance, self.series, self.tolerance)

  def generate_resistors(self, amplification: Range, impedance: Range, series: int, tolerance: float) -> None:
    calculator = ResistorCalculator(ESeriesUtil.SERIES[series], tolerance)
    top_resistance, bottom_resistance = calculator.find(AmplifierValues(amplification, impedance))

    self.r1 = self.Block(Resistor(
      resistance=Range.from_tolerance(top_resistance, tolerance)
    ))
    self.r2 = self.Block(Resistor(
      resistance=Range.from_tolerance(bottom_resistance, tolerance)
    ))


class DifferentialAmplifier(AnalogFilter):
  """Opamp differential amplifier, outputs the difference between the input nodes, scaled by some factor,
  and offset from some reference node.
  This implementation uses the same resistance for the two input resistors (R1, R2),
  and the same resistance for the feedback and reference resistors (Rf, Rg).
  From https://en.wikipedia.org/wiki/Operational_amplifier_applications#Differential_amplifier_(difference_amplifier):
  Vout = Rf/R1 * (Vp - Vn)

  Impedance equations from https://e2e.ti.com/blogs_/archives/b/precisionhub/posts/overlooking-the-obvious-the-input-impedance-of-a-difference-amplifier
    (ignoring the opamp input impedances, which we assume are >> the resistors)
  Rin,p = R1 / (1 - (Rg / (R2+Rg)) * (Vin,n / Vin,p))
  Rin,n = R2 + Rg
  Rout = opamp output impedance - TODO: is this correct?

  ratio specifies Rf/R1, the amplification ratio.

  """
  def __init__(self, ratio: RangeExpr = RangeExpr()):
    super().__init__()

    self.amp = self.Block(Opamp())

    self.pwr = self.Export(self.amp.pwr, [Power])
    self.gnd = self.Export(self.amp.gnd, [Common])

    self.input_positive = self.Port(AnalogSink())
    self.input_negative = self.Port(AnalogSink())
    self.output_reference = self.Port(AnalogSink())
    self.output = self.Port(AnalogSource())

    # TODO ADD PARAMETERS, IMPLEMENT ME


class IntegratorInverting(AnalogFilter):
  """Opamp integrator, outputs the negative integral of the input signal, relative to some reference signal.
  Will clip to the input voltage rails.

  From https://en.wikipedia.org/wiki/Operational_amplifier_applications#Inverting_integrator:
  Vout = - 1/RC * int(Vin) (integrating over time)
  """
  def __init__(self):
    super().__init__()

    self.amp = self.Block(Opamp())

    self.pwr = self.Export(self.amp.pwr, [Power])
    self.gnd = self.Export(self.amp.gnd, [Common])

    self.input = self.Port(AnalogSink())
    self.output = self.Port(AnalogSource())
    self.reference = self.Port(AnalogSink())  # negative reference for the input and output signals

    # TODO ADD PARAMETERS, IMPLEMENT ME
