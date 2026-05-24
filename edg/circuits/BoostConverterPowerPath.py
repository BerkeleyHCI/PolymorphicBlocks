from typing import NamedTuple
from typing_extensions import override

from ..abstract_parts import *
from ..abstract_parts.PartsTable import ExperimentalUserFnPartsTable
from .BuckConverterPowerPath import BuckConverterPowerPath


class BoostConverterPowerPath(InternalSubcircuit, GeneratorBlock):
    """A helper block to generate the power path (inductors, capacitors) for a synchronous boost converter.

    Useful resources:
    https://www.ti.com/lit/an/slva372c/slva372c.pdf
      Component sizing in continuous mode
    http://www.simonbramble.co.uk/dc_dc_converter_design/boost_converter/boost_converter_design.htm
      Detailed analysis of converter with discrete FET and diode
    """

    class Values(NamedTuple):
        dutycycle: Range
        inductance: Range
        input_capacitance: Range
        output_capacitance: Range

        inductor_avg_current: Range
        ripple_scale: float  # divide this by inductance to get the inductor ripple current
        min_ripple: float  # fallback minimum ripple current for component sizing for light-load, may be 0

        inductor_peak_currents: Range  # based on the worst case input spec, for unit testing
        effective_dutycycle: Range

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
        efficiency: Range = Range(0.8, 1.0),
        dutycycle_limit: Range = Range(0.1, 0.9),
        limit_ripple_ratio: Range = Range(0.1, 0.5),
    ) -> "BoostConverterPowerPath.Values":
        """See BuckConverterPowerPath._calculate_parameters, this performs a similar function."""
        dutycycle = 1 - input_voltage / output_voltage * efficiency
        effective_dutycycle = dutycycle.bound_to(dutycycle_limit)  # account for tracking behavior
        inductor_avg_current = output_current / (1 - effective_dutycycle)

        # calculate minimum inductance based on worst case values (operating range corners producing maximum inductance)
        # worst-case input/output voltages and frequency is used to avoid double-counting tolerances as ranges
        # note, for boost converter, L = Vin * D / (f * Iripple) = Vin (Vout - Vin) / (Iripple * f * Vout)
        # this is at a maximum at Vout,max, and on that curve with a critical point at Vin = Vout,max / 2
        inductance_scale_candidates = [
            input_voltage.lower * (output_voltage.upper - input_voltage.lower) / output_voltage.upper,
            input_voltage.upper * (output_voltage.upper - input_voltage.upper) / output_voltage.upper,
        ]
        if output_voltage.upper / 2 in input_voltage:
            inductance_scale_candidates.append(
                output_voltage.upper / 2 * (output_voltage.upper - output_voltage.upper / 2) / output_voltage.upper
            )
        inductance_scale = max(inductance_scale_candidates) / frequency.lower

        inductance = Range.all()
        min_ripple = 0.0
        if sw_current_limits.upper > 0:  # fallback for light-load
            ripple_current = BuckConverterPowerPath._ripple_current_from_sw_current(
                sw_current_limits.upper, limit_ripple_ratio
            )
            inductance = inductance.intersect(inductance_scale / ripple_current)
            min_ripple = ripple_current.lower
        if ripple_ratio.upper < float("inf"):
            assert ripple_ratio.lower > 0, f"invalid non-inf ripple ratio {ripple_ratio}"
            inductance = inductance.intersect(inductance_scale / (inductor_avg_current.upper * ripple_ratio))
        assert inductance.upper < float("inf"), "neither ripple_ratio nor fallback sw_current_limits given"

        inductor_current_ripple = inductor_avg_current * ripple_ratio.intersect(limit_ripple_ratio)
        inductor_peak_currents = Range(
            max(0, inductor_current_ripple.lower - inductor_current_ripple.upper / 2),
            max(inductor_avg_current.upper + inductor_current_ripple.upper / 2, inductor_current_ripple.upper),
        )

        # Capacitor equation Q = CV => i = C dv/dt => for constant current, i * t = C dV => dV = i * t / C
        # C = i * t / dV => C = i / (f * dV)
        # Boost converter draws current from input throughout the entire cycle, and by conversation of power
        # the average input current is Iin = Vout/Vin * Iout = 1/(1-D) * Iout
        # Boost converter current should be much less spikey than buck converter current and probably
        # less filtering than this is acceptable
        input_capacitance = Range.from_lower(
            (output_current.upper / (1 - effective_dutycycle.upper)) / (frequency.lower * input_voltage_ripple)
        )
        output_capacitance = Range.from_lower(
            output_current.upper * effective_dutycycle.upper / (frequency.lower * output_voltage_ripple)
        )

        return cls.Values(
            dutycycle=dutycycle,
            inductance=inductance,
            input_capacitance=input_capacitance,
            output_capacitance=output_capacitance,
            inductor_avg_current=inductor_avg_current,
            ripple_scale=inductance_scale,
            min_ripple=min_ripple,
            inductor_peak_currents=inductor_peak_currents,
            effective_dutycycle=effective_dutycycle,
        )

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
        efficiency: RangeLike = (0.8, 1.0),  # from TI reference
        dutycycle_limit: RangeLike = (0.1, 0.9),  # arbitrary
        ripple_ratio: RangeLike = Range.all(),
    ):
        super().__init__()

        self.pwr_in = self.Port(VoltageSink.empty(), [Power])  # models input / inductor avg. current draw
        self.pwr_out = self.Port(VoltageSink.empty())  # no modeling, output cap only
        self.switch = self.Port(VoltageSource.empty())  # models maximum output avg. current
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
                    BuckConverterPowerPath._buck_inductor_filter,
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

        self.connect(self.pwr_in, self.inductor.a.adapt_to(VoltageSink(current_draw=values.inductor_avg_current)))
        self.connect(
            self.switch,
            self.inductor.b.adapt_to(
                VoltageSource(
                    voltage_out=self.output_voltage,
                    current_limits=BuckConverterPowerPath._ilim_expr(
                        self.inductor.actual_current_rating, self.sw_current_limits, self.actual_inductor_current_ripple
                    )
                    * (1 - values.effective_dutycycle.upper),
                )
            ),
        )

        self.in_cap = self.Block(
            DecouplingCapacitor(capacitance=values.input_capacitance * Farad, exact_capacitance=True)
        ).connected(self.gnd, self.pwr_in)

        self.out_cap = self.Block(
            DecouplingCapacitor(capacitance=values.output_capacitance * Farad, exact_capacitance=True)
        ).connected(self.gnd, self.pwr_out)
