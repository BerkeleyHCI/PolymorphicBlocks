from .DummyDevice import DummyDevice
from .VoltagePorts import VoltageSource, VoltageSink, Power
from ..core import RangeExpr, RangeLike, InOut


class DummyVoltageSource(DummyDevice):
    def __init__(self, voltage_out: RangeLike = RangeExpr.ZERO, current_limits: RangeLike = RangeExpr.ALL) -> None:
        super().__init__()

        self.pwr = self.Port(VoltageSource(voltage_out=voltage_out, current_limits=current_limits), [Power, InOut])

        self.current_drawn = self.Parameter(RangeExpr(self.pwr.link().current_drawn))
        self.voltage_limits = self.Parameter(RangeExpr(self.pwr.link().voltage_limits))


class DummyVoltageSink(DummyDevice):
    def __init__(self, voltage_limit: RangeLike = RangeExpr.ALL, current_draw: RangeLike = RangeExpr.ZERO) -> None:
        super().__init__()

        self.pwr = self.Port(VoltageSink(voltage_limits=voltage_limit, current_draw=current_draw), [Power, InOut])
        self.voltage = self.Parameter(RangeExpr(self.pwr.link().voltage))
        self.current_limits = self.Parameter(RangeExpr(self.pwr.link().current_limits))
