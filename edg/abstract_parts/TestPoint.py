from typing import Any, TypeVar, Generic
from typing_extensions import override, Self

from ..electronics_interfaces import *
from .Connectors import RfConnector, RfConnectorTestPoint


@abstract_block
class TestPoint(InternalSubcircuit, Block):
    """Abstract test point that can take a name as a string, used as the footprint value."""

    def __init__(self, tp_name: StringLike = "") -> None:
        super().__init__()
        self.io = self.Port(Passive(), [InOut])
        self.tp_name = self.ArgParameter(tp_name)


TestPointLinkType = TypeVar("TestPointLinkType", bound=Link)


@non_library
class BaseTypedTestPoint(TypedTestPoint, Block, Generic[TestPointLinkType]):
    """Base class with utility infrastructure for typed test points"""

    def __init__(self, tp_name: StringLike = "") -> None:
        super().__init__()
        self.io: Port[TestPointLinkType]
        self.tp_name = self.ArgParameter(tp_name)

    def connected(self, io: Port[TestPointLinkType]) -> Self:
        builder.block().connect(io, self.io)
        return self


@non_library
class BaseSingleTestPoint(BaseTypedTestPoint[TestPointLinkType], Generic[TestPointLinkType]):
    """Base class that provides naming infrastructure for single-wire test points"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.tp = self.Block(TestPoint(StringExpr()))

    @override
    def contents(self) -> None:
        super().contents()
        self.assign(self.tp.tp_name, (self.tp_name == "").then_else(self.io.link().name(), self.tp_name))


@non_library
class BaseRfTestPoint(BaseTypedTestPoint[TestPointLinkType], Generic[TestPointLinkType]):
    """Base class with utility infrastructure for typed RF test points."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.conn = self.Block(RfConnector())
        self.gnd = self.Export(self.conn.gnd, [Common])

    @override
    def contents(self) -> None:
        super().contents()
        self.conn.with_mixin(RfConnectorTestPoint((self.tp_name == "").then_else(self.io.link().name(), self.tp_name)))


class GroundTestPoint(BaseSingleTestPoint[GroundLink]):
    """Test point with a Ground port."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.io: Ground = self.Port(Ground(), [InOut])
        self.connect(self.io.net, self.tp.io)


class VoltageTestPoint(BaseSingleTestPoint[VoltageLink]):
    """Test point with a VoltageSink port."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.io: VoltageSink = self.Port(VoltageSink(), [InOut])
        self.connect(self.io.net, self.tp.io)


class DigitalTestPoint(BaseSingleTestPoint[DigitalLink]):
    """Test point with a DigitalSink port."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.io: DigitalSink = self.Port(DigitalSink(), [InOut])
        self.connect(self.io.net, self.tp.io)


class DigitalArrayTestPoint(TypedTestPoint, GeneratorBlock):
    """Creates an array of Digital test points, sized from the port array's connections."""

    def __init__(self, tp_name: StringLike = "") -> None:
        super().__init__()
        self.io = self.Port(Vector(DigitalSink.empty()), [InOut])
        self.tp_name = self.ArgParameter(tp_name)
        self.generator_param(self.io.requested(), self.tp_name)

    @override
    def generate(self) -> None:
        super().generate()
        self.tp = ElementDict[DigitalTestPoint]()
        for requested in self.get(self.io.requested()):
            # TODO: link() on Vector is not supported, so we leave the naming to the leaf link in the leaf test point
            if self.get(self.tp_name) == "":
                tp = self.tp[requested] = self.Block(DigitalTestPoint())
            else:
                tp = self.tp[requested] = self.Block(DigitalTestPoint(self.tp_name + f".{requested}"))
            self.connect(self.io.append_elt(DigitalSink.empty(), requested), tp.io)


class AnalogTestPoint(BaseSingleTestPoint[AnalogLink]):
    """Test point with a AnalogSink port"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.io: AnalogSink = self.Port(AnalogSink(), [InOut])
        self.connect(self.io.net, self.tp.io)


class AnalogCoaxTestPoint(BaseRfTestPoint[AnalogLink]):
    """Test point with a AnalogSink port and using a coax connector with shielding connected to gnd.
    No impedance matching, this is intended for lower frequency signals where the wavelength would be
    much longer than the test lead length"""

    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.io: AnalogSink = self.Port(AnalogSink(), [InOut])
        self.connect(self.io.net, self.conn.sig)


class I2cTestPoint(BaseTypedTestPoint[I2cLink]):
    """Two test points for I2C SDA and SCL"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.io: I2cTarget = self.Port(I2cTarget(DigitalBidir.empty()), [InOut])

    @override
    def contents(self) -> None:
        super().contents()
        name_prefix = (self.tp_name == "").then_else(self.io.link().name(), self.tp_name)
        self.tp_scl = self.Block(DigitalTestPoint(name_prefix + ".scl"))
        self.tp_sda = self.Block(DigitalTestPoint(name_prefix + ".sda"))
        self.connect(self.tp_scl.io, self.io.scl)
        self.connect(self.tp_sda.io, self.io.sda)


class SpiTestPoint(BaseTypedTestPoint[SpiLink]):
    """Test points for SPI"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.io: SpiPeripheral = self.Port(SpiPeripheral(DigitalBidir.empty()), [InOut])

    @override
    def contents(self) -> None:
        super().contents()
        name_prefix = (self.tp_name == "").then_else(self.io.link().name(), self.tp_name)
        self.tp_sck = self.Block(DigitalTestPoint(name_prefix + ".sck"))
        self.tp_mosi = self.Block(DigitalTestPoint(name_prefix + ".mosi"))
        self.tp_miso = self.Block(DigitalTestPoint(name_prefix + ".miso"))
        self.connect(self.tp_sck.io, self.io.sck)
        self.connect(self.tp_mosi.io, self.io.mosi)
        self.connect(self.tp_miso.io, self.io.miso)


class CanControllerTestPoint(BaseTypedTestPoint[CanLogicLink]):
    """Two test points for CAN controller-side TXD and RXD"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.io: CanPassivePort = self.Port(CanPassivePort(DigitalBidir.empty()), [InOut])

    @override
    def contents(self) -> None:
        super().contents()
        name_prefix = (self.tp_name == "").then_else(self.io.link().name(), self.tp_name)
        self.tp_txd = self.Block(DigitalTestPoint(name_prefix + ".txd"))
        self.tp_rxd = self.Block(DigitalTestPoint(name_prefix + ".rxd"))
        self.connect(self.tp_txd.io, self.io.txd)
        self.connect(self.tp_rxd.io, self.io.rxd)


class CanDiffTestPoint(BaseTypedTestPoint[CanDiffLink]):
    """Two test points for CAN differential-side canh and canl"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.io: CanDiffPort = self.Port(CanDiffPort(DigitalBidir.empty()), [InOut])

    @override
    def contents(self) -> None:
        super().contents()
        name_prefix = (self.tp_name == "").then_else(self.io.link().name(), self.tp_name)
        self.tp_canh = self.Block(DigitalTestPoint(name_prefix + ".canh"))
        self.tp_canl = self.Block(DigitalTestPoint(name_prefix + ".canl"))
        self.connect(self.tp_canh.io, self.io.canh)
        self.connect(self.tp_canl.io, self.io.canl)
