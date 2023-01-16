import unittest

from edg import *


# class UartConnector(Block):
#   """UART connector, follows the TXD, RXD, GND, +5 pinning of cheap CP2102 dongles."""
#   def __init__(self):
#     super().__init__()
#     self.conn = self.Block(PassiveConnector())
#
#     self.uart = self.Port(UartPort.empty(), [InOut])
#     # note that RX and TX here are from the connected device, so they're flipped from the CP2102's view
#     self.connect(self.uart.rx, self.conn.pins.request('1').adapt_to(DigitalSink()))
#     self.connect(self.uart.tx, self.conn.pins.request('2').adapt_to(DigitalSource()))
#     self.gnd = self.Export(self.conn.pins.request('3').adapt_to(Ground()),
#                            [Common])
#     self.pwr = self.Export(self.conn.pins.request('4').adapt_to(VoltageSink()),
#                            [Power])


class UsbFpgaProgrammerTest(JlcBoardTop):
  """USB UART converter board"""
  def contents(self) -> None:
    super().contents()
    self.usb = self.Block(UsbCReceptacle())

    self.vusb = self.connect(self.usb.pwr)
    self.gnd = self.connect(self.usb.gnd)

    # POWER
    with self.implicit_connect(
        ImplicitConnect(self.vusb, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.ft232 = imp.Block(Ft232hl())
      (self.usb_esd, ), self.usb_chain = self.chain(
        self.usb.usb, imp.Block(UsbEsdDiode()), self.ft232.usb)
      (self.led0, ), _ = self.chain(self.ft232.acbus0, imp.Block(IndicatorLed()))  # TXDEN
      (self.led1, ), _ = self.chain(self.ft232.acbus3, imp.Block(IndicatorLed()))  # RXLED
      (self.led2, ), _ = self.chain(self.ft232.acbus4, imp.Block(IndicatorLed()))  # TXLED

      # self.out = imp.Block(UartConnector())
      # self.connect(self.usbconv.uart, self.out.uart)

    # Misc board
    self.duck = self.Block(DuckLogo())
    self.leadfree = self.Block(LeadFreeIndicator())
    self.id = self.Block(IdDots4())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
      ],
      instance_values=[
        (['refdes_prefix'], '0'),  # unique refdes for panelization
      ],
      class_refinements=[
      ],
      class_values=[
      ],
    )


class UsbFpgaProgrammerTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(UsbFpgaProgrammerTest)
