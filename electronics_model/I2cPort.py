from typing import *

from edg_core import *
from .DigitalPorts import DigitalSink, DigitalSource, DigitalBidir, DigitalSingleSource
from .DigitalPorts import DigitalSinkBridge, DigitalBidirBridge


class I2cLink(Link):
  def __init__(self) -> None:
    # TODO support multi-master buses
    super().__init__()

    self.pull = self.Port(I2cPullupPort())
    self.master = self.Port(I2cMaster(DigitalBidir.empty()))
    self.devices = self.Port(Vector(I2cSlave(DigitalBidir.empty())))

  def contents(self) -> None:
    super().contents()
    # TODO define all IDs

    self.scl = self.connect(self.pull.scl, self.master.scl, self.devices.map_extract(lambda device: device.scl),
                            flatten=True)
    self.sda = self.connect(self.pull.sda, self.master.sda, self.devices.map_extract(lambda device: device.sda),
                            flatten=True)


class I2cPullupPort(Bundle[I2cLink]):
  def __init__(self) -> None:
    super().__init__()
    self.link_type = I2cLink

    self.scl = self.Port(DigitalSingleSource(pullup_capable=True))
    self.sda = self.Port(DigitalSingleSource(pullup_capable=True))


class I2cMaster(Bundle[I2cLink]):
  def __init__(self, model: Optional[DigitalBidir] = None) -> None:
    super().__init__()
    self.link_type = I2cLink

    if model is None:
      model = DigitalBidir()  # ideal by default
    self.scl = self.Port(DigitalSource.from_bidir(model))
    self.sda = self.Port(model)

    self.frequency = self.Parameter(RangeExpr(Default(RangeExpr.EMPTY_ZERO)))


class I2cSlave(Bundle[I2cLink]):
  def __init__(self, model: Optional[DigitalBidir] = None) -> None:
    super().__init__()
    self.link_type = I2cLink
    self.bridge_type = I2cSlaveBridge

    if model is None:
      model = DigitalBidir()  # ideal by default
    self.scl = self.Port(DigitalSink.from_bidir(model))
    self.sda = self.Port(model)

    self.frequency_limit = self.Parameter(RangeExpr(Default(RangeExpr.ALL)))  # range of acceptable frequencies


class I2cSlaveBridge(PortBridge):
  def __init__(self) -> None:
    super().__init__()

    self.outer_port = self.Port(I2cSlave(DigitalBidir.empty()))
    self.inner_link = self.Port(I2cMaster(DigitalBidir.empty()))

  def contents(self) -> None:
    super().contents()

    self.scl_bridge = self.Block(DigitalSinkBridge())
    self.connect(self.outer_port.scl, self.scl_bridge.outer_port)
    self.connect(self.scl_bridge.inner_link, self.inner_link.scl)

    self.sda_bridge = self.Block(DigitalBidirBridge())
    self.connect(self.outer_port.sda, self.sda_bridge.outer_port)
    self.connect(self.sda_bridge.inner_link, self.inner_link.sda)
