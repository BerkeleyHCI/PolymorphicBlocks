from electronics_abstract_parts import *


class LeadFreeIndicator(Label, CircuitBlock):
  def contents(self):
    super().contents()
    self.footprint(
      '', 'calisco:Indicator_LeadFree',
      {},
      value='LeadFree'
    )


class IdDots4(Label, CircuitBlock):
  def contents(self):
    super().contents()
    self.footprint(
      '', 'calisco:Indicator_IdDots_4',
      {},
      value='IdDots4'
    )


class DuckLogo(Label, CircuitBlock):
  def contents(self):
    super().contents()
    self.footprint(
      'U', 'calisco:Symbol_Duckling',
      {},
      value='Duck'
    )
