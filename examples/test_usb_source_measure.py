import unittest

from electronics_abstract_parts.ESeriesUtil import ESeriesRatioUtil
from electronics_abstract_parts.ResistiveDivider import DividerValues
from edg import *


class GatedEmitterFollower(Block):
  """Emitter follower, where each transistor can have its input gated independently,
  and a transistor with a disabled input will turn off.

  For the SMU, this allows a turn-on scheme where the error integrated is railed to off one side,
  and only the off side transistor turns on, then the proper output can be programmed.
  After the output stabilizes, both transistors can be enabled (if desired), to run under the
  analog feedback circuit.
  """
  def __init__(self):
    super().__init__()
    # TODO ADD PARAMETERS, IMPLEMENT ME


class ErrorAmplifier(GeneratorBlock):
  """Not really a general error amplifier circuit, but a subcircuit that performs that function in
  the context of this SMU analog feedback block.

  Consists of a resistive divider between the target and inverted sense signal, followed by
  an opamp follower circuit that is limited by either a resistor, or diode (for source-/sink-only operation).

  The target and sense signal should share a common reference ('zero') voltage, that is also the
  reference fed into the following integrator stage.
  When the measured signal is the same as the target, the sense input is equal-but-opposite from the
  target signal (referenced to the common reference), so the divider output is at common.
  Any deviation upsets this balance, which produces an error signal on the output.

  TODO: diode parameter should be an enum. Current values: '' (no diode), 'sink', 'source' (sinks or sources current)
  """
  @init_in_parent
  def __init__(self, output_resistance: RangeLike = RangeExpr(), input_resistance: RangeLike = RangeExpr(),
               diode_spec: StringLike = ""):
    super().__init__()

    self.amp = self.Block(Opamp())
    self.pwr = self.Export(self.amp.pwr, [Power])
    self.gnd = self.Export(self.amp.gnd, [Common])

    self.target = self.Port(AnalogSink())
    self.actual = self.Port(AnalogSink())
    self.output = self.Port(AnalogSource())

    self.output_resistance = self.Parameter(RangeExpr(output_resistance))
    self.input_resistance = self.Parameter(RangeExpr(input_resistance))
    self.diode_spec = self.Parameter(StringExpr(diode_spec))

    self.series = self.Parameter(IntExpr(24))  # can be overridden by refinements
    self.tolerance = self.Parameter(FloatExpr(0.01))  # can be overridden by refinements

    self.generator(self.generate_amp, self.output_resistance, self.input_resistance, self.diode_spec,
                   self.series, self.tolerance)

  def generate_amp(self, output_resistance: Range, input_resistance: Range, diode_spec: str,
                   series: int, tolerance: float) -> None:
    calculator = ESeriesRatioUtil(ESeriesUtil.SERIES[series], tolerance, DividerValues)
    top_resistance, bottom_resistance = calculator.find(DividerValues(Range.from_tolerance(0.5, tolerance),
                                                                      4 * input_resistance))
    # the 4x factor is a way to specify the series resistance of the divider assuming both resistors are equal,
    # since the DividerValues util only takes the parallel resistance

    self.rtop = self.Block(Resistor(
      resistance=Range.from_tolerance(top_resistance, tolerance)
    ))
    self.rbot = self.Block(Resistor(
      resistance=Range.from_tolerance(bottom_resistance, tolerance)
    ))
    self.connect(self.target, self.rtop.a.as_analog_sink(
      impedance=self.rtop.resistance + self.rbot.resistance
    ))
    self.connect(self.actual, self.rbot.a.as_analog_sink(
      impedance=self.rtop.resistance + self.rbot.resistance
    ))
    self.connect(self.amp.inp, self.rtop.b.as_analog_source(
      voltage_out=self.target.link().voltage.hull(self.actual.link().voltage),
      impedance=1 / (1 / self.rtop.resistance + 1 / self.rbot.resistance)
    ), self.rtop.b.as_analog_sink())  # a side contains aggregate params, b side is dummy

    self.rout = self.Block(Resistor(
      resistance=output_resistance
    ))
    if not diode_spec:
      resistor_output_port = self.amp.out
    else:
      self.diode = self.Block(Diode(  # TODO should be encoded as a voltage difference?
        reverse_voltage=self.amp.out.voltage_out
      ))
      if diode_spec == 'source':
        self.connect(self.amp.out, self.diode.anode.as_analog_sink(
          impedance=self.rout.resistance + self.output.link().sink_impedance
        ))
        resistor_output_port = self.diode.cathode.as_analog_source(
          impedance=self.amp.out.link().source_impedance + self.rout.resistance
        )
      elif diode_spec == 'sink':
        self.connect(self.amp.out, self.diode.cathode.as_analog_sink(
          impedance=self.rout.resistance + self.output.link().sink_impedance
        ))
        resistor_output_port = self.diode.anode.as_analog_source(
          impedance=self.amp.out.link().source_impedance + self.rout.resistance
        )
      else:
        raise ValueError(f"invalid diode spec '{diode_spec}', expected '', 'source', or 'sink'")
    self.connect(resistor_output_port, self.rout.a)
    self.connect(self.output, self.rout.b.as_analog_source(
      impedance=self.rout.resistance
    ), self.amp.inn)


