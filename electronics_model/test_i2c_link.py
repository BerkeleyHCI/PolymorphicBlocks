import unittest

from . import *


class I2cMasterBlock(Block):
  def __init__(self):
    super().__init__()
    self.port = self.Port(I2cMaster())


class I2cPullupBlock(Block):
  def __init__(self):
    super().__init__()
    self.port = self.Port(I2cPullupPort())


class I2cDeviceBlock(Block):
  @init_in_parent
  def __init__(self, address: IntLike):
    super().__init__()
    self.port = self.Port(I2cSlave(DigitalBidir(), [address]))


class I2cTest(DesignTop):
  def __init__(self):
    super().__init__()
    self.master = self.Block(I2cMasterBlock())
    self.pull = self.Block(I2cPullupBlock())
    self.device1 = self.Block(I2cDeviceBlock(1))
    self.device2 = self.Block(I2cDeviceBlock(2))
    self.link = self.connect(self.master.port, self.pull.port, self.device1.port, self.device2.port)


class I2cNoPullTest(DesignTop):
  def __init__(self):
    super().__init__()
    self.master = self.Block(I2cMasterBlock())
    self.device1 = self.Block(I2cDeviceBlock(1))
    self.link = self.connect(self.master.port, self.device1.port)


class I2cConflictTest(DesignTop):
  def __init__(self):
    super().__init__()
    self.master = self.Block(I2cMasterBlock())
    self.pull = self.Block(I2cPullupBlock())
    self.device1 = self.Block(I2cDeviceBlock(1))
    self.device2 = self.Block(I2cDeviceBlock(1))
    self.link = self.connect(self.master.port, self.pull.port, self.device1.port, self.device2.port)


class I2cTestCase(unittest.TestCase):
  def test_i2c(self) -> None:
    compiled = ScalaCompiler.compile(I2cTest)
    self.assertEqual(compiled.get_value(['link', 'addresses']),
                     [2, 1])  # TODO this is probably reversed because of dict (non)ordering

  def test_i2c_nopull(self) -> None:
    with self.assertRaises(CompilerCheckError):
      ScalaCompiler.compile(I2cNoPullTest)

  def test_i2c_conflict(self) -> None:
    with self.assertRaises(CompilerCheckError):
      ScalaCompiler.compile(I2cConflictTest)
