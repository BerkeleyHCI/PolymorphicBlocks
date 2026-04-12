from __future__ import annotations

from typing import TYPE_CHECKING, Any

from typing_extensions import override

from .PassivePort import HasPassivePort, Passive
from ..core import *
from .CircuitBlock import KicadImportablePortAdapter
from .Units import Volt, Ohm

if TYPE_CHECKING:
    from .VoltagePorts import VoltageSource
    from .DigitalPorts import DigitalSource
    from .AnalogPort import AnalogSource


class GroundLink(Link):
    @classmethod
    def _voltage_range(cls, port: Port[GroundLink]) -> RangeExpr:
        if isinstance(port, Ground):
            return port.is_connected().then_else(port.link().voltage, RangeExpr._to_expr_type(RangeExpr.ZERO))
        elif isinstance(port, GroundReference):
            return port.voltage_out
        else:
            raise TypeError

    def __init__(self) -> None:
        super().__init__()

        self.ref = self.Port(GroundReference(), optional=True)
        self.gnds = self.Port(Vector(Ground()))

        self.voltage = self.Parameter(RangeExpr())
        self.voltage_limits = self.Parameter(RangeExpr())

    @override
    def contents(self) -> None:
        super().contents()

        self.net = self.connect(self.ref.net, self.gnds.map_extract(lambda gnd: gnd.net), flatten=True)

        self.description = DescriptionString(
            "<b>voltage</b>: ",
            DescriptionString.FormatUnits(self.voltage, "V"),
            " <b>of limits</b>: ",
            DescriptionString.FormatUnits(self.voltage_limits, "V"),
        )

        self.assign(self.voltage, self.ref.is_connected().then_else(self.ref.voltage_out, (0, 0) * Volt))
        self.assign(self.voltage_limits, self.gnds.intersection(lambda x: x.voltage_limits))
        self.require(self.voltage_limits.contains(self.voltage), "overvoltage")


class GroundBridge(PortBridge):
    def __init__(self) -> None:
        super().__init__()

        self.outer_port = self.Port(Ground())
        self.inner_link = self.Port(GroundReference(voltage_out=RangeExpr()))

    @override
    def contents(self) -> None:
        super().contents()

        self.connect(self.outer_port.net, self.inner_link.net)
        self.assign(self.inner_link.voltage_out, self.outer_port.link().voltage)


class GroundAdapterVoltageSource(PortAdapter["VoltageSource"]):
    def __init__(self) -> None:
        from .VoltagePorts import VoltageSource

        super().__init__()
        self.src = self.Port(Ground())
        self.dst = self.Port(
            VoltageSource(
                voltage_out=self.src.link().voltage,
            )
        )
        self.connect(self.src.net, self.dst.net)


class GroundAdapterDigitalSource(PortAdapter["DigitalSource"]):
    def __init__(self) -> None:
        from .DigitalPorts import DigitalSource

        super().__init__()
        self.src = self.Port(Ground())
        self.dst = self.Port(DigitalSource.empty())
        self.connect(
            self.src.net.adapt_to(
                DigitalSource(
                    voltage_out=self.src.link().voltage,
                    output_thresholds=(self.src.link().voltage.lower(), FloatExpr._to_expr_type(float("inf"))),
                )
            ),
            self.dst,
        )


class GroundAdapterAnalogSource(KicadImportablePortAdapter["AnalogSource"]):
    def __init__(self) -> None:
        from .AnalogPort import AnalogSource

        super().__init__()
        self.src = self.Port(Ground())
        self.dst = self.Port(
            AnalogSource(
                voltage_out=self.src.link().voltage,
                signal_out=self.src.link().voltage,
            )
        )
        self.connect(self.dst.net, self.src.net)


class Ground(HasPassivePort, Port[GroundLink]):
    link_type = GroundLink
    bridge_type = GroundBridge

    def as_voltage_source(self) -> VoltageSource:
        return self._convert(GroundAdapterVoltageSource())

    def as_digital_source(self) -> DigitalSource:
        return self._convert(GroundAdapterDigitalSource())

    def as_analog_source(self) -> AnalogSource:
        return self._convert(GroundAdapterAnalogSource())

    @classmethod
    def from_gnd(cls, gnd: Ground, voltage_limits: RangeLike = RangeExpr.ALL) -> Ground:
        """Creates a ground with an optional voltage offset rating from some other ground"""
        return Ground(voltage_limits=GroundLink._voltage_range(gnd) + voltage_limits)

    def __init__(self, voltage_limits: RangeLike = Range.all()) -> None:
        super().__init__()
        self.net = self.Port(Passive())
        self.voltage_limits = self.Parameter(RangeExpr(voltage_limits))


class GroundReference(HasPassivePort, Port[GroundLink]):
    link_type = GroundLink

    def __init__(self, voltage_out: RangeLike = RangeExpr.ZERO) -> None:
        super().__init__()
        self.net = self.Port(Passive())
        self.voltage_out = self.Parameter(RangeExpr(voltage_out))


from deprecated import deprecated


@deprecated("Use Ground() or GroundReference(...), Ground is no longer directioned")
def GroundSource(*args: Any, **kwargs: Any) -> Ground:
    return Ground()


# Standard port tags for implicit connection scopes / auto-connecting power supplies
Common = PortTag(Ground)  # Common ground (0v) port
