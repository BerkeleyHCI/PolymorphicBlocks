import unittest

from edg import *


class FpgaProgrammingHeader(JlcPart, FootprintBlock):
  """Custom programming header for iCE40 loosely based on the SWD pinning"""
  def __init__(self):
    super().__init__()
    self.pwr = self.Port(VoltageSink(), [Power])
    self.gnd = self.Port(Ground(), [Common])
    self.spi = self.Port(SpiSlave())
    self.cs = self.Port(DigitalSink())
    self.reset = self.Port(DigitalSource())

  def contents(self):
    super().contents()

    self.footprint(  # TODO this should use generic 1.27mm PassiveHeader
      'J', 'Connector_PinHeader_1.27mm:PinHeader_2x05_P1.27mm_Vertical_SMD',  # TODO: pattern needs shroud
      {
        '1': self.pwr,
        '2': self.cs,  # swd: swdio
        '3': self.gnd,
        '4': self.spi.sck,  # swd: swclk
        '5': self.gnd,
        '6': self.spi.mosi,  # DI; swd: swo
        # '7': ,  # key pin technically doesn't exist
        '8': self.spi.miso,  # DO; jtag: tdi or swd: NC
        '9': self.gnd,
        '10': self.reset,
      },
      mfr='XKB Connectivity', part='X1270WVS-2x05B-6TV01',
      value='SWD'
    )
    self.assign(self.lcsc_part, 'C2962219')
    self.assign(self.actual_basic_part, False)


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

      self.out = imp.Block(FpgaProgrammingHeader())
      self.connect(self.ft232.mpsse, self.out.spi)
      self.connect(self.ft232.adbus4, self.out.cs)
      self.connect(self.ft232.adbus7, self.out.reset)

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
