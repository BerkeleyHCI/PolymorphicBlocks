from electronics_abstract_parts import *
from .PassiveConnector_Header import PinHeader127DualShrouded
from .PassiveConnector_TagConnect import TagConnect


class SwdCortexTargetHeader(SwdCortexTargetWithSwoTdiConnector):
  def contents(self):
    super().contents()
    self.conn = self.Block(PinHeader127DualShrouded(10))
    self.connect(self.pwr, self.conn.pins.request('1').adapt_to(VoltageSink()))
    self.connect(self.gnd, self.conn.pins.request('3').adapt_to(Ground()),
                 self.conn.pins.request('5').adapt_to(Ground()),
                 self.conn.pins.request('9').adapt_to(Ground()))
    self.connect(self.swd.swdio, self.conn.pins.request('2').adapt_to(DigitalBidir()))
    self.connect(self.swd.swclk, self.conn.pins.request('4').adapt_to(DigitalSource()))
    self.connect(self.swo, self.conn.pins.request('6').adapt_to(DigitalBidir()))
    self.connect(self.tdi, self.conn.pins.request('8').adapt_to(DigitalBidir()))
    self.connect(self.swd.reset, self.conn.pins.request('10').adapt_to(DigitalSource()))


class SwdCortexTargetTagConnect(SwdCortexTargetWithSwoTdiConnector, FootprintBlock):
  """OFFICIAL tag connect SWD header using the TC2030 series cables.
  https://www.tag-connect.com/wp-content/uploads/bsk-pdf-manager/TC2030-CTX_1.pdf"""
  def contents(self):
    super().contents()
    self.conn = self.Block(TagConnect(6))
    self.connect(self.pwr, self.conn.pins.request('1').adapt_to(VoltageSink()))
    self.connect(self.swd.swdio, self.conn.pins.request('2').adapt_to(DigitalBidir()))  # also TMS
    self.connect(self.swd.reset, self.conn.pins.request('3').adapt_to(DigitalSource()))
    self.connect(self.swd.swclk, self.conn.pins.request('4').adapt_to(DigitalSource()))
    self.connect(self.gnd, self.conn.pins.request('5').adapt_to(Ground()))
    self.connect(self.swo, self.conn.pins.request('6').adapt_to(DigitalBidir()))
    # TODO the block shouldn't have TDI at all, but this maintains compatibility
    self.require(~self.tdi.is_connected())


class SwdCortexTargetTc2050(SwdCortexTargetWithSwoTdiConnector, FootprintBlock):
  """UNOFFICIAL tag connect SWD header, maintaining physical pin compatibility with the 2x05 1.27mm header."""
  def contents(self):
    super().contents()
    self.conn = self.Block(TagConnect(10))
    self.connect(self.pwr, self.conn.pins.request('1').adapt_to(VoltageSink()))
    self.connect(self.gnd, self.conn.pins.request('2').adapt_to(Ground()),
                 self.conn.pins.request('3').adapt_to(Ground()),
                 self.conn.pins.request('5').adapt_to(Ground()))
    self.connect(self.swd.swdio, self.conn.pins.request('10').adapt_to(DigitalBidir()))
    self.connect(self.swd.swclk, self.conn.pins.request('9').adapt_to(DigitalSource()))
    self.connect(self.swo, self.conn.pins.request('8').adapt_to(DigitalBidir()))
    self.connect(self.tdi, self.conn.pins.request('7').adapt_to(DigitalBidir()))
    self.connect(self.swd.reset, self.conn.pins.request('6').adapt_to(DigitalSource()))


class SwdCortexSourceHeaderHorizontal(ProgrammingConnector, FootprintBlock):
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink(), [Power])
    self.gnd = self.Port(Ground(), [Common])  # TODO pin at 0v
    self.swd = self.Port(SwdTargetPort(), [Input])
    self.swo = self.Port(DigitalBidir(), optional=True)
    self.tdi = self.Port(DigitalBidir(), optional=True)

  def contents(self):
    super().contents()

    self.footprint(
      'J', 'edg:PinHeader_2x05_P1.27mm_Horizontal_Shrouded',
      {
        '1': self.pwr,
        '2': self.swd.swdio,
        '3': self.gnd,
        '4': self.swd.swclk,
        '5': self.gnd,
        '6': self.swo,
        # '7': ,  # key pin technically doesn't exist
        '8': self.tdi,  # or NC
        '9': self.gnd,
        '10': self.swd.reset,
      },
      mfr='CNC Tech', part='3220-10-0200-00',
      value='SWD'
    )
