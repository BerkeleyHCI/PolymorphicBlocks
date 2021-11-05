import itertools
from abc import ABCMeta, abstractmethod
from collections import deque
from typing import Sequence, Optional, TypeVar, Tuple, List, Generic, cast
from electronics_model import *
import math


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
    return round(x, sig-int(math.floor(math.log10(abs(x))))-1)

  @classmethod
  def choose_preferred_number(cls, range: Range, tolerance: float, series: Sequence[float], sig: int) -> \
      Optional[float]:
    lower_pow10 = math.floor(math.log10(range.lower))
    upper_pow10 = math.ceil(math.log10(range.upper))

    powers = cls.zigzag_range(lower_pow10, upper_pow10)  # prefer the center power first, then zigzag away from it
    # TODO given the tolerance we can actually bound this further

    for value in series:
      for power in powers:
        pow10_mult = math.pow(10, power)
        value_mult = cls.round_sig(value * pow10_mult, sig)  # this prevents floating point weirdness, eg 819.999
        if Range.from_tolerance(value_mult, tolerance) in range:
          return value_mult

    return None

  E24_DIFF = {  # series as difference from prior series
    1: [1.0],
    3: [2.2, 4.7],
    6: [1.5, 3.3, 6.8],
    12: [1.2, 1.8, 2.7, 3.9, 5.6, 8.2],
    24: [1.1, 1.3, 1.6, 2.0, 2.4, 3.0, 3.6, 4.3, 5.1, 6.2, 7.5, 9.1],
  }

  E24_SERIES = {  # whole series in zigzag order
    1: list(itertools.chain(E24_DIFF[1])),
    3: list(itertools.chain(E24_DIFF[1], E24_DIFF[3])),
    6: list(itertools.chain(E24_DIFF[1], E24_DIFF[3], E24_DIFF[6])),
    12: list(itertools.chain(E24_DIFF[1], E24_DIFF[3], E24_DIFF[6], E24_DIFF[12])),
    24: list(itertools.chain(E24_DIFF[1], E24_DIFF[3], E24_DIFF[6], E24_DIFF[12], E24_DIFF[24])),
  }


RatioOutputType = TypeVar('RatioOutputType')
class ESeriesRatioUtil(Generic[RatioOutputType], metaclass=ABCMeta):
  """Base class for an algorithm that searches pairs of E-series numbers
  to get some desired output (eg, ratio and impedance for a resistive divider).
  The output calculations can be overridden by a subclass.
  Calculation of the initial decade (for both values) and which way to shift decades
  after scanning an entire decade can also be overridden

  Within a decade, this prefers combinations of smaller E-series before moving on,
  eg a satisfying E3 pair is preferred and returned, even if there is a closer E6 pair.
  This has no concept of a distance metric when the spec is satisfied.

  Component tolerances should be handled by the implementing class,
  such as stored as an instance variable.

  The code below is defined in terms of resistors, but this can be used with anything
  that uses the E-series.

  Series should be the zero decade, in the range of [1, 10)
  """
  def __init__(self, series: List[float], round_digits: int = 5):
    self.series = series
    self.round_digits = round_digits

  @abstractmethod
  def _calculate_output(self, r1: float, r2: float) -> RatioOutputType:
    """Given two E-series values, calculate the output parameters."""
    raise NotImplementedError()

  @abstractmethod
  def _get_distance(self, proposed: RatioOutputType, target: RatioOutputType) -> List[float]:
    """Given a proposed output value (from E-series values under test) and the target,
    returns the distance from the acceptable as a list of floats.
    If the list is empty, that means the proposed is considered satisfying.
    Otherwise, distance is sorted by list comparison: for the first element where values differ,
    return the one containing the smallest of the two.

    Note that a non-satisfying zero distance is possible, where the value centers match
    but not the tolerance.

    This somewhat complicated scheme is used to produce a helpful error message."""
    raise NotImplementedError()

  def _no_result_error(self, best_values: Tuple[float, float], best: RatioOutputType,
                       target: RatioOutputType) -> Exception:
    """Given the best tested result and a target, generate an exception to throw.
    This should not throw the exception, only generate it."""
    return Exception("No satisfying result for ratio")

  def _generate_e_series_product(self, r1_decade: int, r2_decade: int) -> List[Tuple[float, float]]:
    """Returns the ordered / sorted cartesian product of all possible pairs of values for the requested decade.
    The output is ordered such that pairs containing numbers earlier in the series comes first,
    so in effect lower E-series combinations are preferred, assuming the series is ordered in a
    zig-zag fashion."""
    r1_series = [ESeriesUtil.round_sig(elt * (10 ** r1_decade), self.round_digits)
                 for elt in self.series]
    r2_series = [ESeriesUtil.round_sig(elt * (10 ** r2_decade), self.round_digits)
                 for elt in self.series]
    out = []
    assert len(r1_series) == len(r2_series), "algorithm depends on same series length"
    for index_max in range(len(r1_series)):
      for index_other in range(index_max):
        out.append((r1_series[index_max], r2_series[index_other]))
        out.append((r1_series[index_other], r2_series[index_max]))
      out.append((r1_series[index_max], r2_series[index_max]))

    return out

  def find(self, target: RatioOutputType) -> Tuple[float, float]:
    """Find a pair of R1, R2 that satisfies the target."""
    initial = self._get_initial_decades(target)
    search_queue = deque(initial)
    searched_decades = set(initial)  # tracks everything that has been on the search queue
    best = None

    while search_queue:
      r1r2_decade = search_queue.popleft()
      product = self._generate_e_series_product(r1r2_decade[0], r1r2_decade[1])

      for (r1, r2) in product:
        output = self._calculate_output(r1, r2)
        output_dist = self._get_distance(output, target)

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


  @abstractmethod
  def _get_initial_decades(self, target: RatioOutputType) -> List[Tuple[int, int]]:
    """Given the target output, return the initial decades (for R1, R2), as log10 to try.
    For example, a decade of 0 means try 1.0, 2.2, 4.7;
    while a decade of -1 means try 10, 22, 47.
    """
    raise NotImplementedError()

  @abstractmethod
  def _get_next_decades(self, decade: Tuple[int, int], target: RatioOutputType) -> List[Tuple[int, int]]:
    """If the target was not found scanning the entire decade, this is called to determine next decades to search.
    This is passed in the current decade and the target.

    Returns a list of decades to search, in order. Internally the search algorithm deduplicates decades.
    This is called for every decade, and results are appended to the end of the search queue after deduplication.
    """
    raise NotImplementedError
