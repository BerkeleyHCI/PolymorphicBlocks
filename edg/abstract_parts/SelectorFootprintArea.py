from ..electronics_model import *
from .PartsTable import PartsTableRow, PartsTableColumn
from .PartsTablePart import PartsTableFootprintSelector


@abstract_block
class SelectorFootprintArea(BlockInterfaceMixin[Block]):
  """A base mixin that defines a footprint_area range specification for blocks that automatically select parts.
  Provides no implementation, only defines the specification parameter."""
  @init_in_parent
  def __init__(self, *args, footprint_area: RangeLike = RangeExpr.ALL, **kwargs):
    super().__init__(*args, **kwargs)
    self.footprint_area = self.ArgParameter(footprint_area)


@non_library
class SelectorFootprintArea(SelectorFootprintArea, PartsTableFootprintSelector):
  KICAD_FOOTPRINT_AREA = PartsTableColumn(Range)

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.generator_param(self.smd_min_package)

  def _row_filter(self, row: PartsTableRow) -> bool:
    return super()._row_filter(row) and \
      (row[self.KICAD_FOOTPRINT_AREA].fuzzy_in(self.get(self.footprint_area)))
