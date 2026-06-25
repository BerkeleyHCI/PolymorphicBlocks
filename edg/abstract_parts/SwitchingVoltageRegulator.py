from typing import Any, Optional

from deprecated import deprecated
from typing_extensions import override

from ..electronics_interfaces import *
from .VoltageRegulator import VoltageRegulator, IdealVoltageRegulator
from .Resettable import Resettable


@abstract_block
class SwitchingVoltageRegulator(VoltageRegulator):
    @staticmethod
    @deprecated("ripple calculation moved into the power-path block itself")
    def _calculate_ripple(
        output_current: RangeLike, ripple_ratio: RangeLike, *, rated_current: Optional[FloatLike] = None
    ) -> RangeExpr:
        """
        Calculates the target inductor ripple current (with parameters - concrete values not necessary)
        given the output current draw, and optionally a non-default ripple ratio and rated current.

        In general, ripple current largely trades off inductor maximum current and inductance.

        The default ripple ratio is an expansion of the heuristic 0.3-0.4 to account for tolerancing.
        the rated current is used to set a reasonable ceiling for ripple current, when the actual current
        is very low. Per the LMR33630 datasheet, the device's rated current should be used in these cases.
        """
        output_current_range = RangeExpr._to_expr_type(output_current)
        ripple_ratio_range = RangeExpr._to_expr_type(ripple_ratio)
        upper_ripple_limit = ripple_ratio_range.upper() * output_current_range.upper()
        if rated_current is not None:  # if rated current is specified, extend the upper limit for small current draws
            # this fallback limit is an arbitrary and low 0.2, not tied to specified ripple ratio since
            # it leads to unintuitive behavior where as the low bound increases (range shrinks) the inductance
            # spec actually becomes larger
            upper_ripple_limit = upper_ripple_limit.max(0.2 * rated_current)
        return RangeExpr._to_expr_type((ripple_ratio_range.lower() * output_current_range.upper(), upper_ripple_limit))

    def __init__(
        self,
        *args: Any,
        input_ripple_limit: FloatLike = 75 * mVolt,
        output_ripple_limit: FloatLike = 25 * mVolt,
        **kwargs: Any,
    ) -> None:
        """https://www.ti.com/lit/an/slta055/slta055.pdf: recommends 75mV for maximum peak-peak ripple voltage"""
        super().__init__(*args, **kwargs)

        self.input_ripple_limit = self.ArgParameter(input_ripple_limit)
        self.output_ripple_limit = self.ArgParameter(output_ripple_limit)

        self.actual_frequency = self.Parameter(RangeExpr())


@abstract_block_default(lambda: IdealBuckConverter)
class BuckConverter(SwitchingVoltageRegulator):
    """Step-down switching converter"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.require(self.pwr_out.voltage.upper() <= self.pwr_in.voltage_limits.upper())


@abstract_block_default(lambda: IdealBuckConverter)
class DiscreteBuckConverter(BuckConverter):
    """Category for discrete buck converter subcircuits (as opposed to integrated components)"""


class IdealBuckConverter(Resettable, DiscreteBuckConverter, IdealModel):
    """Ideal buck converter producing the spec output voltage (buck-boost) limited by input voltage
    and drawing input current from conversation of power"""

    @override
    def contents(self) -> None:
        super().contents()
        effective_output_voltage = self.output_voltage.intersect((0, self.pwr_in.link().voltage.upper()))
        self.gnd.init_from(Ground())
        self.pwr_in.init_from(
            VoltageSink(
                current_draw=effective_output_voltage / self.pwr_in.link().voltage * self.pwr_out.link().current_draw
            )
        )
        self.pwr_out.init_from(VoltageSource(voltage=effective_output_voltage))
        self.reset.init_from(DigitalSink())


@abstract_block_default(lambda: IdealBoostConverter)
class BoostConverter(SwitchingVoltageRegulator):
    """Step-up switching converter"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.require(self.pwr_out.voltage.lower() >= self.pwr_in.voltage_limits.lower())


@abstract_block_default(lambda: IdealBoostConverter)
class DiscreteBoostConverter(BoostConverter):
    """Category for discrete boost converter subcircuits (as opposed to integrated components)"""


class IdealBoostConverter(Resettable, DiscreteBoostConverter, IdealModel):
    """Ideal boost converter producing the spec output voltage (buck-boost) limited by input voltage
    and drawing input current from conversation of power"""

    @override
    def contents(self) -> None:
        super().contents()
        effective_output_voltage = self.output_voltage.intersect((self.pwr_in.link().voltage.lower(), float("inf")))
        self.gnd.init_from(Ground())
        self.pwr_in.init_from(
            VoltageSink(
                current_draw=effective_output_voltage / self.pwr_in.link().voltage * self.pwr_out.link().current_draw
            )
        )
        self.pwr_out.init_from(VoltageSource(voltage=effective_output_voltage))
        self.reset.init_from(DigitalSink())


@abstract_block_default(lambda: BuckBoostConverter)
class BuckBoostConverter(SwitchingVoltageRegulator):
    """Step-up or switch-down switching converter"""


class IdealBuckBoostConverter(IdealVoltageRegulator, BuckBoostConverter):
    pass


class DiscreteBuckBoostConverter(BuckBoostConverter):
    """Category for discrete buck-boost converter subcircuits (as opposed to integrated components)"""
