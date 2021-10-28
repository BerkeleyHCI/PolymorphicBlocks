from __future__ import annotations

from itertools import chain, accumulate, product
from math import log10, floor, ceil
from typing import List, Tuple, NamedTuple, Optional

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
      f"best: {best_values} with ratio={best.ratio}, impednace={best.parallel_impedance}"
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
    # Misc ideas
    # TODO Perhaps pick one end of ratio to be -inf / inf, to specify "pick as close as possible",
    # but what are the practicality constraints (E12 series?)
    super().__init__()

    self.ratio = self.Parameter(RangeExpr(ratio))  # TODO: maybe should be a target output voltage instead?
    self.impedance = self.Parameter(RangeExpr(impedance))

    self.selected_ratio = self.Parameter(RangeExpr())
    self.selected_impedance = self.Parameter(RangeExpr())
    self.selected_series_impedance = self.Parameter(RangeExpr())

    self.top = self.Port(Passive())
    self.center = self.Port(Passive())
    self.bottom = self.Port(Passive())

    self.generator(self.generate_divider, self.ratio, self.impedance)

  @classmethod
  def _ratio_tolerance(cls, r1_center: float, r2_center: float, tol: float) -> Range:
    tol_min = 1 - tol
    tol_max = 1 + tol
    ratio_min = r2_center * tol_min / (r2_center * tol_min + r1_center * tol_max)
    ratio_max = r2_center * tol_max / (r2_center * tol_max + r1_center * tol_min)
    return Range(ratio_min, ratio_max)

  @classmethod
  def _select_resistor(cls, series: List[List[float]], ratio: Range, impedance: Range,
                       tol: float) -> Tuple[float, float]:
    """Returns the nominal resistances of a 2-resistor divider that meets the ratio and parallel impedance requirements,
    considering individual resistor tolerances.
    This algorithm prefers resistors close in decade as possible.
    - TODO series should take tolerances, this allows this to stack with parallel / series resistors by encoding all
      combinations in the series list

    Algorithm overview, for R1 high-side and R2 low-side:
    Select the decade for R1 by adjusting as necessary so the ratio is contained. For example:
      R1 : R2   maxR2/minR1  minR2/maxR1
      1  : 10   82/83        10/18.2      /\ ratio towards 1  (as implemented, we use R1=0.1)
      1  : 1    8.2/9.2      1/9.2
      10 : 1    8.2/18.2     1/83
      100: 1    8.2/108.2    1/821        \/ ratio towards 0
    - Note, common multiples of 10 are canceled out
    - Note, there is overlap between each decade, so we zigzag through decades of R1 until out of range on both sides
    For each candidate, adjust the common decade between R1 and R2 to meet the parallel impedance spec.
    - TODO: this should be an arbitrary evaluation function, eg also support series impedance
    - We bump the impedance to the lowest decade in the tolerated impedance (log10 floor), and see if there is a match
    - If not, keep bumping decades until the impedance is out of range
    """
    R1_DECADE_LIMIT = 1e6

    assert ratio.upper <= 1, f"can't generate ratios > 1, got ratio={ratio}"

    # Track the best candidate in case a divider couldn't be solved, and give an informative message
    best_candidate = (float('inf'), Range(0, 0), (0.0, 0.0))  # ratio center, ratio range w/ tolerance, resistor selection

    tol_min = 1 - tol
    tol_max = 1 + tol

    series_all = list(chain(*series))
    series_min = min(series_all) * tol_min
    series_max = max(series_all) * tol_max

    impedance_shift = floor(log10(impedance.lower))

    def decade_limits(r1_decade: float) -> Range:
      """Returns the ratio limits of the specified decade, accounting for worst case tolerance"""
      return Range(series_min / (series_min + r1_decade*series_max),
                   series_max / (series_max + r1_decade*series_min))

    def try_r1_decade(r1_decade: float) -> Optional[Tuple[float, float]]:
      nonlocal best_candidate
      for subseries in accumulate(series):  # TODO this does some redundant work with lower series
        for r1_center, r2_center in product([elt * r1_decade for elt in subseries], subseries):
          r1r2_ratio = cls._ratio_tolerance(r1_center, r2_center, tol)
          if r1r2_ratio in ratio:
            r1r2_impedance = 1 / (1 / Range.from_tolerance(r1_center, tol) +
                                  1 / Range.from_tolerance(r2_center, tol))
            r1r2_impedance_shift = floor(log10(r1r2_impedance.lower))
            while not (r1r2_impedance.lower > impedance.upper):
              decade = 10 ** (impedance_shift - r1r2_impedance_shift)
              r1r2_impedance = r1r2_impedance * decade
              if r1r2_impedance in impedance:
                return ESeriesUtil.round_sig(r1_center * decade, 3), \
                       ESeriesUtil.round_sig(r2_center * decade, 3)  # TODO don't hardcode sigfigs
              r1r2_impedance_shift += 1

          if abs(r1r2_ratio.center() - ratio.center()) < abs(best_candidate[0] - ratio.center()):
            best_candidate = (r1r2_ratio.center(), r1r2_ratio, (r1_center, r2_center))
      return None

    r1_decade = 1  # zig-zag: 1,  10, 0.1,  100, 0.01,  ... (raise, invert, repeat)
    upper_r1_range = decade_limits(r1_decade)
    lower_r1_range = decade_limits(1 / r1_decade)

    while not ((lower_r1_range.upper < ratio.lower) and (upper_r1_range.lower > ratio.upper)) and \
        r1_decade <= R1_DECADE_LIMIT:
      if upper_r1_range.intersects(ratio):
        res = try_r1_decade(r1_decade)
        if res is not None:
          return res

      if upper_r1_range != lower_r1_range and lower_r1_range.intersects(ratio):
        res = try_r1_decade(1 / r1_decade)
        if res is not None:
          return res

      r1_decade *= 10
      upper_r1_range = decade_limits(r1_decade)
      lower_r1_range = decade_limits(1/ r1_decade)

    raise ValueError(f"Unable to find resistive divider with ratio in {ratio} and impedance in {impedance} "
                     f"within {tol*100}% resistors. "
                     f"Best candidate: r1,r2={best_candidate[2]}, ratio range {best_candidate[1]}")

  def generate_divider(self, ratio: Range, impedance: Range) -> None:
    """Generates a resistive divider meeting the required specifications, with the lowest E-series resistors possible.
    TODO: if no combinations found, try a 3-combination, with a series or parallel connection on one side.
    """
    TOLERANCE = 0.01  # epsilon
    top_resistance, bottom_resistance = self._select_resistor(
      ESeriesUtil.E24_SERIES, ratio, impedance, TOLERANCE)

    self.top_res = self.Block(Resistor(
      resistance=Range.from_tolerance(top_resistance, TOLERANCE)
    ))
    self.bottom_res = self.Block(Resistor(
      resistance=Range.from_tolerance(bottom_resistance, TOLERANCE)
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
