from math import ceil, log10
from typing import List, Tuple

from electronics_abstract_parts import Resistor, Capacitor
from .Categories import *
from .ESeriesUtil import ESeriesRatioUtil, ESeriesUtil, ESeriesRatioValue


@abstract_block
class Opamp(Block):
  """Base class for opamps. Parameters need to be more restricted in subclasses.
  """
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
    decade = ceil(log10(self.parallel_impedance.center()))
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
           self.parallel_impedance.intersects(spec.parallel_impedance)


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
    self.gnd = self.Export(self.amp.gnd, [Common])

    self.input = self.Export(self.amp.inp, [Input])
    # self.output = self.Export(self.amp.out, [Output])
    self.output = self.Port(AnalogSource(), [Output])
    self.reference = self.Port(AnalogSink())

    self.amplification = self.Parameter(RangeExpr(amplification))
    self.impedance = self.Parameter(RangeExpr(impedance))

    self.series = self.Parameter(IntExpr(24))  # can be overridden by refinements
    self.tolerance = self.Parameter(FloatExpr(0.01))  # can be overridden by refinements

    self.generator(self.generate_resistors, self.amplification, self.impedance, self.series, self.tolerance,
                   targets=[self.reference])

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
      impedance=self.r1.resistance + self.r2.resistance
    ))
    self.connect(self.r1.b.as_analog_source(
      voltage_out=self.amp.out.voltage_out,
      impedance=1/(1/self.r1.resistance + 1/self.r2.resistance)
    ), self.r2.a.as_analog_sink(
      # treated as an ideal sink for now
    ), self.amp.inn)
    self.connect(self.reference, self.r2.b.as_analog_sink(
      impedance=self.r1.resistance + self.r2.resistance
    ))


class DifferentialValues(ESeriesRatioValue):
  def __init__(self, ratio: Range, input_impedance: Range):
    self.ratio = ratio  # ratio from difference between inputs to output
    self.input_impedance = input_impedance  # resistance of the input resistor

  @staticmethod
  def from_resistors(r1_range: Range, r2_range: Range) -> 'DifferentialValues':
    """r1 is the input side resistance and r2 is the feedback or ground resistor."""
    return DifferentialValues(
      (r2_range / r1_range),
      r1_range
    )

  def initial_test_decades(self) -> Tuple[int, int]:
    r1_decade = ceil(log10(self.input_impedance.center()))
    r2_decade = ceil(log10((self.input_impedance * self.ratio).center()))
    return r1_decade, r2_decade

  def distance_to(self, spec: 'DifferentialValues') -> List[float]:
    if self.ratio in spec.ratio and self.input_impedance in spec.input_impedance:
      return []
    else:
      return [
        abs(self.ratio.center() - spec.ratio.center()),
        abs(self.input_impedance.center() - spec.input_impedance.center())
      ]

  def intersects(self, spec: 'DifferentialValues') -> bool:
    return self.ratio.intersects(spec.ratio) and \
           self.input_impedance.intersects(spec.input_impedance)


class DifferentialAmplifier(AnalogFilter, GeneratorBlock):
  """Opamp differential amplifier, outputs the difference between the input nodes, scaled by some factor,
  and offset from some reference node.
  This implementation uses the same resistance for the two input resistors (R1, R2),
  and the same resistance for the feedback and reference resistors (Rf, Rg).
  From https://en.wikipedia.org/wiki/Operational_amplifier_applications#Differential_amplifier_(difference_amplifier):
  Vout = Rf/R1 * (Vp - Vn)

  Impedance equations from https://e2e.ti.com/blogs_/archives/b/precisionhub/posts/overlooking-the-obvious-the-input-impedance-of-a-difference-amplifier
    (ignoring the opamp input impedances, which we assume are >> the resistors)
  Rin,n = R1 / (1 - (Rg / (R2+Rg)) * (Vin,n / Vin,p))
  Rin,p = R2 + Rg
  Rout = opamp output impedance - TODO: is this correct?

  ratio specifies Rf/R1, the amplification ratio.
  """
  @init_in_parent
  def __init__(self, ratio: RangeLike = RangeExpr(), input_impedance: RangeLike = RangeExpr()):
    super().__init__()

    self.amp = self.Block(Opamp())
    self.pwr = self.Export(self.amp.pwr, [Power])
    self.gnd = self.Export(self.amp.gnd, [Common])

    self.input_positive = self.Port(AnalogSink())
    self.input_negative = self.Port(AnalogSink())
    self.output_reference = self.Port(AnalogSink())
    self.output = self.Port(AnalogSource())

    self.ratio = self.Parameter(RangeExpr(ratio))
    self.input_impedance = self.Parameter(RangeExpr(input_impedance))

    self.series = self.Parameter(IntExpr(24))  # can be overridden by refinements
    self.tolerance = self.Parameter(FloatExpr(0.01))  # can be overridden by refinements

    self.generator(self.generate_resistors, self.ratio, self.input_impedance, self.series, self.tolerance,
                   targets=[self.input_positive, self.input_negative, self.output_reference])

  def generate_resistors(self, ratio: Range, input_impedance: Range, series: int, tolerance: float) -> None:
    calculator = ESeriesRatioUtil(ESeriesUtil.SERIES[series], tolerance, DifferentialValues)
    r1_resistance, rf_resistance = calculator.find(DifferentialValues(ratio, input_impedance))

    self.r1 = self.Block(Resistor(
      resistance=Range.from_tolerance(r1_resistance, tolerance)
    ))
    self.r2 = self.Block(Resistor(
      resistance=Range.from_tolerance(r1_resistance, tolerance)
    ))
    self.rf = self.Block(Resistor(
      resistance=Range.from_tolerance(rf_resistance, tolerance)
    ))
    self.rg = self.Block(Resistor(
      resistance=Range.from_tolerance(rf_resistance, tolerance)
    ))

    self.connect(self.input_negative, self.r1.a.as_analog_sink(
      # TODO very simplified and probably very wrong
      impedance=self.r1.resistance + self.rf.resistance
    ))
    self.connect(self.input_positive, self.r2.a.as_analog_sink(
      impedance=self.r2.resistance + self.rg.resistance
    ))

    self.connect(self.amp.out, self.output, self.rf.a.as_analog_sink(
      # TODO very simplified and probably very wrong
      impedance=self.r1.resistance + self.rf.resistance
    ))
    self.connect(self.r1.b.as_analog_source(
      voltage_out=self.input_negative.link().voltage.hull(self.output.link().voltage),
      impedance=1 / (1 / self.r1.resistance + 1 / self.rf.resistance)  # combined R1 and Rf resistance
    ), self.rf.b.as_analog_sink(
      # treated as an ideal sink for now
    ), self.amp.inn)
    self.connect(self.r2.b.as_analog_source(
      voltage_out=self.input_positive.link().voltage.hull(self.output_reference.link().voltage),
      impedance=1 / (1 / self.r2.resistance + 1 / self.rg.resistance)  # combined R2 and Rg resistance
    ), self.rg.b.as_analog_sink(
      # treated as an ideal sink for now
    ), self.amp.inp)
    self.connect(self.rg.a.as_analog_sink(
      impedance=self.r2.resistance + self.rg.resistance
    ), self.output_reference)


