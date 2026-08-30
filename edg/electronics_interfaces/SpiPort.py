from typing import *
from typing_extensions import override

from ..electronics_model import *
from .DigitalPorts import DigitalSink, DigitalSource, DigitalBidir
from ..util import deprecated_param_remap


class SpiLink(Link):
    """Controller/peripheral naming conventions follow https://www.oshwa.org/a-resolution-to-redefine-spi-signal-names/,
    though SPI naming in general is a mess.
    Unlike I2C, there is not an authoritative SPI specification.
    Other names exist, including main/subnode (Wikipedia) and controller/target (NXP, following their I2C convention).

    Internal link signal names are not considered part of the stable public API and may change
    without a deprecation phase and backwards compatibility.
    """

    def __init__(self) -> None:
        super().__init__()
        self.controller = self.Port(SpiController(DigitalBidir.empty()))
        self.peripherals = self.Port(Vector(SpiPeripheral(DigitalBidir.empty())))

        self.frequency_limit = self.Parameter(RangeExpr())

    @override
    def contents(self) -> None:
        super().contents()
        self.sck = self.connect(
            self.controller.sck, self.peripherals.map_extract(lambda device: device.sck), flatten=True
        )
        self.miso = self.connect(
            self.controller.miso, self.peripherals.map_extract(lambda device: device.miso), flatten=True
        )
        self.mosi = self.connect(
            self.controller.mosi, self.peripherals.map_extract(lambda device: device.mosi), flatten=True
        )
        self.assign(
            self.frequency_limit,
            self.controller.frequency_limit.intersect(self.peripherals.hull(lambda x: x.frequency_limit)),
        )
        self.require(self.frequency_limit != RangeExpr.EMPTY, "no compatible frequency between devices")


class SpiController(Port[SpiLink]):
    link_type = SpiLink

    @deprecated_param_remap(("frequency", "frequency_limit"), (2, "frequency_limit"))
    def __init__(self, model: Optional[DigitalBidir] = None, *, frequency_limit: RangeLike = RangeExpr.ALL) -> None:
        super().__init__()
        if model is None:
            model = DigitalBidir()  # ideal by default
        self.sck = self.Port(DigitalSource.from_bidir(model))
        self.mosi = self.Port(DigitalSource.from_bidir(model))
        self.miso = self.Port(DigitalSink.from_bidir(model))

        self.frequency_limit = self.Parameter(RangeExpr(frequency_limit))
        self.mode = self.Parameter(RangeExpr())  # modes supported, in [0, 3]  TODO: what about sparse modes?


class SpiPeripheral(Port[SpiLink]):
    link_type = SpiLink

    @deprecated_param_remap((2, "frequency_limit"))
    def __init__(self, model: Optional[DigitalBidir] = None, *, frequency_limit: RangeLike = RangeExpr.ALL) -> None:
        super().__init__()
        if model is None:
            model = DigitalBidir()  # ideal by default
        self.sck = self.Port(DigitalSink.from_bidir(model))
        self.mosi = self.Port(DigitalSink.from_bidir(model))
        self.miso = self.Port(model)
        # TODO: (?) CS is defined separately

        self.frequency_limit = self.Parameter(RangeExpr(frequency_limit))  # range of acceptable frequencies
        self.mode_limit = self.Parameter(RangeExpr())  # range of acceptable modes, in [0, 3]


# legacy names
SpiMaster = SpiController
SpiSlave = SpiPeripheral
