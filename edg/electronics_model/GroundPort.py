from __future__ import annotations

from ..core import *
from .CircuitBlock import CircuitPortBridge, CircuitLink, CircuitPort
from .Units import Volt


class GroundLink(CircuitLink):
    def __init__(self) -> None:
        super().__init__()

        self.ref = self.Port(GroundReference(), optional=True)
        self.gnds = self.Port(Vector(Ground()))

        self.ref_voltage = self.Parameter(RangeExpr())

    def contents(self) -> None:
        super().contents()

        self.description = DescriptionString(
            "<b>voltage</b>: ", DescriptionString.FormatUnits(self.voltage, "V"))

        self.assign(self.ref_voltage, self.ref.is_connected().then_else(
            self.ref.voltage, (0, 0)*Volt
        ))


class GroundBridge(CircuitPortBridge):
    def __init__(self) -> None:
        super().__init__()

        self.outer_port = self.Port(VoltageSink(current_draw=RangeExpr(),
                                                voltage_limits=RangeExpr()))

        # Here we ignore the current_limits of the inner port, instead relying on the main link to handle it
        # The outer port's voltage_limits is untouched and should be defined in the port def.
        # TODO: it's a slightly optimization to handle them here. Should it be done?
        # TODO: or maybe current_limits / voltage_limits shouldn't be a port, but rather a block property?
        self.inner_link = self.Port(VoltageSource(current_limits=RangeExpr.ALL,
                                                  voltage_out=RangeExpr()))

    def contents(self) -> None:
        super().contents()

        self.assign(self.outer_port.current_draw, self.inner_link.link().current_drawn)
        self.assign(self.outer_port.voltage_limits, self.inner_link.link().voltage_limits)

        self.assign(self.inner_link.voltage_out, self.outer_port.link().voltage)


class Ground(CircuitPort):
    bridge_type = GroundBridge

    @staticmethod
    def from_gnd(gnd: VoltageSink, voltage_limits: RangeLike = RangeExpr.ALL,
                 current_draw: RangeLike = RangeExpr.ZERO) -> 'VoltageSink':
        return VoltageSink(
            voltage_limits=gnd.link().voltage + voltage_limits,
            current_draw=current_draw
        )

    def __init__(self, voltage_limits: RangeLike = RangeExpr.ALL,
                 current_draw: RangeLike = RangeExpr.ZERO) -> None:
        super().__init__()
        self.voltage_limits: RangeExpr = self.Parameter(RangeExpr(voltage_limits))
        self.current_draw: RangeExpr = self.Parameter(RangeExpr(current_draw))


class GroundReference(CircuitPort):
    def __init__(self, voltage_out: RangeLike = RangeExpr.ZERO,
                 current_limits: RangeLike = RangeExpr.ALL) -> None:
        super().__init__()
        self.voltage_out: RangeExpr = self.Parameter(RangeExpr(voltage_out))
        self.current_limits: RangeExpr = self.Parameter(RangeExpr(current_limits))


from deprecated import deprecated
@deprecated("Use Ground() or GroundReference(...), Ground is no longer directioned")
def GroundSource(*args, **kwargs):
    return Ground()


# Standard port tags for implicit connection scopes / auto-connecting power supplies
Common = PortTag(Ground)  # Common ground (0v) port
