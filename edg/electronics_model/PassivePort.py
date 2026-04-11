from __future__ import annotations

from typing import TypeVar, Type, Dict, Union, Generic

from typing_extensions import TYPE_CHECKING

from ..core import *
from .CircuitBlock import CircuitPort, CircuitLink, CircuitPortBridge, CircuitPortAdapter, KicadImportablePortAdapter

if TYPE_CHECKING:
    from .GroundPort import Ground
    from .VoltagePorts import VoltageSource, VoltageSink
    from .DigitalPorts import DigitalSource, DigitalSink, DigitalBidir
    from .AnalogPort import AnalogSource, AnalogSink


class PassiveLink(CircuitLink):
    """Copper-only connection"""

    def __init__(self) -> None:
        super().__init__()
        self.passives = self.Port(Vector(Passive()))


class PassiveAdapterGround(CircuitPortAdapter["Ground"]):
    def __init__(self, voltage_limits: RangeLike = RangeExpr.ALL):
        from .GroundPort import Ground

        super().__init__()
        self.src = self.Port(Passive())
        self.dst = self.Port(Ground(voltage_limits=voltage_limits))
        self.connect(self.src, self.dst.net)


class PassiveAdapterVoltageSource(CircuitPortAdapter["VoltageSource"]):
    # TODO we can't use **kwargs b/c init_in_parent needs the initializer list
    def __init__(
        self,
        voltage_out: RangeLike = RangeExpr.ZERO,
        current_limits: RangeLike = RangeExpr.ALL,
        reverse_voltage_limits: RangeLike = RangeExpr.EMPTY,
        reverse_current_draw: RangeLike = RangeExpr.EMPTY,
    ):
        from .VoltagePorts import VoltageSource

        super().__init__()
        self.src = self.Port(Passive())
        self.dst = self.Port(
            VoltageSource(
                voltage_out=voltage_out,
                current_limits=current_limits,
                reverse_voltage_limits=reverse_voltage_limits,
                reverse_current_draw=reverse_current_draw,
            )
        )


class PassiveAdapterVoltageSink(CircuitPortAdapter["VoltageSink"]):
    # TODO we can't use **kwargs b/c the init hook needs an initializer list
    def __init__(
        self,
        voltage_limits: RangeLike = RangeExpr.ALL,
        current_draw: RangeLike = RangeExpr.ZERO,
        reverse_voltage_out: RangeLike = RangeExpr.EMPTY,
        reverse_current_limits: RangeLike = RangeExpr.EMPTY,
    ):
        from .VoltagePorts import VoltageSink

        super().__init__()
        self.src = self.Port(Passive())
        self.dst = self.Port(
            VoltageSink(
                voltage_limits=voltage_limits,
                current_draw=current_draw,
                reverse_voltage_out=reverse_voltage_out,
                reverse_current_limits=reverse_current_limits,
            )
        )


class PassiveAdapterDigitalSource(CircuitPortAdapter["DigitalSource"]):
    # TODO we can't use **kwargs b/c the init hook needs an initializer list
    def __init__(
        self,
        voltage_out: RangeLike = RangeExpr.ZERO,
        current_limits: RangeLike = RangeExpr.ALL,
        output_thresholds: RangeLike = RangeExpr.ALL,
        pullup_capable: BoolLike = False,
        pulldown_capable: BoolLike = False,
        high_driver: BoolLike = True,
        low_driver: BoolLike = True,
        _bridged_internal: BoolLike = False,
    ):
        from .DigitalPorts import DigitalSource

        super().__init__()
        self.src = self.Port(Passive())
        self.dst = self.Port(
            DigitalSource(
                voltage_out=voltage_out,
                current_limits=current_limits,
                output_thresholds=output_thresholds,
                pullup_capable=pullup_capable,
                pulldown_capable=pulldown_capable,
                high_driver=high_driver,
                low_driver=low_driver,
                _bridged_internal=_bridged_internal,
            )
        )


class PassiveAdapterDigitalSink(CircuitPortAdapter["DigitalSink"]):
    # TODO we can't use **kwargs b/c the init hook needs an initializer list
    def __init__(
        self,
        voltage_limits: RangeLike = RangeExpr.ALL,
        current_draw: RangeLike = RangeExpr.ZERO,
        input_thresholds: RangeLike = RangeExpr.EMPTY,
        pullup_capable: BoolLike = False,
        pulldown_capable: BoolLike = False,
        _bridged_internal: BoolLike = False,
    ):
        from .DigitalPorts import DigitalSink

        super().__init__()
        self.src = self.Port(Passive())
        self.dst = self.Port(
            DigitalSink(
                voltage_limits=voltage_limits,
                current_draw=current_draw,
                input_thresholds=input_thresholds,
                pullup_capable=pullup_capable,
                pulldown_capable=pulldown_capable,
                _bridged_internal=_bridged_internal,
            )
        )


