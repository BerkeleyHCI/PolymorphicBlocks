from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TypeVar, Generic, Type, overload, Union, Callable, List, Dict, Any, KeysView, Optional, OrderedDict, \
  Tuple, cast
import itertools
import re
import csv

import sys
if sys.version_info[1] < 8:
  from typing_extensions import Protocol
else:
  from typing import Protocol


# from https://stackoverflow.com/questions/47965083/comparable-types-with-mypy
class Comparable(Protocol):
  def __eq__(self, other: Any) -> bool: ...
  def __lt__(self, other: Any) -> bool: ...


PartsTableColumnType = TypeVar('PartsTableColumnType')
class PartsTableColumn(Generic[PartsTableColumnType]):
  """A column header for a parts table, that allows indexing by an object
  (instead of a string) that also checks the value type.
  Required for use in creating a new parts table entry.
  """
  def __init__(self, value_type: Type[PartsTableColumnType]):
    self.value_type = value_type


class PartsTableRow:
  """A row in the parts table. Immutable.
  Internal type, does not do any error checking (so data should be checked before being
  passed into this object)."""
  def __init__(self, value: Dict[Any, Any]):  # TODO Dict not covariant so we can't check key types
    self.value = value

  @overload
  def __getitem__(self, item: str) -> str: ...
  @overload
  def __getitem__(self, item: PartsTableColumn[PartsTableColumnType]) -> PartsTableColumnType: ...

  def __getitem__(self, item: Union[str, PartsTableColumn[PartsTableColumnType]]) -> \
      Union[str, PartsTableColumnType]:
    return self.value[item]


class PartsTable:
  """A parts table, with data that can be loaded from a CSV, and providing functions for
  filtering and transformation.
  Immutable, all data is copied as needed (see functions for depth of copy).

  Optimization TODO: could probably significantly (~2x) improve performance using not-dicts
  https://www.districtdatalabs.com/simple-csv-data-wrangling-with-python
  """
  @classmethod
  def from_csv_files(cls, csv_names: List[str], encoding='utf-8') -> 'PartsTable':
    dict_rows = []
    for filename in csv_names:
      with open(filename, newline='', encoding=encoding) as csvfile:
        reader = csv.DictReader(csvfile)
        dict_rows.extend([row for row in reader])
    return cls.from_dict_rows(dict_rows)

  @staticmethod
  def from_dict_rows(*dict_rowss: Union[List[Dict[str, str]], List[OrderedDict[str, str]]]) -> 'PartsTable':
    """Creates a parts table from dict rows, such as parsed by csv.DictReader.
    Checks to make sure all incoming rows are dense (have all cells)."""
    all_dict_rows = list(itertools.chain(*dict_rowss))

    if len(all_dict_rows) > 1:  # if nonempty, check for consistency
      first_keys = set(all_dict_rows[0].keys())
      for dict_row in all_dict_rows[1:]:
        difference = first_keys.symmetric_difference(set(dict_row.keys()))
        assert not difference, f"table has different keys: {difference}"
    rows = [PartsTableRow(dict_row) for dict_row in all_dict_rows]
    return PartsTable(rows)

  def __len__(self) -> int:
    return len(self.rows)

  def __init__(self, rows: List[PartsTableRow]):
    """Internal function, just creates a new PartsTable wrapping the rows, without any checking."""
    self.rows = rows

  def filter(self, fn: Callable[[PartsTableRow], bool]) -> PartsTable:
    """Creates a new table view (shallow copy) with rows filtered according to some criteria."""
    new_rows = [row for row in self.rows
                if fn(row)]
    return PartsTable(new_rows)

  def map_new_columns(self, fn: Callable[[PartsTableRow], Optional[Dict[PartsTableColumn[Any], Any]]]) -> PartsTable:
    """Creates a new table (deep copy) with additional rows."""
    new_rows: List[PartsTableRow] = []
    first_keys: Optional[KeysView] = None
    for row in self.rows:
      new_columns = fn(row)
      if new_columns is None:
        continue

      if first_keys is None:
        first_keys = new_columns.keys()
        assert first_keys.isdisjoint(row.value.keys()), \
          f"new columns {new_columns} not disjoint with existing row keys {row.value.keys()}"
      else:
        assert first_keys == new_columns.keys(), \
          f"new columns {new_columns} in row {row} has different keys than first row keys {first_keys}"
      for new_col_key, new_col_val in new_columns.items():
        assert isinstance(new_col_key, PartsTableColumn), \
          f"new column key {new_col_key} in {row} not of type PartsTableColumn"
        assert isinstance(new_col_val, new_col_key.value_type), \
          f"new column elt {new_col_key}={new_col_val} in {row} not of expected type {new_col_key.value_type}"
      new_row_dict = {}
      new_row_dict.update(row.value)
      new_row_dict.update(new_columns)
      new_rows.append(PartsTableRow(new_row_dict))
    return PartsTable(new_rows)

  MapType = TypeVar('MapType')
  def map(self, fn: Callable[[PartsTableRow], MapType]) -> List[MapType]:
    """Applies a transformation function to every row and returns the results as a list."""
    output = []
    for row in self.rows:
      output.append(fn(row))
    return output

  ComparableType = TypeVar('ComparableType', bound=Comparable)
  def sort_by(self, fn: Callable[[PartsTableRow], ComparableType], reverse: bool = False) -> PartsTable:
    """Creates a new table view (shallow copy) with rows sorted in some order.

    TODO this should support Comparable, but that's not a builtin protocol :(
    """
    new_rows = sorted(self.rows, key=fn, reverse=reverse)
    return PartsTable(new_rows)

  def first(self, err="no elements in list") -> PartsTableRow:
    if not self.rows:
      raise IndexError(err)
    return self.rows[0]


