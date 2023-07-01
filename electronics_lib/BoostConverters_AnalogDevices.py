from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Ltc3429_Device(InternalSubcircuit, JlcPart, FootprintBlock):
  @init_in_parent
  def __init__(self, output_voltage: RangeLike):
    super().__init__()
    self.vin = self.Port(VoltageSink(
      voltage_limits=(1.0, 4.4)*Volt,  # maximum minimum startup voltage to abs. max Vin
      # TODO quiescent current
    ), [Power])
    self.gnd = self.Port(Ground(), [Common])
    self.sw = self.Port(VoltageSink())
    self.fb = self.Port(AnalogSink(impedance=(8000, float('inf')) * kOhm))
    self.vout = self.Port(VoltageSource(
      voltage_out=output_voltage,
      current_limits=self.sw.link().current_limits
    ))
    self.nshdn = self.Port(DigitalSink(
      voltage_limits=(-0.3, 6) * Volt,
      current_draw=(0.01, 1)*uAmp,
      input_thresholds=(0.35, 1)*Volt
    ))

  def contents(self) -> None:
    super().contents()
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23-6',
      {
        '1': self.sw,
        '2': self.gnd,
        '3': self.fb,
        '4': self.nshdn,
        '5': self.vout,
        '6': self.vin,
      },
      mfr='Linear Technology', part='LTC3429BES6#TRMPBF',
      datasheet='https://www.analog.com/media/en/technical-documentation/data-sheets/3429fa.pdf'
    )
    self.assign(self.lcsc_part, 'C684773')
    self.assign(self.actual_basic_part, False)


class Ltc3429(VoltageRegulatorEnableWrapper, DiscreteBoostConverter):
  """Low-input-voltage boost converter (starts as low as 0.85V).
  Pin-compatible with the less-expensive UM3429S"""
  NMOS_CURRENT_LIMIT = 0.6
  def _generator_inner_enable_pin(self) -> Port[DigitalLink]:
    return self.ic.nshdn

  def contents(self):
    super().contents()

    self.assign(self.frequency, (380, 630)*kHertz)
    self.require(self.pwr_out.voltage_out.within((2.2, 4.3)*Volt))  # >4.3v requires external diode

    with self.implicit_connect(
        ImplicitConnect(self.pwr_in, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.fb = imp.Block(FeedbackVoltageDivider(
        output_voltage=(1.192, 1.268) * Volt,
        impedance=(40, 400) * kOhm,  # about 25 MOhm worst case input impedance, this is 100x below
        assumed_input_voltage=self.output_voltage
      ))
      self.connect(self.fb.input, self.pwr_out)

      self.ic = imp.Block(Ltc3429_Device(self.fb.actual_input_voltage))
      self.connect(self.ic.vout, self.pwr_out)
      self.connect(self.fb.output, self.ic.fb)

      # TODO add constraint on effective inductance and capacitance range
      self.power_path = imp.Block(BoostConverterPowerPath(
        self.pwr_in.link().voltage, self.fb.actual_input_voltage, self.frequency,
        self.pwr_out.link().current_drawn, (0, self.NMOS_CURRENT_LIMIT)*Amp,
        inductor_current_ripple=self._calculate_ripple(self.pwr_out.link().current_drawn,
                                                       self.ripple_current_factor,
                                                       rated_current=self.NMOS_CURRENT_LIMIT*Amp)
      ))
      self.connect(self.power_path.pwr_out, self.pwr_out)
      self.connect(self.power_path.switch, self.ic.sw)
