from abc import abstractmethod
from typing import Optional, Union

from electronics_model import *
from .PartsTable import PartsTable, PartsTableColumn, PartsTableRow


class PartsTablePart(Block):
  """A 'mixin' for a part that contains a (cached) parts table and filters based on it.
  Subclasses should implement _make_table, which returns the underlying parts table.
  Additional filtering can be done by the generator.
  Defines a PART_NUMBER table column and a part spec arg-param."""
  _TABLE: Optional[PartsTable] = None
  PART_NUMBER_COL: Union[str, PartsTableColumn[str]]

  # These need to be implemented by the part table
  MANUFACTURER_COL: Union[str, PartsTableColumn[str]]
  DESCRIPTION_COL: Union[str, PartsTableColumn[str]]
  DATASHEET_COL: Union[str, PartsTableColumn[str]]

  @classmethod
  @abstractmethod
  def _make_table(cls) -> PartsTable:
    """Returns a parts table for this device. Implement me."""
    ...

  @classmethod
  def _get_table(cls) -> PartsTable:
    if cls._TABLE is None:
      cls._TABLE = cls._make_table()
      if len(cls._TABLE) == 0:
        raise ValueError(f"{cls.__name__} _make_table returned empty table")
    return cls._TABLE

  @init_in_parent
  def __init__(self, *args, part: StringLike = Default(""), **kwargs):
    super().__init__(*args, **kwargs)
    self.part = self.ArgParameter(part)
    self.actual_part = self.Parameter(StringExpr())
    self.matching_parts = self.Parameter(IntExpr())


class PartsTableFootprint(PartsTablePart, Block):
  """A PartsTablePart for footprints that defines footprint-specific columns and a footprint spec arg-param."""
  KICAD_FOOTPRINT = PartsTableColumn(str)

  @init_in_parent
  def __init__(self, *args, footprint_spec: StringLike = Default(""), **kwargs):
    super().__init__(*args, **kwargs)
    self.footprint_spec = self.ArgParameter(footprint_spec)  # actual_footprint left to the actual footprint


  @abstractmethod
  def _make_footprint(self, part: PartsTableRow) -> None:
    """Given a selected part (row), creates the footprint. Implement me."""
    ...
