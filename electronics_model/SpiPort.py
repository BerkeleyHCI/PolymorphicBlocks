from typing import *

from edg_core import *
from .DigitalPorts import DigitalSink, DigitalSource, DigitalBidir


class SpiLink(Link):
  def __init__(self) -> None:
    super().__init__()
    self.master = self.Port(SpiMaster())
    self.devices = self.Port(Vector(SpiSlave()))

  def contents(self) -> None:
    super().contents()
    self.sck = self.connect(self.master.sck, self.devices.map_extract(lambda device: device.sck))
    self.miso = self.connect(self.master.miso, self.devices.map_extract(lambda device: device.miso))
    self.mosi = self.connect(self.master.mosi, self.devices.map_extract(lambda device: device.mosi))


class SpiMaster(Bundle[SpiLink]):
  def __init__(self, model: Optional[DigitalBidir] = None, frequency: RangeLike = RangeExpr()) -> None:
    super().__init__()
    self.link_type = SpiLink

    self.sck = self.Port(DigitalSource(model))
    self.mosi = self.Port(DigitalSource(model))
    self.miso = self.Port(DigitalBidir(model))

    self.frequency = self.Parameter(RangeExpr(frequency))
    self.mode = self.Parameter(RangeExpr())  # modes supported, in [0, 3]  TODO: what about sparse modes?


class SpiSlave(Bundle[SpiLink]):
  # TODO: for now, CS is defined separately
  def __init__(self, model: Optional[DigitalBidir] = None, frequency_limit: RangeLike = RangeExpr()) -> None:
    super().__init__()
    self.link_type = SpiLink

    self.sck = self.Port(DigitalSink(model))
    self.mosi = self.Port(DigitalSink(model))
    self.miso = self.Port(DigitalBidir(model))

    self.frequency_limit = self.Parameter(RangeExpr(frequency_limit))  # range of acceptable frequencies
    self.mode_limit = self.Parameter(RangeExpr())  # range of acceptable modes, in [0, 3]
