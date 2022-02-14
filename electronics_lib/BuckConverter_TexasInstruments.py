from electronics_abstract_parts import *


class Tps561201_Device(DiscreteChip, FootprintBlock):
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

  def contents(self) -> None:
    super().contents()
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23-6',
      {
        '1': self.gnd,
        '2': self.sw,
        '3': self.pwr_in,
        '4': self.fb,
        '5': self.pwr_in,  # en
        '6': self.vbst,
      },
      mfr='Texas Instruments', part='TPS561201',
      datasheet='https://www.ti.com/lit/ds/symlink/tps561201.pdf'
    )


class Tps561201(DiscreteBuckConverter):
  """Adjustable synchronous buck converter in SOT-23-6 with integrated switch"""
  def contents(self):
    super().contents()

    self.require(self.pwr_out.voltage_out.within((0.76, 17)*Volt))
    self.assign(self.frequency, 580*kHertz(tol=0))

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
      self.assign(self.pwr_out.voltage_out, self.fb.actual_input_voltage)
      self.connect(self.fb.output, self.ic.fb)
      self.connect(self.fb.input, self.pwr_out)

      self.hf_in_cap = imp.Block(DecouplingCapacitor(capacitance=0.1*uFarad(tol=0.2)))  # Datasheet 8.2.2.4

      self.vbst_cap = self.Block(Capacitor(capacitance=0.1*uFarad(tol=0.2), voltage=(0, 6) * Volt))
      self.connect(self.vbst_cap.neg.as_voltage_sink(), self.ic.sw)
      self.connect(self.vbst_cap.pos.as_voltage_sink(), self.ic.vbst)

      # TODO: the control mechanism requires a specific capacitor / inductor selection, datasheet 8.2.2.3
      self.power_path = imp.Block(BuckConverterPowerPath(
        self.pwr_in.link().voltage, self.fb.actual_input_voltage, self.frequency,
        self.pwr_out.link().current_drawn, (0, 1.2)*Amp,
        inductor_current_ripple=self._calculate_ripple(self.pwr_out.link().current_drawn, rated_current=1.2*Amp)
      ))
      self.connect(self.power_path.pwr_out, self.pwr_out)
      self.connect(self.power_path.switch, self.ic.sw)


class Tps54202h_Device(DiscreteChip, FootprintBlock):
  @init_in_parent
  def __init__(self, current_draw: RangeLike = RangeExpr()):
    super().__init__()
    self.pwr_in = self.Port(VoltageSink(
      voltage_limits=(4.5, 28)*Volt,
      current_draw=current_draw
    ))
    self.gnd = self.Port(Ground())
    self.sw = self.Port(VoltageSource(
      current_limits=(0, 2)*Amp  # most conservative figures, low-side limited. TODO: better ones?
    ))  # internal switch specs not defined, only bulk current limit defined
    self.fb = self.Port(AnalogSink(impedance=(float('inf'), float('inf')) * Ohm))  # TODO specs not given
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


class Tps54202h(DiscreteBuckConverter, GeneratorBlock):
  """Adjustable synchronous buck converter in SOT-23-6 with integrated switch, 4.5-24v capable"""
  def contents(self):
    super().contents()

    self.require(self.pwr_out.voltage_out.upper() <= self.pwr_in.voltage_limits.upper())

    self.assign(self.frequency, (390, 590)*kHertz)

    self.fb = self.Block(FeedbackVoltageDivider(
      output_voltage=(0.581, 0.611) * Volt,
      impedance=(1, 10) * kOhm,
      assumed_input_voltage=self.output_voltage
    ))
    self.assign(self.pwr_out.voltage_out,
                (0.581*Volt / self.fb.actual_ratio.upper(),
                 0.611*Volt / self.fb.actual_ratio.lower()))

    self.generator(self.generate_converter,
                   self.pwr_in.link().voltage, self.pwr_out.voltage_out,
                   self.pwr_out.link().current_drawn,
                   self.frequency, self.output_ripple_limit, self.input_ripple_limit, self.ripple_current_factor,
                   self.dutycycle_limit)

  def generate_converter(self, input_voltage: Range, output_voltage: Range,
                         output_current: Range, frequency: Range,
                         spec_output_ripple: float, spec_input_ripple: float, ripple_factor: Range,
                         dutycycle_limit: Range) -> None:
    self.ic = self.Block(Tps54202h_Device(
      current_draw=(self.pwr_out.link().current_drawn.lower() * self.pwr_out.voltage_out.lower() / self.pwr_in.link().voltage.upper(),
                    self.pwr_out.link().current_drawn.upper() * self.pwr_out.voltage_out.upper() / self.pwr_in.link().voltage.lower())
    ))
    self.connect(self.pwr_in, self.ic.pwr_in)
    self.connect(self.gnd, self.ic.gnd)

    self.hf_in_cap = self.Block(DecouplingCapacitor(capacitance=0.1*uFarad(tol=0.2)))  # Datasheet 8.2.3.1, "optional"?
    self.connect(self.hf_in_cap.pwr, self.pwr_in)
    self.connect(self.hf_in_cap.gnd, self.gnd)

    self.boot_cap = self.Block(Capacitor(capacitance=0.1*uFarad(tol=0.2), voltage=(0, 6) * Volt))
    self.connect(self.boot_cap.neg.as_voltage_sink(), self.ic.sw)
    self.connect(self.boot_cap.pos.as_voltage_sink(), self.ic.boot)

    self.en_res = self.Block(Resistor(resistance=510*kOhm(tol=0.05), power=0))  # arbitrary tolerance
    # pull-up resistor not used here because the voltage changes
    self.connect(self.pwr_in, self.en_res.a.as_voltage_sink())
    self.connect(self.en_res.b.as_digital_source(), self.ic.en)

    self.connect(self.fb.input, self.pwr_out)
    self.connect(self.fb.gnd, self.gnd)
    self.connect(self.fb.output, self.ic.fb)

    # TODO dedup across all converters
    inductor_out = self._generate_converter(self.ic.sw, 2,
                                            input_voltage=input_voltage, output_voltage=output_voltage,
                                            output_current_max=output_current.upper, frequency=frequency,
                                            spec_output_ripple=spec_output_ripple, spec_input_ripple=spec_input_ripple,
                                            ripple_factor=ripple_factor,
                                            dutycycle_limit=dutycycle_limit)

    self.connect(self.pwr_out, inductor_out.as_voltage_source(
      voltage_out=self.pwr_out.voltage_out,  # TODO cyclic dependency?
      current_limits=(0, 2)*Amp
    ))