class PassiveAdapterDigitalBidir(CircuitPortAdapter["DigitalBidir"]):
    # TODO we can't use **kwargs b/c the init hook needs an initializer list
    def __init__(
        self,
        voltage_limits: RangeLike = RangeExpr.ALL,
        current_draw: RangeLike = RangeExpr.ZERO,
        voltage_out: RangeLike = RangeExpr.ZERO,
        current_limits: RangeLike = RangeExpr.ALL,
        input_thresholds: RangeLike = RangeExpr.EMPTY,
        output_thresholds: RangeLike = RangeExpr.ALL,
        *,
        pullup_capable: BoolLike = False,
        pulldown_capable: BoolLike = False,
        _bridged_internal: BoolLike = False,
    ):
        from .DigitalPorts import DigitalBidir

        super().__init__()
        self.src = self.Port(Passive())
        self.dst = self.Port(
            DigitalBidir(
                voltage_limits=voltage_limits,
                current_draw=current_draw,
                voltage_out=voltage_out,
                current_limits=current_limits,
                input_thresholds=input_thresholds,
                output_thresholds=output_thresholds,
                pullup_capable=pullup_capable,
                pulldown_capable=pulldown_capable,
                _bridged_internal=_bridged_internal,
            )
        )


class PassiveAdapterAnalogSource(KicadImportablePortAdapter["AnalogSource"]):
    # TODO we can't use **kwargs b/c the init hook needs an initializer list
    def __init__(
        self,
        voltage_out: RangeLike = RangeExpr.ZERO,
        signal_out: RangeLike = RangeExpr.ZERO,
        current_limits: RangeLike = RangeExpr.ALL,
        impedance: RangeLike = RangeExpr.ZERO,
    ):
        from .AnalogPort import AnalogSource

        super().__init__()
        self.src = self.Port(Passive())
        self.dst = self.Port(
            AnalogSource(
                voltage_out=voltage_out, signal_out=signal_out, current_limits=current_limits, impedance=impedance
            )
        )
        self.connect(self.src, self.dst.net)


class PassiveAdapterAnalogSink(KicadImportablePortAdapter["AnalogSink"]):
    # TODO we can't use **kwargs b/c the init hook needs an initializer list
    def __init__(
        self,
        voltage_limits: RangeLike = RangeExpr.ALL,
        signal_limits: RangeLike = RangeExpr.ALL,
        current_draw: RangeLike = RangeExpr.ZERO,
        impedance: RangeLike = RangeExpr.INF,
    ):
        from .AnalogPort import AnalogSink

        super().__init__()
        self.src = self.Port(Passive())
        self.dst = self.Port(
            AnalogSink(
                voltage_limits=voltage_limits,
                signal_limits=signal_limits,
                current_draw=current_draw,
                impedance=impedance,
            )
        )
        self.connect(self.src, self.dst.net)


class PassiveBridge(CircuitPortBridge):
    def __init__(self) -> None:
        super().__init__()
        self.outer_port = self.Port(Passive())
        self.inner_link = self.Port(Passive())


class HasPassivePort:
    """A port that contains a single net as a passive port.
    Some functionality may provide convenience functions on this to use the internal net."""

    def __init__(self) -> None:
        super().__init__()
        self.net: Passive


# TODO this should replace CircuitPort and should be the lowest level of abstraction port, #114
class Passive(CircuitPort[PassiveLink]):
    """Basic copper-only port, which can be adapted to a more strongly typed Voltage/Digital/Analog* port"""

    link_type = PassiveLink
    bridge_type = PassiveBridge

    AdaptTargetType = TypeVar("AdaptTargetType", bound=Union[CircuitPort, HasPassivePort])

    def adapt_to(self, that: AdaptTargetType) -> AdaptTargetType:
        from .GroundPort import Ground
        from .VoltagePorts import VoltageSource, VoltageSink
        from .DigitalPorts import DigitalSource, DigitalSink, DigitalBidir
        from .AnalogPort import AnalogSource, AnalogSink

        ADAPTER_TYPE_MAP: Dict[Type[Port], Type[PortAdapter]] = {
            Ground: PassiveAdapterGround,
            VoltageSource: PassiveAdapterVoltageSource,
            VoltageSink: PassiveAdapterVoltageSink,
            DigitalSink: PassiveAdapterDigitalSink,
            DigitalSource: PassiveAdapterDigitalSource,
            DigitalBidir: PassiveAdapterDigitalBidir,
            AnalogSink: PassiveAdapterAnalogSink,
            AnalogSource: PassiveAdapterAnalogSource,
        }

        # this is an experimental style that takes a port that has initializers but is not bound
        # and automatically creates an adapter from it, by matching the port parameter fields
        # with the adapter constructor argument fields by name
        assert isinstance(that, Port), "adapter target must be port"
        assert not that._is_bound(), "adapter target must be model only"
        assert that.__class__ in ADAPTER_TYPE_MAP, f"no adapter to {that.__class__}"
        adapter_cls = ADAPTER_TYPE_MAP[that.__class__]

        # map initializers from that to constructor args
        adapter_init_kwargs = {}  # make everything kwargs for simplicity
        for param_name, param in that._parameters.items():
            assert param.initializer is not None, f"missing initializer for {param_name}"
            adapter_init_kwargs[param_name] = param.initializer

        return self._convert(adapter_cls(**adapter_init_kwargs))  # type: ignore