class IntegratorValues(ESeriesRatioValue):
  def __init__(self, factor: Range, capacitance: Range):
    self.factor = factor  # output scale factor, 1/RC in units of 1/s
    self.capacitance = capacitance  # value of the capacitor

  @staticmethod
  def from_resistors(r1_range: Range, r2_range: Range) -> 'IntegratorValues':
    """r1 is the input resistor and r2 is the capacitor."""
    return IntegratorValues(
      1 / (r1_range * r2_range),
      r2_range
    )

  def initial_test_decades(self) -> Tuple[int, int]:
    """C is given per the spec, so we need factor = 1 / (R * C) => R = 1 / (factor * C)"""
    capacitance_decade = ceil(log10(self.capacitance.center()))
    allowed_resistances = Range.cancel_multiply(1 / self.capacitance, 1 / self.factor)
    resistance_decade = ceil(log10(allowed_resistances.center()))

    return resistance_decade, capacitance_decade

  def distance_to(self, spec: 'IntegratorValues') -> List[float]:
    if self.factor in spec.factor and self.capacitance in spec.capacitance:
      return []
    else:
      return [
        abs(self.factor.center() - spec.factor.center()),
        abs(self.capacitance.center() - spec.capacitance.center())
      ]

  def intersects(self, spec: 'IntegratorValues') -> bool:
    return self.factor.intersects(spec.factor) and \
           self.capacitance.intersects(spec.capacitance)


class IntegratorInverting(AnalogFilter, GeneratorBlock):
  """Opamp integrator, outputs the negative integral of the input signal, relative to some reference signal.
  Will clip to the input voltage rails.

  From https://en.wikipedia.org/wiki/Operational_amplifier_applications#Inverting_integrator:
  Vout = - 1/RC * int(Vin) (integrating over time)
  """
  @init_in_parent
  def __init__(self, factor: RangeLike = RangeExpr(), capacitance: RangeLike = RangeExpr()):
    super().__init__()

    self.amp = self.Block(Opamp())
    self.pwr = self.Export(self.amp.pwr, [Power])
    self.gnd = self.Export(self.amp.gnd, [Common])

    self.input = self.Port(AnalogSink())
    self.output = self.Port(AnalogSource())
    self.reference = self.Port(AnalogSink())  # negative reference for the input and output signals

    self.factor = self.Parameter(RangeExpr(factor))
    self.capacitance = self.Parameter(RangeExpr(capacitance))

    # Series is lower and tolerance is higher because there's a cap involved
    # TODO separate tolerances and series by decade, and for the cap
    self.series = self.Parameter(IntExpr(6))  # can be overridden by refinements
    self.tolerance = self.Parameter(FloatExpr(0.05))  # can be overridden by refinements

    self.generator(self.generate_components, self.factor, self.capacitance, self.series, self.tolerance,
                   targets=[self.input])

  def generate_components(self, factor: Range, capacitance: Range, series: int, tolerance: float) -> None:
    calculator = ESeriesRatioUtil(ESeriesUtil.SERIES[series], tolerance, IntegratorValues)
    sel_resistance, sel_capacitance = calculator.find(IntegratorValues(factor, capacitance))

    self.r = self.Block(Resistor(
      resistance=Range.from_tolerance(sel_resistance, tolerance)
    ))
    self.c = self.Block(Capacitor(
      capacitance=Range.from_tolerance(sel_capacitance, tolerance),
      voltage=self.output.link().voltage
    ))

    self.connect(self.input, self.r.a.as_analog_sink(
      # TODO very simplified and probably very wrong
      impedance=self.r.resistance
    ))
    self.connect(self.amp.out, self.output, self.c.pos.as_analog_sink())  # TODO impedance of the feedback circuit?
    self.connect(self.r.b.as_analog_source(
      impedance=self.r.resistance
    ), self.c.neg.as_analog_sink(), self.amp.inn)
    self.connect(self.reference, self.amp.inp)
