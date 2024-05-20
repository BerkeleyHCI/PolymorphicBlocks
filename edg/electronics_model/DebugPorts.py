from typing import *

from ..core import *
from .DigitalPorts import DigitalSink, DigitalSource, DigitalBidir, DigitalSingleSource


class SwdLink(Link):
  def __init__(self) -> None:
    super().__init__()

    self.host = self.Port(SwdHostPort.empty())
    self.device = self.Port(SwdTargetPort.empty())
    self.pull = self.Port(Vector(SwdPullPort.empty()), optional=True)

  def contents(self) -> None:
    super().contents()
    
    self.swdio = self.connect(self.host.swdio, self.device.swdio, self.pull.map_extract(lambda port: port.swdio),
                              flatten=True)
    self.swclk = self.connect(self.host.swclk, self.device.swclk, self.pull.map_extract(lambda port: port.swclk),
                              flatten=True)


class SwdHostPort(Bundle[SwdLink]):
  link_type = SwdLink

  def __init__(self, model: Optional[DigitalBidir] = None) -> None:
    super().__init__()
    if model is None:
      model = DigitalBidir()  # ideal by default
    self.swdio = self.Port(model)
    self.swclk = self.Port(DigitalSource.from_bidir(model))


class SwdTargetPort(Bundle[SwdLink]):
  link_type = SwdLink

  def __init__(self, model: Optional[DigitalBidir] = None) -> None:
    super().__init__()
    if model is None:
      model = DigitalBidir()  # ideal by default
    self.swdio = self.Port(model)
    self.swclk = self.Port(DigitalSink.from_bidir(model))


class SwdPullPort(Bundle[SwdLink]):
  link_type = SwdLink

  def __init__(self, model: Optional[DigitalSingleSource] = None) -> None:
    super().__init__()
    if model is None:
      model = DigitalSingleSource()  # ideal by default
    self.swdio = self.Port(model)
    self.swclk = self.Port(model)
