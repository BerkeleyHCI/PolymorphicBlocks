from typing_extensions import override

from ..electronics_model import *


class EthernetMdiPairLink(Link):
    """Single pair ethernet twisted-pair MDI connection, between the PHY and magnetics."""

    def __init__(self) -> None:
        super().__init__()
        self.phy = self.Port(EthernetMdiPhyPairPort.empty())
        self.mag = self.Port(EthernetMdiMagPairPort.empty())

    @override
    def contents(self) -> None:
        # KiCad diffpair-friendly naming
        self.dp_P = self.connect(self.phy.pos, self.mag.pos)
        self.dp_N = self.connect(self.phy.neg, self.mag.neg)
        self.center = self.connect(self.phy.center, self.mag.center)


class EthernetMdiPhyPairPort(Port[EthernetMdiPairLink]):
    """PHY-side port of an ethernet twisted-pair MDI connection"""

    link_type = EthernetMdiPairLink

    def __init__(self) -> None:
        super().__init__()
        self.pos = self.Port(Passive())
        self.neg = self.Port(Passive())
        self.center = self.Port(Passive())


class EthernetMdiMagPairPort(Port[EthernetMdiPairLink]):
    """Magnetics-side port of a twisted-pair MDI connection"""

    link_type = EthernetMdiPairLink

    def __init__(self) -> None:
        super().__init__()
        self.pos = self.Port(Passive())
        self.neg = self.Port(Passive())
        self.center = self.Port(Passive())


class EthernetMdiLink(Link):
    """Full (multi-pair) connection for ethernet twisted-pair MDI connection, between the PHY and magnetics.
    Currently supports only 10/100Mbps (100BASE-TX) connections with TX/RX pairs."""

    def __init__(self) -> None:
        super().__init__()
        self.phy = self.Port(EthernetMdi100BaseTxPhyPort.empty())
        self.mag = self.Port(EthernetMdi100BaseTxMagPort.empty())

    @override
    def contents(self) -> None:
        self.tx = self.connect(self.phy.tx, self.mag.tx)
        self.rx = self.connect(self.phy.rx, self.mag.rx)


class EthernetMdi100BaseTxPhyPort(Port[EthernetMdiLink]):
    """PHY-side MDI port for 100BASE-TX / Fast Ethernet"""

    link_type = EthernetMdiLink

    def __init__(self) -> None:
        super().__init__()
        self.tx = self.Port(EthernetMdiPhyPairPort())
        self.rx = self.Port(EthernetMdiPhyPairPort())


class EthernetMdi100BaseTxMagPort(Port[EthernetMdiLink]):
    """Magnetics-side MDI port for 100BASE-TX / Fast Ethernet"""

    link_type = EthernetMdiLink

    def __init__(self) -> None:
        super().__init__()
        self.tx = self.Port(EthernetMdiMagPairPort())
        self.rx = self.Port(EthernetMdiMagPairPort())


class PoeLink(Link):
    """Power over Ethernet connection between the powered device and the post-rectification jack-facing circuit."""

    def __init__(self) -> None:
        super().__init__()
        self.jack = self.Port(PoePowerPort.empty())
        self.poe = self.Port(PoeDevicePort.empty())

    @override
    def contents(self) -> None:
        self.connect(self.jack.pos, self.poe.pos)
        self.connect(self.jack.neg, self.poe.neg)


class PoePowerPort(Port[PoeLink]):
    """Jack side port for Power over Ethernet, post-rectification."""

    link_type = PoeLink

    def __init__(self) -> None:
        super().__init__()
        self.pos = self.Port(Passive())
        self.neg = self.Port(Passive())


class PoeDevicePort(Port[PoeLink]):
    """Powered device side port for Power over Ethernet. Generally exposed by a PoE controller subcircuit"""

    link_type = PoeLink

    def __init__(self) -> None:
        super().__init__()
        self.pos = self.Port(Passive())
        self.neg = self.Port(Passive())
