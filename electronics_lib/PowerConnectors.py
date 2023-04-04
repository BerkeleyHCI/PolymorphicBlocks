from electronics_abstract_parts import *


@abstract_block
class PowerBarrelJack(Connector, PowerSource, Block):
  """Barrel jack that models a configurable voltage / max current power supply."""
  @init_in_parent
  def __init__(self,
               voltage_out: RangeLike = RangeExpr(),
               current_limits: RangeLike = Default(RangeExpr.ALL)) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSource(voltage_out=voltage_out, current_limits=current_limits))
    self.gnd = self.Port(GroundSource())


class Pj_102a(PowerBarrelJack, FootprintBlock):
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


class LipoConnector(Connector, Battery):
  """PassiveConnector (abstract connector) that is expected to have a LiPo on one end.
  Both the voltage specification and the actual voltage can be specified as parameters.
  THERE IS NO STANDARD LIPO PINNING OR CONNECTOR - MAKE SURE TO VERIFY THIS!
  BE PREPARED FOR REVERSE POLARITY CONNECTIONS.
  Default pinning has ground being pin 1, and power being pin 2.

  Connector type not specified, up to the user through a refinement.
  Uses pins 1 and 2."""
  @init_in_parent
  def __init__(self, voltage: RangeLike = Default((2.5, 4.2)*Volt), *args,
               actual_voltage: RangeLike = Default((2.5, 4.2)*Volt), **kwargs):
    super().__init__(voltage, *args, **kwargs)
    self.conn = self.Block(PassiveConnector())

    self.connect(self.gnd, self.conn.pins.request('1').adapt_to(GroundSource()))
    self.connect(self.pwr, self.conn.pins.request('2').adapt_to(VoltageSource(
      voltage_out=actual_voltage,  # arbitrary from https://www.mouser.com/catalog/additional/Adafruit_3262.pdf
      current_limits=(0, 5.5)*Amp,  # arbitrary assuming low capacity, 10 C discharge
    )))
    self.assign(self.actual_capacity, (500, 600)*mAmp)  # arbitrary
