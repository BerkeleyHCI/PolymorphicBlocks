from typing import *

from edg_core import *
from .DigitalPorts import DigitalSink, DigitalSource, DigitalBidir


class SpiLink(Link):
  def __init__(self) -> None:
    super().__init__()
    self.master = self.Port(SpiMaster(DigitalBidir.empty()))
    self.devices = self.Port(Vector(SpiSlave(DigitalBidir.empty())))

  def contents(self) -> None:
    super().contents()
    self.sck = self.connect(self.master.sck, self.devices.map_extract(lambda device: device.sck),
                            flatten=True)
    self.miso = self.connect(self.master.miso, self.devices.map_extract(lambda device: device.miso),
                             flatten=True)
    self.mosi = self.connect(self.master.mosi, self.devices.map_extract(lambda device: device.mosi),
                             flatten=True)


class SpiMaster(Bundle[SpiLink]):
  def __init__(self, model: Optional[DigitalBidir] = None,
               frequency: RangeLike = Default(RangeExpr.EMPTY_ZERO)) -> None:
    super().__init__()
    self.link_type = SpiLink

    if model is None:
      model = DigitalBidir()  # ideal by default
    self.sck = self.Port(DigitalSource.from_bidir(model))
    self.mosi = self.Port(DigitalSource.from_bidir(model))
    self.miso = self.Port(model)

    self.frequency = self.Parameter(RangeExpr(frequency))
    self.mode = self.Parameter(RangeExpr())  # modes supported, in [0, 3]  TODO: what about sparse modes?


class SpiSlave(Bundle[SpiLink]):
  # TODO: for now, CS is defined separately
  def __init__(self, model: Optional[DigitalBidir] = None,
               frequency_limit: RangeLike = Default(RangeExpr.ALL)) -> None:
    super().__init__()
    self.link_type = SpiLink

    if model is None:
      model = DigitalBidir()  # ideal by default
    self.sck = self.Port(DigitalSink.from_bidir(model))
    self.mosi = self.Port(DigitalSink.from_bidir(model))
    self.miso = self.Port(model)

    self.frequency_limit = self.Parameter(RangeExpr(frequency_limit))  # range of acceptable frequencies
    self.mode_limit = self.Parameter(RangeExpr())  # range of acceptable modes, in [0, 3]
