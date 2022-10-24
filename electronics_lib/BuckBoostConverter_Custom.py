from electronics_abstract_parts import *


class CustomBuckBoostConverter(DiscreteBoostConverter):
  """Custom buck-boost that has two PWM inputs for the input high and output low switches,
  with diodes for the complementary switches (non-synchronous)."""
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.low_pwm = self.Port(DigitalSink.empty())
    self.high_pwm = self.Port(DigitalSink.empty())

  def contents(self):
    super().contents()

    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.power_path = imp.Block(BuckBoostConverterPowerPath(
        self.pwr_in.link().voltage, self.ic.vout.voltage_out, self.frequency,
        self.pwr_out.link().current_drawn, self.ic.vout.current_limits,
        inductor_current_ripple=self._calculate_ripple(self.pwr_out.link().current_drawn,
                                                       self.ripple_current_factor,
                                                       rated_current=self.ic.vout.current_limits.lower())
      ))
      self.connect(self.power_path.pwr_out, self.pwr_out)
      self.connect(self.power_path.switch, self.ic.sw)
