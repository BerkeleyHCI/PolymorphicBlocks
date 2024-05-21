from ..electronics_abstract_parts import *


class Xc9142_Device(InternalSubcircuit, FootprintBlock, GeneratorBlock):
  parts_output_voltage_current = [  # from Table 2, Vout and Ilim
    ('18', Range(1.764, 1.836), Range(0.96, 2.30)),
    ('25', Range(2.450, 2.550), Range(1.19, 2.30)),
    ('30', Range(2.940, 3.060), Range(0.96, 2.30)),
    ('33', Range(3.234, 3.366), Range(0.98, 2.30)),
    ('50', Range(4.900, 5.100), Range(1.07, 2.30)),
  ]
  parts_frequency = [  # fosc
    ('C', Range(1.02e6, 1.38e6)),  # 1.2MHz
    ('D', Range(2.40e6, 3.60e6)),  # 3.0MHz
  ]
  parts_package = [
    ('MR-G', 'Package_TO_SOT_SMD:SOT-23-5'),
  ]

  @init_in_parent
  def __init__(self, output_voltage: RangeLike, frequency: RangeLike = Range.all()):
    super().__init__()

    self.vin = self.Port(VoltageSink(
      voltage_limits=(0.90, 6.0)*Volt,  # maximum minimum startup voltage to max input voltage
      # TODO quiescent current
    ), [Power])
    self.gnd = self.Port(Ground(), [Common])
    self.ce = self.Port(DigitalSink.from_supply(self.gnd, self.vin,
                                                voltage_limit_tolerance=(0, 5)*Volt,
                                                input_threshold_abs=(0.2, 0.6)*Volt))
    self.sw = self.Port(VoltageSink())
    self.vout = self.Port(VoltageSource.empty())

    self.output_voltage = self.ArgParameter(output_voltage)
    self.frequency = self.ArgParameter(frequency)
    self.generator_param(self.output_voltage, self.frequency)

    self.actual_current_limit = self.Parameter(RangeExpr())  # set by part number
    self.actual_frequency = self.Parameter(RangeExpr())  # set by part number

  def generate(self) -> None:
    super().generate()

    part_number_voltage, part_voltage, part_current = [
      (part, part_voltage, part_current) for (part, part_voltage, part_current) in self.parts_output_voltage_current
      if part_voltage in self.get(self.output_voltage)][0]
    part_number_frequency, part_frequency = [
      (part, part_frequency) for (part, part_frequency) in self.parts_frequency
      if part_frequency in self.get(self.frequency)][0]  # lower frequency preferred, 'safer' option for compatibility
    part_number_package, part_package = self.parts_package[0]  # SOT-23-5 hardcoded for now

    self.assign(self.actual_frequency, part_frequency)
    self.assign(self.actual_current_limit, (0, part_current.lower))
    self.vout.init_from(VoltageSource(
      voltage_out=part_voltage, current_limits=self.sw.link().current_limits
    ))

    self.footprint(
      'U', part_package,
      {
        '1': self.ce,
        '2': self.gnd,
        '3': self.vin,
        '4': self.vout,
        '5': self.sw,
      },
      mfr='Torex Semiconductor Ltd', part=f'XC9142*{part_number_voltage}{part_number_frequency}{part_number_package}',
      datasheet='https://www.torexsemi.com/file/xc9141/XC9141-XC9142.pdf'
    )


class Xc9142(Resettable, DiscreteBoostConverter, GeneratorBlock):
  """Low-input-voltage boost converter (starts as low as 0.9V) with fixed output.
  XC9142 has PWM/PFM functionality, compared to PWM only for XC9141.
  Semi pin compatible with XC9140, LTC3525, MAX1724."""
  def contents(self):
    super().contents()
    self.generator_param(self.reset.is_connected())

    with self.implicit_connect(
        ImplicitConnect(self.pwr_in, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.ic = imp.Block(Xc9142_Device(self.output_voltage))
      self.connect(self.ic.vout, self.pwr_out)
      self.assign(self.actual_frequency, self.ic.actual_frequency)

      self.power_path = imp.Block(BoostConverterPowerPath(
        self.pwr_in.link().voltage, self.ic.vout.voltage_out, self.actual_frequency,
        self.pwr_out.link().current_drawn, self.ic.actual_current_limit,
        inductor_current_ripple=self._calculate_ripple(self.pwr_out.link().current_drawn,
                                                       self.ripple_current_factor,
                                                       rated_current=self.ic.actual_current_limit.lower()),
        input_voltage_ripple=self.input_ripple_limit,
        output_voltage_ripple=self.output_ripple_limit
      ))
      self.connect(self.power_path.pwr_out, self.pwr_out)
      self.connect(self.power_path.switch, self.ic.sw)

  def generate(self):
    super().generate()
    if self.get(self.reset.is_connected()):
      self.connect(self.reset, self.ic.ce)
    else:  # CE resistor: recommended through a <1M resistor; must not be left open
      self.ce_res = self.Block(PullupResistor(100*kOhm(tol=0.2))).connected(pwr=self.pwr_in, io=self.ic.ce)
