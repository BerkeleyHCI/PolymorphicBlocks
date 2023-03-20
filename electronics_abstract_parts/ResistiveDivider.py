from __future__ import annotations

from math import log10, ceil
from typing import List, Tuple

from electronics_model import *
from . import Analog, Resistor
from .Categories import InternalSubcircuit
from .ESeriesUtil import ESeriesUtil, ESeriesRatioUtil, ESeriesRatioValue


class DividerValues(ESeriesRatioValue['DividerValues']):
  """Resistive divider calculator using the ESeriesRatioUtil infrastructure.

  R1 is the high-side resistor, and R2 is the low-side resistor, such that
  Vout = Vin * R2 / (R1 + R2)

  Example of decade adjustment:
  R1 : R2   maxR2/minR1  minR2/maxR1  (theoretical)
  1  : 10   100/101      10/20        /\ ratio towards 1
  1  : 1    10/11        1/11
  10 : 1    10/20        1/101
  100: 1    10/110       1/1001       \/ ratio towards 0
  """
  def __init__(self, ratio: Range, parallel_impedance: Range):
    self.ratio = ratio  # amplification factor from in to out
    self.parallel_impedance = parallel_impedance  # parallel impedance into the opamp negative pin

  @staticmethod
  def from_resistors(r1_range: Range, r2_range: Range) -> 'DividerValues':
    """This uses a slight rewriting of terms to avoid duplication of terms and not double-count tolerances:
    ratio = R2 / (R1 + R2) => divide  through by R2 / R2
    ratio = 1 / (R1 / R2 + 1)
    """
    return DividerValues(
      1 / (r1_range / r2_range + 1),
      1 / (1 / r1_range + 1 / r2_range)
    )

  def initial_test_decades(self) -> Tuple[int, int]:
    decade = ceil(log10(self.parallel_impedance.center()))
    return decade, decade

  def distance_to(self, spec: 'DividerValues') -> List[float]:
    if self.ratio in spec.ratio and self.parallel_impedance in spec.parallel_impedance:
      return []
    else:
      return [
        abs(self.ratio.center() - spec.ratio.center()),
        abs(self.parallel_impedance.center() - spec.parallel_impedance.center())
      ]

  def intersects(self, spec: 'DividerValues') -> bool:
    return self.ratio.intersects(spec.ratio) and \
           self.parallel_impedance.intersects(spec.parallel_impedance)


class ResistiveDivider(InternalSubcircuit, GeneratorBlock):
  """Abstract, untyped (Passive) resistive divider, that takes in a ratio and parallel impedance spec."""

  @init_in_parent
  def __init__(self, ratio: RangeLike, impedance: RangeLike, *,
               series: IntLike = Default(24), tolerance: FloatLike = Default(0.01)) -> None:
    super().__init__()

    self.ratio = self.ArgParameter(ratio)
    self.impedance = self.ArgParameter(impedance)

    self.actual_ratio = self.Parameter(RangeExpr())
    self.actual_impedance = self.Parameter(RangeExpr())
    self.actual_series_impedance = self.Parameter(RangeExpr())

    self.top = self.Port(Passive.empty())
    self.center = self.Port(Passive.empty())
    self.bottom = self.Port(Passive.empty())

    self.generator(self.generate_divider, self.ratio, self.impedance, series, tolerance)

  def contents(self) -> None:
    super().contents()

    self.description = DescriptionString(
      "<b>ratio:</b> ", DescriptionString.FormatUnits(self.actual_ratio, ""),
      " <b>of spec</b> ", DescriptionString.FormatUnits(self.ratio, ""),
      "\n<b>impedance:</b> ", DescriptionString.FormatUnits(self.actual_impedance, "Ω"),
      " <b>of spec:</b> ", DescriptionString.FormatUnits(self.impedance, "Ω"))


  def generate_divider(self, ratio: Range, impedance: Range, series: int, tolerance: float) -> None:
    """Generates a resistive divider meeting the required specifications, with the lowest E-series resistors possible.
    """

    # TODO: not fully optimal in that the ratio doesn't need to be recalculated if we're shifting both decades
    # (to achieve some impedance spec), but it uses shared infrastructure that doesn't assume this ratio optimization
    calculator = ESeriesRatioUtil(ESeriesUtil.SERIES[series], tolerance, DividerValues)
    top_resistance, bottom_resistance = calculator.find(DividerValues(ratio, impedance))

    self.top_res = self.Block(Resistor(
      resistance=Range.from_tolerance(top_resistance, tolerance)
    ))
    self.bottom_res = self.Block(Resistor(
      resistance=Range.from_tolerance(bottom_resistance, tolerance)
    ))

    self.connect(self.top_res.a, self.top)
    self.connect(self.top_res.b, self.center, self.bottom_res.a)
    self.connect(self.bottom_res.b, self.bottom)

    self.assign(self.actual_impedance,
                1 / (1 / self.top_res.actual_resistance + 1 / self.bottom_res.actual_resistance))
    self.assign(self.actual_series_impedance,
                self.top_res.actual_resistance + self.bottom_res.actual_resistance)
    self.assign(self.actual_ratio,
                1 / (self.top_res.actual_resistance / self.bottom_res.actual_resistance + 1))


