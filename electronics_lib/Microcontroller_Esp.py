from electronics_abstract_parts import *
from electronics_lib import PinHeader254, TagConnect


# contains common blocks for ESP microcontrollers


@abstract_block_default(lambda: EspProgrammingPins)
class EspAutoProgrammingHeader(ProgrammingConnector):
  """Abstract programming header for ESP series micros, including reset and IO0 for auto-programming."""
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.gnd = self.Port(Ground.empty(), [Common])
    self.uart = self.Port(UartPort.empty(), [Output])


class EspProgrammingPins(EspAutoProgrammingHeader):
  """Programming header for ESP series micros using 2.54mm headers, matching the pinning in the reference schematics.
  TODO: does NOT support auto-programming (but needs to be compatible with the interface)."""
  def contents(self) -> None:
    super().contents()

    self.conn = self.Block(PinHeader254())
    self.connect(self.pwr, self.conn.pins.request('1').adapt_to(VoltageSink()))
    # RXD, TXD reversed to reflect the programmer's side view
    self.connect(self.uart.rx, self.conn.pins.request('2').adapt_to(DigitalSink()))
    self.connect(self.uart.tx, self.conn.pins.request('3').adapt_to(DigitalSource()))
    self.connect(self.gnd, self.conn.pins.request('4').adapt_to(Ground()))


class EspProgrammingTc2030(EspAutoProgrammingHeader):
  """UNOFFICIAL tag connect header, based on a modification of the FT232 cable
  (https://www.tag-connect.com/product/tc2030-ftdi-ttl-232rg-vsw3v3)
  but adding the auto-programming pins (and using DTR instead of CTS into the cable).
  Power pins compatible with the official SWD header.
  """
  def contents(self) -> None:
    super().contents()

    self.conn = self.Block(TagConnect(6))
    self.connect(self.pwr, self.conn.pins.request('1').adapt_to(VoltageSink()))
    self.connect(self.uart.rx, self.conn.pins.request('3').adapt_to(DigitalSink()))
    self.connect(self.uart.tx, self.conn.pins.request('4').adapt_to(DigitalSource()))
    self.connect(self.gnd, self.conn.pins.request('5').adapt_to(Ground()))

    # TODO CTS on pin 2, RTS on pin 6
