from electronics_abstract_parts import *
from .PassiveConnector import PassiveConnector

# contains common blocks for ESP microcontrollers


class EspProgrammingHeader(ProgrammingConnector):
  """Programming header for ESP32 series, matching the pinning in the reference schematics."""
  def __init__(self) -> None:
    super().__init__()

    # TODO: should these also act as sources?
    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.gnd = self.Port(Ground.empty(), [Common])  # TODO pin at 0v
    self.uart = self.Port(UartPort.empty(), [Output])

    self.conn = self.Block(PassiveConnector())
    self.connect(self.pwr, self.conn.pins.allocate('1').adapt_to(VoltageSink()))
    # RXD, TXD reversed to reflect the programmer's side view
    self.connect(self.uart.rx, self.conn.pins.allocate('2').adapt_to(DigitalSource()))
    self.connect(self.uart.tx, self.conn.pins.allocate('3').adapt_to(DigitalSink()))
    self.connect(self.gnd, self.conn.pins.allocate('4').adapt_to(Ground()))


class PulldownJumper(Block):
  def __init__(self) -> None:
    super().__init__()

    self.gnd = self.Port(Ground.empty(), [Common])
    self.io = self.Port(DigitalSource.empty(), [Output])

    self.conn = self.Block(PassiveConnector())
    self.connect(self.io, self.conn.pins.allocate('1').adapt_to(DigitalSource()))
    self.connect(self.gnd, self.conn.pins.allocate('2').adapt_to(VoltageSink()))
