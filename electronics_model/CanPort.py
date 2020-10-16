from typing import *

from edg_core import *
from .DigitalPorts import DigitalSink, DigitalSource, DigitalBidir, DigitalBidirBridge


class CanLogicLink(Link):
  """Logic level CAN link, RXD and TXD signals"""
  def __init__(self) -> None:
    super().__init__()
    self.controller = self.Port(CanControllerPort())  # TODO mark as required
    self.transceiver = self.Port(CanTransceiverPort())  # TODO mark as required

    # TODO write custom top level digital constraints
    # TODO model frequency ... somewhere

  def contents(self) -> None:
    super().contents()
    # TODO future: digital constraints through link inference

    self.txd = self.connect(self.controller.txd, self.transceiver.txd)
    self.rxd = self.connect(self.controller.rxd, self.transceiver.rxd)


class CanControllerPort(Bundle[CanLogicLink]):
  def __init__(self, model: Optional[DigitalBidir] = None) -> None:
    super().__init__()
    self.link_type = CanLogicLink

    self.txd = self.Port(DigitalSource(model))
    self.rxd = self.Port(DigitalSink(model))


class CanTransceiverPort(Bundle[CanLogicLink]):
  def __init__(self, model: Optional[DigitalBidir] = None) -> None:
    super().__init__()
    self.link_type = CanLogicLink

    self.txd = self.Port(DigitalSink(model))
    self.rxd = self.Port(DigitalSource(model))


class CanDiffLink(Link):
  """Differential CAN link, CANH and CANL signals"""
  def __init__(self) -> None:
    super().__init__()
    self.nodes = self.Port(Vector(CanDiffPort()))  # TODO mark as required

    # TODO write custom top level digital constraints
    # TODO future: digital constraints through link inference

  def contents(self) -> None:
    super().contents()

    self.canh = self.connect(self.nodes.map_extract(lambda node: node.canh))
    self.canl = self.connect(self.nodes.map_extract(lambda node: node.canl))


class CanDiffPort(Bundle[CanDiffLink]):
  def __init__(self, model: Optional[DigitalBidir] = None) -> None:
    super().__init__()
    self.link_type = CanDiffLink
    self.bridge_type = CanDiffBridge

    self.canh = self.Port(DigitalBidir(model))
    self.canl = self.Port(DigitalBidir(model))


class CanDiffBridge(PortBridge):
  def __init__(self) -> None:
    super().__init__()

    self.outer_port = self.Port(CanDiffPort())
    self.inner_link = self.Port(CanDiffPort())

  def contents(self) -> None:
    super().contents()

    self.canh_bridge = self.Block(DigitalBidirBridge())
    self.connect(self.outer_port.canh, self.canh_bridge.outer_port)
    self.connect(self.canh_bridge.inner_link, self.inner_link.canh)

    self.canl_bridge = self.Block(DigitalBidirBridge())
    self.connect(self.outer_port.canl, self.canl_bridge.outer_port)
    self.connect(self.canl_bridge.inner_link, self.inner_link.canl)
