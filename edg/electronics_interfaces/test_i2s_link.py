import unittest

from ..core.HdlUserExceptions import UnconnectableError
from ..electronics_model import *
from .DigitalPorts import DigitalBidir, DigitalSink
from .I2sPort import I2sController, I2sTargetReceiver


class I2sControllerBlock(Block):
    def __init__(self, sample_rate_limit: RangeLike = RangeExpr.ALL, bit_limit: RangeLike = RangeExpr.ALL) -> None:
        super().__init__()
        self.port = self.Port(I2sController(DigitalBidir(), sample_rate_limit=sample_rate_limit, bit_limit=bit_limit))


class I2sTargetReceiverBlock(Block):
    def __init__(self, sample_rate_limit: RangeLike = RangeExpr.ALL, bit_limit: RangeLike = RangeExpr.ALL) -> None:
        super().__init__()
        self.port = self.Port(
            I2sTargetReceiver(DigitalSink(), sample_rate_limit=sample_rate_limit, bit_limit=bit_limit)
        )


class I2sTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.controller = self.Block(I2sControllerBlock())
        self.target = self.Block(I2sTargetReceiverBlock())
        self.connect(self.controller.port, self.target.port)


class I2sOverconnectTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.controller = self.Block(I2sControllerBlock())
        self.target1 = self.Block(I2sTargetReceiverBlock())
        self.target2 = self.Block(I2sTargetReceiverBlock())
        self.connect(self.controller.port, self.target1.port, self.target2.port)


class I2sSampleRateTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.controller = self.Block(I2sControllerBlock(sample_rate_limit=(0, 48) * kHertz))
        self.target = self.Block(I2sTargetReceiverBlock(sample_rate_limit=(8, 96) * kHertz))
        self.connect(self.controller.port, self.target.port)
        self.require(self.controller.port.link().sample_rate_limit == (8, 48) * kHertz, _unchecked=True)


class I2sSampleRateInvalidTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.controller = self.Block(I2sControllerBlock(sample_rate_limit=(0, 16) * kHertz))
        self.target = self.Block(I2sTargetReceiverBlock(sample_rate_limit=(48, 96) * kHertz))
        self.connect(self.controller.port, self.target.port)


class I2sBitsTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.controller = self.Block(I2sControllerBlock(bit_limit=(8, 16) * Bit))
        self.target = self.Block(I2sTargetReceiverBlock(bit_limit=(16, 32) * Bit))
        self.connect(self.controller.port, self.target.port)
        self.require(self.controller.port.link().bit_limit == (16, 16) * Bit, _unchecked=True)


class I2sBitsInvalidTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.controller = self.Block(I2sControllerBlock(bit_limit=(0, 8) * Bit))
        self.target = self.Block(I2sTargetReceiverBlock(bit_limit=(16, 16) * Bit))
        self.connect(self.controller.port, self.target.port)


class I2sTestCase(unittest.TestCase):
    def test_link(self) -> None:
        ScalaCompiler.compile(I2sTest)

    def test_overconnect(self) -> None:
        with self.assertRaises(UnconnectableError):
            ScalaCompiler.compile(I2sOverconnectTest)

    def test_frequency(self) -> None:
        ScalaCompiler.compile(I2sSampleRateTest)

    def test_frequency_invalid(self) -> None:
        with self.assertRaises(CompilerCheckError):
            ScalaCompiler.compile(I2sSampleRateInvalidTest)

    def test_bits(self) -> None:
        ScalaCompiler.compile(I2sBitsTest)

    def test_bits_invalid(self) -> None:
        with self.assertRaises(CompilerCheckError):
            ScalaCompiler.compile(I2sBitsInvalidTest)
