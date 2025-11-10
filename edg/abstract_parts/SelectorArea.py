from ..electronics_model import *
from .PartsTable import PartsTableRow
from .PartsTablePart import PartsTableFootprintFilter, PartsTablePart


@abstract_block
class SelectorArea(PartsTablePart):
  """A base mixin that defines a footprint_area range specification for blocks that automatically select parts.
  Provides no implementation, only defines the specification parameter.

  Some common areas for SMD parts:
  01005   R=0.72    C=0.72    D=0.72
  0201    R=0.98    C=0.98    D=0.98
  0402    R=1.7484  C=1.6744  D=1.7484
  0603    R=4.3216  C=4.3216  D=4.3216
  0805    R=6.384   C=6.664   D=6.384
  1206    R=10.2144 C=10.58   D=10.2144
  1812    R=23.01   C=23.4    D=23.01
  2512    R=29.3376           D=29.3376
  """
  def __init__(self, *args, footprint_area: RangeLike = RangeExpr.ALL, **kwargs):
    super().__init__(*args, **kwargs)
    self.footprint_area = self.ArgParameter(footprint_area)

  @classmethod
  def _footprint_area(cls, footprint_name: str) -> float:
    return FootprintDataTable.area_of(footprint_name)


@non_library
class PartsTableAreaSelector(PartsTableFootprintFilter, SelectorArea):
  """Defines an implementation for the area selector using parts tables and KICAD_FOOTPRINT."""
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.generator_param(self.footprint_area)

  def _row_filter(self, row: PartsTableRow) -> bool:
    return super()._row_filter(row) and \
      (Range.exact(FootprintDataTable.area_of(row[self.KICAD_FOOTPRINT])).fuzzy_in(self.get(self.footprint_area)))

  @classmethod
  def _row_area(cls, row: PartsTableRow) -> float:
    """Returns the area of the part in the row, for use in sorting."""
    return FootprintDataTable.area_of(row[cls.KICAD_FOOTPRINT])
