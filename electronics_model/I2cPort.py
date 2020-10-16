from typing import *

from edg_core import *
from .DigitalPorts import DigitalSink, DigitalSource, DigitalBidir, DigitalSingleSource


class I2cLink(Link):
  def __init__(self) -> None:
    # TODO support multi-master buses
    super().__init__()

    self.pull = self.Port(I2cPullupPort())
    self.master = self.Port(I2cMaster())
    self.devices = self.Port(Vector(I2cSlave()))

  def contents(self) -> None:
    super().contents()
    # TODO define all IDs

    self.scl = self.connect(
      self.pull.scl,
      self.master.scl, self.devices.map_extract(lambda device: device.scl))
    self.sda = self.connect(
      self.pull.sda,
      self.master.sda, self.devices.map_extract(lambda device: device.sda))


class I2cPullupPort(Bundle[I2cLink]):
  def __init__(self) -> None:
    super().__init__()
    self.link_type = I2cLink

    self.scl = self.Port(DigitalSingleSource())
    self.sda = self.Port(DigitalSingleSource())


class I2cMaster(Bundle[I2cLink]):
  def __init__(self, model: Optional[DigitalBidir] = None) -> None:
    super().__init__()
    self.link_type = I2cLink

    self.scl = self.Port(DigitalSource(model))
    self.sda = self.Port(DigitalBidir(model))

    self.frequency = self.Parameter(RangeExpr())


class I2cSlave(Bundle[I2cLink]):
  def __init__(self, model: Optional[DigitalBidir] = None) -> None:
    super().__init__()
    self.link_type = I2cLink

    self.scl = self.Port(DigitalSink(model))
    self.sda = self.Port(DigitalBidir(model))

    self.frequency_limit = self.Parameter(RangeExpr())  # range of acceptable frequencies
