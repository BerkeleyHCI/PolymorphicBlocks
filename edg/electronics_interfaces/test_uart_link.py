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


class UartTestCase(unittest.TestCase):
    def test_link(self) -> None:
        ScalaCompiler.compile(UartTest)

    def test_overconnect(self) -> None:
        with self.assertRaises(UnconnectableError):
            ScalaCompiler.compile(UartOverconnectTest)
