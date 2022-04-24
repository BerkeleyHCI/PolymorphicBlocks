import itertools
import math
from abc import ABCMeta
from collections import deque
from typing import Sequence, Optional, TypeVar, Tuple, List, Generic, Type

from electronics_model import *


class ESeriesUtil:
  """Helper methods for working with the E series of preferred numbers."""
  @staticmethod
  def zigzag_range(start: int, end: int) -> Sequence[int]:
    if start >= end:
      return []

    center = int((start + end - 1) / 2)
    lower = list(range(start, center))
    upper = list(range(center + 1, end))
    output = [center]

    while lower or upper:
      if lower:
        output.append(lower.pop(0))
      if upper:
        output.append(upper.pop(0))

    return output

  @staticmethod
  def round_sig(x: float, sig: int) -> float:
    # this prevents floating point weirdness, eg 819.999
    return round(x, sig-int(math.floor(math.log10(abs(x))))-1)

  @classmethod
  def choose_preferred_number(cls, within: Range, series: Sequence[float], tolerance: float) -> \
      Optional[float]:
    lower_pow10 = math.floor(math.log10(within.lower))
    if within.upper == float('inf'):
      upper_pow10 = lower_pow10 + 1  # arbitrarily give it one more power of 10 if it's unbounded
    else:
      upper_pow10 = math.ceil(math.log10(within.upper))

    powers = cls.zigzag_range(lower_pow10, upper_pow10)  # prefer the center power first, then zigzag away from it
    # TODO given the tolerance we can actually bound this further

    for value in series:
      for power in powers:
        pow10_mult = math.pow(10, power)
        value_mult = cls.round_sig(value * pow10_mult, cls.ROUND_DIGITS)
        if Range.from_tolerance(value_mult, tolerance) in within:
          return value_mult

    return None

  ROUND_DIGITS = 5

  E24_DIFF = {  # series as difference from prior series
    1: [1.0],
    3: [2.2, 4.7],
    6: [1.5, 3.3, 6.8],
    12: [1.2, 1.8, 2.7, 3.9, 5.6, 8.2],
    24: [1.1, 1.3, 1.6, 2.0, 2.4, 3.0, 3.6, 4.3, 5.1, 6.2, 7.5, 9.1],
  }

  E192_DIFF = {
    48: [1.00, 1.05, 1.10, 1.15, 1.21, 1.27, 1.33, 1.40, 1.47, 1.54, 1.62, 1.69,
         1.78, 1.87, 1.96, 2.05, 2.15, 2.26, 2.37, 2.49, 2.61, 2.74, 2.87, 3.01,
         3.16, 3.32, 3.48, 3.65, 3.83, 4.02, 4.22, 4.42, 4.64, 4.87, 5.11, 5.36,
         5.62, 5.90, 6.19, 6.49, 6.81, 7.15, 7.50, 7.87, 8.25, 8.66, 9.09, 9.53],
    96: [1.02, 1.07, 1.13, 1.18, 1.24, 1.30, 1.37, 1.43, 1.50, 1.58, 1.65, 1.74,
         1.82, 1.91, 2.00, 2.10, 2.21, 2.32, 2.43, 2.55, 2.67, 2.80, 2.94, 3.09,
         3.24, 3.40, 3.57, 3.74, 3.92, 4.12, 4.32, 4.53, 4.75, 4.99, 5.23, 5.49,
         5.76, 6.04, 6.34, 6.65, 6.98, 7.32, 7.68, 8.06, 8.45, 8.87, 9.31, 9.76],
    192: [1.01, 1.04, 1.06, 1.09, 1.11, 1.14, 1.17, 1.20, 1.23, 1.26, 1.29, 1.32,
          1.35, 1.38, 1.42, 1.45, 1.49, 1.52, 1.56, 1.60, 1.64, 1.67, 1.72, 1.76,
          1.80, 1.84, 1.89, 1.93, 1.98, 2.03, 2.08, 2.13, 2.18, 2.23, 2.29, 2.34,
          2.40, 2.46, 2.52, 2.58, 2.64, 2.71, 2.77, 2.84, 2.91, 2.98, 3.05, 3.12,
          3.20, 3.28, 3.36, 3.44, 3.52, 3.61, 3.70, 3.79, 3.88, 3.97, 4.07, 4.17,
          4.27, 4.37, 4.48, 4.59, 4.70, 4.81, 4.93, 5.05, 5.17, 5.30, 5.42, 5.56,
          5.69, 5.83, 5.97, 6.12, 6.26, 6.42, 6.57, 6.73, 6.90, 7.06, 7.23, 7.41,
          7.59, 7.77, 7.96, 8.16, 8.35, 8.56, 8.76, 8.98, 9.20, 9.42, 9.65, 9.88],
  }

  SERIES = {  # whole series in zigzag order
    1: list(itertools.chain(E24_DIFF[1])),
    3: list(itertools.chain(E24_DIFF[1], E24_DIFF[3])),
    6: list(itertools.chain(E24_DIFF[1], E24_DIFF[3], E24_DIFF[6])),
    12: list(itertools.chain(E24_DIFF[1], E24_DIFF[3], E24_DIFF[6], E24_DIFF[12])),
    24: list(itertools.chain(E24_DIFF[1], E24_DIFF[3], E24_DIFF[6], E24_DIFF[12], E24_DIFF[24])),

    # These are E192 without the E24 series
    48: list(itertools.chain(E192_DIFF[48])),
    96: list(itertools.chain(E192_DIFF[48], E192_DIFF[96])),
    192: list(itertools.chain(E192_DIFF[48], E192_DIFF[96], E192_DIFF[192])),

    # These are E24 + E192, prioritizing E24
    2448: list(itertools.chain(E24_DIFF[1], E24_DIFF[3], E24_DIFF[6], E24_DIFF[12], E24_DIFF[24],
                               E192_DIFF[48])),
    2496: list(itertools.chain(E24_DIFF[1], E24_DIFF[3], E24_DIFF[6], E24_DIFF[12], E24_DIFF[24],
                               E192_DIFF[48], E192_DIFF[96])),
    24192: list(itertools.chain(E24_DIFF[1], E24_DIFF[3], E24_DIFF[6], E24_DIFF[12], E24_DIFF[24],
                                E192_DIFF[48], E192_DIFF[96], E192_DIFF[192])),
  }


