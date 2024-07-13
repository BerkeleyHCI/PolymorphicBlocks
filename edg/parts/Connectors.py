from ..abstract_parts import *
from .PassiveConnector_Header import JstShSmHorizontal


@abstract_block
class PowerBarrelJack(Connector, PowerSource, Block):
  """Barrel jack that models a configurable voltage / max current power supply."""
  @init_in_parent
  def __init__(self,
               voltage_out: RangeLike = RangeExpr(),
               current_limits: RangeLike = RangeExpr.ALL) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSource(voltage_out=voltage_out, current_limits=current_limits))
    self.gnd = self.Port(Ground())


class Pj_102ah(PowerBarrelJack, FootprintBlock):
  """Barrel jack for 2.1mm ID and 5.5mm OD"""
  def contents(self):
    super().contents()
    self.require(self.pwr.voltage_out.within((0, 24)*Volt))  # datasheet ratings for connector
    self.require(self.pwr.current_limits.within((0, 2.5)*Volt))
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


class Pj_036ah(PowerBarrelJack, FootprintBlock):
  """SMT Barrel jack for 2.1mm ID and 5.5mm OD"""
  def contents(self):
    super().contents()
    self.require(self.pwr.voltage_out.within((0, 24)*Volt))  # datasheet ratings for connector
    self.require(self.pwr.current_limits.within((0, 5)*Volt))

    self.footprint(
      'J', 'Connector_BarrelJack:BarrelJack_CUI_PJ-036AH-SMT_Horizontal',
      {
        '1': self.pwr,
        '2': self.gnd,
        # '3': # TODO optional switch
      },
      mfr='CUI Devices', part='PJ-036AH-SMT',
      datasheet='https://www.cuidevices.com/product/resource/pj-036ah-smt-tr.pdf'
    )


class LipoConnector(Connector, Battery):
  """PassiveConnector (abstract connector) that is expected to have a LiPo on one end.
  Both the voltage specification and the actual voltage can be specified as parameters.
  THERE IS NO STANDARD LIPO PINNING OR CONNECTOR - MAKE SURE TO VERIFY THIS!
  BE PREPARED FOR REVERSE POLARITY CONNECTIONS.
  Default pinning has ground being pin 1, and power being pin 2.

  Connector type not specified, up to the user through a refinement."""
  @init_in_parent
  def __init__(self, voltage: RangeLike = (2.5, 4.2)*Volt, *args,
               actual_voltage: RangeLike = (2.5, 4.2)*Volt, **kwargs):
    from ..electronics_model.PassivePort import PassiveAdapterVoltageSink
    super().__init__(voltage, *args, **kwargs)
    self.chg = self.Port(VoltageSink.empty(), optional=True)  # ideal port for charging
    self.conn = self.Block(PassiveConnector())

    self.connect(self.gnd, self.conn.pins.request('1').adapt_to(Ground()))
    pwr_pin = self.conn.pins.request('2')
    self.connect(self.pwr, pwr_pin.adapt_to(VoltageSource(
      voltage_out=actual_voltage,  # arbitrary from https://www.mouser.com/catalog/additional/Adafruit_3262.pdf
      current_limits=(0, 5.5)*Amp,  # arbitrary assuming low capacity, 10 C discharge
    )))
    self.chg_adapter = self.Block(PassiveAdapterVoltageSink())
    self.connect(pwr_pin, self.chg_adapter.src)
    self.connect(self.chg, self.chg_adapter.dst)
    self.assign(self.actual_capacity, (500, 600)*mAmp)  # arbitrary


class QwiicTarget(Connector):
  """A Qwiic (https://www.sparkfun.com/qwiic) connector to a I2C target.
  This would be on a board with a host controller."""
  def __init__(self):
    super().__init__()
    self.conn = self.Block(JstShSmHorizontal(4))
    self.gnd = self.Export(self.conn.pins.request('1').adapt_to(Ground()), [Common])
    self.pwr = self.Export(self.conn.pins.request('2').adapt_to(VoltageSink(
      voltage_limits=3.3*Volt(tol=0.05),  # required 3.3v per the spec, tolerance assumed
      current_draw=(0, 226)*mAmp,  # per the Qwiic FAQ, max current for the cable
    )), [Power])
    self.i2c = self.Port(I2cTarget(DigitalBidir.empty()), [InOut])
    self.connect(self.i2c.sda, self.conn.pins.request('3').adapt_to(DigitalBidir()))
    self.connect(self.i2c.scl, self.conn.pins.request('4').adapt_to(DigitalBidir()))
