from typing import NamedTuple, Callable
from typing_extensions import override

from ..abstract_parts import *
from ..abstract_parts.PartsTable import PartsTableRow, ExperimentalUserFnPartsTable


class BuckConverterPowerPath(InternalSubcircuit, GeneratorBlock):
    """A helper block to generate the power path (inductors, capacitors) for a switching buck converter.

    Useful resources:
    https://www.ti.com/lit/an/slva477b/slva477b.pdf
      Component sizing in continuous mode
    http://www.onmyphd.com/?p=voltage.regulators.buck.step.down.converter
      Very detailed analysis including component sizing, operating modes, calculating losses
    """

    @staticmethod
    def _d_inverse_d(d_range: Range) -> Range:
        """Some power calculations require the maximum of D*(1-D), which has a maximum at D=0.5"""
        # can't use range ops since they will double-count the tolerance of D, so calculate endpoints separately
        range_endpoints = [d_range.lower * (1 - d_range.lower), d_range.upper * (1 - d_range.upper)]
        raw_range = Range(min(range_endpoints), max(range_endpoints))
        if 0.5 in d_range:  # the function has a maximum at 0.5
            return raw_range.hull(Range.exact(0.5 * (1 - 0.5)))
        else:
            return raw_range

    @staticmethod
    def _ripple_current_from_sw_current(sw_current: float, ripple_ratio: Range) -> Range:
        """Calculates the ripple current from a total switch current and ripple ratio."""
        return Range(  # separate range parts to avoid double-counting tolerances
            sw_current / (1 + ripple_ratio.lower) * ripple_ratio.lower,
            sw_current / (1 + ripple_ratio.upper) * ripple_ratio.upper,
        )

    class Values(NamedTuple):
        dutycycle: Range
        inductance: Range
        input_capacitance: Range
        output_capacitance: Range

        inductor_avg_current: Range
        ripple_scale: float  # divide this by inductance to get the inductor ripple current
        min_ripple: float  # fallback minimum ripple current for component sizing for light-load, may be 0
        output_capacitance_scale: float  # multiply inductor ripple by this to get required output capacitance

        inductor_peak_currents: Range  # based on the worst case input spec, for unit testing
        effective_dutycycle: Range  # duty cycle adjusted for tracking behavior

    @classmethod
    def _calculate_parameters(
        cls,
        input_voltage: Range,
        output_voltage: Range,
        frequency: Range,
        output_current: Range,
        sw_current_limits: Range,
        ripple_ratio: Range,
        input_voltage_ripple: float,
        output_voltage_ripple: float,
        efficiency: Range = Range(0.9, 1.0),
        dutycycle_limit: Range = Range(0.1, 0.9),
        limit_ripple_ratio: Range = Range(0.1, 0.5),
    ) -> "BuckConverterPowerPath.Values":
        """Calculates parameters for the buck converter power path.

        This uses the continuous conduction mode (CCM) equations to calculate component sizes.
        DCM is not explicitly calculated since it requires additional parameters like minimum on-time.
        The limit_ripple_ratio provides some broadly sane values for light-load / DCM operation.
        This also ignores higher-order component behavior like capacitor ESR.

        The ripple_ratio is optional and may be set to Range.all(), allowing the inductor selector
        to optimize the inductor by trading off inductance and max current.

        Values for component selections are bounded by:
        - the ripple_ratio at output_current (if ripple_ratio < inf), and
        - the limit_ripple_ratio at sw_current_limits (if sw_current_limits is not zero), as a fallback
          for light-load conditions (where otherwise current goes to zero and inductance goes to the moon)
        """
        dutycycle = output_voltage / input_voltage / efficiency
        effective_dutycycle = dutycycle.bound_to(dutycycle_limit)  # account for tracking behavior

        # calculate minimum inductance based on worst case values (operating range corners producing maximum inductance)
        # worst-case input/output voltages and frequency is used to avoid double-counting tolerances as ranges
        # note, for buck converter, L = (Vin - Vout) * D / (f * Iripple) = Vout (Vin - Vout) / (Iripple * f * Vin)
        # this is at a maximum at Vin,max, and on that curve with a critical point at Vout = Vin,max / 2
        # note, the same formula calculates ripple-from-inductance and inductance-from-ripple
        inductance_scale_candidates = [
            output_voltage.lower * (input_voltage.upper - output_voltage.lower) / input_voltage.upper,
            output_voltage.upper * (input_voltage.upper - output_voltage.upper) / input_voltage.upper,
        ]
        if input_voltage.upper / 2 in output_voltage:
            inductance_scale_candidates.append(
                input_voltage.upper / 2 * (input_voltage.upper - input_voltage.upper / 2) / input_voltage.upper
            )
        inductance_scale = max(inductance_scale_candidates) / frequency.lower

        inductance = Range.all()
        min_ripple = 0.0
        if sw_current_limits.upper > 0:  # fallback for light-load
            ripple_current = cls._ripple_current_from_sw_current(sw_current_limits.upper, limit_ripple_ratio)
            inductance = inductance.intersect(inductance_scale / ripple_current)
            min_ripple = ripple_current.lower
        if ripple_ratio.upper < float("inf"):
            assert ripple_ratio.lower > 0, f"invalid non-inf ripple ratio {ripple_ratio}"

            inductance = inductance.intersect(inductance_scale / (output_current.upper * ripple_ratio))
        assert inductance.upper < float("inf"), "neither ripple_ratio nor fallback sw_current_limits given"

        input_capacitance = Range.from_lower(
            output_current.upper
            * cls._d_inverse_d(effective_dutycycle).upper
            / (frequency.lower * input_voltage_ripple)
        )
        output_capacitance_scale = 1 / (8 * frequency.lower * output_voltage_ripple)

        # these are static worst-case estimates for the range of specified ripple currents
        # mainly used for unit testing
        inductor_current_ripple = output_current * ripple_ratio.intersect(limit_ripple_ratio)
        inductor_peak_currents = Range(
            max(0, output_current.lower - inductor_current_ripple.upper / 2),
            max(output_current.upper + inductor_current_ripple.upper / 2, inductor_current_ripple.upper),
        )
        output_capacitance = Range.from_lower(output_capacitance_scale * inductor_current_ripple.upper)

        return cls.Values(
            dutycycle=dutycycle,
            inductance=inductance,
            input_capacitance=input_capacitance,
            output_capacitance=output_capacitance,
            inductor_avg_current=output_current / efficiency,
            ripple_scale=inductance_scale,
            min_ripple=min_ripple,
            output_capacitance_scale=output_capacitance_scale,
            inductor_peak_currents=inductor_peak_currents,
            effective_dutycycle=effective_dutycycle,
        )

    @staticmethod
    @ExperimentalUserFnPartsTable.user_fn([float, float, float])
    def _buck_inductor_filter(
        max_avg_current: float, ripple_scale: float, min_ripple: float
    ) -> Callable[[PartsTableRow], bool]:
        """Applies further filtering to inductors using the trade-off between inductance and peak-peak current.
        max_avg_current is the maximum average current (not accounting for ripple) seen by the inductor
        ripple_scale is the scaling factor from 1/L to ripple
        This structure also works for boost converters, which would have its ripple_scale calculated differently."""

        def filter_fn(row: PartsTableRow) -> bool:
            ripple_current = max(ripple_scale / row[TableInductor.INDUCTANCE].lower, min_ripple)
            max_current_pp = max_avg_current + ripple_current / 2
            return max_current_pp in row[TableInductor.CURRENT_RATING]

        return filter_fn

    @staticmethod
    def _ilim_expr(inductor_ilim: RangeExpr, sw_ilim: RangeExpr, inductor_iripple: RangeExpr) -> RangeExpr:
        """Returns the average current limit, as an expression, derived from the inductor and switch (instantaneous)
        current limits."""
        iout_limit_inductor = inductor_ilim - (inductor_iripple.upper() / 2)
        iout_limit_sw = (sw_ilim.upper() > 0).then_else(sw_ilim - (inductor_iripple.upper() / 2), Range.all())
        return iout_limit_inductor.intersect(iout_limit_sw).intersect(Range.from_lower(0))

    def __init__(
        self,
        input_voltage: RangeLike,
        output_voltage: RangeLike,
        frequency: RangeLike,
        output_current: RangeLike,
        sw_current_limits: RangeLike,
        *,
        input_voltage_ripple: FloatLike,
        output_voltage_ripple: FloatLike,
        efficiency: RangeLike = (0.9, 1.0),  # from TI reference
        dutycycle_limit: RangeLike = (0.1, 0.9),
        ripple_ratio: RangeLike = Range.all(),
    ):
        super().__init__()

        self.pwr_in = self.Port(VoltageSink.empty(), [Power])  # no modeling, input cap only
        self.pwr_out = self.Port(VoltageSource.empty())  # models max output avg. current
        # technically VoltageSink is the wrong model, but this is used to pass the current draw to the chip
        # (and its input pin) without need the top-level to explicitly pass a parameter to the chip
        self.switch = self.Port(VoltageSink.empty())  # models input / inductor avg. current draw
        self.gnd = self.Port(Ground.empty(), [Common])

        self.input_voltage = self.ArgParameter(input_voltage)
        self.output_voltage = self.ArgParameter(output_voltage)
        self.frequency = self.ArgParameter(frequency)
        self.output_current = self.ArgParameter(output_current)
        self.sw_current_limits = self.ArgParameter(sw_current_limits)

        self.efficiency = self.ArgParameter(efficiency)
        self.input_voltage_ripple = self.ArgParameter(input_voltage_ripple)
        self.output_voltage_ripple = self.ArgParameter(output_voltage_ripple)
        self.dutycycle_limit = self.ArgParameter(dutycycle_limit)
        self.ripple_ratio = self.ArgParameter(ripple_ratio)  # only used to force a ripple ratio at the actual currents

        self.generator_param(
            self.input_voltage,
            self.output_voltage,
            self.frequency,
            self.output_current,
            self.sw_current_limits,
            self.input_voltage_ripple,
            self.output_voltage_ripple,
            self.efficiency,
            self.dutycycle_limit,
            self.ripple_ratio,
        )

        self.actual_dutycycle = self.Parameter(RangeExpr())
        self.actual_inductor_current_ripple = self.Parameter(RangeExpr())
        self.actual_inductor_current_peak = self.Parameter(RangeExpr())

    @override
    def contents(self) -> None:
        super().contents()

        self.description = DescriptionString(
            "<b>duty cycle:</b> ",
            DescriptionString.FormatUnits(self.actual_dutycycle, ""),
            " <b>of limits:</b> ",
            DescriptionString.FormatUnits(self.dutycycle_limit, ""),
            "\n",
            "<b>output current avg:</b> ",
            DescriptionString.FormatUnits(self.output_current, "A"),
            ", <b>ripple:</b> ",
            DescriptionString.FormatUnits(self.actual_inductor_current_ripple, "A"),
        )

    @override
    def generate(self) -> None:
        super().generate()
        values = self._calculate_parameters(
            self.get(self.input_voltage),
            self.get(self.output_voltage),
            self.get(self.frequency),
            self.get(self.output_current),
            self.get(self.sw_current_limits),
            self.get(self.ripple_ratio),
            self.get(self.input_voltage_ripple),
            self.get(self.output_voltage_ripple),
            efficiency=self.get(self.efficiency),
            dutycycle_limit=self.get(self.dutycycle_limit),
        )
        self.assign(self.actual_dutycycle, values.dutycycle)
        self.require(values.dutycycle == values.effective_dutycycle, "dutycycle outside limit")

        self.inductor = self.Block(
            Inductor(
                inductance=values.inductance * Henry,
                current=values.inductor_avg_current,  # min-bound only, the real filter happens in the filter_fn
                frequency=self.frequency,
                experimental_filter_fn=ExperimentalUserFnPartsTable.serialize_fn(
                    self._buck_inductor_filter,
                    values.inductor_avg_current.upper,
                    values.ripple_scale,
                    values.min_ripple,
                ),
            )
        )
        self.assign(self.actual_inductor_current_ripple, values.ripple_scale / self.inductor.actual_inductance)
        self.assign(
            self.actual_inductor_current_peak, values.inductor_avg_current + self.actual_inductor_current_ripple / 2
        )

        self.connect(
            self.switch,
            self.inductor.a.adapt_to(VoltageSink(current_draw=self.output_current * values.effective_dutycycle)),
        )
        self.connect(
            self.pwr_out,
            self.inductor.b.adapt_to(
                VoltageSource(
                    voltage=self.output_voltage,
                    current_limits=self._ilim_expr(
                        self.inductor.actual_current_rating, self.sw_current_limits, self.actual_inductor_current_ripple
                    )
                    * self.efficiency,
                )
            ),
        )

        self.in_cap = self.Block(
            DecouplingCapacitor(capacitance=values.input_capacitance * Farad, exact_capacitance=True)
        ).connected(self.gnd, self.pwr_in)
        self.out_cap = self.Block(
            DecouplingCapacitor(
                capacitance=(Range.exact(float("inf")) * Farad).hull(
                    (
                        values.output_capacitance_scale
                        * self.actual_inductor_current_ripple.upper().max(values.min_ripple)
                    )
                ),
                exact_capacitance=True,
            )
        ).connected(self.gnd, self.pwr_out)
