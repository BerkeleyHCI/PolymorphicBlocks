from electronics_abstract_parts import *


class CustomBuckBoostConverter(DiscreteBoostConverter):
  """Custom buck-boost that has two PWM inputs for the input high and output low switches,
  with diodes for the complementary switches (non-synchronous)."""
  @init_in_parent
  def __init__(self, *args,
               pwm_frequency: RangeLike = (100, 1000)*kHertz,
               voltage_drop: RangeLike = (0, 1)*Volt, rds_on: RangeLike = (0, 1.0)*Ohm,
               **kwargs):
    super().__init__(*args, **kwargs)

    self.buck_pwm = self.Port(DigitalSink.empty())
    self.boost_pwm = self.Port(DigitalSink.empty())

    self.assign(self.frequency, pwm_frequency)
    self.voltage_drop = self.ArgParameter(voltage_drop)
    self.rds_on = self.ArgParameter(rds_on)

  def contents(self):
    super().contents()

    self.power_path = self.Block(BuckBoostConverterPowerPath(
      self.pwr_in.link().voltage, self.output_voltage, self.frequency,
      self.pwr_out.link().current_drawn, Range.all(),  # TODO model current limits from FETs
      inductor_current_ripple=self._calculate_ripple(self.pwr_out.link().current_drawn,
                                                     self.ripple_current_factor,
                                                     rated_current=self.pwr_out.link().current_drawn.upper())
    ))
    self.connect(self.power_path.pwr_in, self.pwr_in)
    self.connect(self.power_path.pwr_out, self.pwr_out)
    self.connect(self.power_path.gnd, self.gnd)
    self.in_high_switch = self.Block(HighSideSwitch(max_rds=self.rds_on.upper()))
    self.connect(self.in_high_switch.pwr, self.pwr_in)
    self.connect(self.in_high_switch.gnd, self.gnd)
    self.connect(self.in_high_switch.control, self.buck_pwm)
    self.in_low_diode = self.Block(Diode(
      reverse_voltage=self.pwr_in.link().voltage,
      current=self.power_path.switch_in.current_draw,
      voltage_drop=self.voltage_drop
    ))
    # TODO in high (buck) switch
    self.connect(self.gnd, self.in_low_diode.anode.adapt_to(Ground()))
    self.connect(self.power_path.switch_in,  # internal node not modeled, assumed specs correct
                 self.in_high_switch.output.as_voltage_source(),
                 self.in_low_diode.cathode.adapt_to(VoltageSink()))
    self.out_high_diode = self.Block(Diode(
      reverse_voltage=self.output_voltage,
      current=(0, self.power_path.inductor_spec_peak_current),
      voltage_drop=self.voltage_drop
    ))
    self.out_low_switch = self.Block(Fet.NFet(
      drain_voltage=self.output_voltage,
      drain_current=(0, self.power_path.inductor_spec_peak_current),
      gate_voltage=(self.boost_pwm.link().output_thresholds.upper(),
                    self.boost_pwm.link().voltage.upper()),
      rds_on=self.rds_on,
    ))
    self.connect(self.power_path.switch_out,  # internal node not modeled, assumed specs correct
                 self.out_high_diode.anode.adapt_to(VoltageSink()),
                 self.out_low_switch.drain.adapt_to(VoltageSink()))
    self.connect(self.boost_pwm, self.out_low_switch.gate.adapt_to(DigitalSink(
      # TODO model me
    )))
    self.connect(self.gnd, self.out_low_switch.source.adapt_to(Ground()))
    self.connect(self.pwr_out, self.out_high_diode.cathode.adapt_to(VoltageSource(
      voltage_out=self.output_voltage,  # assumed external controller regulates correctly
      # TODO derive current limits
    )))
