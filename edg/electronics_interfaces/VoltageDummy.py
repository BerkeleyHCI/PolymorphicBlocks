from deprecated import deprecated

from ..electronics_model import *
from .DummyDevices import BaseDummyBlock
from .VoltagePorts import VoltageSource, VoltageSink, Power, VoltageLink


class DummyVoltageSource(BaseDummyBlock[VoltageLink]):
    def __init__(
        self,
        voltage: RangeLike = RangeExpr.ZERO,
        current_limits: RangeLike = RangeExpr.ALL,
        reverse_voltage_limits: RangeLike = RangeExpr.EMPTY,
        reverse_current_draw: RangeLike = RangeExpr.EMPTY,
    ) -> None:
        super().__init__()

        self.io: VoltageSource = self.Port(
            VoltageSource(
                voltage=voltage,
                current_limits=current_limits,
                reverse_voltage_limits=reverse_voltage_limits,
                reverse_current_draw=reverse_current_draw,
            ),
            [Power, InOut],
        )

        self.current_draw = self.Parameter(RangeExpr(self.io.link().current_draw))
        self.voltage_limits = self.Parameter(RangeExpr(self.io.link().voltage_limits))
        self.reverse_voltage = self.Parameter(RangeExpr(self.io.link().reverse_voltage))

    @property
    @deprecated(f"DummyVoltageSource.pwr is deprecated, use .io instead.")
    def pwr(self) -> VoltageSource:
        return self.io

    @property
    @deprecated(f"Use current_draw")
    def current_drawn(self) -> RangeExpr:
        return self.current_draw


class DummyVoltageSink(BaseDummyBlock[VoltageLink]):

    def __init__(
        self,
        voltage_limit: RangeLike = RangeExpr.ALL,
        current_draw: RangeLike = RangeExpr.ZERO,
        reverse_voltage: RangeLike = RangeExpr.EMPTY,
        reverse_current_limits: RangeLike = RangeExpr.EMPTY,
    ) -> None:
        super().__init__()

        self.io: VoltageSink = self.Port(
            VoltageSink(
                voltage_limits=voltage_limit,
                current_draw=current_draw,
                reverse_voltage=reverse_voltage,
                reverse_current_limits=reverse_current_limits,
            ),
            [Power, InOut],
        )

        self.voltage = self.Parameter(RangeExpr(self.io.link().voltage))
        self.current_limits = self.Parameter(RangeExpr(self.io.link().current_limits))

    @property
    @deprecated(f"DummyVoltageSink.pwr is deprecated, use .io instead.")
    def pwr(self) -> VoltageSink:
        return self.io
