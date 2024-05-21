from ..abstract_parts import *
from deprecated import deprecated


@deprecated("non-circuit footprints should be added in layout as non-schematic items")
class LeadFreeIndicator(Label, FootprintBlock):
  def contents(self):
    super().contents()
    self.footprint(
      'U', 'edg:Indicator_LeadFree',
      {},
      value='LeadFree'
    )


@deprecated("non-circuit footprints should be added in layout as non-schematic items")
class IdDots4(Label, FootprintBlock):
  def contents(self):
    super().contents()
    self.footprint(
      'U', 'edg:Indicator_IdDots_4',
      {},
      value='IdDots4'
    )


@deprecated("non-circuit footprints should be added in layout as non-schematic items")
class DuckLogo(Label, FootprintBlock):
  def contents(self):
    super().contents()
    self.footprint(
      'U', 'edg:Symbol_Duckling',
      {},
      value='Duck'
    )


@deprecated("non-circuit footprints should be added in layout as non-schematic items")
class LemurLogo(Label, FootprintBlock):
  def contents(self):
    super().contents()
    self.footprint(
      'U', 'edg:Symbol_LemurSmall',
      {},
      value='Lemur'
    )
