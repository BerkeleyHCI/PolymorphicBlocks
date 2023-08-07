import unittest

from . import *


class I2cControllerBlock(Block):
  def __init__(self):
    super().__init__()
    self.port = self.Port(I2cController())


class I2cPullupBlock(Block):
  def __init__(self):
    super().__init__()
    self.port = self.Port(I2cPullupPort())


class I2cTargetBlock(Block):
  @init_in_parent
  def __init__(self, address: IntLike):
    super().__init__()
    self.port = self.Port(I2cTarget(DigitalBidir(), [address]))


class I2cTest(DesignTop):
  def __init__(self):
    super().__init__()
    self.controller = self.Block(I2cControllerBlock())
    self.pull = self.Block(I2cPullupBlock())
    self.device1 = self.Block(I2cTargetBlock(1))
    self.device2 = self.Block(I2cTargetBlock(2))
    self.link = self.connect(self.controller.port, self.pull.port, self.device1.port, self.device2.port)

    self.require(self.controller.port.link().addresses == [1, 2], unchecked=True)


class I2cNoPullTest(DesignTop):
  def __init__(self):
    super().__init__()
    self.controller = self.Block(I2cControllerBlock())
    self.device1 = self.Block(I2cTargetBlock(1))
    self.link = self.connect(self.controller.port, self.device1.port)


class I2cConflictTest(DesignTop):
  def __init__(self):
    super().__init__()
    self.master = self.Block(I2cControllerBlock())
    self.pull = self.Block(I2cPullupBlock())
    self.device1 = self.Block(I2cTargetBlock(1))
    self.device2 = self.Block(I2cTargetBlock(1))
    self.link = self.connect(self.master.port, self.pull.port, self.device1.port, self.device2.port)


class I2cTestCase(unittest.TestCase):
  def test_i2c(self) -> None:
    ScalaCompiler.compile(I2cTest)

  def test_i2c_nopull(self) -> None:
    with self.assertRaises(CompilerCheckError):
      ScalaCompiler.compile(I2cNoPullTest)

  def test_i2c_conflict(self) -> None:
    with self.assertRaises(CompilerCheckError):
      ScalaCompiler.compile(I2cConflictTest)
