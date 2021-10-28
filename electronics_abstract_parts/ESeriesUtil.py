import itertools
from abc import ABCMeta, abstractmethod
from typing import Sequence, Optional, TypeVar, Tuple, List, Generic, cast
from electronics_model import *
from itertools import chain
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

  E24_SERIES = [
    [1.0],  # E1
    [2.2, 4.7],  # E3
    [1.5, 3.3, 6.8],  # E6
    [1.2, 1.8, 2.7, 3.9, 5.6, 8.2],  # E12
    [1.1, 1.3, 1.6, 2.0, 2.4, 3.0, 3.6, 4.3, 5.1, 6.2, 7.5, 9.1],  # E24
  ]

  # Zigzag (lower E-series first) of the E12 series
  E24_SERIES_ZIGZAG = list(chain(*E24_SERIES))


RatioOutputType = TypeVar('RatioOutputType')
class ESeriesRatioUtil(Generic[RatioOutputType], metaclass=ABCMeta):
  """Base class for an algorithm that searches pairs of E-series numbers
  to get some desired output (eg, ratio and impedance for a resistive divider).
  The output calculations can be overridden by a subclass.
  Calculation of the initial decade (for both values) and which way to shift decades
  after scanning an entire decade is also included.

  Within a decade, this prefers combinations of smaller E-series before moving on,
  eg a satisfying E3 pair is preferred and returned, even if there is a closer E6 pair.
  This has no concept of a distance metric.

  Tolerances should be handled by the implementing class, stored as a instance variable.

  The code below is defined in terms of resistors, but this can be used with anything
  that uses the E-series.
  """
  def __init__(self, series: List[float], round_digits: int = 5):
    self.series = series
    self.round_digits = round_digits

  @abstractmethod
  def _calculate_output(self, r1: float, r2: float) -> RatioOutputType:
    """Given two E-series values, calculate the output parameters."""
    raise NotImplementedError()

  @abstractmethod
  def _is_acceptable(self, proposed: RatioOutputType, target: RatioOutputType) -> bool:
    """Given a proposed output value (from E-series values under test) and the target,
    returns whether it is acceptable."""
    raise NotImplementedError()

  def _generate_e_series_product(self, r1_decade: int, r2_decade: int) -> List[Tuple[float, float]]:
    """Returns the ordered / sorted cartesian product of all possible pairs of values for the requested decade.
    TODO - zigzag ordering"""
    r1_series = [ESeriesUtil.round_sig(elt * (10 ** r1_decade), self.round_digits)
                 for elt in self.series]
    r2_series = [ESeriesUtil.round_sig(elt * (10 ** r2_decade), self.round_digits)
                 for elt in self.series]
    out = []
    for r1_elt in r1_series:
      for r2_elt in r2_series:
        out.append((r1_elt, r2_elt))

    return out

  def find(self, target: RatioOutputType) -> Tuple[float, float]:
    """Find a pair of R1, R2 that satisfies the target."""
    searched_decades = set()  # keep track of what has been tried to avoid infinite loops
    r1r2_decade = self._get_initial_decade(target)
    r1r2_target = r1r2_decade
    while True:
      searched_decades.add(r1r2_decade)

      product = self._generate_e_series_product(r1r2_decade[0], r1r2_decade[1])
      outputs = [(elt, self._calculate_output(elt[0], elt[1])) for elt in product]
      matches = [(elt, output) for (elt, output) in outputs if self._is_acceptable(output, target)]
      if matches:
        return matches[0][0]
      else:
        if r1r2_target == r1r2_decade:  # calculate new target if needed
          adjust = self._get_next_decade([output for (elt, output) in outputs], target)
          if adjust == (0, 0):
            raise ValueError("No value found TODO better error message")
          r1r2_target = (r1r2_decade[0] + adjust[0], r1r2_decade[1] + adjust[1])

        if r1r2_decade[0] < r1r2_target[0]:  # prefer adjusting R1 first
          r1r2_decade = (r1r2_decade[0] + 1, r1r2_decade[1])
        elif r1r2_decade[0] > r1r2_target[0]:
          r1r2_decade = (r1r2_decade[0] - 1, r1r2_decade[1])
        elif r1r2_decade[1] < r1r2_target[1]:  # then adjust R2
          r1r2_decade = (r1r2_decade[0], r1r2_decade[1] + 1)
        elif r1r2_decade[1] > r1r2_target[1]:
          r1r2_decade = (r1r2_decade[0], r1r2_decade[1] - 1)
        else:
          raise ValueError("decade equals target")

  @abstractmethod
  def _get_initial_decade(self, target: RatioOutputType) -> Tuple[int, int]:
    """Given the target output, return the initial decades (for R1, R2), as log10 to try.
    For example, a decade of 0 means try 1.0, 2.2, 4.7;
    while a decade of -1 means try 10, 22, 47.
    """
    raise NotImplementedError()

  @abstractmethod
  def _get_next_decade(self, decade_outputs: List[RatioOutputType], target: RatioOutputType) -> Tuple[int, int]:
    """If the target was not found scanning the entire decade, return the direction to adjust the decades for R1, R2.
    Adjustment should be 0, 1, or -1.
    The algorithm will try all combinations of increments, and if nothing is found again, calls this again.
    Returning (0, 0) means that nothing else can be done and no adjustments can satisfy -
    and will error out with no solution.
    The algorithm will also check for backtracking, which will also error out with no solution
    """
    raise NotImplementedError