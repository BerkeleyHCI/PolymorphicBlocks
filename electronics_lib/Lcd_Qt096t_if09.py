from typing import *
from electronics_abstract_parts import *
from electronics_lib import Fpc050


class Qt096t_if09_Device(DiscreteChip):
  def __init__(self) -> None:
    super().__init__()

    self.conn = self.Block(Fpc050(length=8))

    # both Vdd and VddI
    self.vdd = self.Export(self.conn.pins.allocate('7').adapt_to(VoltageSink(
      voltage_limits=(2.5, 4.8) * Volt,  # 2.75v typ
      current_draw=(0.02, 2.02) * mAmp  # ST7735S Table 7.3, IDDI + IDD, typ - max
    )))
    self.gnd = self.Export(self.conn.pins.allocate('2').adapt_to(Ground()))

    io_model = DigitalSink.from_supply(
      self.gnd, self.vdd,
      voltage_limit_tolerance=(-0.3, 0.3)*Volt,
      current_draw=0*mAmp(tol=0),
      input_threshold_factor=(0.3, 0.7),
    )
    self.reset = self.Export(self.conn.pins.allocate('3').adapt_to(io_model))
    # data / command selection pin
    self.rs = self.Export(self.conn.pins.allocate('4').adapt_to(io_model))
    self.cs = self.Export(self.conn.pins.allocate('8').adapt_to(io_model))

    self.spi = self.Port(SpiSlave.empty())
    self.connect(self.spi.sck, self.conn.pins.allocate('6').adapt_to(io_model))  # scl
    self.connect(self.spi.mosi, self.conn.pins.allocate('5').adapt_to(io_model))  # sda
    self.spi.miso.not_connected()

    self.leda = self.Export(self.conn.pins.allocate('1'))  # TODO maybe something else?


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
    self.spi = self.Export(self.device.spi)
    self.led = self.Port(DigitalSink().empty())

  def contents(self):
    super().contents()

    self.led_res = self.Block(Resistor(resistance=100*Ohm(tol=0.05)))  # TODO dynamic sizing, power
    self.connect(self.led_res.a.adapt_to(DigitalSink(
      # no voltage limits, since the resistor is autogen'd
      input_thresholds=(3, 3),  # TODO more accurate model
      current_draw=(16, 20) * mAmp  # TODO user-configurable?
    )), self.led)
    self.connect(self.led_res.b, self.device.leda)

    self.vdd_cap = self.Block(DecouplingCapacitor(capacitance=1*uFarad(tol=0.2))).connected(self.gnd, self.pwr)
