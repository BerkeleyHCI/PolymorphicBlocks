import unittest

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


class SourceMeasureControl(Block):
  """Analog feedback circuit for the source-measure unit
  """
  def __init__(self):
    super().__init__()

    self.pwr = self.Port(VoltageSink(), [Power])
    self.gnd = self.Port(Ground(), [Common])
    self.center_reference = self.Port(VoltageSink())

    self.control_voltage = self.Port(AnalogSink())
    self.control_current_source = self.Port(AnalogSink())
    self.control_current_sink = self.Port(AnalogSink())
    self.measured_voltage = self.Port(AnalogSource())
    self.measured_current = self.Port(AnalogSource())
    # TODO ADD PARAMETERS, IMPLEMENT ME


class AnalogMerge(Block):
  """Directly connects the input AnalogSinks and provides an AnalogSource port. Just copper on the board.
  TODO: in the future, this should use block-side port arrays
  """
  def __init__(self):
    super().__init__()

    self.in1 = self.Port(AnalogSink())
    self.in2 = self.Port(AnalogSink())
    self.in3 = self.Port(AnalogSink())
    self.out = self.Port(AnalogSource(), [Output])
    # TODO ADD PARAMETERS, IMPLEMENT ME


class ErrorAmplifier(Block):
  """Error amplifier circuit. Really not quite sure quite how this works, looks like an opamp follower after a
  resistive divider. Configurable diode and resistors.

  TODO: diode parameter should be an enum. Current values: '' (no diode), 'sink', 'source' (sinks or sources current)
  """
  @init_in_parent
  def __init__(self, resistance: RangeLike = RangeExpr(), diode: StringLike = ""):
    super().__init__()

    self.amp = self.Block(Opamp())

    self.pwr = self.Export(self.amp.pwr, [Power])
    self.gnd = self.Export(self.amp.gnd, [Common])

    self.target = self.Port(AnalogSink())
    self.actual = self.Port(AnalogSink())
    self.output = self.Port(AnalogSource())
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
        imp.Block(LinearRegulator(output_voltage=3.3*Volt(tol=0.05))),
        # TODO next revision: 3.0 volt high precision LDO?
      )

      self.v3v3 = self.connect(self.reg_3v3.pwr_out)

    with self.implicit_connect(
        ImplicitConnect(self.reg_3v3.pwr_out, [Power]),
        ImplicitConnect(self.reg_3v3.gnd, [Common]),
    ) as imp:
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

    # TODO add DACs
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
