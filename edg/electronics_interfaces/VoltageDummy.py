import warnings
from typing import Any

from ..electronics_model import *
from .DummyDevices import BaseDummyBlock
from .VoltagePorts import VoltageSource, VoltageSink, Power, VoltageLink


class DummyVoltageSource(BaseDummyBlock[VoltageLink]):
    def __init__(
        self,
        voltage_out: RangeLike = RangeExpr.ZERO,
        current_limits: RangeLike = RangeExpr.ALL,
        reverse_voltage_limits: RangeLike = RangeExpr.EMPTY,
        reverse_current_draw: RangeLike = RangeExpr.EMPTY,
    ) -> None:
        super().__init__()

        self.io: VoltageSource = self.Port(
            VoltageSource(
                voltage_out=voltage_out,
                current_limits=current_limits,
                reverse_voltage_limits=reverse_voltage_limits,
                reverse_current_draw=reverse_current_draw,
            ),
            [Power, InOut],
        )

        self.current_drawn = self.Parameter(RangeExpr(self.io.link().current_drawn))
        self.voltage_limits = self.Parameter(RangeExpr(self.io.link().voltage_limits))
        self.reverse_voltage = self.Parameter(RangeExpr(self.io.link().reverse_voltage))

    def __getattr__(self, item: str) -> Any:
        if item == "pwr":
            warnings.warn(
                f"DummyVoltageSource.pwr is deprecated, use .io instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            return self.io
        else:
            raise AttributeError(
                item
            )  # ideally we'd use super().__getattr__(...), but that's not defined in base classes


class DummyVoltageSink(BaseDummyBlock[VoltageLink]):

    def __init__(
        self,
        voltage_limit: RangeLike = RangeExpr.ALL,
        current_draw: RangeLike = RangeExpr.ZERO,
        reverse_voltage_out: RangeLike = RangeExpr.EMPTY,
        reverse_current_limits: RangeLike = RangeExpr.EMPTY,
    ) -> None:
        super().__init__()

        self.io: VoltageSink = self.Port(
            VoltageSink(
                voltage_limits=voltage_limit,
                current_draw=current_draw,
                reverse_voltage_out=reverse_voltage_out,
                reverse_current_limits=reverse_current_limits,
            ),
            [Power, InOut],
        )

        self.voltage = self.Parameter(RangeExpr(self.io.link().voltage))
        self.current_limits = self.Parameter(RangeExpr(self.io.link().current_limits))

    def __getattr__(self, item: str) -> Any:
        if item == "pwr":
            warnings.warn(
                f"DummyVoltageSink.pwr is deprecated, use .io instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            return self.io
        else:
            raise AttributeError(
                item
            )  # ideally we'd use super().__getattr__(...), but that's not defined in base classes
