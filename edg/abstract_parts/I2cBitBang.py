from typing import cast

from typing_extensions import override

from ..electronics_model import *
from .Categories import *


class I2cControllerBitBang(BitBangAdapter, Block):
  """Bit-bang adapter for I2C controller"""
  def __init__(self) -> None:
    super().__init__()
    self.i2c = self.Port(I2cController.empty(), [Output])
    self.scl = self.Port(DigitalBidir.empty())
    self.sda = self.Port(DigitalBidir.empty())

  @override
  def contents(self) -> None:
    super().contents()
    self.connect(self.i2c.scl, self.scl)
    self.connect(self.i2c.sda, self.sda)

  def connected_from(self, scl: Port[DigitalLink], sda: Port[DigitalLink]) -> 'I2cControllerBitBang':
    cast(Block, builder.get_enclosing_block()).connect(scl, self.scl)
    cast(Block, builder.get_enclosing_block()).connect(sda, self.sda)
    return self
