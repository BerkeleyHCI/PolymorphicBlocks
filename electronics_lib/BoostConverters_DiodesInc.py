from electronics_abstract_parts import *


class Ap3012_Device(DiscreteChip, FootprintBlock):
  @init_in_parent
  def __init__(self):
    super().__init__()
    self.pwr_in = self.Port(VoltageSink(
      voltage_limits=(2.6, 16)*Volt,
      # TODO quiescent current
    ), [Power])
    self.gnd = self.Port(Ground(), [Common])
    self.sw = self.Port(VoltageSource(
      current_limits=(0, 500)*mAmp  # TODO how to model sink current limits?!
    ))
    self.fb = self.Port(AnalogSink(impedance=(12500, float('inf')) * kOhm))  # based on input current spec

  def contents(self):
    super().contents()
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23-5',
      {
        '1': self.sw,
        '2': self.gnd,
        '3': self.fb,
        '4': self.pwr_in,  # /SHDN
        '5': self.pwr_in,
      },
      mfr='Diodes Incorporated', part='AP3012KTR-G1',
      datasheet='https://www.diodes.com/assets/Datasheets/AP3012.pdf'
    )


class Ap3012(DiscreteBoostConverter):
  """Adjustable boost converter in SOT-23-5 with integrated switch"""
  def contents(self):
    super().contents()

    self.assign(self.frequency, (1.1, 1.9)*MHertz)
    self.require(self.pwr_out.voltage_out.within((1.33, 29)*Volt))

    with self.implicit_connect(
        ImplicitConnect(self.pwr_in, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.ic = imp.Block(Ap3012_Device())

      self.fb = imp.Block(FeedbackVoltageDivider(
        output_voltage=(1.17, 1.33) * Volt,
        impedance=(1, 10) * kOhm,
        assumed_input_voltage=self.output_voltage
      ))
      self.assign(self.pwr_out.voltage_out, self.fb.actual_input_voltage)
      self.connect(self.fb.input, self.pwr_out)
      self.connect(self.fb.output, self.ic.fb)

      self.power_path = imp.Block(BoostConverterPowerPath(
        self.pwr_in.link().voltage, self.fb.actual_input_voltage, self.frequency,
        self.pwr_out.link().current_drawn, (0, 0.5)*Amp,
        inductor_current_ripple=self._calculate_ripple(self.pwr_out.link().current_drawn,
                                                       self.ripple_current_factor,
                                                       rated_current=0.5*Amp)
      ))
      self.connect(self.power_path.pwr_out, self.pwr_out)
      self.connect(self.power_path.switch, self.ic.sw)

      self.rect = self.Block(Diode(
        reverse_voltage=(0, self.pwr_out.voltage_out.upper()),
        current=self.pwr_out.link().current_drawn,
        voltage_drop=(0, 0.4)*Volt,
        reverse_recovery_time=(0, 500) * nSecond  # guess from Digikey's classification for "fast recovery"
      ))
      self.connect(self.ic.sw, self.rect.anode.adapt_to(VoltageSink()))
      self.connect(self.pwr_out, self.rect.cathode.adapt_to(VoltageSource(
        voltage_out=self.pwr_out.voltage_out,  # TODO cyclic dependency?
        current_limits=(0, 0.5)*Amp  # TODO proper switch current modeling?
      )))
