import unittest

from ..electronics_model import *
from .DigitalPorts import DigitalBidir
from .SpiPort import SpiController, SpiPeripheral


class SpiControllerBlock(Block):
    def __init__(self, frequency_limit: RangeLike = RangeExpr.ALL) -> None:
        super().__init__()
        self.port = self.Port(SpiController(frequency_limit=frequency_limit))


class SpiPeripheralBlock(Block):
    def __init__(self, frequency_limit: RangeLike = RangeExpr.ALL) -> None:
        super().__init__()
        self.port = self.Port(SpiPeripheral(DigitalBidir(), frequency_limit=frequency_limit))


class SpiTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.controller = self.Block(SpiControllerBlock())
        self.device1 = self.Block(SpiPeripheralBlock())
        self.device2 = self.Block(SpiPeripheralBlock())
        self.connect(self.controller.port, self.device1.port, self.device2.port)


class SpiFrequencyTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.controller = self.Block(SpiControllerBlock(frequency_limit=(1, 10) * MHertz))
        self.device1 = self.Block(SpiPeripheralBlock(frequency_limit=(2, 8) * MHertz))
        self.device2 = self.Block(SpiPeripheralBlock(frequency_limit=(0.5, 5) * MHertz))
        self.connect(self.controller.port, self.device1.port, self.device2.port)
        # bus may run at any frequency the controller and any peripheral is capable of
        self.require(self.controller.port.link().frequency_limit == (1, 8) * MHertz, _unchecked=True)


class SpiFrequencyInvalidTest(DesignTop):
    """Invalid connection with no overlapping frequency range, e.g. fixed-frequency non-programmable
    controller with incompatible peripheral"""

    def __init__(self) -> None:
        super().__init__()
        self.controller = self.Block(SpiControllerBlock(frequency_limit=(1, 1) * MHertz))
        self.device = self.Block(SpiPeripheralBlock(frequency_limit=(0.01, 0.1) * MHertz))
        self.connect(self.controller.port, self.device.port)


class SpiTestCase(unittest.TestCase):
    def test_link(self) -> None:
        ScalaCompiler.compile(SpiTest)

    def test_frequency(self) -> None:
        ScalaCompiler.compile(SpiFrequencyTest)

    def test_frequency_invalid(self) -> None:
        with self.assertRaises(CompilerCheckError):
            ScalaCompiler.compile(SpiFrequencyInvalidTest)
