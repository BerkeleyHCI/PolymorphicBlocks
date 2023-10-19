from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Ap3012_Device(InternalSubcircuit, JlcPart, FootprintBlock):
  @init_in_parent
  def __init__(self):
    super().__init__()
    self.pwr_in = self.Port(VoltageSink(
      voltage_limits=(2.6, 16)*Volt,
      # TODO quiescent current
    ), [Power])
    self.gnd = self.Port(Ground(), [Common])
    self.sw = self.Port(VoltageSink())
    self.fb = self.Port(AnalogSink(impedance=(12500, float('inf')) * kOhm))  # based on input current spec

    self.nshdn = self.Port(DigitalSink(
      voltage_limits=(0, 16) * Volt,
      current_draw=(0, 55)*uAmp,
      input_thresholds=(0.4, 1.5)*Volt
    ))

  def contents(self):
    super().contents()
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23-5',
      {
        '1': self.sw,
        '2': self.gnd,
        '3': self.fb,
        '4': self.nshdn,
        '5': self.pwr_in,
      },
      mfr='Diodes Incorporated', part='AP3012K',
      datasheet='https://www.diodes.com/assets/Datasheets/AP3012.pdf'
    )
    self.assign(self.lcsc_part, 'C460356')
    self.assign(self.actual_basic_part, False)


class Ap3012(VoltageRegulatorEnableWrapper, DiscreteBoostConverter):
  """Adjustable boost converter in SOT-23-5 with integrated switch"""
  def _generator_inner_reset_pin(self) -> Port[DigitalLink]:
    return self.ic.nshdn

  def contents(self):
    super().contents()

    self.assign(self.actual_frequency, (1.1, 1.9)*MHertz)
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
      self.connect(self.fb.input, self.pwr_out)
      self.connect(self.fb.output, self.ic.fb)

      self.power_path = imp.Block(BoostConverterPowerPath(
        self.pwr_in.link().voltage, self.fb.actual_input_voltage, self.actual_frequency,
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
        voltage_out=self.fb.actual_input_voltage,
        current_limits=self.power_path.switch.current_limits
      )))