@non_library
class BaseVoltageDivider(Block):
  """Base class that defines a resistive divider that takes in a voltage source and ground, and outputs
  an analog constant-voltage signal.
  The actual output voltage is defined as a ratio of the input voltage, and the divider is specified by
  ratio and impedance.
  Subclasses should define the ratio and impedance spec."""
  @init_in_parent
  def __init__(self, impedance: RangeLike) -> None:
    super().__init__()

    self.impedance = self.ArgParameter(impedance)
    self.ratio = self.Parameter(RangeExpr())  # "internal" forward-declared parameter
    self.div = self.Block(ResistiveDivider(ratio=self.ratio, impedance=impedance))

    self.input = self.Port(VoltageSink().empty(), [Input])  # forward declaration only
    self.output = self.Export(self.div.center.adapt_to(AnalogSource(
      voltage_out=(self.input.link().voltage.lower() * self.div.actual_ratio.lower(),
                   self.input.link().voltage.upper() * self.div.actual_ratio.upper()),
      current_limits=RangeExpr.ALL,
      impedance=self.div.actual_impedance
    )), [Output])
    self.connect(self.input, self.div.top.adapt_to(VoltageSink(
      current_draw=self.output.link().current_drawn,
      voltage_limits=RangeExpr.ALL
    )))
    self.gnd = self.Export(self.div.bottom.adapt_to(Ground()), [Common])

    self.actual_ratio = self.Parameter(RangeExpr(self.div.actual_ratio))
    self.actual_impedance = self.Parameter(RangeExpr(self.div.actual_impedance))
    self.actual_series_impedance = self.Parameter(RangeExpr(self.div.actual_series_impedance))


class VoltageDivider(Analog, BaseVoltageDivider):
  """Voltage divider that takes in an output voltage and parallel impedance spec, and produces an output analog signal
  of the appropriate magnitude (as a fraction of the input voltage)"""
  @init_in_parent
  def __init__(self, *, output_voltage: RangeLike, impedance: RangeLike) -> None:
    super().__init__(impedance=impedance)

    self.output_voltage = self.ArgParameter(output_voltage)

    ratio_lower = self.output_voltage.lower() / self.input.link().voltage.lower()
    ratio_upper = self.output_voltage.upper() / self.input.link().voltage.upper()
    self.require(ratio_lower <= ratio_upper,
                   "can't generate divider to create output voltage of tighter tolerance than input voltage")
    self.assign(self.ratio, (ratio_lower, ratio_upper))


