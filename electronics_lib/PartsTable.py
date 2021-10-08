from __future__ import annotations

from typing import TypeVar, Generic, Type, overload, Union, Callable, List, Dict, Any


PartsTableColumnType = TypeVar('PartsTableColumnType')
class PartsTableColumn(Generic[PartsTableColumnType]):
  """A column header for a parts table, that allows indexing by an object
  (instead of a string) that also checks the value type.
  Required for use in creating a new parts table entry.
  """
  def __init__(self, value_type: Type[PartsTableColumnType]):
    self.value_type = value_type


class PartsTableRow:
  """A row in the parts table. Immutable."""
  def __init__(self):
    pass

  @overload
  def __getitem__(self, item: str) -> str: ...
  @overload
  def __getitem__(self, item: PartsTableColumn[PartsTableColumnType]) -> PartsTableColumnType: ...

  def __getitem__(self, item: Union[str, PartsTableColumnType[PartsTableColumnType]]) -> \
      Union[str, PartsTableColumnType]:
    pass


class PartsTable:
  """A parts table, with data that can be loaded from a CSV, and providing functions for
  filtering and transformation.
  Immutable, all data is copied as needed (see functions for depth of copy).
  """
  @staticmethod
  def from_csvs(cls, csvs):
    pass

  def __init__(self, rows: List[PartsTableRow]):
    pass

  def filter(self, fn: Callable[[PartsTableRow], bool]) -> PartsTable:
    """Creates a new table view (shallow copy) with rows filtered according to some criteria."""
    pass

  def map_new_columns(self, fn: Callable[[PartsTableRow], Dict[PartsTableColumn[Any], Any]]) -> PartsTable:
    """Creates a new table (deep copy) with additional rows."""
    pass

  def sort_by(self, fn: Callable[[PartsTableRow], Union[float, int]]) -> PartsTable:
    """Creates a new table view (shallow copy) with rows sorted in some order."""
    pass
