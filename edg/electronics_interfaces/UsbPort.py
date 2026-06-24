from typing import *

from typing_extensions import override

from ..electronics_model import *
from .DigitalPorts import DigitalBidir
from ..electronics_model.PassivePort import PassiveBridge


class UsbLink(Link):
    def __init__(self) -> None:
        super().__init__()
        self.host = self.Port(UsbHostPort())
        self.device = self.Port(UsbDevicePort())
        self.passive = self.Port(Vector(UsbPassivePort()), optional=True)

    @override
    def contents(self) -> None:
        super().contents()
        # TODO write protocol-level signal constraints?

        self.d_P = self.connect(
            self.host.dp, self.device.dp, self.passive.map_extract(lambda port: port.dp), flatten=True
        )
        self.d_N = self.connect(
            self.host.dm, self.device.dm, self.passive.map_extract(lambda port: port.dm), flatten=True
        )


class UsbHostBridge(PortBridge):
    def __init__(self) -> None:
        super().__init__()
        self.outer_port = self.Port(UsbHostPort.empty())
        self.inner_link = self.Port(UsbDevicePort.empty())

    @override
    def contents(self) -> None:
        super().contents()

        self.dm_bridge = self.Block(PassiveBridge())
        self.connect(self.outer_port.dm, self.dm_bridge.outer_port)
        self.connect(self.dm_bridge.inner_link, self.inner_link.dm)

        self.dp_bridge = self.Block(PassiveBridge())
        self.connect(self.outer_port.dp, self.dp_bridge.outer_port)
        self.connect(self.dp_bridge.inner_link, self.inner_link.dp)


class UsbHostPort(Port[UsbLink]):
    link_type = UsbLink
    bridge_type = UsbHostBridge

    def __init__(self) -> None:
        super().__init__()
        self.dp = self.Port(Passive())
        self.dm = self.Port(Passive())


class UsbDeviceBridge(PortBridge):
    def __init__(self) -> None:
        super().__init__()
        self.outer_port = self.Port(UsbDevicePort.empty())
        self.inner_link = self.Port(UsbHostPort.empty())

    @override
    def contents(self) -> None:
        super().contents()

        self.dm_bridge = self.Block(PassiveBridge())
        self.connect(self.outer_port.dm, self.dm_bridge.outer_port)
        self.connect(self.dm_bridge.inner_link, self.inner_link.dm)

        self.dp_bridge = self.Block(PassiveBridge())
        self.connect(self.outer_port.dp, self.dp_bridge.outer_port)
        self.connect(self.dp_bridge.inner_link, self.inner_link.dp)


class UsbDevicePort(Port[UsbLink]):
    link_type = UsbLink
    bridge_type = UsbDeviceBridge

    def __init__(self) -> None:
        super().__init__()
        self.dp = self.Port(Passive())
        self.dm = self.Port(Passive())


class UsbPassivePort(Port[UsbLink]):
    link_type = UsbLink

    def __init__(self) -> None:
        super().__init__()
        self.dp = self.Port(Passive())
        self.dm = self.Port(Passive())


class UsbCcLink(Link):
    def __init__(self) -> None:
        super().__init__()
        # TODO should we have UFP/DFP/DRD support?
        # TODO note that CC is pulled up on source (DFP) side
        self.a = self.Port(UsbCcPort())
        self.b = self.Port(UsbCcPort())

    @override
    def contents(self) -> None:
        super().contents()
        # TODO perhaps enable crossover connections as optional layout optimization?
        self.cc1 = self.connect(self.a.cc1, self.b.cc1)
        self.cc2 = self.connect(self.a.cc2, self.b.cc2)


class UsbCcPort(Port[UsbCcLink]):
    link_type = UsbCcLink

    def __init__(self) -> None:
        super().__init__()
        self.cc1 = self.Port(Passive())
        self.cc2 = self.Port(Passive())
