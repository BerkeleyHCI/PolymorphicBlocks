from typing import Tuple, Union


class Range:
  """A range type that indicates a range of values and provides utility functions. Immutable.
   Ends are treated as inclusive (closed).
   """

  @staticmethod
  def cancel_multiply(input_side: 'Range', output_side: 'Range') -> 'Range':
    """
    This satisfies the property, for Range x:
    cancel_multiply(x, 1/x) = Range(1, 1)

    Range multiplication is weird and 1/x * x does not cancel out, because it's tolerance-expanding.
    Using the RC frequency example, w = 1/(2 pi R C), which solves for the output and tolerances of w
    given R and C (with tolerances), if we want instead solve for C given R and target w,
    we can't simply do C = 1/(2 pi R w) - which would be tolerance-expanding from R and w to C.

    To understand why, it helps to break ranges into tuples:

    [w_max  = 1/2pi * [1/R_min  * [1/C_min
     w_min]            1/R_max]    1/C_max]

    Note that to cancel the tuples (so they equal [1, 1], we need to invert the components
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
    output tolerance (so no result would satisfy the original equation).
    """
    assert isinstance(input_side, Range) and isinstance(output_side, Range)
    assert input_side.lower >= 0 and input_side.upper >= 0, "TODO support negative values"
    assert output_side.lower >= 0 and output_side.upper >= 0, "TODO support negative values"
    lower = input_side.upper * output_side.lower
    upper = input_side.lower * output_side.upper
    assert lower <= upper, f"empty range in cancel-multiply {input_side} and {output_side}"
    return Range(lower, upper)

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
  def from_abs_tolerance(center: float, tolerance: Union[float, Tuple[float, float]]) -> 'Range':
    """Creates a Range given a center value and absolute tolerance.
    If a single tolerance is given, it is treated as bidirectional (+/- value).
    If a tuple of two values is given, it is treated as negative, then positive tolerance."""
    if isinstance(tolerance, tuple):
      assert tolerance[0] <= tolerance[1], f"invalid tolerance {tolerance}"
      return Range(center + tolerance[0], center + tolerance[1])
    elif isinstance(tolerance, (float, int)):
      assert tolerance >= 0, f"bidirectional tolerance {tolerance} must be positive"
      return Range(center - tolerance, center + tolerance)
    else:
      raise ValueError(f"unknown tolerance format {tolerance}")

  @staticmethod
  def from_lower(lower: float) -> 'Range':
    """Creates a Range from lower to positive infinity"""
    return Range(lower, float('inf'))

  @staticmethod
  def from_upper(upper: float) -> 'Range':
    """Creates a Range from negative infinity to upper"""
    return Range(float('-inf'), upper)

  @staticmethod
  def zero_to_upper(upper: float) -> 'Range':
    """Creates a Range from zero to upper"""
    return Range(0, upper)

  @staticmethod
  def exact(value: float) -> 'Range':
    """Creates a Range that is exactly this value (no tolerance)"""
    return Range(value, value)

  @staticmethod
  def all() -> 'Range':
    """Creates a Range that is a superset of every range"""
    return Range(float('-inf'), float('inf'))

  def __repr__(self) -> str:
    return f"Range({self.lower, self.upper})"

  def __init__(self, lower: float, upper: float):
    assert lower <= upper, f"invalid range with lower {lower} > upper {upper}"
    self.lower = float(lower)
    self.upper = float(upper)

  def __eq__(self, other) -> bool:
    if not isinstance(other, Range):
      return False
    return self.lower == other.lower and self.upper == other.upper

  def center(self) -> float:
    return (self.lower + self.upper) / 2

  def __contains__(self, item: Union['Range', float]) -> bool:
    """Return whether other range or float is contained (a subset of) this range."""
    if isinstance(item, (float, int)):
      return self.lower <= item <= self.upper
    elif isinstance(item, Range):
      return self.lower <= item.lower and item.upper <= self.upper
    else:
      return NotImplemented

  def intersects(self, other: 'Range') -> bool:
    return (self.upper >= other.lower) and (self.lower <= other.upper)

  def __add__(self, other: Union['Range', float]) -> 'Range':
    if isinstance(other, Range):
      return Range(self.lower + other.lower, self.upper + other.upper)
    elif isinstance(other, (float, int)):
      return Range(self.lower + other, self.upper + other)
    else:
      return NotImplemented

  def __rsub__(self, other: float) -> 'Range':
    if isinstance(other, (float, int)):
      return Range(other - self.upper, other - self.lower)
    else:
      return NotImplemented

  def __mul__(self, other: Union['Range', float]) -> 'Range':
    if isinstance(other, Range):
      corners = [self.lower * other.lower,
                 self.lower * other.upper,
                 self.upper * other.lower,
                 self.upper * other.upper]
      return Range(min(corners), max(corners))
    elif isinstance(other, (float, int)):
      if other >= 0:
        return Range(self.lower * other, self.upper * other)
      else:
        return Range(self.upper * other, self.lower * other)
    else:
      return NotImplemented

  def __rmul__(self, other: float) -> 'Range':
    if isinstance(other, (float, int)):
      if other >= 0:
        return Range(other * self.lower, other * self.upper)
      else:
        return Range(other * self.upper, other * self.lower)
    else:
      return NotImplemented

  def __truediv__(self, other: Union['Range', float]) -> 'Range':
    if isinstance(other, Range):
      assert other.lower >= 0 or other.upper <= 0, "TODO invert with range crossing zero not supported"
      corners = [self.lower / other.lower,
                 self.lower / other.upper,
                 self.upper / other.lower,
                 self.upper / other.upper]
      return Range(min(corners), max(corners))
    elif isinstance(other, (float, int)):
      if other >= 0:
        return Range(self.lower / other, self.upper / other)
      else:
        return Range(self.upper / other, self.lower / other)
    else:
      return NotImplemented

  def __rtruediv__(self, other: float) -> 'Range':
    assert self.lower >= 0 or self.upper <= 0, "TODO invert with range crossing zero not supported"
    if isinstance(other, (float, int)):
      return Range(other / self.upper, other / self.lower)
    else:
      return NotImplemented

  def extend_upper_to(self, new_upper: float) -> 'Range':
    if new_upper > self.upper:
      return Range(self.lower, new_upper)
    else:
      return self

  def bound_to(self, bounds: 'Range') -> 'Range':
    """Adjusts this range to be within the input bounds.
    If the ranges intersect, returns the intersection.
    If the ranges do not intersect, returns the point at the closer edge of the bounds."""
    if self.lower < bounds.lower:
      new_lower = bounds.lower
    elif self.lower > bounds.upper:
      new_lower = bounds.upper
    else:
      new_lower = self.lower

    if self.upper < bounds.lower:
      new_upper = bounds.lower
    elif self.upper > bounds.upper:
      new_upper = bounds.upper
    else:
      new_upper = self.upper

    return Range(new_lower, new_upper)

  def fuzzy_in(self, container: 'Range') -> bool:
    DOUBLE_FLOAT_ROUND_FACTOR = 1e-7  # approximate multiplier to account for double <-> float rounding issues
    """Contains operation that allows fuzziness due to floating point imprecision."""
    if container.lower >= 0:
      lower = container.lower * (1 - DOUBLE_FLOAT_ROUND_FACTOR)
    else:
      lower = container.lower * (1 + DOUBLE_FLOAT_ROUND_FACTOR)

    if self.upper >= 0:
      upper = container.upper * (1 + DOUBLE_FLOAT_ROUND_FACTOR)
    else:
      upper = container.upper * (1 - DOUBLE_FLOAT_ROUND_FACTOR)
    return self in Range(lower, upper)
