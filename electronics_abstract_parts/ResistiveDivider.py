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

  alternatively, avoiding duplication of terms:
  ratio = 1 / (R1 / R2 + 1)

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
    return DividerValues(
      1 / (r1_range / r2_range + 1),
      1 / (1 / r1_range + 1 / r2_range)
    )

  def _get_distance(self, proposed: DividerValues, target: DividerValues) -> List[float]:
    if proposed.ratio in target.ratio and proposed.parallel_impedance in target.parallel_impedance:
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

  def _get_initial_decades(self, target: DividerValues) -> List[Tuple[int, int]]:
    # TODO: adjust initial ratio to intersect?
    # This really is only a problem for very small ratios:
    # below 1/10 it will waste time scanning the (0, 0) decade
    # and only below it will fail as it scans the (0, 0) decade and can't find a single step
    # to make it intersect
    decade = ceil(log10(target.parallel_impedance.upper))
    return [(decade, decade)]

  def _get_next_decades(self, decade: Tuple[int, int], best: DividerValues, target: DividerValues) -> \
      List[Tuple[int, int]]:
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

    new_decades = []

    # test adjustments that shift both decades in the same direction (changes impedance)
    down_decade = (decade[0] - 1, decade[1] - 1)
    up_decade = (decade[0] + 1, decade[1] + 1)
    if target.ratio.intersects(ratio_of_decade(down_decade)) and \
        target.parallel_impedance.intersects(impedance_of_decade(down_decade)):
      new_decades.append(down_decade)
    if target.ratio.intersects(ratio_of_decade(up_decade)) and \
        target.parallel_impedance.intersects(impedance_of_decade(up_decade)):
      new_decades.append(up_decade)

    # test adjustments that shift decades independently (changes ratio)
    up_r1_decade = (decade[0] - 1, decade[1])
    up_r2_decade = (decade[0], decade[1] + 1)
    down_r1_decade = (decade[0] + 1, decade[1])
    down_r2_decade = (decade[0], decade[1] - 1)
    if target.ratio.intersects(ratio_of_decade(up_r1_decade)) and \
        target.parallel_impedance.intersects(impedance_of_decade(up_r1_decade)):
      new_decades.append(up_r1_decade)
    if target.ratio.intersects(ratio_of_decade(up_r2_decade)) and \
        target.parallel_impedance.intersects(impedance_of_decade(up_r2_decade)):
      new_decades.append(up_r2_decade)
    if target.ratio.intersects(ratio_of_decade(down_r1_decade)) and \
        target.parallel_impedance.intersects(impedance_of_decade(down_r1_decade)):
      new_decades.append(down_r1_decade)
    if target.ratio.intersects(ratio_of_decade(down_r2_decade)) and \
        target.parallel_impedance.intersects(impedance_of_decade(down_r2_decade)):
      new_decades.append(down_r2_decade)

    return new_decades


class ResistiveDivider(DiscreteApplication, GeneratorBlock):
  """Abstract, untyped (Passive) resistive divider, that takes in a ratio and parallel impedance spec."""

  @init_in_parent
  def __init__(self, ratio: RangeLike = RangeExpr(), impedance: RangeLike = RangeExpr()) -> None:
    super().__init__()

    self.ratio = self.Parameter(RangeExpr(ratio))
    self.impedance = self.Parameter(RangeExpr(impedance))

    self.series = self.Parameter(IntExpr(24))  # can be overridden by refinements
    self.tolerance = self.Parameter(FloatExpr(0.01))  # can be overridden by refinements

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
                1 / (self.top_res.resistance / self.bottom_res.resistance + 1))


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
