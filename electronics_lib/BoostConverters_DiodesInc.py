from electronics_abstract_parts import *


class Ap3012_Device(DiscreteChip, FootprintBlock):
  @init_in_parent
  def __init__(self, current_draw: RangeLike = RangeExpr()):
    # TODO the power path doesn't actually go through Vin, instead it goes through the inductor
    # But this is modeled here to be similar to the buck case, and the macromodel is valid anyways
    super().__init__()
    self.pwr_in = self.Port(VoltageSink(
      voltage_limits=(2.6, 16)*Volt,
      current_draw=current_draw
    ))
    self.gnd = self.Port(Ground())
    self.sw = self.Port(VoltageSource(
      current_limits=(0, 500)*mAmp  # TODO how to model sink current limits?!
    ))
    self.fb = self.Port(AnalogSink(impedance=(12500, float('inf')) * kOhm))  # based on input current spec
    # voltage_out=(1.33, 29)*Volt,  # minimum-but-not-minimum from FB max # TODO need const prop range subsetting

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


class Ap3012(DiscreteBoostConverter, GeneratorBlock):
  """Adjustable boost converter in SOT-23-5 with integrated switch"""
  def contents(self):
    super().contents()

    self.require(self.pwr_out.voltage_out.lower() >= self.pwr_in.voltage_limits.lower())

    self.assign(self.frequency, (1.1, 1.9)*MHertz)

    self.fb = self.Block(FeedbackVoltageDivider(
      output_voltage=(1.17, 1.33) * Volt,
      impedance=(1, 10) * kOhm,
      assumed_input_voltage=self.output_voltage
    ))
    self.assign(self.pwr_out.voltage_out,
                (1.17*Volt / self.fb.actual_ratio.upper(),
                 1.33*Volt / self.fb.actual_ratio.lower()))

    self.generator(self.generate_converter,
                   self.pwr_in.link().voltage, self.pwr_out.voltage_out,
                   self.pwr_out.link().current_drawn,
                   self.frequency, self.output_ripple_limit, self.input_ripple_limit, self.ripple_current_factor,
                   self.dutycycle_limit)


  def generate_converter(self, input_voltage: Range, output_voltage: Range,
                         output_current: Range, frequency: Range,
                         spec_output_ripple: float, spec_input_ripple: float, ripple_factor: Range,
                         dutycycle_limit: Range) -> None:
    self.ic = self.Block(Ap3012_Device(
      current_draw=(self.pwr_out.link().current_drawn.lower() * self.pwr_out.voltage_out.lower() / self.pwr_in.link().voltage.upper(),
                    self.pwr_out.link().current_drawn.upper() * self.pwr_out.voltage_out.upper() / self.pwr_in.link().voltage.lower())
    ))
    self.connect(self.pwr_in, self.ic.pwr_in)
    self.connect(self.gnd, self.ic.gnd)

    self.connect(self.fb.input, self.pwr_out)
    self.connect(self.fb.gnd, self.gnd)
    self.connect(self.fb.output, self.ic.fb)

    self.rect = self.Block(Diode(
      reverse_voltage=(0, self.pwr_out.voltage_out.upper()),
      current=self.pwr_out.link().current_drawn,
      voltage_drop=(0, 0.4)*Volt,
      reverse_recovery_time=(0, 500) * nSecond  # guess from Digikey's classification for "fast recovery"
    ))
    self.connect(self.ic.sw, self.rect.anode.as_voltage_sink())
    diode_out = self.rect.cathode.as_voltage_source(
      voltage_out=self.pwr_out.voltage_out,  # TODO cyclic dependency?
      current_limits=(0, 0.5)*Amp  # TODO proper switch current modeling?
    )
    self.connect(diode_out, self.pwr_out)

    self._generate_converter(self.ic.sw, 0.5,
                             input_voltage=input_voltage, output_voltage=output_voltage,
                             output_current_max=output_current.upper, frequency=frequency,
                             spec_output_ripple=spec_output_ripple, spec_input_ripple=spec_input_ripple,
                             ripple_factor=ripple_factor,
                             dutycycle_limit=dutycycle_limit)
