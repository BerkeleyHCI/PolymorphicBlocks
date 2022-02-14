from electronics_abstract_parts import *


class Ltc3429_Device(DiscreteChip, FootprintBlock):
  @init_in_parent
  def __init__(self, current_draw: RangeLike = RangeExpr()):
    super().__init__()
    self.vin = self.Port(VoltageSink(
      voltage_limits=(1.0, 4.4)*Volt,  # maximum minimum startup voltage to abs. max Vin
      current_draw=current_draw
    ))
    self.gnd = self.Port(Ground())
    self.sw = self.Port(VoltageSource())
    self.fb = self.Port(AnalogSink(impedance=(8000, float('inf')) * kOhm))
    self.vout = self.Port(Passive()) # TODO model as voltage source

  def contents(self) -> None:
    super().contents()
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23-6',
      {
        '1': self.sw,
        '2': self.gnd,
        '3': self.fb,
        '4': self.vin,  # /SHDN
        '5': self.vout,
        '6': self.vin,
      },
      mfr='Linear Technology', part='LTC3429BES6#TRMPBF',
      datasheet='https://www.analog.com/media/en/technical-documentation/data-sheets/3429fa.pdf'
    )

class Ltc3429(DiscreteBoostConverter, GeneratorBlock):
  """Low-input-voltage boost converter (starts as low as 0.85V).
  Pin-compatible with the less-expensive UM3429S"""
  NMOS_CURRENT_LIMIT = 0.6

  def contents(self):
    super().contents()

    self.require(self.pwr_out.voltage_out.within((2.2, 4.3)*Volt))  # >4.3v requires external diode
    self.require(self.pwr_out.voltage_out.lower() >= self.pwr_in.voltage_limits.lower())
    self.assign(self.frequency, (380, 630)*kHertz)

    self.fb = self.Block(FeedbackVoltageDivider(
      output_voltage=(1.192, 1.268) * Volt,
      impedance=(40, 400) * kOhm,  # about 25 MOhm worst case input impedance, this is 100x below
      assumed_input_voltage=self.output_voltage
    ))
    self.assign(self.pwr_out.voltage_out,
                (1.192*Volt / self.fb.actual_ratio.upper(),
                 1.268*Volt / self.fb.actual_ratio.lower()))

    self.generator(self.generate_converter,
                   self.pwr_in.link().voltage, self.output_voltage,
                   self.pwr_out.link().current_drawn,
                   self.frequency, self.output_ripple_limit, self.input_ripple_limit, self.ripple_current_factor,
                   self.dutycycle_limit)


  def generate_converter(self, input_voltage: Range, output_voltage: Range,
                         output_current: Range, frequency: Range,
                         spec_output_ripple: float, spec_input_ripple: float, ripple_factor: Range,
                         dutycycle_limit: Range) -> None:
    self.ic = self.Block(Ltc3429_Device(
      current_draw=(self.pwr_out.link().current_drawn.lower() * self.pwr_out.voltage_out.lower() / self.pwr_in.link().voltage.upper(),
                    self.pwr_out.link().current_drawn.upper() * self.pwr_out.voltage_out.upper() / self.pwr_in.link().voltage.lower())
    ))
    self.connect(self.pwr_in, self.ic.vin)
    self.connect(self.gnd, self.ic.gnd)

    self.connect(self.fb.input, self.pwr_out)
    self.connect(self.fb.gnd, self.gnd)
    self.connect(self.fb.output, self.ic.fb)

    self._generate_converter(self.ic.sw, self.NMOS_CURRENT_LIMIT,  # 600 mAmp NMOS current limit
                             input_voltage=input_voltage, output_voltage=output_voltage,
                             output_current_max=output_current.upper, frequency=frequency,
                             spec_output_ripple=spec_output_ripple, spec_input_ripple=spec_input_ripple,
                             ripple_factor=ripple_factor,
                             dutycycle_limit=dutycycle_limit)

    # TODO add constraint on effective inductance and capacitance range
    self.connect(self.pwr_out, self.ic.vout.as_voltage_source(
      voltage_out=self.pwr_out.voltage_out,  # TODO cyclic dependency?
      current_limits=(0, self.NMOS_CURRENT_LIMIT)*Amp
    ))