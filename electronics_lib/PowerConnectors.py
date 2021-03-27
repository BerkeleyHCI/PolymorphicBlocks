from electronics_abstract_parts import *


@abstract_block
class PowerBarrelJack(BarrelJack):
  """Barrel jack that models a configurable voltage / max current power supply."""
  @init_in_parent
  def __init__(self,
               voltage_out: RangeLike = Default(RangeExpr.ALL),
               current_limits: RangeLike = Default(RangeExpr.ALL)) -> None:
    super().__init__()

    self.pwr = self.Port(ElectricalSource(voltage_out=voltage_out, current_limits=current_limits))
    self.gnd = self.Port(GroundSource())


class Pj_102a(PowerBarrelJack, CircuitBlock):
  """Barrel jack with 2.1mm ID and 5.5mm OD"""
  def contents(self):
    super().contents()
    self.footprint(
      'J', 'Connector_BarrelJack:BarrelJack_CUI_PJ-102AH_Horizontal',
      {
        '1': self.pwr,
        '2': self.gnd,
        # '3': # TODO optional switch
      },
      mfr='CUI Devices', part='PJ-102AH',
      datasheet='https://www.cui.com/product/resource/digikeypdf/pj-102a.pdf'
    )
