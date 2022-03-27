from typing import *
from electronics_abstract_parts import *


class Qt096t_if09_Device(DiscreteChip, FootprintBlock):
  def __init__(self) -> None:
    super().__init__()

    self.vdd = self.Port(VoltageSink(
      voltage_limits=(2.5, 4.8) * Volt,  # 2.75v typ
      current_draw=(0.02, 2.02) * mAmp  # ST7735S Table 7.3, IDDI + IDD, typ - max
    ))
    self.gnd = self.Port(Ground())

    io_model = DigitalBidir.from_supply(
      self.gnd, self.vdd,
      voltage_limit_tolerance=(-0.3, 0.3)*Volt,
      current_draw=0*mAmp(tol=0),
      current_limits=0*mAmp(tol=0),
      input_threshold_factor=(0.3, 0.7),
      output_threshold_factor=(0.2, 0.8)
    )
    self.reset = self.Port(DigitalSink.from_bidir(io_model))
    self.rs = self.Port(DigitalSink.from_bidir(io_model))
    self.cs = self.Port(DigitalSink.from_bidir(io_model))
    self.sda = self.Port(io_model)
    self.scl = self.Port(DigitalSink.from_bidir(io_model))

    self.leda = self.Port(Passive())  # TODO maybe something else?

  def contents(self):
    super().contents()

    pinning: Dict[str, CircuitPort] = {
      '1': self.leda,
      '2': self.gnd,
      '3': self.reset,
      '4': self.rs,  # data / command selection pin
      '5': self.sda,
      '6': self.scl,
      '7': self.vdd,  # both Vdd and VddI
      '8': self.cs,
    }

    self.footprint(
      'U', 'Connector_FFC-FPC:Hirose_FH12-8S-0.5SH_1x08-1MP_P0.50mm_Horizontal',
      pinning,
      part='QT096T_IF09, FH12-8S-0.5SH(55)'  # TODO multiple parts
    )
    # Mostly footprint compatible with TE 1775333-8, which is significantly cheaper



class Qt096t_if09(Lcd, Block):
  """ST7735S-based LCD module with a 8-pin 0.5mm-pitch FPC connector"""
  def __init__(self) -> None:
    super().__init__()

    self.device = self.Block(Qt096t_if09_Device())
    self.gnd = self.Export(self.device.gnd, [Common])
    self.pwr = self.Export(self.device.vdd, [Power])
    self.reset = self.Export(self.device.reset)
    self.rs = self.Export(self.device.rs)
    self.cs = self.Export(self.device.cs)
    self.spi = self.Port(SpiSlave())
    self.led = self.Port(DigitalSink(
      # no voltage limits, since the resistor is autogen'd
      input_thresholds=(3, 3),  # TODO more accurate model
      current_draw=(16, 20) * mAmp  # TODO user-configurable?
    ))

  def contents(self):
    super().contents()

    self.led_res = self.Block(Resistor(resistance=100*Ohm(tol=0.05)))  # TODO dynamic sizing, power
    self.connect(self.led_res.a.as_digital_sink(), self.led)
    self.connect(self.led_res.b, self.device.leda)
    self.connect(self.spi.sck, self.device.scl)
    self.connect(self.spi.mosi, self.device.sda)

    self.vdd_cap = self.Block(DecouplingCapacitor(capacitance=1*uFarad(tol=0.2)))
    self.connect(self.vdd_cap.pwr, self.pwr)
    self.connect(self.vdd_cap.gnd, self.gnd)

    self.spi.miso.not_connected()
