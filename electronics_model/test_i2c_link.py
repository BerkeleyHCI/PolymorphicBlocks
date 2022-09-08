import unittest

from . import *


class I2cMasterBlock(Block):
  def __init__(self):
    super().__init__()
    self.port = self.Port(I2cMaster())


class I2cDeviceBlock(Block):
  @init_in_parent
  def __init__(self, address: IntLike):
    super().__init__()
    self.port = self.Port(I2cSlave(DigitalBidir(), [address]))


class I2cTest(Block):
  def __init__(self):
    super().__init__()
    self.master = self.Block(I2cMasterBlock())
    self.device1 = self.Block(I2cDeviceBlock(1))
    self.device2 = self.Block(I2cDeviceBlock(2))
    self.link = self.connect(self.master.port, self.device1.port, self.device2.port)


class I2cConflictTest(Block):
  def __init__(self):
    super().__init__()
    self.master = self.Block(I2cMasterBlock())
    self.device1 = self.Block(I2cDeviceBlock(1))
    self.device2 = self.Block(I2cDeviceBlock(1))
    self.link = self.connect(self.master.port, self.device1.port, self.device2.port)


class I2cTestCase(unittest.TestCase):
  def test_i2c(self) -> None:
    compiled = ScalaCompiler.compile(I2cTest)
    self.assertEqual(compiled.get_value(['link', 'addresses']),
                     [1, 2])

  def test_i2c_conflict(self) -> None:
    compiled = ScalaCompiler.compile(I2cConflictTest)
