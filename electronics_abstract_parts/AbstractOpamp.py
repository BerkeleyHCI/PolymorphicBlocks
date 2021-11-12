from math import ceil, log10
from typing import NamedTuple, List, Tuple

from electronics_model import *
from .Categories import *
from .ESeriesUtil import ESeriesRatioUtil


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


class ResistorCalculator(ESeriesRatioUtil[AmplifierValues]):
  class NoMatchException(Exception):
    pass

  def __init__(self, series: List[float], tolerance: float):
    super().__init__(series)  # TODO custom range series
    self.tolerance = tolerance

  def _calculate_output(self, r1: float, r2: float) -> AmplifierValues:
    """This uses resistive divider conventions: R1 is output-side and R2 is ground-side
    """
    r1_range = Range.from_tolerance(r1, self.tolerance)
    r2_range = Range.from_tolerance(r2, self.tolerance)
    return AmplifierValues(
      (r1_range / r2_range) + 1,
      1 / (1 / r1_range + 1 / r2_range)
    )

  def _get_distance(self, proposed: AmplifierValues, target: AmplifierValues) -> List[float]:
    if proposed.ratio in target.ratio and proposed.parallel_impedance in target.parallel_impedance:
      return []
    else:
      return [
        abs(proposed.ratio.center() - target.ratio.center()),
        abs(proposed.parallel_impedance.center() - target.parallel_impedance.center())
      ]

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
    def decade_intersects(test_decade: Tuple[int, int]) -> bool:
      def range_of_decade(range_decade: int) -> Range:
        """Given a decade, return the range of possible values - for example, decade 0
        would mean 1.0, 2.2, 4.7 and would return a range of (1, 10)."""
        return Range(10 ** range_decade, 10 ** (range_decade + 1))
      def impedance_of_decade(r1r2_decade: Tuple[int, int]) -> Range:
        """Given R1, R2 decade as a tuple, returns the possible impedance range."""
        return 1 / (1 / range_of_decade(r1r2_decade[0]) + 1 / range_of_decade(r1r2_decade[1]))
      def ratio_of_decade(r1r2_decade: Tuple[int, int]) -> Range:
        """Given R1, R2 decade as a tuple, returns the possible ratio range."""
        return 1 / (range_of_decade(r1r2_decade[0]) / range_of_decade(r1r2_decade[1]) + 1)

      return (target.ratio.intersects(ratio_of_decade(test_decade)) and
              target.parallel_impedance.intersects(impedance_of_decade(test_decade)))

    new_decades = []

    # test adjustments that shift both decades in the same direction (changes impedance)
    down_decade = (decade[0] - 1, decade[1] - 1)
    if decade_intersects(down_decade):
      new_decades.append(down_decade)
    up_decade = (decade[0] + 1, decade[1] + 1)
    if decade_intersects(up_decade):
      new_decades.append(up_decade)

    # test adjustments that shift decades independently (changes ratio)
    up_r1_decade = (decade[0] - 1, decade[1])
    if decade_intersects(up_r1_decade):
      new_decades.append(up_r1_decade)
    up_r2_decade = (decade[0], decade[1] + 1)
    if decade_intersects(up_r2_decade):
      new_decades.append(up_r2_decade)
    down_r1_decade = (decade[0] + 1, decade[1])
    if decade_intersects(down_r1_decade):
      new_decades.append(down_r1_decade)
    down_r2_decade = (decade[0], decade[1] - 1)
    if decade_intersects(down_r2_decade):
      new_decades.append(down_r2_decade)

    return new_decades


class Amplifier(AnalogFilter):
  """Opamp non-inverting amplifier, outputs a scaled-up version of the input signal.

  From https://en.wikipedia.org/wiki/Operational_amplifier_applications#Non-inverting_amplifier:
  Vout = Vin (1 + R1/R2)

  The input and output impedances given are a bit more complex, so this simplifies it to
  the opamp's specified pin impedances - TODO: is this correct(ish)?
  """
  def __init__(self):
    super().__init__()

    self.amp = self.Block(Opamp())

    self.pwr = self.Export(self.amp.pwr, [Power])
    self.gnd = self.Export(self.amp.gnd, [Common])

    self.input = self.Export(self.amp.inp, [Input])
    self.output = self.Export(self.amp.out, [Output])

    # TODO ADD PARAMETERS, IMPLEMENT ME


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
