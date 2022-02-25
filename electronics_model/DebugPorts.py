from typing import *

from edg_core import *
from .DigitalPorts import DigitalSink, DigitalSource, DigitalBidir


class SwdLink(Link):
  def __init__(self) -> None:
    super().__init__()

    self.host: SwdHostPort = self.Port(SwdHostPort(DigitalBidir.empty()))
    self.device: SwdTargetPort = self.Port(SwdTargetPort(DigitalBidir.empty()))

  def contents(self) -> None:
    super().contents()
    
    self.swdio = self.connect(self.host.swdio, self.device.swdio)
    self.swclk = self.connect(self.host.swclk, self.device.swclk)
    self.swo = self.connect(self.host.swo, self.device.swo)
    self.reset = self.connect(self.host.reset, self.device.reset)


class SwdHostPort(Bundle[SwdLink]):
  def __init__(self, model: Optional[DigitalBidir] = None) -> None:
    super().__init__()
    self.link_type = SwdLink

    if model is None:
      model = DigitalBidir()  # ideal by default
    self.swdio = self.Port(model)
    self.swclk = self.Port(DigitalSource.from_bidir(model))
    self.swo = self.Port(DigitalSink.from_bidir(model))
    self.reset = self.Port(DigitalSource.from_bidir(model))


class SwdTargetPort(Bundle[SwdLink]):
  def __init__(self, model: Optional[DigitalBidir] = None) -> None:
    super().__init__()
    self.link_type = SwdLink

    if model is None:
      model = DigitalBidir()  # ideal by default
    self.swdio = self.Port(model)
    self.swclk = self.Port(DigitalSink.from_bidir(model))
    self.swo = self.Port(DigitalSource.from_bidir(model))
    self.reset = self.Port(DigitalSink.from_bidir(model))
