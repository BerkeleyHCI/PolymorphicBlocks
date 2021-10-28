from __future__ import annotations

from math import log10, ceil
from typing import List, Tuple, NamedTuple

from edg_core import *
from electronics_model import Common, Passive
from . import AnalogFilter, DiscreteApplication, Resistor, Filter
from .ESeriesUtil import ESeriesUtil, ESeriesRatioUtil


class DividerValues(NamedTuple):
  ratio: Range
  parallel_impedance: Range


class ResistiveDividerCalculator(ESeriesRatioUtil[DividerValues]):
  """Resistive divider calculator using the ESeriesRatioUtil infrastructure.

  R1 is the high-side resistor, and R2 is the low-side resistor, such that
  Vout = Vin * R2 / (R1 + R2)

  Example of decade adjustment:
  R1 : R2   maxR2/minR1  minR2/maxR1
  1  : 10   82/83        10/18.2      /\ ratio towards 1
  1  : 1    8.2/9.2      1/9.2
  10 : 1    8.2/18.2     1/83
  100: 1    8.2/108.2    1/821        \/ ratio towards 0

  TODO - not fully optimal in that the ratio doesn't need to be recalculated if we're shifting both decades
  (to achieve some impedance spec), but it uses shared infrastructure that doesn't assume this ratio optimization
  """
  class NoMatchException(Exception):
    pass

  def __init__(self, series: List[float], tolerance: float):
    super().__init__(series)  # TODO custom range series
    self.tolerance = tolerance

  def _calculate_output(self, r1: float, r2: float) -> DividerValues:
    r1_range = Range.from_tolerance(r1, self.tolerance)
    r2_range = Range.from_tolerance(r2, self.tolerance)
    ratio_min = r2_range.lower / (r2_range.lower + r1_range.upper)
    ratio_max = r2_range.upper / (r2_range.upper + r1_range.lower)
    impedance_min = 1 / (1 / r1_range.lower + 1 / r2_range.lower)
    impedance_max = 1 / (1 / r1_range.upper + 1 / r2_range.upper)
    return DividerValues(
      Range(ratio_min, ratio_max),
      Range(impedance_min, impedance_max)
    )

  def _get_distance(self, proposed: DividerValues, target: DividerValues) -> List[float]:
    if proposed.ratio.fuzzy_in(target.ratio) and proposed.parallel_impedance.fuzzy_in(target.parallel_impedance):
      return []
    else:
      return [
        abs(proposed.ratio.center() - target.ratio.center()),
        abs(proposed.parallel_impedance.center() - target.parallel_impedance.center())
      ]

  def _no_result_error(self, best_values: Tuple[float, float], best: DividerValues,
                       target: DividerValues) -> Exception:
    return ResistiveDividerCalculator.NoMatchException(
      f"No resistive divider found for target ratio={target.ratio}, impedance={target.parallel_impedance}, "
      f"best: {best_values} with ratio={best.ratio}, impedance={best.parallel_impedance}"
    )

  def _get_initial_decade(self, target: DividerValues) -> Tuple[int, int]:
    decade = ceil(log10(target.parallel_impedance.upper))
    return decade, decade

  def _get_next_decade(self, decade_outputs: List[DividerValues], target: DividerValues) -> Tuple[int, int]:
    ratio_range = Range(
      min([output.ratio.lower for output in decade_outputs]),
      max([output.ratio.upper for output in decade_outputs])
    )
    parallel_impedance_range = Range(
      min([output.parallel_impedance.lower for output in decade_outputs]),
      max([output.parallel_impedance.upper for output in decade_outputs])
    )
    if target.ratio.fuzzy_in(ratio_range):  # ratio contained, only impedance needs shifting
      if target.parallel_impedance.lower < parallel_impedance_range.lower:
        return -1, -1
      elif target.parallel_impedance.upper > parallel_impedance_range.upper:
        return 1, 1
      else:
        return 0, 0  # both ranges contained, nothing to do!
    else:  # ratio also needs shifting
      if target.ratio.lower < ratio_range.lower:  # current range too high, decrease R2 and increase R1
        return 1, -1
      elif target.ratio.upper > ratio_range.upper:
        return -1, 1
      else:
        return 0, 0  # this really shouldn't happen


class ResistiveDivider(DiscreteApplication, GeneratorBlock):
  """Abstract, untyped (Passive) resistive divider, that takes in a ratio and parallel impedance spec."""

  @init_in_parent
  def __init__(self, ratio: RangeLike = RangeExpr(), impedance: RangeLike = RangeExpr()) -> None:
    super().__init__()

    self.ratio = self.Parameter(RangeExpr(ratio))
    self.impedance = self.Parameter(RangeExpr(impedance))

    self.series = self.Parameter(IntExpr(24))  # can be overridden by refinements
    self.tolerance = self.Parameter(FloatExpr(0.1))  # can be overridden by refinements

    self.selected_ratio = self.Parameter(RangeExpr())
    self.selected_impedance = self.Parameter(RangeExpr())
    self.selected_series_impedance = self.Parameter(RangeExpr())

    self.top = self.Port(Passive())
    self.center = self.Port(Passive())
    self.bottom = self.Port(Passive())

    self.generator(self.generate_divider, self.ratio, self.impedance, self.series, self.tolerance)

  def generate_divider(self, ratio: Range, impedance: Range, series: int, tolerance: float) -> None:
    """Generates a resistive divider meeting the required specifications, with the lowest E-series resistors possible.
    """
    calculator = ResistiveDividerCalculator(ESeriesUtil.E24_SERIES[series], tolerance)
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

    self.assign(self.selected_impedance,
                1 / (1/self.top_res.resistance + 1/self.bottom_res.resistance))
    self.assign(self.selected_series_impedance,
                self.top_res.resistance + self.bottom_res.resistance)
    self.assign(self.selected_ratio,
                self.bottom_res.resistance / (self.top_res.resistance + self.bottom_res.resistance))


