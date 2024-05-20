from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Tps561201_Device(InternalSubcircuit, JlcPart, FootprintBlock):
  @init_in_parent
  def __init__(self):
    super().__init__()
    self.sw = self.Port(VoltageSource())  # internal switch specs not defined, only bulk current limit defined
    self.pwr_in = self.Port(VoltageSink(
      voltage_limits=(4.5, 17)*Volt,
      current_draw=self.sw.link().current_drawn  # TODO quiescent current
    ), [Power])
    self.gnd = self.Port(Ground(), [Common])
    self.fb = self.Port(AnalogSink(impedance=(8000, float('inf')) * kOhm))  # based on input current spec
    self.vbst = self.Port(VoltageSource())
    self.en = self.Port(DigitalSink(
      voltage_limits=(-0.1, 17)*Volt,
      input_thresholds=(0.8, 1.6)*Volt
    ))

  def contents(self) -> None:
    super().contents()
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23-6',
      {
        '1': self.gnd,
        '2': self.sw,
        '3': self.pwr_in,
        '4': self.fb,
        '5': self.en,
        '6': self.vbst,
      },
      mfr='Texas Instruments', part='TPS561201',
      datasheet='https://www.ti.com/lit/ds/symlink/tps561201.pdf'
    )
    self.assign(self.lcsc_part, 'C220433')
    self.assign(self.actual_basic_part, False)


