from typing import Any

from typing_extensions import override

from ..abstract_parts import *


class CustomSyncBuckConverterIndependent(DiscreteBoostConverter):
    """Custom synchronous buck with two PWM inputs for the high and low side gate drivers.
    Because of the MOSFET body diode, will probably be fine-ish if the low side FET is not driven."""

    def __init__(
        self,
        *args: Any,
        frequency: RangeLike = (100, 1000) * kHertz,
        ripple_ratio: RangeLike = (0.2, 0.5),
        voltage_drop: RangeLike = (0, 1) * Volt,
        rds_on: RangeLike = (0, 1.0) * Ohm,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.pwr_logic = self.Port(VoltageSink.empty())
        self.pwm_low = self.Port(DigitalSink.empty())
        self.pwm_high = self.Port(DigitalSink.empty())

        self.frequency = self.ArgParameter(frequency)
        self.ripple_ratio = self.ArgParameter(ripple_ratio)
        self.voltage_drop = self.ArgParameter(voltage_drop)
        self.rds_on = self.ArgParameter(rds_on)

    @override
    def contents(self) -> None:
        super().contents()

        self.assign(self.actual_frequency, self.frequency)
        self.power_path = self.Block(
            BuckConverterPowerPath(
                self.pwr_in.link().voltage,
                self.output_voltage,
                self.actual_frequency,
                self.pwr_out.link().current_drawn,
                Range.exact(0),
                input_voltage_ripple=self.input_ripple_limit,
                output_voltage_ripple=self.output_ripple_limit,
                ripple_ratio=self.ripple_ratio,
            )
        )
        self.connect(self.power_path.pwr_in, self.pwr_in)
        self.connect(self.power_path.gnd, self.gnd)

        self.sw = self.Block(FetHalfBridge(frequency=self.frequency, fet_rds=self.rds_on))
        self.connect(self.sw.gnd, self.gnd)
        (self.pwr_in_force,), _ = self.chain(  # use average current draw for boundary ports
            self.pwr_in, self.Block(ForcedVoltageCurrentDraw(self.power_path.switch.link().current_drawn)), self.sw.pwr
        )
        self.connect(self.sw.pwr_logic, self.pwr_logic)
        sw_ctl = self.sw.with_mixin(HalfBridgeIndependent())
        self.connect(sw_ctl.low_ctl, self.pwm_low)
        self.connect(sw_ctl.high_ctl, self.pwm_high)
        (self.sw_out_force,), _ = self.chain(
            self.sw.out,  # current draw used to size FETs, size for peak current
            self.Block(ForcedVoltageCurrentDraw(self.power_path.actual_inductor_current_peak)),
            self.power_path.switch,
        )
        (self.pwr_out_force,), _ = self.chain(
            self.power_path.pwr_out,
            self.Block(
                ForcedVoltageCurrentLimit(
                    self.power_path.pwr_out.current_limits.intersect(
                        self.sw.actual_current_limits - self.power_path.actual_inductor_current_ripple.upper() / 2
                    ).intersect(Range.from_lower(0))
                )
            ),
            self.pwr_out,
        )
