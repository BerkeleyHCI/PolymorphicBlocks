from typing import Tuple, Union


class Range:
  """A range type that indicates a range of values and provides utility functions. Immutable.
   Ends are treated as inclusive (closed).
   """

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
