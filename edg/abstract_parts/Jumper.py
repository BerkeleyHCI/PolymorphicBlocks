from typing_extensions import override

from ..electronics_interfaces import *


@abstract_block
class Jumper(DiscreteComponent, Block):
    """A two-ported passive-typed jumper (a disconnect-able connection), though is treated
    as always connected for model purposes.

    Wrapping blocks can add typed port and parameter propagation semantics."""

    def __init__(self) -> None:
        super().__init__()
        self.a = self.Port(Passive())
        self.b = self.Port(Passive())


class GroundJumper(TypedJumper, Block):
    def __init__(self) -> None:
        super().__init__()
        self.input = self.Port(Ground(), [Input])
        self.output = self.Port(Ground(), [Output])

    @override
    def contents(self) -> None:
        super().contents()
        self.device = self.Block(Jumper())
        self.connect(self.input.net, self.device.a)
        self.connect(self.output.net, self.device.b)


class VoltageJumper(TypedJumper, Block):
    def __init__(self) -> None:
        super().__init__()
        self.input = self.Port(VoltageSink(current_draw=RangeExpr(), reverse_voltage_out=RangeExpr()), [Input])
        self.output = self.Port(
            VoltageSource(
                voltage_out=self.input.link().voltage, reverse_current_draw=self.input.link().reverse_current_draw
            ),
            [Output],
        )

    @override
    def contents(self) -> None:
        super().contents()
        self.device = self.Block(Jumper())
        self.assign(self.input.current_draw, self.output.link().current_draw)
        self.assign(self.input.reverse_voltage_out, self.output.link().reverse_voltage)
        self.connect(self.input.net, self.device.a)
        self.connect(self.output.net, self.device.b)


class DigitalJumper(TypedJumper, Block):
    def __init__(self) -> None:
        super().__init__()
        self.input = self.Port(DigitalSink(current_draw=RangeExpr()), [Input])
        self.output = self.Port(
            DigitalSource(voltage_out=self.input.link().voltage, output_thresholds=self.input.link().output_thresholds),
            [Output],
        )

    @override
    def contents(self) -> None:
        super().contents()
        self.device = self.Block(Jumper())
        self.assign(self.input.current_draw, self.output.link().current_draw)  # for model purposes, treat as connected
        self.connect(self.input.net, self.device.a)
        self.connect(self.output.net, self.device.b)
