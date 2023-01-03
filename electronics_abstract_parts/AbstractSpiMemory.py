from electronics_model import *
from .Categories import *


@abstract_block
class SpiMemory(Block):
  """Base class for SPI memory, with acceptable sizes (in bits) as a range."""
  @init_in_parent
  def __init__(self, size: RangeLike) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.gnd = self.Port(Ground.empty(), [Common])

    self.spi = self.Port(SpiSlave.empty())
    self.cs = self.Port(DigitalSink.empty())

    self.size = self.ArgParameter(size)
    self.actual_size = self.Parameter(IntExpr())
