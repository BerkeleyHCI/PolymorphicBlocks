from typing import *

from edg_core import *
from .DigitalPorts import DigitalSink, DigitalSource, DigitalBidir, DigitalSingleSource, DigitalBidirBridge, \
  DigitalSinkBridge


class I2cLink(Link):
  def __init__(self) -> None:
    # TODO support multi-master buses
    super().__init__()

    self.pull = self.Port(I2cPullupPort(), optional=True)
    self.master = self.Port(I2cMaster(DigitalBidir.empty()))
    self.devices = self.Port(Vector(I2cSlave(DigitalBidir.empty())))

    # this is assigned by some bridges, otherwise left uninitialized
    self.pull_through_master = self.Parameter(BoolExpr())
    self.has_pull = self.Parameter(BoolExpr(self.pull.is_connected()))
    self.pull_scl_voltage = self.pull.scl.voltage_out
    self.pull_sda_voltage = self.pull.sda.voltage_out
    self.pull_scl_output_threshold = self.pull.scl.output_thresholds
    self.pull_sda_output_threshold = self.pull.sda.output_thresholds

  def contents(self) -> None:
    super().contents()
    # TODO define all IDs
    self.require(self.pull.is_connected() | self.pull_through_master)
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

    self.assign(self.inner_link.link().pull_through_master, self.outer_port.link().has_pull)

    # this duplicates DigitalBidirBridge but mixing in the pullup
    self.scl_bridge = self.Block(DigitalSinkBridge())
    self.connect(self.outer_port.scl, self.scl_bridge.outer_port)
    self.connect(self.scl_bridge.inner_link, self.inner_link.scl)

    self.sda_bridge = self.Block(DigitalBidirBridge())
    self.connect(self.outer_port.sda, self.sda_bridge.outer_port)
    self.connect(self.sda_bridge.inner_link, self.inner_link.sda)
