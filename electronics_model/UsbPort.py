from typing import *

from edg_core import *
from .DigitalPorts import DigitalBidir, DigitalSingleSource


class UsbLink(Link):
  def __init__(self) -> None:
    super().__init__()
    self.host = self.Port(UsbHostPort())
    self.device = self.Port(UsbDevicePort())
    self.passive = self.Port(Vector(UsbPassivePort()), optional=True)

  def contents(self) -> None:
    super().contents()
    # TODO write protocol-level signal constraints?

    self.d_P = self.connect(self.host.dp, self.device.dp,
                           self.passive.map_extract(lambda port: port.dp))
    self.d_N = self.connect(self.host.dm, self.device.dm,
                           self.passive.map_extract(lambda port: port.dm))


class UsbHostPort(Bundle[UsbLink]):
  def __init__(self) -> None:
    super().__init__()
    self.link_type = UsbLink

    self.dp = self.Port(DigitalBidir())
    self.dm = self.Port(DigitalBidir())


class UsbDevicePort(Bundle[UsbLink]):
  def __init__(self, model: Optional[DigitalBidir] = None) -> None:
    super().__init__()
    self.link_type = UsbLink

    if model is None:
      model = DigitalBidir()  # ideal by default
    self.dp = self.Port(model)
    self.dm = self.Port(model)


class UsbPassivePort(Bundle[UsbLink]):
  def __init__(self) -> None:
    super().__init__()
    self.link_type = UsbLink

    self.dp = self.Port(DigitalBidir())
    self.dm = self.Port(DigitalBidir())


class UsbCcLink(Link):
  def __init__(self) -> None:
    super().__init__()
    # TODO should we have UFP/DFP/DRD support?
    # TODO note that CC is pulled up on source (DFP) side
    self.a = self.Port(UsbCcPort())
    self.b = self.Port(UsbCcPort())

  def contents(self) -> None:
    super().contents()
    # TODO perhaps enable crossover connections as optional layout optimization?
    # TODO check both b and pull aren't simultaneously connected?
    # TODO write protocol-level signal constraints?
    self.cc1 = self.connect(self.a.cc1, self.b.cc1)
    self.cc2 = self.connect(self.a.cc2, self.b.cc2)


class UsbCcPort(Bundle[UsbCcLink]):
  def __init__(self, pullup_capable: BoolLike = Default(False)) -> None:
    super().__init__()
    self.link_type = UsbCcLink

    self.cc1 = self.Port(DigitalBidir(pullup_capable=pullup_capable))
    self.cc2 = self.Port(DigitalBidir(pullup_capable=pullup_capable))
