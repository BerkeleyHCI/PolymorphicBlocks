from typing import *

from edg_core import *
from .DigitalPorts import DigitalSink, DigitalSource, DigitalBidir


class UartLink(Link):
  def __init__(self) -> None:
    super().__init__()
    self.a = self.Port(UartPort())
    self.b = self.Port(UartPort())

  def contents(self) -> None:
    super().contents()

    self.a_tx = self.connect(self.a.tx, self.b.rx)
    self.b_tx = self.connect(self.b.tx, self.a.rx)


class UartPort(Bundle[UartLink]):
  def __init__(self, model: Optional[DigitalBidir] = None) -> None:
    super().__init__()
    self.link_type = UartLink

    self.tx = self.Port(DigitalSource(model))
    self.rx = self.Port(DigitalSink(model))

    self.baud = self.Parameter(RangeExpr(Default(RangeExpr.EMPTY_ZERO)))
    self.baud_limit = self.Parameter(RangeExpr(Default(RangeExpr.INF)))
