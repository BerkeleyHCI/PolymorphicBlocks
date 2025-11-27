from __future__ import annotations

import csv
import itertools
from typing import TypeVar, Generic, Type, overload, Union, Callable, List, Dict, Any, KeysView, Optional, OrderedDict, \
  cast, Tuple, Sequence, Protocol

from typing_extensions import ParamSpec

from ..core import Range


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
    self.values = value

  @overload
  def __getitem__(self, item: str) -> str: ...
  @overload
  def __getitem__(self, item: PartsTableColumn[PartsTableColumnType]) -> PartsTableColumnType: ...

  def __getitem__(self, item: Union[str, PartsTableColumn[PartsTableColumnType]]) -> \
      Union[str, PartsTableColumnType]:
    value = self.values[item]
    if isinstance(item, str):
      assert isinstance(value, str)
      return value
    elif isinstance(item, PartsTableColumn):
      assert isinstance(value, item.value_type)
      return value
    else:
      raise TypeError()


class PartsTable:
  """A parts table, with data that can be loaded from a CSV, and providing functions for
  filtering and transformation.
  Immutable, all data is copied as needed (see functions for depth of copy).

  Optimization TODO: could probably significantly (~2x) improve performance using not-dicts
  https://www.districtdatalabs.com/simple-csv-data-wrangling-with-python
  """
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

  @classmethod
  def from_csv_files(cls, csv_names: List[str], encoding: str='utf-8') -> 'PartsTable':
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

  def map_new_columns(self, fn: Callable[[PartsTableRow], Optional[Dict[PartsTableColumn[Any], Any]]],
                      overwrite: bool = False) -> PartsTable:
    """Creates a new table (deep copy) with additional rows.
    All entries must have the same keys.
    Specify overwrite=True to overwrite an existing row. To preserve the existing value (no-op), return it.
    Return None to drop the row."""
    new_rows: List[PartsTableRow] = []
    first_keys: Optional[KeysView] = None
    for row in self.rows:
      new_columns = fn(row)
      if new_columns is None:
        continue

      if first_keys is None:
        first_keys = new_columns.keys()
        assert first_keys.isdisjoint(row.values.keys()) or overwrite, \
          f"new columns {new_columns} overwrites existing row keys {row.values.keys()} without overwrite=True"
      else:
        assert first_keys == new_columns.keys(), \
          f"new columns {new_columns} in row {row} has different keys than first row keys {first_keys}"
      for new_col_key, new_col_val in new_columns.items():
        assert isinstance(new_col_key, PartsTableColumn), \
          f"new column key {new_col_key} in {row} not of type PartsTableColumn"
        assert isinstance(new_col_val, new_col_key.value_type), \
          f"new column elt {new_col_key}={new_col_val} in {row} not of expected type {new_col_key.value_type}"
      new_row_dict = {}
      new_row_dict.update(row.values)
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

  def first(self, err: str="no elements in list") -> PartsTableRow:
    if not self.rows:
      raise IndexError(err)
    return self.rows[0]


UserFnMetaParams = ParamSpec('UserFnMetaParams')
UserFnType = TypeVar('UserFnType', bound=Callable, covariant=True)
class UserFnSerialiable(Protocol[UserFnMetaParams, UserFnType]):
  """A protocol that marks functions as usable in deserialize, that they have been registered."""
  _is_serializable: None  # guard attribute

  def __call__(self, *args: UserFnMetaParams.args, **kwargs: UserFnMetaParams.kwargs) -> UserFnType: ...
  __name__: str


class ExperimentalUserFnPartsTable(PartsTable):
  """A PartsTable that can take in a user-defined function for filtering and (possibly) other operations.
  These functions are serialized to a string by an internal name (cannot execute arbitrary code,
  bounded to defined functions in the codebase), and some arguments can be serialized with the name
  (think partial(...)).
  Functions must be pre-registered using the @ExperimentalUserFnPartsTable.user_fn(...) decorator,
  non-pre-registered functions will not be available.

  This is intended to support searches on parts tables that are cross-coupled across multiple parameters,
  but still restricted to within on table (e.g., no cross-optimizing RC filters).

  EXPERIMENTAL - subject to change without notice."""

  _FN_SERIALIZATION_SEPARATOR = ";"

  _user_fns: Dict[str, Tuple[Callable, Sequence[Type]]] = {}  # name -> fn, [arg types]
  _fn_name_dict: Dict[Callable, str] = {}

  @staticmethod
  def user_fn(param_types: Sequence[Type] = []) -> Callable[[Callable[UserFnMetaParams, UserFnType]],
      UserFnSerialiable[UserFnMetaParams, UserFnType]]:
    def decorator(fn: Callable[UserFnMetaParams, UserFnType]) -> UserFnSerialiable[UserFnMetaParams, UserFnType]:
      """Decorator to register a user function that can be used in ExperimentalUserFnPartsTable."""
      if fn.__name__ in ExperimentalUserFnPartsTable._user_fns or fn in ExperimentalUserFnPartsTable._fn_name_dict:
          raise ValueError(f"Function {fn.__name__} already registered.")
      ExperimentalUserFnPartsTable._user_fns[fn.__name__] = (fn, param_types)
      ExperimentalUserFnPartsTable._fn_name_dict[fn] = fn.__name__
      return fn  # type: ignore
    return decorator

  @classmethod
  def serialize_fn(cls, fn: UserFnSerialiable[UserFnMetaParams, UserFnType],
                   *args: UserFnMetaParams.args, **kwargs: UserFnMetaParams.kwargs) -> str:
    """Serializes a user function to a string."""
    assert not kwargs, "kwargs not supported in serialization"
    if fn not in cls._fn_name_dict:
      raise ValueError(f"Function {fn} not registered.")
    fn_ctor, fn_argtypes = cls._user_fns[fn.__name__]
    def serialize_arg(tpe: Type, val: Any) -> str:
      assert isinstance(val, tpe), f"in serialize {val}, expected {tpe}, got {type(val)}"
      if tpe is bool:
        return str(val)
      elif tpe is int:
        return str(val)
      elif tpe is float:
        return str(val)
      elif tpe is Range:
        return f"({val.lower},{val.upper})"
      else:
        raise TypeError(f"cannot serialize type {tpe} in user function serialization")
    serialized_args = [serialize_arg(tpe, arg) for tpe, arg in zip(fn_argtypes, args)]
    return cls._FN_SERIALIZATION_SEPARATOR.join([fn.__name__] + serialized_args)

  @classmethod
  def deserialize_fn(cls, serialized: str) -> Any:
    """Deserializes and applies a user function from a string."""
    split = serialized.split(cls._FN_SERIALIZATION_SEPARATOR)
    if split[0] not in cls._user_fns:
      raise ValueError(f"Function {serialized} not registered.")
    fn_ctor, fn_argtypes = cls._user_fns[split[0]]
    assert len(split) == len(fn_argtypes) + 1
    def deserialize_arg(tpe: Type, val: str) -> Any:
      if tpe is bool:
        return val == 'True'
      elif tpe is int:
        return int(val)
      elif tpe is float:
        return float(val)
      elif tpe is Range:
        parts = val[1:-1].split(",")
        return Range(float(parts[0]), float(parts[1]))
      else:
        raise TypeError(f"cannot deserialize type {tpe} in user function serialization")
    deserialized_args = [deserialize_arg(tpe, arg) for tpe, arg in zip(fn_argtypes, split[1:])]
    return fn_ctor(*deserialized_args)
