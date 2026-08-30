import unittest

from ..core.HdlUserExceptions import UnconnectableError
from ..electronics_model import *
from .DigitalPorts import DigitalBidir
from .CanPort import CanControllerPort, CanTransceiverPort, CanDiffPort


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


class CanDiffBlock(Block):
    def __init__(self, bitrate_limit: RangeLike = RangeExpr.ALL) -> None:
        super().__init__()
        self.port = self.Port(CanDiffPort(bitrate_limit=bitrate_limit))


class CanDiffTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.node1 = self.Block(CanDiffBlock())
        self.node2 = self.Block(CanDiffBlock())
        self.node3 = self.Block(CanDiffBlock())
        self.connect(self.node1.port, self.node2.port, self.node3.port)


class CanBadConnectTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.controller = self.Block(CanControllerBlock())
        self.diff = self.Block(CanDiffBlock())
        self.connect(self.controller.port, self.diff.port)


class CanDiffFrequencyTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.node1 = self.Block(CanDiffBlock(bitrate_limit=(0, 1) * MHertz))
        self.node2 = self.Block(CanDiffBlock(bitrate_limit=(0.5, 1) * MHertz))
        self.node3 = self.Block(CanDiffBlock(bitrate_limit=(0.25, 0.5) * MHertz))
        self.connect(self.node1.port, self.node2.port, self.node3.port)
        self.require(self.node1.port.link().bitrate_limit == (0.5, 0.5) * MHertz, _unchecked=True)


class CanDiffFrequencyInvalidTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.node1 = self.Block(CanDiffBlock(bitrate_limit=(0, 0.25) * MHertz))
        self.node2 = self.Block(CanDiffBlock(bitrate_limit=(0.5, 1) * MHertz))
        self.connect(self.node1.port, self.node2.port)


class CanTestCase(unittest.TestCase):
    def test_logic_link(self) -> None:
        ScalaCompiler.compile(CanLogicTest)

    def test_logic_overconnect(self) -> None:
        with self.assertRaises(UnconnectableError):
            ScalaCompiler.compile(CanLogicOverconnectTest)

    def test_logic_frequency(self) -> None:
        ScalaCompiler.compile(CanLogicFrequencyTest)

    def test_logic_frequency_invalid(self) -> None:
        with self.assertRaises(CompilerCheckError):
            ScalaCompiler.compile(CanLogicFrequencyInvalidTest)

    def test_diff_link(self) -> None:
        ScalaCompiler.compile(CanDiffTest)

    def test_bad_connect(self) -> None:
        with self.assertRaises(UnconnectableError):
            ScalaCompiler.compile(CanBadConnectTest)

    def test_diff_frequency(self) -> None:
        ScalaCompiler.compile(CanDiffFrequencyTest)

    def test_diff_frequency_invalid(self) -> None:
        with self.assertRaises(CompilerCheckError):
            ScalaCompiler.compile(CanDiffFrequencyInvalidTest)
