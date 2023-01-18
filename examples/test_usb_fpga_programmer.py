import unittest

from edg import *


class FpgaProgrammingHeader(Block):
  """Custom programming header for iCE40 loosely based on the SWD pinning"""
  def __init__(self):
    super().__init__()
    self.pwr = self.Port(VoltageSink.empty(), optional=True)
    self.gnd = self.Port(Ground.empty(), [Common])
    self.spi = self.Port(SpiSlave.empty())
    self.cs = self.Port(DigitalSink.empty())
    self.reset = self.Port(DigitalSink.empty())

  def contents(self):
    super().contents()
    self.conn = self.Block(PinHeader127DualShrouded(10))
    self.connect(self.pwr, self.conn.pins.request('1').adapt_to(VoltageSink()))
    self.connect(self.gnd, self.conn.pins.request('3').adapt_to(Ground()),
                 self.conn.pins.request('5').adapt_to(Ground()),
                 self.conn.pins.request('9').adapt_to(Ground()))
    self.connect(self.cs, self.conn.pins.request('2').adapt_to(DigitalSink()))  # swd: swdio
    self.connect(self.spi.sck, self.conn.pins.request('4').adapt_to(DigitalSink()))  # swd: swclk
    self.connect(self.spi.mosi, self.conn.pins.request('6').adapt_to(DigitalSink()))  # swd: swo
    self.connect(self.spi.miso, self.conn.pins.request('8').adapt_to(DigitalSource()))  # swd: NC or jtag: tdi
    self.connect(self.reset, self.conn.pins.request('10').adapt_to(DigitalSink()))


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
      # since USB is 5.25 max, we can't use the 5.2v Zener that is a basic part =(
      self.vusb_protect = imp.Block(ProtectionZenerDiode(voltage=(5.25, 6)*Volt))

      self.ft232 = imp.Block(Ft232hl())
      (self.usb_esd, ), self.usb_chain = self.chain(
        self.usb.usb, imp.Block(UsbEsdDiode()), self.ft232.usb)
      (self.led0, ), _ = self.chain(self.ft232.acbus0, imp.Block(IndicatorLed(Led.White)))  # TXDEN
      (self.led1, ), _ = self.chain(self.ft232.acbus3, imp.Block(IndicatorLed(Led.Yellow)))  # RXLED
      (self.led2, ), _ = self.chain(self.ft232.acbus4, imp.Block(IndicatorLed(Led.Red)))  # TXLED

      self.out = imp.Block(FpgaProgrammingHeader())
      self.connect(self.ft232.mpsse, self.out.spi)
      self.connect(self.ft232.adbus4, self.out.cs)
      self.connect(self.ft232.adbus7, self.out.reset)

    # Misc board
    self.duck = self.Block(DuckLogo())
    self.lemur = self.Block(LemurLogo())
    self.id = self.Block(IdDots4())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
      ],
      instance_values=[
        (['refdes_prefix'], 'F'),  # unique refdes for panelization
        (['vusb_protect', 'diode', 'footprint_spec'], 'Diode_SMD:D_SOD-123'),
      ],
      class_refinements=[
        (UsbEsdDiode, Pgb102st23),  # as recommended by the FT232H datasheet, also for the weird "sot-23" package
      ],
      class_values=[
      ],
    )


class UsbFpgaProgrammerTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(UsbFpgaProgrammerTest)
