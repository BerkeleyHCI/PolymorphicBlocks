import unittest

from ..core.HdlUserExceptions import UnconnectableError
from ..electronics_model import *
from .DigitalPorts import DigitalBidir
from .CanPort import CanControllerPort, CanTransceiverPort


class CanControllerBlock(Block):
    def __init__(self, bitrate_limit: RangeLike = RangeExpr.ALL) -> None:
        super().__init__()
        self.port = self.Port(CanControllerPort(DigitalBidir(), bitrate_limit=bitrate_limit))


class CanTransceiverBlock(Block):
    def __init__(self, bitrate_limit: RangeLike = RangeExpr.ALL) -> None:
        super().__init__()
        self.port = self.Port(CanTransceiverPort(DigitalBidir(), bitrate_limit=bitrate_limit))


class CanLogicTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.controller = self.Block(CanControllerBlock())
        self.transceiver = self.Block(CanTransceiverBlock())
        self.connect(self.controller.port, self.transceiver.port)


class CanLogicOverconnectTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.controller = self.Block(CanControllerBlock())
        self.transceiver1 = self.Block(CanTransceiverBlock())
        self.transceiver2 = self.Block(CanTransceiverBlock())
        self.connect(self.controller.port, self.transceiver1.port, self.transceiver2.port)


class CanLogicFrequencyTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.controller = self.Block(CanControllerBlock(bitrate_limit=(0, 1) * MHertz))
        self.transceiver = self.Block(CanTransceiverBlock(bitrate_limit=(0.5, 1) * MHertz))
        self.connect(self.controller.port, self.transceiver.port)
        self.require(self.controller.port.link().bitrate_limit == (0.5, 1) * MHertz, _unchecked=True)


class CanLogicFrequencyInvalidTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        # this generally isn't plausible in practice
        self.controller = self.Block(CanControllerBlock(bitrate_limit=(0, 0.25) * MHertz))
        self.transceiver = self.Block(CanTransceiverBlock(bitrate_limit=(0.5, 1) * MHertz))
        self.connect(self.controller.port, self.transceiver.port)


class CanLogicTestCase(unittest.TestCase):
    def test_link(self) -> None:
        ScalaCompiler.compile(CanLogicTest)

    def test_overconnect(self) -> None:
        with self.assertRaises(UnconnectableError):
            ScalaCompiler.compile(CanLogicOverconnectTest)

    def test_frequency(self) -> None:
        ScalaCompiler.compile(CanLogicFrequencyTest)

    def test_frequency_invalid(self) -> None:
        with self.assertRaises(CompilerCheckError):
            ScalaCompiler.compile(CanLogicFrequencyInvalidTest)
