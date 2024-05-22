from typing import *

from ..core import *
from .DigitalPorts import DigitalSink, DigitalSource, DigitalBidir


class UartLink(Link):
  def __init__(self) -> None:
    super().__init__()
    self.a = self.Port(UartPort(DigitalBidir.empty()))
    self.b = self.Port(UartPort(DigitalBidir.empty()))

  def contents(self) -> None:
    super().contents()

    self.a_tx = self.connect(self.a.tx, self.b.rx)
    self.b_tx = self.connect(self.b.tx, self.a.rx)


class UartPort(Bundle[UartLink]):
  link_type = UartLink

  def __init__(self, model: Optional[DigitalBidir] = None) -> None:
    super().__init__()
    if model is None:
      model = DigitalBidir()  # ideal by default
    self.tx = self.Port(DigitalSource.from_bidir(model))
    self.rx = self.Port(DigitalSink.from_bidir(model))

    self.baud = self.Parameter(RangeExpr(RangeExpr.ZERO))
    self.baud_limit = self.Parameter(RangeExpr(RangeExpr.INF))
