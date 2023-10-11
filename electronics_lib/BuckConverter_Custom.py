from electronics_abstract_parts import *


class CustomBuckConverter(DiscreteBoostConverter):
    """Custom buck with PWM inputs for the high side gate driver
    and diodes for the complementary switches (non-synchronous)."""
    @init_in_parent
    def __init__(self, *args,
                 pwm_frequency: RangeLike = (100, 1000)*kHertz,
                 voltage_drop: RangeLike = (0, 1)*Volt, rds_on: RangeLike = (0, 1.0)*Ohm,
                 **kwargs):
        super().__init__(*args, **kwargs)

        self.pwm = self.Port(DigitalSink.empty())

        self.assign(self.frequency, pwm_frequency)
        self.voltage_drop = self.ArgParameter(voltage_drop)
        self.rds_on = self.ArgParameter(rds_on)

    def contents(self):
        super().contents()

        self.power_path = self.Block(BuckConverterPowerPath(
            self.pwr_in.link().voltage, self.output_voltage, self.frequency,
            self.pwr_out.link().current_drawn, Range.all(),  # TODO model current limits from FETs
            inductor_current_ripple=self._calculate_ripple(self.pwr_out.link().current_drawn,
                                                           self.ripple_current_factor,
                                                           rated_current=self.pwr_out.link().current_drawn.upper()),
            input_voltage_ripple=self.input_ripple_limit,
            output_voltage_ripple=self.output_ripple_limit,
            dutycycle_limit=(0, 1)
        ))
        self.connect(self.power_path.pwr_in, self.pwr_in)
        self.connect(self.power_path.pwr_out, self.pwr_out)
        self.connect(self.power_path.gnd, self.gnd)

        self.in_high_switch = self.Block(HighSideSwitch(max_rds=self.rds_on.upper()))
        self.connect(self.in_high_switch.pwr, self.pwr_in)
        self.connect(self.in_high_switch.gnd, self.gnd)
        self.connect(self.in_high_switch.control, self.pwm)
        self.in_low_diode = self.Block(Diode(
            reverse_voltage=self.pwr_in.link().voltage,
            current=self.power_path.switch.current_draw,
            voltage_drop=self.voltage_drop
        ))
        # TODO in high (buck) switch
        self.connect(self.gnd, self.in_low_diode.anode.adapt_to(Ground()))
        self.connect(self.power_path.switch,  # internal node not modeled, assumed specs correct
                     self.in_high_switch.output.as_voltage_source(),
                     self.in_low_diode.cathode.adapt_to(VoltageSink()))