ESeriesRatioValueType = TypeVar('ESeriesRatioValueType', bound='ESeriesRatioValue')
class ESeriesRatioValue(Generic[ESeriesRatioValueType], metaclass=ABCMeta):
  """Abstract base class for the calculated output value for a resistor ... thing.
  Yes, not too descriptive, but example applications are:
  - resistive divider: ratio and impedance
  - non-inverting amplifier: amplification factor and impedance
  - really anything that takes two E-series values and where there isn't
  a nice closed-form solution so we test-and-check across decades
  """
  @staticmethod
  def from_resistors(r1: Range, r2: Range) -> ESeriesRatioValueType:
    """Calculates the range of outputs possible given input range of resistors."""
    ...

  def initial_test_decades(self) -> Tuple[int, int]:
    """Returns the initial decades to test that can satisfy this spec."""
    ...

  def distance_to(self, spec: ESeriesRatioValueType) -> List[float]:
    """Returns a distance vector to the spec, or the empty list if satisfying the spec"""
    ...

  def intersects(self, spec: ESeriesRatioValueType) -> bool:
    """Return whether this intersects with some spec - whether some subset of the resistors
    can potentially satisfy some spec"""
    ...


class ESeriesRatioUtil(Generic[ESeriesRatioValueType], metaclass=ABCMeta):
  """Base class for an algorithm that searches pairs of E-series numbers
  to get some desired output (eg, ratio and impedance for a resistive divider).
  The output calculations are determined by the value_type class.
  Calculation of the initial decade (for both values) and which way to shift decades
  after scanning an entire decade can also be overridden

  Within a decade, this prefers combinations of smaller E-series before moving on,
  eg a satisfying E3 pair is preferred and returned, even if there is a closer E6 pair.
  This has no concept of a distance metric when the spec is satisfied.

  The code below is defined in terms of resistors, but this can be used with anything
  that uses the E-series.

  Series should be the zero decade, in the range of [1, 10)
  """
  class NoMatchException(Exception):
    pass

  def __init__(self, series: List[float], tolerance: float, value_type: Type[ESeriesRatioValueType]):
    self.series = series
    self.tolerance = tolerance
    self.value_type = value_type

  def _no_result_error(self, best_values: Tuple[float, float], best: ESeriesRatioValueType,
                       target: ESeriesRatioValueType) -> Exception:
    """Given the best tested result and a target, generate an exception to throw.
    This should not throw the exception, only generate it."""
    return self.NoMatchException(f"No ratio found for target {target}, "
                                 f"best: {best}, with values {best_values}")

  @staticmethod
  def _generate_e_series_product(series: List[float], r1_decade: int, r2_decade: int) -> List[Tuple[float, float]]:
    """Returns the ordered / sorted cartesian product of all possible pairs of values for the requested decade.
    The output is ordered such that pairs containing numbers earlier in the series comes first,
    so in effect lower E-series combinations are preferred, assuming the series is ordered in a
    zig-zag fashion."""
    r1_series = [ESeriesUtil.round_sig(elt * (10 ** r1_decade), ESeriesUtil.ROUND_DIGITS)
                 for elt in series]
    r2_series = [ESeriesUtil.round_sig(elt * (10 ** r2_decade), ESeriesUtil.ROUND_DIGITS)
                 for elt in series]
    out = []
    assert len(r1_series) == len(r2_series), "algorithm depends on same series length"
    for index_max in range(len(r1_series)):
      for index_other in range(index_max):
        out.append((r1_series[index_max], r2_series[index_other]))
        out.append((r1_series[index_other], r2_series[index_max]))
      out.append((r1_series[index_max], r2_series[index_max]))

    return out

  def find(self, target: ESeriesRatioValueType) -> Tuple[float, float]:
    """Find a pair of R1, R2 that satisfies the target."""
    initial = target.initial_test_decades()
    search_queue = deque([initial])
    searched_decades = {initial}  # tracks everything that has been on the search queue
    best = None

    while search_queue:
      r1r2_decade = search_queue.popleft()
      product = self._generate_e_series_product(self.series,
                                                r1r2_decade[0], r1r2_decade[1])

      for (r1, r2) in product:
        output = self.value_type.from_resistors(Range.from_tolerance(r1, self.tolerance),
                                                Range.from_tolerance(r2, self.tolerance))
        output_dist = output.distance_to(target)

        if best is None or output_dist < best[2]:
          best = ((r1, r2), output, output_dist)
          if not output_dist:
            break

      assert best is not None
      if not best[2]:  # distance vector empty = satisfying
        return best[0]
      else:
        next_decades = self._get_next_decades(r1r2_decade, target)
        for next_decade in next_decades:
          if next_decade not in searched_decades and -15 < next_decade[0] < 15 and -15 < next_decade[1] < 15:
            searched_decades.add(next_decade)
            search_queue.append(next_decade)

    # if it gets here, the search queue has been exhausted without a result
    assert best is not None
    raise self._no_result_error(best[0], best[1], target)

  def _get_next_decades(self, decade: Tuple[int, int], target: ESeriesRatioValueType) -> List[Tuple[int, int]]:
    """If the target was not found scanning the entire decade, this is called to determine next decades to search.
    This is passed in the current decade and the target.

    Returns a list of decades to search, in order. Internally the search algorithm deduplicates decades.
    This is called for every decade, and results are appended to the end of the search queue after deduplication.

    The default algorithm returns all adjacent combinations of decades where the output
    intersects the target.
    """
    def range_of_decade(range_decade: int) -> Range:
      """Given a decade, return the range of possible values - for example, decade 0
      would mean 1.0, 2.2, 4.7 and would return a range of (1, 10)."""
      return Range(10 ** range_decade, 10 ** (range_decade + 1))

    test_decades = [
      # adjustments shifting both decades in the same direction
      (decade[0] - 1, decade[1] - 1),
      (decade[0] + 1, decade[1] + 1),
      # adjustments shifting decades independently
      (decade[0] - 1, decade[1]),
      (decade[0], decade[1] + 1),
      (decade[0] + 1, decade[1]),
      (decade[0], decade[1] - 1),
    ]

    new_decades = [decade for decade in test_decades
                   if self.value_type.from_resistors(range_of_decade(decade[0]),
                                                     range_of_decade(decade[1])).intersects(target)]
    return new_decades
