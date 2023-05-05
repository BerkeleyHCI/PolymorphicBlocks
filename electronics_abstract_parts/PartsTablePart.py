from abc import abstractmethod
from typing import Optional, Union, Any

from electronics_model import *
from .PartsTable import PartsTable, PartsTableColumn, PartsTableRow
from .StandardPinningFootprint import StandardPinningFootprint


@non_library
class PartsTablePart(Block):
  """A 'mixin' for a part that contains a (cached) parts table and filters based on it.
  Subclasses should implement _make_table, which returns the underlying parts table.
  Additional filtering can be done by the generator.
  Defines a PART_NUMBER table column and a part spec arg-param."""
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
  @abstractmethod
  def _row_sort_by(cls, row: PartsTableRow) -> Any:
    """Defines a sorting key for rows of this parts table. Implement me."""
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
    self.matching_parts = self.Parameter(ArrayStringExpr())


@non_library
class PartsTableSelector(PartsTablePart, GeneratorBlock):
  """PartsTablePart that includes the parts selection framework logic.
  Subclasses only need to extend _row_filter and _row_generate with part-specific logic."""
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.part_value = self.GeneratorParam(self.part)

  def _row_filter(self, row: PartsTableRow) -> bool:
    """Returns whether the candidate row satisfies the requirements (should be kept).
    Only called within generate(), so has access to GeneratorParam.get().
    Subclasses should chain this by and-ing with a  super() call."""
    return not self.part_value.get() or (self.part_value.get() == row[self.PART_NUMBER_COL])

  def _row_generate(self, row: PartsTableRow) -> None:
    """Once a row is selected, this is called to generate the implementation given the part selection.
    Subclasses super chain this with a super() call.
    If there is no matching row, this is not called."""
    self.assign(self.actual_part, row[self.PART_NUMBER_COL])

  def generate(self):
    matching_rows = self._get_table().filter(lambda row: self._row_filter(row))
    self.assign(self.matching_parts, matching_rows.map(lambda row: row[self.PART_NUMBER_COL]))
    if len(matching_rows) > 0:
      selected_row = matching_rows.first()
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
class PartsTableFootprintSelector(PartsTableSelector, PartsTableFootprint, StandardPinningFootprint, FootprintBlock):
  """PartsTableFootprint that includes the parts selection framework logic and footprint generator,
  including rows by a footprint spec.
  Subclasses must additionally define the fields required by StandardPinningFootprint, which defines the
  footprint name to pin mapping."""

  # this needs to be defined by the implementing subclass
  REFDES_PREFIX: str

  @init_in_parent
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.footprint_spec_value = self.GeneratorParam(self.footprint_spec)

  def _row_filter(self, row: PartsTableRow) -> bool:
    return super()._row_filter(row) and \
      ((not self.footprint_spec_value.get()) or self.footprint_spec_value.get() == row[self.KICAD_FOOTPRINT])

  def _row_generate(self, row: PartsTableRow) -> None:
    super()._row_generate(row)
    self.footprint(
      self.REFDES_PREFIX, row[self.KICAD_FOOTPRINT],
      self._make_pinning(row[self.KICAD_FOOTPRINT]),
      mfr=row[self.MANUFACTURER_COL], part=row[self.PART_NUMBER_COL],
      value=row[self.DESCRIPTION_COL],
      datasheet=row[self.DATASHEET_COL]
    )