class Tps561201(VoltageRegulatorEnableWrapper, DiscreteBuckConverter):
  """Adjustable synchronous buck converter in SOT-23-6 with integrated switch"""
  def _generator_inner_reset_pin(self) -> Port[DigitalLink]:
    return self.ic.en

  def contents(self):
    super().contents()

    self.assign(self.actual_frequency, 580*kHertz(tol=0))

    with self.implicit_connect(
        ImplicitConnect(self.pwr_in, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.ic = imp.Block(Tps561201_Device())

      self.fb = imp.Block(FeedbackVoltageDivider(
        output_voltage=(0.749, 0.787) * Volt,
        impedance=(1, 10) * kOhm,
        assumed_input_voltage=self.output_voltage
      ))
      self.connect(self.fb.input, self.pwr_out)
      self.connect(self.fb.output, self.ic.fb)

      self.hf_in_cap = imp.Block(DecouplingCapacitor(capacitance=0.1*uFarad(tol=0.2)))  # Datasheet 8.2.2.4

      self.vbst_cap = self.Block(Capacitor(capacitance=0.1*uFarad(tol=0.2), voltage=(0, 6) * Volt))
      self.connect(self.vbst_cap.neg.adapt_to(VoltageSink()), self.ic.sw)
      self.connect(self.vbst_cap.pos.adapt_to(VoltageSink()), self.ic.vbst)

      # TODO: the control mechanism requires a specific capacitor / inductor selection, datasheet 8.2.2.3
      self.power_path = imp.Block(BuckConverterPowerPath(
        self.pwr_in.link().voltage, self.fb.actual_input_voltage, self.actual_frequency,
        self.pwr_out.link().current_drawn, (0, 1.2)*Amp,
        inductor_current_ripple=self._calculate_ripple(self.pwr_out.link().current_drawn,
                                                       self.ripple_current_factor,
                                                       rated_current=1.2*Amp),
        input_voltage_ripple=self.input_ripple_limit,
        output_voltage_ripple=self.output_ripple_limit,
      ))
      # ForcedVoltage needed to provide a voltage value so current downstream can be calculated
      # and then the power path can generate
      (self.forced_out, ), _ = self.chain(self.power_path.pwr_out,
                                          self.Block(ForcedVoltage(self.fb.actual_input_voltage)),
                                          self.pwr_out)
      self.connect(self.power_path.switch, self.ic.sw)


class Tps54202h_Device(InternalSubcircuit, JlcPart, FootprintBlock):
  @init_in_parent
  def __init__(self):
    super().__init__()
    self.sw = self.Port(VoltageSource(
      current_limits=(0, 2)*Amp  # most conservative figures, low-side limited. TODO: better ones?
    ))  # internal switch specs not defined, only bulk current limit defined
    self.pwr_in = self.Port(VoltageSink(
      voltage_limits=(4.5, 28)*Volt,
      current_draw=self.sw.link().current_drawn  # TODO quiescent current
    ), [Power])
    self.gnd = self.Port(Ground(), [Common])
    self.fb = self.Port(AnalogSink())  # no impedance specs
    self.boot = self.Port(VoltageSource())
    self.en = self.Port(DigitalSink(  # must be connected, floating is disable
      voltage_limits=(-0.1, 7) * Volt,
      input_thresholds=(1.16, 1.35)*Volt
    ))

  def contents(self) -> None:
    super().contents()
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23-6',
      {
        '1': self.gnd,
        '2': self.sw,
        '3': self.pwr_in,
        '4': self.fb,
        '5': self.en,
        '6': self.boot,
      },
      mfr='Texas Instruments', part='TPS54202H',
      datasheet='https://www.ti.com/lit/ds/symlink/tps54202h.pdf'
    )
    self.assign(self.lcsc_part, 'C527684')
    self.assign(self.actual_basic_part, False)


class Tps54202h(Resettable, DiscreteBuckConverter, GeneratorBlock):
  """Adjustable synchronous buck converter in SOT-23-6 with integrated switch, 4.5-24v capable
  Note: TPS54202 has frequency spread-spectrum operation and internal pull-up on EN
  TPS54202H has no internal EN pull-up but a Zener diode clamp to limit voltage.
  """
  def contents(self):
    super().contents()
    self.generator_param(self.reset.is_connected())

    self.assign(self.actual_frequency, (390, 590)*kHertz)

    with self.implicit_connect(
        ImplicitConnect(self.pwr_in, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.ic = imp.Block(Tps54202h_Device())

      self.fb = imp.Block(FeedbackVoltageDivider(
        output_voltage=(0.581, 0.611) * Volt,
        impedance=(1, 10) * kOhm,
        assumed_input_voltage=self.output_voltage
      ))
      self.connect(self.fb.input, self.pwr_out)
      self.connect(self.fb.output, self.ic.fb)

      self.hf_in_cap = imp.Block(DecouplingCapacitor(capacitance=0.1*uFarad(tol=0.2)))  # Datasheet 8.2.3.1, "optional"?

      self.boot_cap = self.Block(Capacitor(capacitance=0.1*uFarad(tol=0.2), voltage=(0, 6) * Volt))
      self.connect(self.boot_cap.neg.adapt_to(VoltageSink()), self.ic.sw)
      self.connect(self.boot_cap.pos.adapt_to(VoltageSink()), self.ic.boot)

      self.power_path = imp.Block(BuckConverterPowerPath(
        self.pwr_in.link().voltage, self.fb.actual_input_voltage, self.actual_frequency,
        self.pwr_out.link().current_drawn, (0, 2)*Amp,
        inductor_current_ripple=self._calculate_ripple(self.pwr_out.link().current_drawn,
                                                       self.ripple_current_factor,
                                                       rated_current=2*Amp),
        input_voltage_ripple=self.input_ripple_limit,
        output_voltage_ripple=self.output_ripple_limit,
      ))
      # ForcedVoltage needed to provide a voltage value so current downstream can be calculated
      # and then the power path can generate
      (self.forced_out, ), _ = self.chain(self.power_path.pwr_out,
                                          self.Block(ForcedVoltage(self.fb.actual_input_voltage)),
                                          self.pwr_out)
      self.connect(self.power_path.switch, self.ic.sw)

  def generate(self):
    super().generate()
    if self.get(self.reset.is_connected()):
      self.connect(self.reset, self.ic.en)
    else:  # by default tie high to enable regulator
      # an internal 6.9v Zener clamps the enable voltage, datasheet recommends at 510k resistor
      # a pull-up resistor isn't used because
      self.en_res = self.Block(Resistor(resistance=510*kOhm(tol=0.05), power=0*Amp(tol=0)))
      self.connect(self.pwr_in, self.en_res.a.adapt_to(VoltageSink()))
      self.connect(self.en_res.b.adapt_to(DigitalSource()), self.ic.en)
