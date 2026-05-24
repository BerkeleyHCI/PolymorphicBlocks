from typing_extensions import override

from ..abstract_parts import *
from ..abstract_parts.PartsTable import ExperimentalUserFnPartsTable
from .BuckConverterPowerPath import BuckConverterPowerPath
from .BoostConverterPowerPath import BoostConverterPowerPath


class BuckBoostConverterPowerPath(InternalSubcircuit, GeneratorBlock):
    """A helper block to generate the power path (inductors, capacitors) for a 4-switch buck-boost converter.

    Main assumptions in component sizing
    - Operating only in continuous mode, TODO: also consider boundary and discontinuous mode
    - TODO: account for capacitor ESR?

    Useful resources:
    https://www.ti.com/lit/an/slva535b/slva535b.pdf
      Largely based on this document, the tl;dr of which is combine the buck and boost equations
    """

    def __init__(
        self,
        input_voltage: RangeLike,
        output_voltage: RangeLike,
        frequency: RangeLike,
        output_current: RangeLike,
        sw_current_limits: RangeLike,
        *,
        efficiency: RangeLike = (0.8, 1.0),  # from TI reference
        input_voltage_ripple: FloatLike = 75 * mVolt,
        output_voltage_ripple: FloatLike = 25 * mVolt,  # arbitrary
        ripple_ratio: RangeLike = Range.all(),
    ):
        super().__init__()

        self.pwr_in = self.Port(VoltageSink.empty(), [Power])  # no modeling, input cap only
        self.switch_in = self.Port(VoltageSink.empty())  # models input / inductor avg. current draw
        self.switch_out = self.Port(VoltageSource.empty())  # models maximum output avg. current
        self.pwr_out = self.Port(VoltageSink.empty())  # no modeling, output cap only
        self.gnd = self.Port(Ground.empty(), [Common])

        self.input_voltage = self.ArgParameter(input_voltage)
        self.output_voltage = self.ArgParameter(output_voltage)
        self.frequency = self.ArgParameter(frequency)
        self.output_current = self.ArgParameter(output_current)
        self.sw_current_limits = self.ArgParameter(sw_current_limits)
        self.efficiency = self.ArgParameter(efficiency)
        self.input_voltage_ripple = self.ArgParameter(input_voltage_ripple)
        self.output_voltage_ripple = self.ArgParameter(output_voltage_ripple)
        self.ripple_ratio = self.ArgParameter(ripple_ratio)  # only used to force a ripple ratio at the actual currents

        # duty cycle limits not supported, since the crossover point has a dutycycle of 0 (boost) and 1 (buck)
        self.generator_param(
            self.input_voltage,
            self.output_voltage,
            self.frequency,
            self.output_current,
            self.sw_current_limits,
            self.input_voltage_ripple,
            self.output_voltage_ripple,
            self.efficiency,
            self.ripple_ratio,
        )

        self.actual_buck_dutycycle = self.Parameter(RangeExpr())  # possible actual duty cycle in buck mode
        self.actual_boost_dutycycle = self.Parameter(RangeExpr())  # possible actual duty cycle in boost mode
        self.actual_inductor_current_ripple = self.Parameter(RangeExpr())
        self.actual_inductor_current_peak = self.Parameter(
            RangeExpr()
        )  # inductor current accounting for ripple (upper is peak)

    @override
    def contents(self) -> None:
        super().contents()

        self.description = DescriptionString(
            "<b>duty cycle:</b> ",
            DescriptionString.FormatUnits(self.actual_buck_dutycycle, ""),
            " (buck)",
            ", ",
            DescriptionString.FormatUnits(self.actual_boost_dutycycle, ""),
            " (boost)\n",
            "<b>output current avg:</b> ",
            DescriptionString.FormatUnits(self.output_current, "A"),
            ", <b>ripple:</b> ",
            DescriptionString.FormatUnits(self.actual_inductor_current_ripple, "A"),
        )

    @override
    def generate(self) -> None:
        super().generate()
        buck_values = BuckConverterPowerPath._calculate_parameters(
            self.get(self.input_voltage),
            self.get(self.output_voltage),
            self.get(self.frequency),
            self.get(self.output_current),
            self.get(self.sw_current_limits),
            self.get(self.ripple_ratio),
            self.get(self.input_voltage_ripple),
            self.get(self.output_voltage_ripple),
            efficiency=self.get(self.efficiency),
            dutycycle_limit=Range(0, 1),
        )
        boost_values = BoostConverterPowerPath._calculate_parameters(
            self.get(self.input_voltage),
            self.get(self.output_voltage),
            self.get(self.frequency),
            self.get(self.output_current),
            self.get(self.sw_current_limits),
            self.get(self.ripple_ratio),
            self.get(self.input_voltage_ripple),
            self.get(self.output_voltage_ripple),
            efficiency=self.get(self.efficiency),
            dutycycle_limit=Range(0, 1),
        )
        self.assign(self.actual_buck_dutycycle, buck_values.effective_dutycycle)
        self.assign(self.actual_boost_dutycycle, boost_values.effective_dutycycle)

        combined_ripple_scale = max(buck_values.ripple_scale, boost_values.ripple_scale)
        combined_inductor_avg_current = buck_values.inductor_avg_current.hull(boost_values.inductor_avg_current)
        combined_min_ripple = max(buck_values.min_ripple, boost_values.min_ripple)

        self.inductor = self.Block(
            Inductor(
                inductance=buck_values.inductance.intersect(boost_values.inductance) * Henry,
                current=buck_values.inductor_avg_current.hull(boost_values.inductor_avg_current),
                frequency=self.frequency,
                experimental_filter_fn=ExperimentalUserFnPartsTable.serialize_fn(
                    BuckConverterPowerPath._buck_inductor_filter,
                    combined_inductor_avg_current.upper,
                    combined_ripple_scale,
                    combined_min_ripple,
                ),
            )
        )
        self.connect(self.switch_in, self.inductor.a.adapt_to(VoltageSink(current_draw=combined_inductor_avg_current)))
        self.connect(
            self.switch_out,
            self.inductor.b.adapt_to(
                VoltageSource(
                    voltage_out=self.output_voltage,
                    current_limits=BuckConverterPowerPath._ilim_expr(
                        self.inductor.actual_current_rating, self.sw_current_limits, self.actual_inductor_current_ripple
                    )
                    * (1 - boost_values.effective_dutycycle.upper),
                )
            ),
        )
        self.assign(self.actual_inductor_current_ripple, combined_ripple_scale / self.inductor.actual_inductance)
        self.assign(
            self.actual_inductor_current_peak, combined_inductor_avg_current + self.actual_inductor_current_ripple / 2
        )

        self.in_cap = self.Block(
            DecouplingCapacitor(
                capacitance=buck_values.input_capacitance.intersect(boost_values.input_capacitance) * Farad,
                exact_capacitance=True,
            )
        ).connected(self.gnd, self.pwr_in)
        self.out_cap = self.Block(
            DecouplingCapacitor(
                capacitance=(Range.exact(float("inf")) * Farad).hull(
                    (buck_values.output_capacitance_scale * self.actual_inductor_current_ripple.upper()).max(
                        boost_values.output_capacitance.lower
                    )
                ),
                exact_capacitance=True,
            )
        ).connected(self.gnd, self.pwr_out)
