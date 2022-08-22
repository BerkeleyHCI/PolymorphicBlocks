from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Ap3418_Device(DiscreteChip, FootprintBlock, JlcPart):
  @init_in_parent
  def __init__(self):
    super().__init__()
    self.sw = self.Port(VoltageSource())  # internal switch specs not defined, only bulk current limit defined
    self.pwr_in = self.Port(VoltageSink(
      voltage_limits=(2.5, 5.5)*Volt,
      current_draw=self.sw.link().current_drawn  # TODO quiescent current
    ), [Power])
    self.gnd = self.Port(Ground(), [Common])
    self.fb = self.Port(AnalogSink(impedance=(10, float('inf')) * MOhm))  # based on input current spec

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
    self.assign(self.lcsc_part, 'C500769')
    self.assign(self.actual_basic_part, False)


class Ap3418(DiscreteBuckConverter):
  """Adjustable synchronous buck converter in SOT-23-5 with integrated switch"""
  def contents(self):
    super().contents()

    self.assign(self.frequency, 1.4*MHertz(tol=0))

    with self.implicit_connect(
        ImplicitConnect(self.pwr_in, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.ic = imp.Block(Ap3418_Device())

      self.fb = imp.Block(FeedbackVoltageDivider(
        output_voltage=(0.588, 0.612) * Volt,
        impedance=(10, 100) * kOhm,
        assumed_input_voltage=self.output_voltage
      ))
      self.assign(self.pwr_out.voltage_out, self.fb.actual_input_voltage)
      self.connect(self.fb.input, self.pwr_out)
      self.connect(self.fb.output, self.ic.fb)

      # TODO: the control mechanism requires a specific capacitor / inductor selection, datasheet 8.2.2.3
      self.power_path = imp.Block(BuckConverterPowerPath(
        self.pwr_in.link().voltage, self.fb.actual_input_voltage, self.frequency,
        self.pwr_out.link().current_drawn, (0, 1.5)*Amp,
        inductor_current_ripple=self._calculate_ripple(
          self.pwr_out.link().current_drawn,
          self.ripple_current_factor,
          rated_current=1.5*Amp),
        dutycycle_limit=(0, 1)
      ))
      self.connect(self.power_path.pwr_out, self.pwr_out)
      self.connect(self.power_path.switch, self.ic.sw)
