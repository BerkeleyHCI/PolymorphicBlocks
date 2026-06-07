import unittest

from ..electronics_model import *
from .DigitalPorts import DigitalBidir
from .I2cPort import I2cController, I2cPullupPort, I2cTarget


class I2cControllerBlock(Block):
    def __init__(self) -> None:
        super().__init__()
        self.port = self.Port(I2cController())


class I2cPullupBlock(Block):
    def __init__(self) -> None:
        super().__init__()
        self.port = self.Port(I2cPullupPort())


class I2cTargetBlock(Block):
    def __init__(self, address: IntLike):
        super().__init__()
        self.port = self.Port(I2cTarget(DigitalBidir(), [address]))


class I2cTest(DesignTop):
    def __init__(self) -> None:
        super().__init__()
        self.controller = self.Block(I2cControllerBlock())
        self.pull = self.Block(I2cPullupBlock())
        self.device1 = self.Block(I2cTargetBlock(1))
        self.device2 = self.Block(I2cTargetBlock(2))
        self.link = self.connect(self.controller.port, self.pull.port, self.device1.port, self.device2.port)

        self.require(self.controller.port.link().addresses == [1, 2], unchecked=True)


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
