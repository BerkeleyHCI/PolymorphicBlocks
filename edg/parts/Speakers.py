from ..abstract_parts import *
from .JlcPart import JlcPart


@abstract_block
class Speaker(HumanInterface):
    """Abstract speaker part with speaker input port."""

    def __init__(self) -> None:
        super().__init__()
        self.input = self.Port(SpeakerPort.empty(), [Input])


class ConnectorSpeaker(Speaker):
    """Speaker that delegates to a PassiveConnector and with configurable impedance."""

    def __init__(self, impedance: RangeLike = 8 * Ohm(tol=0)):
        super().__init__()
        self.input.init_from(SpeakerPort(AnalogSink(impedance=impedance)))

        self.conn = self.Block(PassiveConnector())

        self.connect(self.input.a.net, self.conn.pins.request("1"))
        self.connect(self.input.b.net, self.conn.pins.request("2"))
