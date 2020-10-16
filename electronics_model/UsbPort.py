from typing import *

from edg_core import *
from .DigitalPorts import DigitalBidir


class UsbLink(Link):
  def __init__(self) -> None:
    super().__init__()
    self.host = self.Port(UsbHostPort())
    self.device = self.Port(UsbDevicePort())
    self.passive = self.Port(Vector(UsbPassivePort()))

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
  def __init__(self) -> None:
    super().__init__()
    self.link_type = UsbLink

    self.dp = self.Port(DigitalBidir())
    self.dm = self.Port(DigitalBidir())


class UsbPassivePort(Bundle[UsbLink]):
  def __init__(self) -> None:
    super().__init__()
    self.link_type = UsbLink

    self.dp = self.Port(DigitalBidir())
    self.dm = self.Port(DigitalBidir())
