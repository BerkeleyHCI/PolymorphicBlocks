from __future__ import annotations

import re
from typing import *


SourceMap = Callable[[Dict[str, Any]], Optional[Any]]
SourceFilter = Callable[[Dict[str, Any]], bool]


class ProductTable():  # internal helper type
  def __init__(self, header: List[str], rows: List[List[Any]]):
    # deal with some weird null character nonsense
    self.header: List[str] = [header_elt.encode('utf-8').decode('utf-8-sig') for header_elt in header]
    self.rows: List[List[Any]] = rows

  def __add__(self, other: ProductTable):
    assert self.header == other.header, f"headers not equal: {self.header}, {other.header}"
    return ProductTable(self.header, self.rows + other.rows)

  def __len__(self) -> int:
    return len(self.rows)

  def row_to_dict(self, row: List[Any]) -> Dict[str, Any]:
    assert len(row) == len(self.header)
    return {key: value for (key, value) in zip(self.header, row)}

  def first(self, err="no elements in list") -> Dict[str, Any]:
    if not self.rows:
      raise IndexError(err)
    return self.row_to_dict(self.rows[0])

  def derived_column(self, name: str, fn: SourceMap, missing=None) -> ProductTable:
    new_header = self.header + [name]
    def proc_row(row: List[Any]) -> Optional[List[Any]]:
      new_value = fn(self.row_to_dict(row))
      if new_value is None:
        if missing == 'discard':
          return None
        else:
          raise ValueError("Derived column %s produced no result for row %s" % (name, row))
      else:
        return row + [new_value]
    new_rows = [proc_row(row) for row in self.rows]
    cleaned_rows = [row for row in new_rows if row is not None]
    return ProductTable(new_header, cleaned_rows)

  def filter(self, fn: SourceFilter) -> ProductTable:
    new_rows = [row for row in self.rows if fn(self.row_to_dict(row))]
    return ProductTable(self.header, new_rows)

  def sort(self, fn: SourceMap, reverse: bool = False) -> ProductTable:
    def row_key(row: List[Any]) -> Any:
      return fn(self.row_to_dict(row))
    new_rows = sorted(self.rows, key=row_key, reverse=reverse)
    return ProductTable(self.header, new_rows)

def Column(name: str) -> SourceMap:
  def inner(row: Dict[str, Any]) -> Optional[Any]:
    return row[name]  # assume the input row is not sparse, that they key exists even if the cell is empty
  return inner


SI_PREFIX_DICT = {
  '': 1,
  'p': 1e-12,
  'n': 1e-9,
  'μ': 1e-6,
  'µ': 1e-6,
  'u': 1e-6,
  'm': 1e-3,
  'k': 1e3,
  'M': 1e6,
  'G': 1e9,
}


def Lit(value: Any) -> SourceMap:
  def inner(row: Dict[str, Any]) -> Optional[Any]:
    return value
  return inner


def ChooseFirst(*sources: SourceMap) -> SourceMap:
  def inner(row: Dict[str, Any]) -> Optional[Any]:
    for source in sources:
      result = source(row)
      if result is not None:
        return result
    return None
  return inner


def MapDict(source: SourceMap, mapping: dict) -> SourceMap:
  def inner(row: Dict[str, Any]) -> Optional[Tuple[float, float]]:
    result = source(row)
    if result is None or result not in mapping:
      return None
    return mapping[result]
  return inner


def FormatRegex(source: SourceMap, regex: str, format: str) -> SourceMap:
  pattern = re.compile(regex)
  def inner(row: Dict[str, Any]) -> Optional[str]:
    result = cast(str, source(row))
    m = pattern.match(result)
    if not m:
      return None
    return format.format(*m.groups())
  return inner


def ParseValue(source: SourceMap, units: str) -> SourceMap:
  pattern = re.compile('(\d+\.?\d*)\s*(\w*)' + units)
  def inner(row: Dict[str, Any]) -> Optional[float]:
    result = source(row)
    if result is None:
      return None
    m = pattern.search(result)
    if not m:
      return None
    return float(m.group(1)) * SI_PREFIX_DICT[m.group(2)]
  return inner


def StringContains(src: SourceMap, elts: List[str]) -> SourceFilter:
  def inner(row: Dict[str, Any]) -> bool:
    return src(row) in elts
  return inner


def Not(src: SourceFilter) -> SourceFilter:
  def inner(row: Dict[str, Any]) -> bool:
    return not src(row)
  return inner


def Range(lower_source: SourceMap, upper_source: SourceMap) -> SourceMap:
  def inner(row: Dict[str, Any]) -> Optional[Tuple[float, float]]:
    lower_result = lower_source(row)
    upper_result = upper_source(row)
    if not isinstance(lower_result, float) or not isinstance(upper_result, float):
      return None
    return (lower_result, upper_result)
  return inner


def RangeFromLower(source: SourceMap) -> SourceMap:
  def inner(row: Dict[str, Any]) -> Optional[Tuple[float, float]]:
    result = source(row)
    if not isinstance(result, float):
      return None
    return (result, float('inf'))
  return inner


def RangeFromUpper(source: SourceMap, lower: float = -float('inf')) -> SourceMap:
  def inner(row: Dict[str, Any]) -> Optional[Tuple[float, float]]:
    result = source(row)
    if not isinstance(result, float):
      return None
    return (lower, result)
  return inner


def RangeFromTolerance(source: SourceMap, tolerance: SourceMap) -> SourceMap:
  # Parse tolerances of the form ±10%
  def inner(row: Dict[str, Any]) -> Optional[Tuple[float, float]]:
    source_value = cast(float, source(row))
    tolerance_value = cast(str, tolerance(row))
    if tolerance_value[0] == '±' and tolerance_value[-1] == '%':
      source_tolerance = float(tolerance_value[1:-1]) / 100 * source_value
    elif tolerance_value[0] == '±' and tolerance_value[-3:] == 'ppm':
      source_tolerance = float(tolerance_value[1:-3]) / 1000000 * source_value
    else:
      return None  # TODO process items of form ±0.25pF
    return (source_value - source_tolerance, source_value + source_tolerance)
  return inner


def RangeContains(containing: SourceMap, contained: SourceMap) -> SourceFilter:
  def inner(row: Dict[str, Any]) -> bool:
    containing_value = cast(tuple, containing(row))
    contained_value = cast(tuple, contained(row))
    return containing_value[0] <= contained_value[0] and containing_value[1] >= contained_value[1]
  return inner


def Implication(cond: SourceFilter, req: SourceFilter) -> SourceFilter:
  def inner(row: Dict[str, Any]) -> bool:
    return not cond(row) or req(row)
  return inner


def ContainsString(containing: SourceMap, contained_list: Optional[str]) -> SourceFilter:
  def inner(row: Dict[str, Any]) -> bool:
    if contained_list is None:
      return True
    else:
      # TODO support some kind of separator in contained_list
      return containing(row) == contained_list
  return inner
