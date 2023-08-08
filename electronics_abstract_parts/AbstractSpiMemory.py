from electronics_model import *
from .Categories import *


@abstract_block
class SpiMemory(Memory, Block):
  """Base class for SPI memory, with acceptable sizes (in bits) as a range."""
  @init_in_parent
  def __init__(self, size: RangeLike) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.gnd = self.Port(Ground.empty(), [Common])

    self.spi = self.Port(SpiPeripheral.empty())
    self.cs = self.Port(DigitalSink.empty())

    self.size = self.ArgParameter(size)
    self.actual_size = self.Parameter(IntExpr())


@abstract_block
class SpiMemoryQspi(BlockInterfaceMixin[SpiMemory]):
  """SPI memory that also supports QSPI mode (4-line SPI).
  Vanilla SPI SDI maps to IO0, and SDO maps to IO1.
  EXPERIMENTAL - interface subject to change.
  May prevent the use of some chip functions that conflict with QSPI lines."""
  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.io2 = self.Port(DigitalBidir.empty())
    self.io3 = self.Port(DigitalBidir.empty())
