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
  def __init__(self,
               voltage_out: RangeLike = Default(RangeExpr.EMPTY_ZERO),  # TODO dedup w/ AnalogSource?
               current_limits: RangeLike = Default(RangeExpr.ALL),
               impedance: RangeLike = Default(RangeExpr.ZERO)) -> None:
    super().__init__()
    self.link_type = SpeakerLink

    self.a = self.Port(AnalogSource(voltage_out=voltage_out, current_limits=current_limits, impedance=impedance))
    self.b = self.Port(AnalogSource(voltage_out=voltage_out, current_limits=current_limits, impedance=impedance))


class SpeakerPort(Bundle[SpeakerLink]):
  def __init__(self, impedance: RangeLike = Default(RangeExpr.INF)) -> None:
    super().__init__()
    self.link_type = SpeakerLink

    self.a = self.Port(AnalogSink(impedance=impedance))  # TODO how to model max power?
    self.b = self.Port(AnalogSink(impedance=impedance))
