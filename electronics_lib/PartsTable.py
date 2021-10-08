from __future__ import annotations

import itertools
from typing import TypeVar, Generic, Type, overload, Union, Callable, List, Dict, Any, KeysView, Optional, OrderedDict

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
  @staticmethod
  def from_dict_rows(*dict_rowss: Union[List[Dict[str, str]], List[OrderedDict[str, str]]]):
    """Creates a parts table from dict rows, such as parsed by csv.DictReader.
    Checks to make sure all incoming rows are dense (have all cells)."""
    all_dict_rows = list(itertools.chain(*dict_rowss))

    if len(all_dict_rows) > 1:  # if nonempty, check for consistency
      first_keys = all_dict_rows[0].keys()
      for dict_row in all_dict_rows[1:]:
        assert dict_row.keys() == first_keys, f"row {dict_row} has different keys than first row keys {first_keys}"
    rows = [PartsTableRow(dict_row) for dict_row in all_dict_rows]
    return PartsTable(rows)

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

  def sort_by(self, fn: Callable[[PartsTableRow], Union[float, int]], reverse: bool = False) -> PartsTable:
    """Creates a new table view (shallow copy) with rows sorted in some order."""
    new_rows = sorted(self.rows, key=fn, reverse=reverse)
    return PartsTable(new_rows)

  def first(self, err="no elements in list") -> PartsTableRow:
    if not self.rows:
      raise IndexError(err)
    return self.rows[0]
