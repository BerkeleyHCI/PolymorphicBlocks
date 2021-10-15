from typing import Tuple, Union


class Range:
  """A range type that indicates a range of values and provides utility functions. Immutable.
   Ends are treated as inclusive (closed).
   """

  @staticmethod
  def cancel_multiply(input_side: 'Range', output_side: 'Range') -> 'Range':
    """
    Range multiplication is weird and 1/x * x does not cancel out, because it's tolerance-expanding.
    Using the RC frequency example, w = 1/(2 pi R C), which solves for the output and tolerances of w
    given R and C (with tolerances), if we want instead solve for C given R and target w,
    we can't simply do C = 1/(2 pi R w) - which would be tolerance-expanding from R and w to C.

    To understand why, it helps to break ranges into vectors:

    [w_max  = 1/2pi * [1/R_min  * [1/C_min
     w_min]            1/R_max]    1/C_max]

    Note that to cancel the vectors (so they equal [1, 1], we need to invert the vector components
    without flipping the order. For example, to move the C to the left side, we need to multiply
    both sides by:

    [C_min
     C_max]

    which itself is an invalid range, since the top element is lower than the bottom element.
    Doing the same with w, this resolves into

    [C_min  = 1/2pi * [1/R_min  * [1/w_max
     C_max]            1/R_max]    1/w_min]

    So that this function does is:
    flip(input_side * flip(output_side))
    and the above would be expressed as:
    C = cancel_multiply(1/(2*pi*R), 1/w)

    THIS MAY RETURN AN EMPTY RANGE - for example, if the input tolerance is larger than the
    output tolerance (so no result would satisfy the original equiation).
    """
    pass

  @staticmethod
  def from_tolerance(center: float, tolerance: Union[float, Tuple[float, float]]) -> 'Range':
    """Creates a Range given a center value and normalized tolerance percentage.
    If a single tolerance is given, it is treated as bidirectional (+/- value).
    If a tuple of two values is given, it is treated as negative, then positive tolerance."""
    if isinstance(tolerance, tuple):
      assert tolerance[0] <= tolerance[1], f"invalid tolerance {tolerance}"
      return Range(center * (1 + tolerance[0]), center * (1 + tolerance[1]))
    elif isinstance(tolerance, (float, int)):
      assert tolerance >= 0, f"bidirectional tolerance {tolerance} must be positive"
      return Range(center * (1 - tolerance), center * (1 + tolerance))
    else:
      raise ValueError(f"unknown tolerance format {tolerance}")

  @staticmethod
  def from_lower(lower: float) -> 'Range':
    """Creates a Range from lower to positive infinity"""
    return Range(lower, float('inf'))

  @staticmethod
  def from_upper(upper: float) -> 'Range':
    """Creates a Range from upper to negative infinity"""
    return Range(float('-inf'), upper)

  @staticmethod
  def all() -> 'Range':
    """Creates a Range that is a superset of every range"""
    return Range(float('-inf'), float('inf'))

  def __repr__(self) -> str:
    return f"Range({self.lower, self.upper})"

  def __init__(self, lower: float, upper: float):
    assert lower <= upper, f"invalid range with lower {lower} > upper {upper}"
    self.lower = lower
    self.upper = upper

  def __contains__(self, item: Union['Range', float]) -> bool:
    """Return whether other range or float is contained (a subset of) this range."""
    if isinstance(item, (float, int)):
      return self.lower <= item <= self.upper
    elif isinstance(item, Range):
      return self.lower <= item.lower and item.upper <= self.upper
    else:
      raise ValueError(f"unknown other {item}")

  def __mul__(self, other: float) -> 'Range':
    if isinstance(other, (float, int)):
      if other >= 0:
        return Range(self.lower * other, self.upper * other)
      else:
        return Range(self.upper * other, self.lower * other)
    else:
      return NotImplemented

  def __eq__(self, other) -> bool:
    if not isinstance(other, Range):
      return False
    return self.lower == other.lower and self.upper == other.upper
