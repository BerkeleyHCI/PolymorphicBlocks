from electronics_abstract_parts import *
from .PassiveConnector_Header import PinHeader127DualShrouded
from .PassiveConnector_TagConnect import TagConnect


class SwdCortexTargetHeader(SwdCortexTargetConnector, SwdCortexTargetConnectorReset, SwdCortexTargetConnectorSwo,
                            SwdCortexTargetConnectorTdi):
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
    self.connect(self.reset, self.conn.pins.request('10').adapt_to(DigitalSource()))


class SwdCortexTargetTagConnect(SwdCortexTargetConnector, SwdCortexTargetConnectorReset, SwdCortexTargetConnectorSwo):
  """OFFICIAL tag connect SWD header using the TC2030 series cables.
  https://www.tag-connect.com/wp-content/uploads/bsk-pdf-manager/TC2030-CTX_1.pdf"""
  def contents(self):
    super().contents()
    self.conn = self.Block(TagConnect(6))
    self.connect(self.pwr, self.conn.pins.request('1').adapt_to(VoltageSink()))
    self.connect(self.swd.swdio, self.conn.pins.request('2').adapt_to(DigitalBidir()))  # also TMS
    self.connect(self.reset, self.conn.pins.request('3').adapt_to(DigitalSource()))
    self.connect(self.swd.swclk, self.conn.pins.request('4').adapt_to(DigitalSource()))
    self.connect(self.gnd, self.conn.pins.request('5').adapt_to(Ground()))
    self.connect(self.swo, self.conn.pins.request('6').adapt_to(DigitalBidir()))


class SwdCortexTargetTc2050(SwdCortexTargetConnector, SwdCortexTargetConnectorReset, SwdCortexTargetConnectorSwo,
                            SwdCortexTargetConnectorTdi):
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
    self.connect(self.reset, self.conn.pins.request('6').adapt_to(DigitalSource()))
