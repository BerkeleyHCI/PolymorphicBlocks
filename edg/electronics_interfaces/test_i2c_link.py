import unittest

from ..electronics_model import *
from .DigitalPorts import DigitalBidir
from .I2cPort import I2cController, I2cPullupPort, I2cTarget


class I2cControllerBlock(Block):
    def __init__(self, frequency_limit: RangeLike = RangeExpr.ALL) -> None:
        super().__init__()
        self.port = self.Port(I2cController(frequency_limit=frequency_limit))


class I2cPullupBlock(Block):
    def __init__(self) -> None:
        super().__init__()
        self.port = self.Port(I2cPullupPort())


class I2cTargetBlock(Block):
    def __init__(self, address: IntLike, frequency_limit: RangeLike = RangeExpr.ALL) -> None:
        super().__init__()
        self.port = self.Port(I2cTarget(DigitalBidir(), addresses=[address], frequency_limit=frequency_limit))


class I2cTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.controller = self.Block(I2cControllerBlock())
        self.pull = self.Block(I2cPullupBlock())
        self.device1 = self.Block(I2cTargetBlock(1))
        self.device2 = self.Block(I2cTargetBlock(2))
        self.link = self.connect(self.controller.port, self.pull.port, self.device1.port, self.device2.port)

        self.require(self.controller.port.link().addresses == [1, 2], _unchecked=True)


class I2cNoPullTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.controller = self.Block(I2cControllerBlock())
        self.device1 = self.Block(I2cTargetBlock(1))
        self.link = self.connect(self.controller.port, self.device1.port)


class I2cConflictTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.controller = self.Block(I2cControllerBlock())
        self.pull = self.Block(I2cPullupBlock())
        self.device1 = self.Block(I2cTargetBlock(1))
        self.device2 = self.Block(I2cTargetBlock(1))
        self.link = self.connect(self.controller.port, self.pull.port, self.device1.port, self.device2.port)


class I2cControllerNestedBlock(Block):
    def __init__(self) -> None:
        super().__init__()
        self.port = self.Port(I2cController.empty())
        self.controller = self.Block(I2cControllerBlock())
        self.pull = self.Block(I2cPullupBlock())
        self.device1 = self.Block(I2cTargetBlock(0))
        self.device2 = self.Block(I2cTargetBlock(1))
        self.link = self.connect(self.port, self.controller.port, self.pull.port, self.device1.port, self.device2.port)


class I2cNestedTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.controller = self.Block(I2cControllerNestedBlock())
        self.device = self.Block(I2cTargetBlock(2))
        self.link = self.connect(self.controller.port, self.device.port)
        self.require(self.controller.port.addresses == [0, 1])
        # also checks that we don't need a pullup if there is a nested one


class I2cNestedExtraPullTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.controller = self.Block(I2cControllerNestedBlock())
        self.pull = self.Block(I2cPullupBlock())  # redundant with pullup in controller
        self.device = self.Block(I2cTargetBlock(2))
        self.link = self.connect(self.controller.port, self.pull.port, self.device.port)


class I2cFrequencyTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.controller = self.Block(I2cControllerBlock(frequency_limit=(0, 400) * kHertz))
        self.pull = self.Block(I2cPullupBlock())
        self.device1 = self.Block(I2cTargetBlock(1, frequency_limit=(0, 100) * kHertz))
        self.device2 = self.Block(I2cTargetBlock(2, frequency_limit=(10, 400) * kHertz))
        self.connect(self.controller.port, self.pull.port, self.device1.port, self.device2.port)
        # whole bus must run within all devices' limits
        self.require(self.controller.port.link().frequency_limit == (10, 100) * kHertz, _unchecked=True)


class I2cFrequencyInvalidTest(DesignTop):
    """Checks that non-overlapping frequencies are an error.
    This generally doesn't happen in practice, since devices tend to support low speeds"""

    def __init__(self) -> None:
        super().__init__()
        self.controller = self.Block(I2cControllerBlock(frequency_limit=(400, 400) * kHertz))
        self.pull = self.Block(I2cPullupBlock())
        self.device = self.Block(I2cTargetBlock(1, frequency_limit=(100, 100) * kHertz))
        self.connect(self.controller.port, self.pull.port, self.device.port)


class I2cTestCase(unittest.TestCase):
    def test_i2c(self) -> None:
        ScalaCompiler.compile(I2cTest)

    def test_i2c_nopull(self) -> None:
        with self.assertRaises(CompilerCheckError):
            ScalaCompiler.compile(I2cNoPullTest)

    def test_i2c_conflict(self) -> None:
        with self.assertRaises(CompilerCheckError):
            ScalaCompiler.compile(I2cConflictTest)

    def test_i2c_nested(self) -> None:
        ScalaCompiler.compile(I2cNestedTest)

    def test_i2c_nested_extrapull(self) -> None:
        with self.assertRaises(CompilerCheckError):
            ScalaCompiler.compile(I2cNestedExtraPullTest)

    def test_i2c_frequency(self) -> None:
        ScalaCompiler.compile(I2cFrequencyTest)

    def test_i2c_frequency_invalid(self) -> None:
        with self.assertRaises(CompilerCheckError):
            ScalaCompiler.compile(I2cFrequencyInvalidTest)
