from electronics_abstract_parts import *


# These adapters are needed to properly orient the boost-side switch, since it outputs on the high side
# and inputs in the center
class VoltageSinkConnector(DummyDevice, NetBlock):
  """Connects two voltage sinks together (FET top sink to exterior source)."""
  @init_in_parent
  def __init__(self, voltage_out: RangeLike, current_limits: RangeLike) -> None:
    super().__init__()
    self.a = self.Port(VoltageSource(
      voltage_out=voltage_out,
      current_limits=(0, 0)*Amp  # should not be used
    ), [Input])  # FET top: set output voltage
    self.b = self.Port(VoltageSource(
      voltage_out=voltage_out,
      current_limits=current_limits
    ), [Output])  # exterior source: set output voltage + Ilim


class CustomSyncBuckBoostConverter(DiscreteBoostConverter):
  """Custom synchronous buck-boost with four PWMs for the switches.
  Because of the MOSFET body diode, will probably be fine-ish if the buck low-side FET and the boost high-side FET
  are not driven"""
  @init_in_parent
  def __init__(self, *args,
               frequency: RangeLike = (100, 1000)*kHertz,
               voltage_drop: RangeLike = (0, 1)*Volt, rds_on: RangeLike = (0, 1.0)*Ohm,
               **kwargs):
    super().__init__(*args, **kwargs)

    self.pwr_logic = self.Port(VoltageSink.empty())
    self.buck_pwm_low = self.Port(DigitalSink.empty())
    self.buck_pwm_high = self.Port(DigitalSink.empty())
    self.boost_pwm_low = self.Port(DigitalSink.empty())
    self.boost_pwm_high = self.Port(DigitalSink.empty())

    self.frequency = self.ArgParameter(frequency)
    self.voltage_drop = self.ArgParameter(voltage_drop)
    self.rds_on = self.ArgParameter(rds_on)

  def contents(self):
    super().contents()

    self.assign(self.actual_frequency, self.frequency)
    self.power_path = self.Block(BuckBoostConverterPowerPath(
      self.pwr_in.link().voltage, self.output_voltage, self.actual_frequency,
      self.pwr_out.link().current_drawn, Range.all(),  # TODO model current limits from FETs
      inductor_current_ripple=self._calculate_ripple(self.pwr_out.link().current_drawn,
                                                     self.ripple_current_factor,
                                                     rated_current=self.pwr_out.link().current_drawn.upper())
    ))
    self.connect(self.power_path.pwr_in, self.pwr_in)
    self.connect(self.power_path.pwr_out, self.pwr_out)
    self.connect(self.power_path.gnd, self.gnd)

    self.buck_sw = self.Block(FetHalfBridge(frequency=self.frequency))
    self.connect(self.buck_sw.gnd, self.gnd)
    self.connect(self.buck_sw.pwr_logic, self.pwr_logic)
    self.connect(self.buck_sw.low_ctl, self.buck_pwm_low)
    self.connect(self.buck_sw.high_ctl, self.buck_pwm_high)
    self.connect(self.pwr_in, self.buck_sw.pwr)
    self.connect(  # current draw used to size FETs, size for peak current
      self.buck_sw.out,
      self.power_path.switch_in.adapt_to(VoltageSink(current_draw=self.power_path.actual_inductor_current))
    )

    self.boost_sw = self.Block(FetHalfBridge(frequency=self.frequency))
    self.connect(self.boost_sw.gnd, self.gnd)
    self.connect(self.boost_sw.pwr_logic, self.pwr_logic)
    self.connect(self.boost_sw.low_ctl, self.boost_pwm_low)
    self.connect(self.boost_sw.high_ctl, self.boost_pwm_high)
    (self.boost_pwr_conn, ), _ = self.chain(
      self.boost_sw.pwr,
      self.Block(VoltageSinkConnector(0*Volt(tol=0), 0*Amp(tol=0))),  # TODO FIXME
      self.pwr_out
    )
    self.connect(  # current draw used to size FETs, size for peak current
      self.power_path.switch_out.adapt_to(VoltageSink(current_draw=self.power_path.actual_inductor_current)),
      self.boost_sw.out
    )
    # (self.boost_sw_force, ), _ = self.chain(
    #   self.boost_sw.out,  # current draw used to size FETs, size for peak current
    #   self.Block(ForcedVoltageCurrentDraw(self.power_path.inductor_spec_peak_current)),
    #   self.power_path.switch)
