from typing import *

from edg_core import *
from .AnalogPort import AnalogSource, AnalogSink


class SpeakerLink(Link):
  def __init__(self) -> None:
    super().__init__()
    self.source = self.Port(SpeakerDriverPort())
    self.sink = self.Port(SpeakerPort())

  def contents(self) -> None:
    super().contents()

    self.a = self.connect(self.source.a, self.sink.a)
    self.b = self.connect(self.source.b, self.sink.b)


class SpeakerDriverPort(Bundle[SpeakerLink]):
  link_type = SpeakerLink

  def __init__(self, model: Optional[AnalogSource] = None) -> None:
    super().__init__()

    if model is None:
      model = AnalogSource()  # ideal by default
    self.a = self.Port(model)
    self.b = self.Port(model)


class SpeakerPort(Bundle[SpeakerLink]):
  link_type = SpeakerLink

  def __init__(self, model: Optional[AnalogSink] = None) -> None:
    super().__init__()
    if model is None:
      model = AnalogSink()  # ideal by default
    self.a = self.Port(model)  # TODO how to model max power?
    self.b = self.Port(model)
