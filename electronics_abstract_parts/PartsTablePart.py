from abc import abstractmethod
from typing import Optional, Union, Any

from electronics_model import *
from .PartsTable import PartsTable, PartsTableColumn, PartsTableRow
from .StandardFootprint import StandardFootprint


class PartsTableBase:
  """A base class defining infrastructure for building a (cached) parts table.
  Subclasses should implement _make_table, which returns the underlying parts table.
  Additional filtering can be done by the generator."""
  _TABLE: Optional[PartsTable] = None

  # These need to be implemented by the part table
  PART_NUMBER_COL: Union[str, PartsTableColumn[str]]
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


@non_library
class PartsTablePart(Block):
  """A mixin for a part that is selected from a table, defining parameters to allow manual part selection
  as well as matching parts.
  Subclasses must implement this."""

  @init_in_parent
  def __init__(self, *args, part: StringLike = Default(""), **kwargs):
    super().__init__(*args, **kwargs)
    self.part = self.ArgParameter(part)
    self.actual_part = self.Parameter(StringExpr())
    self.matching_parts = self.Parameter(ArrayStringExpr())


@non_library
class PartsTableSelector(PartsTablePart, GeneratorBlock, PartsTableBase):
  """PartsTablePart that includes the parts selection framework logic.
  Subclasses only need to extend _row_filter and _row_generate with part-specific logic."""
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.generator_param(self.part)

  def _row_filter(self, row: PartsTableRow) -> bool:
    """Returns whether the candidate row satisfies the requirements (should be kept).
    Only called within generate(), so has access to GeneratorParam.get().
    Subclasses should chain this by and-ing with a super() call."""
    return not self.get(self.part) or (self.get(self.part) == row[self.PART_NUMBER_COL])

  def _table_postprocess(self, table: PartsTable) -> PartsTable:
    """Optional postprocessing step that takes a table and returns a transformed table.
    Only called within generate(), so has access to GeneratorParam.get().
    Subclasses should chain with the results of a super() call."""
    return table

  @classmethod
  def _row_sort_by(cls, row: PartsTableRow) -> Any:
    """Defines an optional sorting key for rows of this parts table."""
    return []

  def _row_generate(self, row: PartsTableRow) -> None:
    """Once a row is selected, this is called to generate the implementation given the part selection.
    Subclasses super chain this with a super() call.
    If there is no matching row, this is not called."""
    self.assign(self.actual_part, row[self.PART_NUMBER_COL])

  def generate(self):
    matching_table = self._get_table().filter(lambda row: self._row_filter(row))
    postprocessed_table = self._table_postprocess(matching_table)
    self.assign(self.matching_parts, postprocessed_table.map(lambda row: row[self.PART_NUMBER_COL]))
    postprocessed_table = postprocessed_table.sort_by(self._row_sort_by)
    if len(postprocessed_table) > 0:
      selected_row = postprocessed_table.first()
      self._row_generate(selected_row)
    else:  # if no matching part, generate a parameter error instead of crashing
      self.require(False, "no matching part")


@non_library
class PartsTableFootprint(PartsTablePart, Block):
  """A PartsTablePart for footprints that defines footprint-specific columns and a footprint spec arg-param.
  This Block doesn't need to directly be a footprint, only that the part search can filter on footprint."""
  KICAD_FOOTPRINT = PartsTableColumn(str)

  @init_in_parent
  def __init__(self, *args, footprint_spec: StringLike = Default(""), **kwargs):
    super().__init__(*args, **kwargs)
    self.footprint_spec = self.ArgParameter(footprint_spec)  # actual_footprint left to the actual footprint


@non_library
class PartsTableFootprintSelector(PartsTableSelector, PartsTableFootprint, StandardFootprint, FootprintBlock):
  """PartsTableFootprint that includes the parts selection framework logic and footprint generator,
  including rows by a footprint spec.
  Subclasses must additionally define the fields required by StandardPinningFootprint, which defines the
  footprint name to pin mapping."""

  # this needs to be defined by the implementing subclass
  REFDES_PREFIX: str

  @init_in_parent
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.generator_param(self.footprint_spec)

  def _row_filter(self, row: PartsTableRow) -> bool:
    return super()._row_filter(row) and \
      ((not self.get(self.footprint_spec)) or self.get(self.footprint_spec) == row[self.KICAD_FOOTPRINT])

  def _row_generate(self, row: PartsTableRow) -> None:
    super()._row_generate(row)
    self.footprint(
      self.REFDES_PREFIX, row[self.KICAD_FOOTPRINT],
      self._make_pinning(row[self.KICAD_FOOTPRINT]),
      mfr=row[self.MANUFACTURER_COL], part=row[self.PART_NUMBER_COL],
      value=row[self.DESCRIPTION_COL],
      datasheet=row[self.DATASHEET_COL]
    )
