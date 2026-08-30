import unittest

from ..core.HdlUserExceptions import UnconnectableError
from ..electronics_model import *
from .DigitalPorts import DigitalBidir
from .UartPort import UartPort


class UartBlock(Block):
    def __init__(self, baud_limit: RangeLike = RangeExpr.ALL) -> None:
        super().__init__()
        self.port = self.Port(UartPort(DigitalBidir(), baud_limit=baud_limit))


class UartTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.device1 = self.Block(UartBlock())
        self.device2 = self.Block(UartBlock())
        self.connect(self.device1.port, self.device2.port)


class UartOverconnectTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.device1 = self.Block(UartBlock())
        self.device2 = self.Block(UartBlock())
        self.device3 = self.Block(UartBlock())
        self.connect(self.device1.port, self.device2.port, self.device3.port)


class UartFrequencyTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.device1 = self.Block(UartBlock(baud_limit=(9600, 115200) * Hertz))
        self.device2 = self.Block(UartBlock(baud_limit=(38400, 921600) * Hertz))
        self.connect(self.device1.port, self.device2.port)
        self.require(self.device1.port.link().baud_limit == (38400, 115200) * Hertz, _unchecked=True)


class UartFrequencyInvalidTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.device1 = self.Block(UartBlock(baud_limit=(9600, 38400) * Hertz))
        self.device2 = self.Block(UartBlock(baud_limit=(115200, 921600) * Hertz))
        self.connect(self.device1.port, self.device2.port)


class UartTestCase(unittest.TestCase):
    def test_link(self) -> None:
        ScalaCompiler.compile(UartTest)

    def test_overconnect(self) -> None:
        with self.assertRaises(UnconnectableError):
            ScalaCompiler.compile(UartOverconnectTest)

    def test_frequency(self) -> None:
        ScalaCompiler.compile(UartFrequencyTest)

    def test_frequency_invalid(self) -> None:
        with self.assertRaises(CompilerCheckError):
            ScalaCompiler.compile(UartFrequencyInvalidTest)
