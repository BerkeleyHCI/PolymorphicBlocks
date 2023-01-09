import unittest

from edg import *


class UartConnector(Block):
  """UART connector, follows the TXD, RXD, GND, +5 pinning of cheap CP2102 dongles."""
  def __init__(self):
    super().__init__()
    self.conn = self.Block(PassiveConnector())

    self.uart = self.Port(UartPort.empty(), [InOut])
    # note that RX and TX here are from the connected device, so they're flipped from the CP2102's view
    self.connect(self.uart.rx, self.conn.pins.request('1').adapt_to(DigitalSink()))
    self.connect(self.uart.tx, self.conn.pins.request('2').adapt_to(DigitalSource()))
    self.gnd = self.Export(self.conn.pins.request('3').adapt_to(Ground()),
                           [Common])
    self.pwr = self.Export(self.conn.pins.request('4').adapt_to(VoltageSink()),
                           [Power])


class UsbUartTest(JlcBoardTop):
  """USB UART converter board"""
  def contents(self) -> None:
    super().contents()
    self.usb_uart = self.Block(UsbCReceptacle())

    self.vusb = self.connect(self.usb_uart.pwr)
    self.gnd = self.connect(self.usb_uart.gnd)

    # POWER
    with self.implicit_connect(
        ImplicitConnect(self.vusb, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.usbconv = imp.Block(Cp2102())
      (self.usb_esd, ), self.usb_chain = self.chain(
        self.usb_uart.usb, imp.Block(UsbEsdDiode()), self.usbconv.usb)
      (self.led, ), _ = self.chain(
        self.usbconv.nsuspend, imp.Block(IndicatorLed()))

      self.out = imp.Block(UartConnector())
      self.connect(self.usbconv.uart, self.out.uart)

    # Misc board
    self.duck = self.Block(DuckLogo())
    self.leadfree = self.Block(LeadFreeIndicator())
    self.id = self.Block(IdDots4())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['out', 'conn'], PinHeader254),
      ],
      instance_values=[
      ],
      class_refinements=[
      ],
      class_values=[
      ],
    )


class UsbUartTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(UsbUartTest)
