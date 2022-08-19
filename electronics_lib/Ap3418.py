from electronics_abstract_parts import *


class Ap3418_Device(DiscreteChip, FootprintBlock):
  @init_in_parent
  def __init__(self):
    super().__init__()
    self.sw = self.Port(VoltageSource())  # internal switch specs not defined, only bulk current limit defined
    self.pwr_in = self.Port(VoltageSink(
      voltage_limits=(2.5, 5.5)*Volt,
      current_draw=self.sw.link().current_drawn  # TODO quiescent current
    ), [Power])
    self.gnd = self.Port(Ground(), [Common])
    self.fb = self.Port(AnalogSink(impedance=(8000, float('inf')) * kOhm))  # based on input current spec
    self.en = self.Port(DigitalSink(  # must be connected, floating is disable
      voltage_limits=(-0.3, self.pwr_in.link().voltage+0.3) * Volt
    ))

  def contents(self) -> None:
    super().contents()
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23-5',
      {
        '1': self.pwr_in,  # en
        '2': self.gnd,
        '3': self.sw,
        '4': self.pwr_in,  # supply input pin
        '5': self.fb,
      },
      mfr='Diodes Incorporated', part='AP3418',
      datasheet='https://www.diodes.com/assets/Datasheets/AP3418.pdf'
    )


class Ap3418(DiscreteBuckConverter):
  """Adjustable synchronous buck converter in SOT-23-6 with integrated switch"""
  def contents(self):
    super().contents()

    self.assign(self.frequency, 1.4*MHertz(tol=0))

    with self.implicit_connect(
        ImplicitConnect(self.pwr_in, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.ic = imp.Block(Ap3418_Device())

      self.fb = imp.Block(FeedbackVoltageDivider(
        output_voltage=(0.749, 0.787) * Volt,
        impedance=(1, 10) * kOhm,
        assumed_input_voltage=self.output_voltage
      ))
      self.assign(self.pwr_out.voltage_out, self.fb.actual_input_voltage)
      self.connect(self.fb.input, self.pwr_out)
      self.connect(self.fb.output, self.ic.fb)

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