@abstract_block
class BaseVoltageDivider(Filter, Block):
  """Base class that defines a resistive divider that takes in a voltage source and ground, and outputs
  an analog constant-voltage signal.
  The actual output voltage is defined as a ratio of the input voltage, and the divider is specified by
  ratio and impedance.
  Subclasses should define the ratio and impedance spec."""
  @init_in_parent
  def __init__(self) -> None:
    super().__init__()

    self.ratio = self.Parameter(RangeExpr())
    self.impedance = self.Parameter(RangeExpr())
    self.div = self.Block(ResistiveDivider(ratio=self.ratio, impedance=self.impedance))

    self.input = self.Export(self.div.top.as_voltage_sink(
      current_draw=RangeExpr(),
      voltage_limits=RangeExpr.ALL
    ), [Input])
    self.output = self.Export(self.div.center.as_analog_source(
      voltage_out=(self.input.link().voltage.lower() * self.div.selected_ratio.lower(),
                   self.input.link().voltage.upper() * self.div.selected_ratio.upper()),
      current_limits=RangeExpr.ALL,
      impedance=self.div.selected_impedance
    ), [Output])
    self.gnd = self.Export(self.div.bottom.as_ground(), [Common])

    self.selected_ratio = self.Parameter(RangeExpr(self.div.selected_ratio))
    self.selected_impedance = self.Parameter(RangeExpr(self.div.selected_impedance))
    self.selected_series_impedance = self.Parameter(RangeExpr(self.div.selected_series_impedance))

    self.assign(self.input.current_draw, self.output.link().current_drawn)
    # TODO also model static current draw into gnd


class VoltageDivider(BaseVoltageDivider):
  """Voltage divider that takes in a ratio and parallel impedance spec, and produces an output analog signal
  of the appropriate magnitude (as a fraction of the input voltage)"""
  @init_in_parent
  def __init__(self, *, output_voltage: RangeLike = RangeExpr(),
               impedance: RangeLike = RangeExpr()) -> None:
    super().__init__()

    self.output_voltage = self.Parameter(RangeExpr(output_voltage))  # TODO eliminate this casting?
    self.assign(self.impedance, impedance)

    ratio_lower = self.output_voltage.lower() / self.input.link().voltage.lower()
    ratio_upper = self.output_voltage.upper() / self.input.link().voltage.upper()
    self.require(ratio_lower <= ratio_upper,
                   "can't generate divider to create output voltage of tighter tolerance than input voltage")
    self.assign(self.ratio, (ratio_lower, ratio_upper))


class FeedbackVoltageDivider(BaseVoltageDivider):
  """Voltage divider that takes in a ratio and parallel impedance spec, and produces an output analog signal
  of the appropriate magnitude (as a fraction of the input voltage)"""
  @init_in_parent
  def __init__(self, *, output_voltage: RangeLike = RangeExpr(),
               impedance: RangeLike = RangeExpr(),
               assumed_input_voltage: RangeLike = RangeExpr()) -> None:
    super().__init__()

    self.output_voltage = self.Parameter(RangeExpr(output_voltage))  # TODO eliminate this casting?
    self.assumed_input_voltage = self.Parameter(RangeExpr(assumed_input_voltage))  # TODO eliminate this casting?
    self.assign(self.impedance, impedance)

    ratio_lower = self.output_voltage.upper() / self.assumed_input_voltage.upper()
    ratio_upper = self.output_voltage.lower() / self.assumed_input_voltage.lower()
    self.require(ratio_lower <= ratio_upper,
                   "can't generate feedback divider with input voltage of tighter tolerance than output voltage")
    self.assign(self.ratio, (ratio_lower, ratio_upper))


class SignalDivider(AnalogFilter, Block):
  """Specialization of ResistiveDivider for Analog signals"""
  @init_in_parent
  def __init__(self, ratio: RangeLike = RangeExpr(),
               impedance: RangeLike = RangeExpr()) -> None:
    super().__init__()

    self.div = self.Block(ResistiveDivider(ratio=ratio, impedance=impedance))
    self.input = self.Export(self.div.top.as_analog_sink(
      impedance=self.div.selected_series_impedance,
      current_draw=RangeExpr(),
      voltage_limits=RangeExpr.ALL
    ), [Input])
    self.output = self.Export(self.div.center.as_analog_source(
      voltage_out=(self.input.link().voltage.lower() * self.div.selected_ratio.lower(),
                   self.input.link().voltage.upper() * self.div.selected_ratio.upper()),
      current_limits=RangeExpr.ALL,
      impedance=self.div.selected_impedance
    ), [Output])
    self.gnd = self.Export(self.div.bottom.as_ground(), [Common])
    self.assign(self.input.current_draw, self.output.link().current_drawn)