class VoltageSenseDivider(Analog, BaseVoltageDivider):
  """Voltage divider that takes in an output voltage and parallel impedance spec, and produces an output analog signal
  of the appropriate magnitude (as a fraction of the input voltage).
  Unlike the normal VoltageDivider, the output is defined in terms of full scale voltage - that is, the voltage
  output at the maximum input voltage, which makes the tolerance specification more useful for sensing applications
  with variable input voltage.

  TODO: can this be unified with VoltageDivider?"""
  @init_in_parent
  def __init__(self, *, full_scale_voltage: RangeLike, impedance: RangeLike) -> None:
    super().__init__(impedance=impedance)

    self.full_scale_voltage = self.ArgParameter(full_scale_voltage)

    ratio_lower = self.full_scale_voltage.lower() / self.input.link().voltage.upper()
    ratio_upper = self.full_scale_voltage.upper() / self.input.link().voltage.upper()
    self.require(ratio_lower <= ratio_upper,
                 "can't generate divider to create output voltage of tighter tolerance than input voltage")
    self.assign(self.ratio, (ratio_lower, ratio_upper))


class FeedbackVoltageDivider(Analog, BaseVoltageDivider):
  """Voltage divider that takes in a ratio and parallel impedance spec, and produces an output analog signal
  of the appropriate magnitude (as a fraction of the input voltage)"""
  @init_in_parent
  def __init__(self, *, output_voltage: RangeLike, impedance: RangeLike,
               assumed_input_voltage: RangeLike) -> None:
    super().__init__(impedance=impedance)

    self.output_voltage = self.ArgParameter(output_voltage)
    self.assumed_input_voltage = self.ArgParameter(assumed_input_voltage)
    self.actual_input_voltage = self.Parameter(RangeExpr(
      (self.output_voltage.lower() / self.actual_ratio.upper(),
       self.output_voltage.upper() / self.actual_ratio.lower())
    ))

  def contents(self) -> None:
    super().contents()

    self.description = DescriptionString(  # TODO forward from internal?
      "<b>ratio:</b> ", DescriptionString.FormatUnits(self.actual_ratio, ""),
      " <b>of spec</b> ", DescriptionString.FormatUnits(self.ratio, ""),
      "\n<b>impedance:</b> ", DescriptionString.FormatUnits(self.actual_impedance, "Ω"),
      " <b>of spec:</b> ", DescriptionString.FormatUnits(self.impedance, "Ω"))

    ratio_lower = self.output_voltage.upper() / self.assumed_input_voltage.upper()
    ratio_upper = self.output_voltage.lower() / self.assumed_input_voltage.lower()
    self.require(ratio_lower <= ratio_upper,
                 "can't generate feedback divider with input voltage of tighter tolerance than output voltage")
    self.assign(self.ratio, (ratio_lower, ratio_upper))


class SignalDivider(Analog, Block):
  """Specialization of ResistiveDivider for Analog signals"""
  @init_in_parent
  def __init__(self, ratio: RangeLike, impedance: RangeLike) -> None:
    super().__init__()

    self.div = self.Block(ResistiveDivider(ratio=ratio, impedance=impedance))
    self.input = self.Port(AnalogSink.empty(), [Input])  # forward declaration
    self.output = self.Export(self.div.center.adapt_to(AnalogSource(
      voltage_out=(self.input.link().voltage.lower() * self.div.actual_ratio.lower(),
                   self.input.link().voltage.upper() * self.div.actual_ratio.upper()),
      current_limits=RangeExpr.ALL,
      impedance=self.div.actual_impedance
    )), [Output])
    self.connect(self.input, self.div.top.adapt_to(AnalogSink(
      impedance=self.div.actual_series_impedance,
      current_draw=self.output.link().current_drawn,
      voltage_limits=RangeExpr.ALL
    )))
    self.gnd = self.Export(self.div.bottom.adapt_to(Ground()), [Common])