class PartsTableUtil:
  class ParseError(Exception):
    pass

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
  SI_PREFIXES = ''.join(SI_PREFIX_DICT.keys())

  NUMBER_REGEX = '\d+(?:\.\d+)?'

  VALUE_REGEX = re.compile(f'^({NUMBER_REGEX})\s*([{SI_PREFIXES}]?)(.+)$')
  DefaultType = TypeVar('DefaultType')
  @classmethod
  @overload
  def parse_value(cls, value: str, units: str) -> float: ...
  @classmethod
  @overload
  def parse_value(cls, value: str, units: str, default: DefaultType) -> Union[DefaultType, float]: ...
  @classmethod
  def parse_value(cls, value: str, units: str, default: Union[Type[ParseError], DefaultType] = ParseError) -> Union[DefaultType, float]:
    """Parses a value with unit and SI prefixes, for example '20 nF' would be parsed as 20e-9.
    If the input is not a value:
      if default is not specified, raises a ParseError.
      if default is specified, returns the default."""
    matches = cls.VALUE_REGEX.match(value)
    if matches is not None and matches.group(3) == units:
      return float(matches.group(1)) * cls.SI_PREFIX_DICT[matches.group(2)]
    else:
      if default == cls.ParseError:
        raise cls.ParseError(f"Cannot parse units {units} from {value}")
      else:
        return default  #type:ignore


  TOLERANCE_REGEX = re.compile(f'^(±)\s*({NUMBER_REGEX})\s*(ppm|%)$')
  @classmethod
  def parse_tolerance(cls, value: str) -> Tuple[float, float]:
    """Parses a tolerance value and returns the negative and positive tolerance as a tuple of normalized values.
    For example, ±10% would be returned as (-0.1, 0.1)"""
    matches = cls.TOLERANCE_REGEX.match(value)
    if matches is not None and matches.group(1) == '±':  # only support the ± case right now
      if matches.group(3) == '%':
        scale = 1.0/100
      elif matches.group(3) == 'ppm':
        scale = 1e-6
      else:
        raise cls.ParseError(f"Cannot determine tolerance scale from {value}")
      parsed = float(matches.group(2))
      return -parsed * scale, parsed * scale
    else:
      raise cls.ParseError(f"Cannot determine tolerance type from {value}")

  @staticmethod
  def strip_parameter(value: str) -> str:
    """Given a value string that possibly contains a parameter (eg, 2V @ 1A),
    strips the @ and everything after.
    If the string does not contain @, it is passed through as-is.
    """
    if '@' in value:
      return value[:value.find('@')].rstrip()
    else:
      return value


  @staticmethod
  def with_source_dir(filenames: List[str], subdir: Optional[str] = None) -> List[str]:
    """Given a list of filenames, prepends the absolute path to the calling source file, with an optional subdir.
    """
    from types import FrameType
    import inspect
    import os

    calling_filename = cast(FrameType, cast(FrameType, inspect.currentframe()).f_back).f_code.co_filename
    prefix_dir = os.path.dirname(calling_filename)
    if subdir is not None:
      prefix_dir = os.path.join(prefix_dir, subdir)
    return [os.path.join(prefix_dir, filename) for filename in filenames]

  class RegexRemapper:
    """
    A utility class for transforming strings by applying a regex to the input string,
    then applying the captured groups to an output string.

    If the regex does not match, returns None.
    Crashes if the regex matches, but a capture group in the remap string is unavailable.

    For example, RegexRemapper(r'^duck(\\d\\d)$', 'quack{0}').apply('duck02') returns 'quack02'.
    """
    def __init__(self, regex: str, remap: str):
      self.regex = re.compile(regex)
      self.remap = remap

    def apply(self, input: str) -> Optional[str]:
      match = self.regex.match(input)
      if match is not None:
        return self.remap.format(*match.groups())
      else:
        return None


class LazyTable(metaclass=ABCMeta):
  """A wrapper around PartTable that doesn't generate the table until the first time it's requested.
  The generated table is then stored for future use."""

  _table: PartsTable

  @classmethod
  def table(cls) -> PartsTable:
    if not hasattr(cls, '_table'):
      cls._table = cls._generate_table()
    return cls._table

  @classmethod
  @abstractmethod
  def _generate_table(cls) -> PartsTable: ...
