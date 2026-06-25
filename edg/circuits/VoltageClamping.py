from typing import Dict
from typing_extensions import override

from ..abstract_parts import *


class AnalogClampResistor(Protection, KiCadImportableBlock):
    """Inline resistor that limits the current (to a parameterized amount) which works in concert
    with ESD diodes in the downstream device to clamp the signal voltage to allowable levels.

    The protection voltage can be extended beyond the modeled range from the input signal,
    and can also be specified to allow zero output voltage (for when the downstream device
    is powered down)

    TODO: clamp_target should be inferred from the target voltage_limits,
    but voltage_limits doesn't always get propagated"""

    def __init__(
        self,
        clamp_target: RangeLike = (0, 3) * Volt,
        clamp_current: RangeLike = (0.25, 2.5) * mAmp,
        protection_voltage: RangeLike = (0, 0) * Volt,
        zero_out: BoolLike = False,
    ):
        super().__init__()

        self.clamp_target = self.ArgParameter(clamp_target)
        self.clamp_current = self.ArgParameter(clamp_current)
        self.protection_voltage = self.ArgParameter(protection_voltage)
        self.zero_out = self.ArgParameter(zero_out)

        self.signal_in = self.Port(AnalogSink(), [Input])
        self.signal_out = self.Port(
            AnalogSource(
                voltage=self.signal_in.link().voltage.intersect(self.clamp_target),
                signal=self.signal_in.link().signal,
                impedance=RangeExpr(),
            ),
            [Output],
        )

    @override
    def contents(self) -> None:
        super().contents()

        # TODO bidirectional clamping calcs?
        self.res = self.Block(
            Resistor(
                resistance=1
                / self.clamp_current
                * self.zero_out.then_else(
                    self.signal_in.link().voltage.hull(self.protection_voltage).upper(),
                    self.signal_in.link().voltage.hull(self.protection_voltage).upper() - self.clamp_target.upper(),
                )
            )
        )
        self.connect(self.res.a, self.signal_in.net)
        self.connect(self.res.b, self.signal_out.net)
        self.assign(self.signal_out.impedance, self.signal_in.link().source_impedance + self.res.actual_resistance)

    @override
    def symbol_pinning(self, symbol_name: str) -> Dict[str, Port]:
        assert symbol_name == "Device:R"
        return {"1": self.signal_in, "2": self.signal_out}


class DigitalClampResistor(Protection, KiCadImportableBlock):
    """Inline resistor that limits the current (to a parameterized amount) which works in concert
    with ESD diodes in the downstream device to clamp the signal voltage to allowable levels.

    The protection voltage can be extended beyond the modeled range from the input signal,
    and can also be specified to allow zero output voltage (for when the downstream device
    is powered down)

    TODO: clamp_target should be inferred from the target voltage_limits,
    but voltage_limits doesn't always get propagated."""

    def __init__(
        self,
        clamp_target: RangeLike = (0, 3) * Volt,
        clamp_current: RangeLike = (1.0, 10) * mAmp,
        protection_voltage: RangeLike = (0, 0) * Volt,
        zero_out: BoolLike = False,
    ):
        super().__init__()

        self.clamp_target = self.ArgParameter(clamp_target)
        self.clamp_current = self.ArgParameter(clamp_current)
        self.protection_voltage = self.ArgParameter(protection_voltage)
        self.zero_out = self.ArgParameter(zero_out)

        self.signal_in = self.Port(DigitalSink(current_draw=RangeExpr()), [Input])
        self.signal_out = self.Port(
            DigitalSource(
                voltage=self.signal_in.link().voltage.intersect(self.clamp_target),
                output_thresholds=self.signal_in.link().output_thresholds,
            ),
            [Output],
        )

    @override
    def contents(self) -> None:
        super().contents()

        # TODO bidirectional clamping calcs?
        self.assign(self.signal_in.current_draw, self.signal_out.link().current_draw)
        self.res = self.Block(
            Resistor(
                resistance=1
                / self.clamp_current
                * self.zero_out.then_else(
                    self.signal_in.link().voltage.hull(self.protection_voltage).upper(),
                    self.signal_in.link().voltage.hull(self.protection_voltage).upper() - self.clamp_target.upper(),
                )
            )
        )
        self.connect(self.res.a, self.signal_in.net)
        self.connect(self.res.b, self.signal_out.net)

    @override
    def symbol_pinning(self, symbol_name: str) -> Dict[str, Port]:
        assert symbol_name == "Device:R"
        return {"1": self.signal_in, "2": self.signal_out}
