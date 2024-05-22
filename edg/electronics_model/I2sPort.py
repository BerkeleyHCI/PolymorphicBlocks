from typing import *

from ..core import *
from .DigitalPorts import DigitalSink, DigitalSource, DigitalBidir


class I2sLink(Link):
  def __init__(self) -> None:
    super().__init__()
    self.controller = self.Port(I2sController(DigitalBidir.empty()))
    self.target_receiver = self.Port(I2sTargetReceiver(DigitalSink.empty()))
    # TODO: multiple receivers, target transmitters, eg microphones

  def contents(self) -> None:
    super().contents()
    self.sck = self.connect(self.controller.sck, self.target_receiver.sck)
    self.ws = self.connect(self.controller.ws, self.target_receiver.ws)
    self.sd = self.connect(self.controller.sd, self.target_receiver.sd)


class I2sController(Bundle[I2sLink]):
  """Controller is both controller (drives SCK and WS lines) and transmitter (SD is output)"""
  link_type = I2sLink

  def __init__(self, model: Optional[DigitalBidir] = None) -> None:
    super().__init__()
    if model is None:
      model = DigitalBidir()  # ideal by default
    self.sck = self.Port(DigitalSource.from_bidir(model))
    self.ws = self.Port(DigitalSource.from_bidir(model))
    self.sd = self.Port(model)  # bidirectional


class I2sTargetReceiver(Bundle[I2sLink]):
  """Target means SCK and WS are inputs, receiver means SD is input"""
  link_type = I2sLink

  def __init__(self, model: Optional[DigitalSink] = None) -> None:
    super().__init__()
    if model is None:
      model = DigitalSink()  # ideal by default
    self.sck = self.Port(model)
    self.ws = self.Port(model)
    self.sd = self.Port(model)
