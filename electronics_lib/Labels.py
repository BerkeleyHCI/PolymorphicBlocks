from electronics_abstract_parts import *


class LeadFreeIndicator(Label, FootprintBlock):
  def contents(self):
    super().contents()
    self.footprint(
      'U', 'edg:Indicator_LeadFree',
      {},
      value='LeadFree'
    )


class IdDots4(Label, FootprintBlock):
  def contents(self):
    super().contents()
    self.footprint(
      'U', 'edg:Indicator_IdDots_4',
      {},
      value='IdDots4'
    )


class DuckLogo(Label, FootprintBlock):
  def contents(self):
    super().contents()
    self.footprint(
      'U', 'edg:Symbol_Duckling',
      {},
      value='Duck'
    )


class LemurLogo(Label, FootprintBlock):
  def contents(self):
    super().contents()
    self.footprint(
      'U', 'edg:Symbol_LemurSmall',
      {},
      value='Lemur'
    )
