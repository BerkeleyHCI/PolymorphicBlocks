from typing import *

from typing_extensions import override

from ..core import *
from .DigitalPorts import DigitalSink, DigitalSource, DigitalBidir, DigitalBidirBridge, DigitalSinkBridge


class I2cLink(Link):
    """I2C connection, using terminology from the auhtoritative NXP specification at
    https://www.nxp.com/docs/en/user-guide/UM10204.pdf.
    """

    def __init__(self) -> None:
        super().__init__()

        self.controller = self.Port(I2cController(DigitalBidir.empty()))
        self.targets = self.Port(Vector(I2cTarget(DigitalBidir.empty())))

        # in concept we should only have one pullup, but optional handling on non-vector ports is a mess
        # and this breaks where we have to create a bridge, since the internal link has a disconnected pull port
        # so this structurally allows multiple pullups, but an assertion checks that there aren't multiple
        self.pull = self.Port(Vector(I2cPullupPort().empty()), optional=True)

        self.addresses = self.Parameter(ArrayIntExpr(self.targets.flatten(lambda x: x.addresses)))

        self.has_pull = self.Parameter(BoolExpr(self.pull.any_connected()))

    @override
    def contents(self) -> None:
        super().contents()
        self.require(self.pull.any_connected() | self.controller.has_pullup)
        self.require(self.pull.length() <= 1, "at most one pullup")
        self.require(self.addresses.all_unique(), "conflicting addresses on I2C bus")
        self.scl = self.connect(
            self.pull.map_extract(lambda device: device.scl),
            self.controller.scl,
            self.targets.map_extract(lambda device: device.scl),
            flatten=True,
        )
        self.sda = self.connect(
            self.pull.map_extract(lambda device: device.sda),
            self.controller.sda,
            self.targets.map_extract(lambda device: device.sda),
            flatten=True,
        )


class I2cPullupPort(Bundle[I2cLink]):
    link_type = I2cLink

    def __init__(self) -> None:
        super().__init__()
        self.scl = self.Port(DigitalSource(low_driver=False, high_driver=False, pullup_capable=True))
        self.sda = self.Port(DigitalSource(low_driver=False, high_driver=False, pullup_capable=True))


class I2cController(Bundle[I2cLink]):
    link_type = I2cLink

    def __init__(self, model: Optional[DigitalBidir] = None, has_pullup: BoolLike = False) -> None:
        super().__init__()
        if model is None:
            model = DigitalBidir()  # ideal by default
        self.scl = self.Port(DigitalSource.from_bidir(model))
        self.sda = self.Port(model)

        self.frequency = self.Parameter(RangeExpr(RangeExpr.ZERO))
        self.has_pullup = self.Parameter(BoolExpr(has_pullup))


class I2cTargetBridge(PortBridge):
    def __init__(self) -> None:
        super().__init__()

        self.outer_port = self.Port(I2cTarget.empty())
        self.inner_link = self.Port(I2cController(DigitalBidir.empty(), self.outer_port.link().has_pull))

    @override
    def contents(self) -> None:
        super().contents()

        self.outer_port.init_from(I2cTarget(DigitalBidir.empty(), self.inner_link.link().addresses))

        # this duplicates DigitalBidirBridge but mixing in the pullup
        self.scl_bridge = self.Block(DigitalSinkBridge())
        self.connect(self.outer_port.scl, self.scl_bridge.outer_port)
        self.connect(self.scl_bridge.inner_link, self.inner_link.scl)

        self.sda_bridge = self.Block(DigitalBidirBridge())
        self.connect(self.outer_port.sda, self.sda_bridge.outer_port)
        self.connect(self.sda_bridge.inner_link, self.inner_link.sda)


class I2cTarget(Bundle[I2cLink]):
    link_type = I2cLink
    bridge_type = I2cTargetBridge

    def __init__(self, model: Optional[DigitalBidir] = None, addresses: ArrayIntLike = []) -> None:
        """Addresses specified excluding the R/W bit (as a 7-bit number, as directly used by Arduino)"""
        super().__init__()
        if model is None:
            model = DigitalBidir()  # ideal by default
        self.scl = self.Port(DigitalSink.from_bidir(model))
        self.sda = self.Port(model)

        self.frequency_limit = self.Parameter(RangeExpr(RangeExpr.ALL))  # range of acceptable frequencies
        self.addresses = self.Parameter(ArrayIntExpr(addresses))


# legacy names
I2cMaster = I2cController
I2cSlave = I2cTarget