class SourceMeasureControl(Block):
  """Analog feedback circuit for the source-measure unit
  """
  def __init__(self):
    super().__init__()

    self.pwr = self.Port(VoltageSink(), [Power])
    self.gnd = self.Port(Ground(), [Common])
    self.ref_center = self.Port(AnalogSink())

    self.control_voltage = self.Port(AnalogSink())
    self.control_current_source = self.Port(AnalogSink())
    self.control_current_sink = self.Port(AnalogSink())
    self.measured_voltage = self.Port(AnalogSource())
    self.measured_current = self.Port(AnalogSource())
    # TODO ADD PARAMETERS, IMPLEMENT ME


class UsbSourceMeasureTest(BoardTop):
  def contents(self) -> None:
    super().contents()

    # USB PD port that supplies power to the load
    self.pwr_usb = self.Block(UsbCReceptacle(voltage_out=(4.5, 21)*Volt, current_limits=(0, 5)*Amp))

    # Data-only USB port, for example to connect to a computer that can't source USB PD
    # so the PD port can be connected to a dedicated power brick.
    self.data_usb = self.Block(UsbCReceptacle())

    # TODO next revision: add a USB data port switch so the PD port can also take data

    self.gnd_merge = self.Block(MergedVoltageSource())
    self.connect(self.pwr_usb.gnd, self.gnd_merge.sink1)
    self.connect(self.data_usb.gnd, self.gnd_merge.sink2)

    self.gnd = self.connect(self.gnd_merge.source)
    self.vusb = self.connect(self.pwr_usb.pwr)

    with self.implicit_connect(
        ImplicitConnect(self.gnd_merge.source, [Common]),
    ) as imp:
      (self.reg_5v, self.reg_3v3), _ = self.chain(
        self.pwr_usb.pwr,
        imp.Block(BuckConverter(output_voltage=5.0*Volt(tol=0.05))),
        imp.Block(LinearRegulator(output_voltage=3.3*Volt(tol=0.05)))
      )
      self.v3v3 = self.connect(self.reg_3v3.pwr_out)

      (self.reg_analog, self.led_analog), _ = self.chain(
        self.reg_5v.pwr_out,
        imp.Block(LinearRegulator(output_voltage=2.5*Volt(tol=0.05))),
        imp.Block(VoltageIndicatorLed())
      )
      self.vref = self.connect(self.reg_analog.pwr_out)

      (self.ref_div, ), _ = self.chain(
        self.reg_analog.pwr_out,
        imp.Block(VoltageDivider(output_voltage=1.25*Volt(tol=0.05), impedance=(10, 100)*kOhm))
      )

    with self.implicit_connect(
        ImplicitConnect(self.pwr_usb.pwr, [Power]),
        ImplicitConnect(self.gnd_merge.source, [Common]),
    ) as imp:
      self.control = imp.Block(SourceMeasureControl())
      self.connect(self.control.ref_center, self.ref_div.output)

    with self.implicit_connect(
        ImplicitConnect(self.reg_3v3.pwr_out, [Power]),
        ImplicitConnect(self.reg_3v3.gnd, [Common]),
    ) as imp:
      # TODO check zener voltage is reasonable
      self.led_3v3 = imp.Block(VoltageIndicatorLed())
      self.prot_3v3 = imp.Block(ProtectionZenerDiode(voltage=(3.5, 3.8)*Volt))

      # TODO next revision: optional clamping diode on CC lines (as present in PD buddy sink, but not OtterPill)
      self.pd = imp.Block(Fusb302b())
      self.connect(self.pd.vbus, self.pwr_usb.pwr)
      self.connect(self.pwr_usb.cc, self.pd.cc)

      self.mcu = imp.Block(Lpc1549_48(frequency=12 * MHertz(tol=0.005)))
      (self.swd, ), _ = self.chain(imp.Block(SwdCortexTargetWithTdiConnector()), self.mcu.swd)
      (self.crystal, ), _ = self.chain(self.mcu.xtal, imp.Block(OscillatorCrystal(frequency=12 * MHertz(tol=0.005))))  # TODO can we not specify this and instead infer from MCU specs?

      (self.usb_esd, ), _ = self.chain(self.data_usb.usb, imp.Block(UsbEsdDiode()), self.mcu.usb_0)

      (self.i2c_pull, ), _ = self.chain(self.mcu.i2c_0, imp.Block(I2cPullup()), self.pd.i2c)
      self.connect(self.mcu.new_io(DigitalBidir), self.pd.int)

      self.rgb = imp.Block(IndicatorSinkRgbLed())
      self.connect(self.mcu.new_io(DigitalBidir), self.rgb.red)
      self.connect(self.mcu.new_io(DigitalBidir), self.rgb.green)
      self.connect(self.mcu.new_io(DigitalBidir), self.rgb.blue)

      shared_spi = self.mcu.new_io(SpiMaster)
      (self.dac_v, ), _ = self.chain(shared_spi, imp.Block(Mcp4921()),
                                     self.control.control_voltage)
      (self.dac_ip, ), _ = self.chain(shared_spi, imp.Block(Mcp4921()),
                                      self.control.control_current_source)
      (self.dac_in, ), _ = self.chain(shared_spi, imp.Block(Mcp4921()),
                                      self.control.control_current_sink)

      (self.adc_v, ), _ = self.chain(self.control.measured_voltage, imp.Block(Mcp3201()),
                                     shared_spi)
      (self.adc_i, ), _ = self.chain(self.control.measured_current, imp.Block(Mcp3201()),
                                     shared_spi)

      self.connect(self.reg_analog.pwr_out,
                   self.dac_v.ref, self.dac_ip.ref, self.dac_in.ref,
                   self.adc_v.ref, self.adc_i.ref)

      self.connect(self.mcu.new_io(DigitalBidir), self.dac_v.cs)
      self.connect(self.mcu.new_io(DigitalBidir), self.dac_ip.cs)
      self.connect(self.mcu.new_io(DigitalBidir), self.dac_in.cs)
      self.connect(self.mcu.new_io(DigitalBidir), self.adc_v.cs)
      self.connect(self.mcu.new_io(DigitalBidir), self.adc_i.cs)
      self.connect(self.mcu.new_io(DigitalBidir),
                   self.dac_v.ldac, self.dac_ip.ldac, self.dac_in.ldac)

    # TODO add analog feedback control chain
    # TODO add power transistors and sensors
    # TODO add UI elements: output enable tactile switch + LCD + 4 directional buttons

    # TODO next revision: Blackberry trackball UI?

    # TODO next revision: add high precision ADCs
    # TODO next revision: add speaker?

    # Misc board
    self.duck = self.Block(DuckLogo())
    self.leadfree = self.Block(LeadFreeIndicator())
    self.id = self.Block(IdDots4())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['reg_5v'], Tps54202h),
        (['reg_3v3'], Ld1117),
        (['reg_analog'], Ld1117),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], ';'.join([

        ])),
        # allow the regulator to go into tracking mode
        (['reg_5v', 'dutycycle_limit'], Range(0, float('inf'))),
      ],
      class_refinements=[
        (SwdCortexTargetWithTdiConnector, SwdCortexTargetTc2050),
      ],
    )


class UsbTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(UsbSourceMeasureTest)
