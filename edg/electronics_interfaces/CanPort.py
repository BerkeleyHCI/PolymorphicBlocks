from typing import *

from typing_extensions import override

from ..electronics_model import *
from .DigitalPorts import DigitalSink, DigitalSource, DigitalBidir, DigitalBidirBridge
from ..electronics_model.PassivePort import PassiveBridge


class CanLogicLink(Link):
    """Logic level CAN link, RXD and TXD signals"""

    def __init__(self) -> None:
        super().__init__()
        self.controller = self.Port(CanControllerPort(DigitalBidir.empty()))
        self.transceiver = self.Port(CanTransceiverPort(DigitalBidir.empty()))
        self.passive = self.Port(Vector(CanPassivePort(DigitalBidir.empty())), optional=True)

        # 0-1 Mbit/s are standard CANbus, 1-8 Mbit/s imply CAN-FD
        self.bitrate_limit = self.Parameter(RangeExpr())

    @override
    def contents(self) -> None:
        super().contents()

        self.txd = self.connect(
            self.controller.txd, self.transceiver.txd, self.passive.map_extract(lambda port: port.txd), flatten=True
        )
        self.rxd = self.connect(
            self.controller.rxd, self.transceiver.rxd, self.passive.map_extract(lambda port: port.rxd), flatten=True
        )

        self.assign(self.bitrate_limit, self.controller.bitrate_limit.intersect(self.transceiver.bitrate_limit))
        self.require(self.bitrate_limit != RangeExpr.EMPTY, "no compatible bitrate between devices")


class CanControllerPort(Port[CanLogicLink]):
    link_type = CanLogicLink

    def __init__(self, model: Optional[DigitalBidir] = None, *, bitrate_limit: RangeLike = RangeExpr.ALL) -> None:
        super().__init__()
        if model is None:  # ideal by default
            model = DigitalBidir()
        self.txd = self.Port(DigitalSource.from_bidir(model))
        self.rxd = self.Port(DigitalSink.from_bidir(model))
        self.bitrate_limit = self.Parameter(RangeExpr(bitrate_limit))


class CanTransceiverPort(Port[CanLogicLink]):
    link_type = CanLogicLink

    def __init__(self, model: Optional[DigitalBidir] = None, *, bitrate_limit: RangeLike = RangeExpr.ALL) -> None:
        super().__init__()
        if model is None:  # ideal by default
            model = DigitalBidir()
        self.txd = self.Port(DigitalSink.from_bidir(model))
        self.rxd = self.Port(DigitalSource.from_bidir(model))
        self.bitrate_limit = self.Parameter(RangeExpr(bitrate_limit))


class CanPassivePort(Port[CanLogicLink]):
    link_type = CanLogicLink

    def __init__(self, model: Optional[DigitalBidir] = None) -> None:
        super().__init__()
        if model is None:  # ideal by default
            model = DigitalBidir()
        self.txd = self.Port(DigitalSink.from_bidir(model))
        self.rxd = self.Port(DigitalSink.from_bidir(model))


class CanDiffLink(Link):
    """Differential CAN link, CANH and CANL signals"""

    def __init__(self) -> None:
        super().__init__()
        self.nodes = self.Port(Vector(CanDiffPort.empty()))  # TODO mark as required

        self.bitrate_limit = self.Parameter(RangeExpr())

    @override
    def contents(self) -> None:
        super().contents()

        self.canh = self.connect(self.nodes.map_extract(lambda node: node.canh), flatten=True)
        self.canl = self.connect(self.nodes.map_extract(lambda node: node.canl), flatten=True)

        self.assign(self.bitrate_limit, self.nodes.intersection(lambda x: x.bitrate_limit))
        self.require(self.bitrate_limit != RangeExpr.EMPTY, "no compatible bitrate between devices")


class CanDiffBridge(PortBridge):
    def __init__(self) -> None:
        super().__init__()

        self.outer_port = self.Port(CanDiffPort.empty())
        self.inner_link = self.Port(CanDiffPort())

    @override
    def contents(self) -> None:
        super().contents()

        self.canh_bridge = self.Block(PassiveBridge())
        self.connect(self.outer_port.canh, self.canh_bridge.outer_port)
        self.connect(self.canh_bridge.inner_link, self.inner_link.canh)

        self.canl_bridge = self.Block(PassiveBridge())
        self.connect(self.outer_port.canl, self.canl_bridge.outer_port)
        self.connect(self.canl_bridge.inner_link, self.inner_link.canl)

        self.assign(self.outer_port.bitrate_limit, self.inner_link.link().bitrate_limit)


class CanDiffPort(Port[CanDiffLink]):
    link_type = CanDiffLink
    bridge_type = CanDiffBridge

    def __init__(self, *, bitrate_limit: RangeLike = RangeExpr.ALL) -> None:
        super().__init__()
        self.canh = self.Port(Passive())
        self.canl = self.Port(Passive())

        self.bitrate_limit = self.Parameter(RangeExpr(bitrate_limit))
