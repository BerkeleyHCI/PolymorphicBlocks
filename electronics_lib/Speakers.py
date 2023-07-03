from electronics_abstract_parts import *
from .JlcPart import JlcPart


@abstract_block
class Speaker(HumanInterface):
  """Abstract speaker part with speaker input port."""
  def __init__(self):
    super().__init__()
    self.input = self.Port(SpeakerPort().empty(), [Input])


class ConnectorSpeaker(Speaker):
  """Speaker that delegates to a PassiveConnector and with configurable impedance."""
  @init_in_parent
  def __init__(self, impedance: RangeLike = 8*Ohm(tol=0)):
    super().__init__()

    self.conn = self.Block(PassiveConnector())

    self.connect(self.input.a, self.conn.pins.request('1').adapt_to(AnalogSink(
      impedance=impedance)
    ))
    self.connect(self.input.b, self.conn.pins.request('2').adapt_to(AnalogSink(
      impedance=impedance)
    ))
