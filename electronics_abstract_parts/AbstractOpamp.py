from math import ceil, log10
from typing import List, Tuple

from electronics_abstract_parts import Resistor
from .Categories import *
from .ESeriesUtil import ESeriesRatioUtil, ESeriesUtil, ESeriesRatioValue


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


class AmplifierValues(ESeriesRatioValue):
  def __init__(self, amplification: Range, parallel_impedance: Range):
    self.amplification = amplification  # amplification factor from in to out
    self.parallel_impedance = parallel_impedance  # parallel impedance into the opamp negative pin

  @staticmethod
  def from_resistors(r1_range: Range, r2_range: Range) -> 'AmplifierValues':
    """r2 is the low-side resistor (Vin- to GND) and r1 is the high-side resistor (Vin- to Vout)."""
    return AmplifierValues(
      (r1_range / r2_range) + 1,
      1 / (1 / r1_range + 1 / r2_range)
    )

  def initial_test_decades(self) -> Tuple[int, int]:
    decade = ceil(log10(self.parallel_impedance.upper))
    return decade, decade

  def distance_to(self, spec: 'AmplifierValues') -> List[float]:
    if self.amplification in spec.amplification and self.parallel_impedance in spec.parallel_impedance:
      return []
    else:
      return [
        abs(self.amplification.center() - spec.amplification.center()),
        abs(self.parallel_impedance.center() - spec.parallel_impedance.center())
      ]

  def intersects(self, spec: 'AmplifierValues') -> bool:
    return self.amplification.intersects(spec.amplification) and \
           self.parallel_impedance.intersects(
             spec.parallel_impedance)


class Amplifier(AnalogFilter, GeneratorBlock):
  """Opamp non-inverting amplifier, outputs a scaled-up version of the input signal.

  From https://en.wikipedia.org/wiki/Operational_amplifier_applications#Non-inverting_amplifier:
  Vout = Vin (1 + R1/R2)

  The input and output impedances given are a bit more complex, so this simplifies it to
  the opamp's specified pin impedances - TODO: is this correct(ish)?
  """
  @init_in_parent
  def __init__(self, amplification: RangeLike = RangeExpr(), impedance: RangeLike = (10, 100)*kOhm):
    super().__init__()

    self.amp = self.Block(Opamp())

    self.pwr = self.Export(self.amp.pwr, [Power])
    self.gnd = self.Port(Ground(), [Common])
    # self.gnd = self.Export(self.amp.gnd, [Common])  # TODO staged generators

    self.input = self.Export(self.amp.inp, [Input])
    # self.output = self.Export(self.amp.out, [Output])
    self.output = self.Port(AnalogSource(), [Output])

    self.amplification = self.Parameter(RangeExpr(amplification))
    self.impedance = self.Parameter(RangeExpr(impedance))

    self.series = self.Parameter(IntExpr(24))  # can be overridden by refinements
    self.tolerance = self.Parameter(FloatExpr(0.01))  # can be overridden by refinements

    self.generator(self.generate_resistors, self.amplification, self.impedance, self.series, self.tolerance,
                   targets=[self.gnd])

  def generate_resistors(self, amplification: Range, impedance: Range, series: int, tolerance: float) -> None:
    calculator = ESeriesRatioUtil(ESeriesUtil.SERIES[series], tolerance, AmplifierValues)
    top_resistance, bottom_resistance = calculator.find(AmplifierValues(amplification, impedance))

    self.r1 = self.Block(Resistor(
      resistance=Range.from_tolerance(top_resistance, tolerance)
    ))
    self.r2 = self.Block(Resistor(
      resistance=Range.from_tolerance(bottom_resistance, tolerance)
    ))
    self.connect(self.amp.out, self.output, self.r1.a.as_analog_sink(

    ))
    self.connect(self.r1.b.as_analog_source(

    ), self.r2.a.as_analog_sink(

    ), self.amp.inn)
    self.connect(self.r2.b.as_ground(), self.gnd, self.amp.gnd)


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
