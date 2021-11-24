import unittest
from typing import cast

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
  @init_in_parent
  def __init__(self, current: RangeLike = RangeExpr(), rds_on: RangeLike = RangeExpr()):
    super().__init__()

    self.pwr = self.Port(VoltageSink(), [Power])
    self.gnd = self.Port(Ground(), [Common])
    self.out = self.Port(VoltageSource())

    self.control = self.Port(AnalogSink())
    self.high_en = self.Port(DigitalSink())
    self.low_en = self.Port(DigitalSink())

    self.current = self.Parameter(RangeExpr(current))
    self.rds_on = self.Parameter(RangeExpr(rds_on))

  def contents(self) -> None:
    super().contents()

    self.high_fet = self.Block(NFet(drain_voltage=self.pwr.link().voltage,
                                    drain_current=self.current,
                                    gate_voltage=self.control.link().voltage,
                                    rds_on=self.rds_on,
                                    gate_charge=RangeExpr.ALL,  # don't care, it's analog not switching
                                    power=self.pwr.link().voltage * self.current))
    self.low_fet = self.Block(PFet(drain_voltage=self.pwr.link().voltage,
                                   drain_current=self.current,
                                   gate_voltage=self.control.link().voltage,
                                   rds_on=self.rds_on,
                                   gate_charge=RangeExpr.ALL,  # don't care, it's analog not switching
                                   power=self.pwr.link().voltage * self.current))

    self.connect(self.pwr, self.high_fet.drain.as_voltage_sink(
      current_draw=self.current,
      voltage_limits=self.high_fet.selected_drain_voltage_rating.intersect(
        self.low_fet.selected_drain_voltage_rating)
    ))
    self.connect(self.gnd, self.low_fet.drain.as_voltage_sink())
    output_driver = self.high_fet.source.as_voltage_source(
      voltage_out=self.pwr.link().voltage,
      current_limits=self.current
    )
    self.connect(output_driver, self.low_fet.source.as_voltage_sink(),
                 self.out)

    # TODO all the analog parameter modeling
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.high_gate = imp.Block(DigitalAnalogIsolatedSwitch())
      self.connect(self.high_en, self.high_gate.signal)
      self.low_gate = imp.Block(DigitalAnalogIsolatedSwitch())
      self.connect(self.low_en, self.low_gate.signal)

      self.connect(self.control, self.high_gate.ain, self.low_gate.ain)

      self.high_res = self.Block(Resistor(resistance=4.7*kOhm(tol=0.05)))
      self.low_res = self.Block(Resistor(resistance=4.7*kOhm(tol=0.05)))

      self.connect(self.high_fet.source, self.high_res.a)
      self.connect(self.low_fet.source, self.low_res.a)
      self.connect(self.high_res.b.as_analog_source(), self.high_gate.apull)
      self.connect(self.low_res.b.as_analog_source(), self.low_gate.apull)
      self.connect(self.high_gate.aout, self.high_fet.gate.as_analog_sink())
      self.connect(self.low_gate.aout, self.low_fet.gate.as_analog_sink())


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
                   self.series, self.tolerance,
                   targets=[self.target, self.actual, self.output])

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
    ), self.rbot.b.as_analog_sink())  # a side contains aggregate params, b side is dummy

    self.rout = self.Block(Resistor(
      resistance=output_resistance
    ))
    if not diode_spec:
      resistor_output_port = self.amp.out
    else:
      self.diode = self.Block(Diode(  # TODO should be encoded as a voltage difference?
        reverse_voltage=self.amp.out.voltage_out,
        current=RangeExpr.ZERO,  # an approximation, current rating not significant here
        voltage_drop=(0, 0.5)*Volt,  # arbitrary low threshold
        reverse_recovery_time=(0, 500)*nSecond  # arbitrary for "fast recovery"
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
    self.connect(resistor_output_port, self.rout.a.as_analog_sink())
    self.connect(self.output, self.rout.b.as_analog_source(
      impedance=self.rout.resistance
    ), self.amp.inn)


class SourceMeasureControl(Block):
  """Analog feedback circuit for the source-measure unit
  """
  @init_in_parent
  def __init__(self, current: RangeLike = RangeExpr(), rds_on: RangeLike = RangeExpr()):
    super().__init__()

    self.pwr = self.Port(VoltageSink(), [Power])
    self.pwr_logic = self.Port(VoltageSink())
    self.gnd = self.Port(Ground(), [Common])
    self.ref_center = self.Port(AnalogSink())

    self.out = self.Port(VoltageSource())

    self.measured_voltage = self.Port(AnalogSource())
    self.measured_current = self.Port(AnalogSource())

    self.current = self.Parameter(RangeExpr(current))
    self.rds_on = self.Parameter(RangeExpr(rds_on))

    with self.implicit_connect(
            ImplicitConnect(self.pwr_logic, [Power]),
            ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.err_volt = imp.Block(ErrorAmplifier(output_resistance=4.7*kOhm(tol=0.05),
                                               input_resistance=(10, 100)*kOhm))
      self.control_voltage = self.Export(self.err_volt.target)
      self.err_source = imp.Block(ErrorAmplifier(output_resistance=4.7*kOhm(tol=0.05),
                                                 input_resistance=(10, 100)*kOhm,
                                                 diode_spec='source'))
      self.control_current_source = self.Export(self.err_source.target)
      self.err_sink = imp.Block(ErrorAmplifier(output_resistance=4.7*kOhm(tol=0.05),
                                               input_resistance=(10, 100)*kOhm,
                                               diode_spec='sink'))
      self.control_current_sink = self.Export(self.err_sink.target)
      self.err_curr_merge = MergedAnalogSource.merge(self, self.err_source.output, self.err_sink.output)
      self.err_merge = MergedAnalogSource.merge(self, self.err_volt.output, self.err_curr_merge.source)

      self.int = imp.Block(IntegratorInverting(
        factor=Range.from_tolerance(1 / 4.7e-6, 0.15),
        capacitance=1*nFarad(tol=0.15)))
      self.int_link = self.connect(self.err_merge.source, self.int.input)  # to support impedance check waive
      self.connect(self.ref_center, self.int.reference)

    with self.implicit_connect(
            ImplicitConnect(self.pwr, [Power]),
            ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.amp = imp.Block(Amplifier(amplification=Range.from_tolerance(20, 0.05),
                                     impedance=(1, 10)*kOhm))
      self.connect(self.int.output, self.amp.input)
      self.connect(self.ref_center, self.amp.reference)

      self.driver = imp.Block(GatedEmitterFollower(
        current=self.current, rds_on=self.rds_on
      ))
      self.connect(self.amp.output, self.driver.control)
      self.high_en = self.Export(self.driver.high_en)
      self.low_en = self.Export(self.driver.low_en)

      (self.isen, ), _ = self.chain(
        self.driver.out,
        imp.Block(CurrentSenseResistor(resistance=0.1*Ohm(tol=0.01), current_limits=self.current)),
        self.out)
      self.imeas = imp.Block(DifferentialAmplifier(
        ratio=Range.from_tolerance(1, 0.05),
        input_impedance=10*kOhm(tol=0.05)))
      self.connect(self.imeas.input_positive, self.isen.sense_in)
      self.connect(self.imeas.input_negative, self.isen.sense_out)
      self.connect(self.imeas.output_reference, self.ref_center)
      self.connect(self.imeas.output, self.measured_current,
                   self.err_source.actual, self.err_sink.actual)

      self.vmeas = imp.Block(DifferentialAmplifier(
        ratio=Range.from_tolerance(1/22, 0.05),
        input_impedance=220*kOhm(tol=0.05)))
      self.connect(self.vmeas.input_positive, self.isen.pwr_out.as_analog_source())
      # TODO FIX ME - less jank bridging
      from electronics_model.VoltagePorts import VoltageSinkAdapterAnalogSource
      self.gnd_adapter = self.Block(VoltageSinkAdapterAnalogSource())
      self.connect(self.gnd_adapter.src, self.gnd)
      self.connect(self.vmeas.input_negative, self.gnd_adapter.dst)
      self.connect(self.vmeas.output_reference, self.ref_center)
      self.connect(self.vmeas.output, self.measured_voltage,
                   self.err_volt.actual)


class UsbSourceMeasureTest(BoardTop):
  def contents(self) -> None:
    super().contents()

    # USB PD port that supplies power to the load
    # TODO the transistor is only rated at Vgs=+/-20V
    self.pwr_usb = self.Block(UsbCReceptacle(voltage_out=(4.5, 20)*Volt, current_limits=(0, 5)*Amp))

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
      (self.reg_5v, self.reg_3v3, self.led_3v3), _ = self.chain(
        self.pwr_usb.pwr,
        imp.Block(BuckConverter(output_voltage=5.0*Volt(tol=0.05))),
        imp.Block(LinearRegulator(output_voltage=3.3*Volt(tol=0.05))),
        imp.Block(VoltageIndicatorLed())
      )
      self.v3v3 = self.connect(self.reg_3v3.pwr_out)

      (self.reg_analog, self.led_analog), _ = self.chain(
        self.reg_5v.pwr_out,
        imp.Block(LinearRegulator(output_voltage=3.0*Volt(tol=0.05))),
        imp.Block(VoltageIndicatorLed())
      )
      self.vanalog = self.connect(self.reg_analog.pwr_out)

      (self.ref_div, self.ref_buf), _ = self.chain(
        self.reg_analog.pwr_out,
        imp.Block(VoltageDivider(output_voltage=1.5*Volt(tol=0.05), impedance=(10, 100)*kOhm)),
        imp.Block(OpampFollower())
      )
      self.connect(self.reg_analog.pwr_out, self.ref_buf.pwr)
      self.vcenter = self.connect(self.ref_buf.output)

    with self.implicit_connect(
        ImplicitConnect(self.pwr_usb.pwr, [Power]),
        ImplicitConnect(self.gnd_merge.source, [Common]),
    ) as imp:
      self.control = imp.Block(SourceMeasureControl(
        current=(0, 3)*Amp,
        rds_on=(0, 0.2)*Ohm
      ))
      self.connect(self.control.pwr_logic, self.reg_3v3.pwr_out)
      self.connect(self.control.ref_center, self.ref_buf.output)

    with self.implicit_connect(
        ImplicitConnect(self.reg_3v3.pwr_out, [Power]),
        ImplicitConnect(self.reg_3v3.gnd, [Common]),
    ) as imp:
      self.prot_3v3 = imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.75)*Volt))

      # TODO next revision: optional clamping diode on CC lines (as present in PD buddy sink, but not OtterPill)
      self.pd = imp.Block(Fusb302b())
      self.connect(self.pd.vbus, self.pwr_usb.pwr)
      self.connect(self.pwr_usb.cc, self.pd.cc)

      self.mcu = imp.Block(Lpc1549_48(frequency=12 * MHertz(tol=0.005)))
      (self.swd, ), _ = self.chain(imp.Block(SwdCortexTargetWithTdiConnector()), self.mcu.swd)
      (self.crystal, ), _ = self.chain(self.mcu.xtal, imp.Block(OscillatorCrystal(frequency=12 * MHertz(tol=0.005))))  # TODO can we not specify this and instead infer from MCU specs?

      (self.usb_esd, ), _ = self.chain(self.data_usb.usb, imp.Block(UsbEsdDiode()), self.mcu.usb_0)

      (self.i2c_pull, ), _ = self.chain(self.mcu.i2c_0, imp.Block(I2cPullup()), self.pd.i2c)
      self.pd_int_net = self.connect(self.mcu.new_io(DigitalBidir), self.pd.int)

      self.rgb = imp.Block(IndicatorSinkRgbLed())
      self.rgb_r_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb.red)
      self.rgb_g_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb.green)
      self.rgb_b_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb.blue)

      (self.sw1, ), self.sw1_chain = self.chain(imp.Block(DigitalSwitch()), self.mcu.new_io(DigitalBidir))
      (self.sw2, ), self.sw2_chain = self.chain(imp.Block(DigitalSwitch()), self.mcu.new_io(DigitalBidir))
      (self.sw3, ), self.sw3_chain = self.chain(imp.Block(DigitalSwitch()), self.mcu.new_io(DigitalBidir))

      shared_spi = self.mcu.new_io(SpiMaster)
      self.spi_net = self.connect(shared_spi)

      self.lcd = imp.Block(Qt096t_if09())
      self.connect(self.reg_3v3.pwr_out.as_digital_source(), self.lcd.led)
      self.lcd_reset_net = self.connect(self.mcu.new_io(DigitalBidir), self.lcd.reset)
      self.lcd_rs_net = self.connect(self.mcu.new_io(DigitalBidir), self.lcd.rs)
      self.connect(shared_spi, self.lcd.spi)  # MISO unused
      self.lcd_cs_net = self.connect(self.mcu.new_io(DigitalBidir), self.lcd.cs)

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

      self.dac_v_cs_net = self.connect(self.mcu.new_io(DigitalBidir), self.dac_v.cs)
      self.dac_ip_cs_net = self.connect(self.mcu.new_io(DigitalBidir), self.dac_ip.cs)
      self.dac_in_cs_net = self.connect(self.mcu.new_io(DigitalBidir), self.dac_in.cs)
      self.adc_v_cs_net = self.connect(self.mcu.new_io(DigitalBidir), self.adc_v.cs)
      self.adc_i_cs_net = self.connect(self.mcu.new_io(DigitalBidir), self.adc_i.cs)
      self.dac_ldac_net = self.connect(self.mcu.new_io(DigitalBidir),
                   self.dac_v.ldac, self.dac_ip.ldac, self.dac_in.ldac)

      self.high_en_net = self.connect(self.mcu.new_io(DigitalBidir), self.control.high_en)
      self.low_en_net = self.connect(self.mcu.new_io(DigitalBidir), self.control.low_en)

    # TODO add UI elements: output enable tactile switch + LCD + 4 directional buttons

    self.outn = self.Block(BananaSafetyJack())
    self.connect(self.outn.port.as_voltage_sink(), self.gnd_merge.source)
    self.outp = self.Block(BananaSafetyJack())
    self.connect(self.outp.port.as_voltage_sink(), self.control.out)

    # TODO next revision: Blackberry trackball UI?

    # TODO next revision: add high precision ADCs
    # TODO next revision: add speaker?

    # Misc board
    self.duck = self.Block(DuckLogo())
    self.leadfree = self.Block(LeadFreeIndicator())
    self.id = self.Block(IdDots4())

    self.jlc_th1 = self.Block(JlcToolingHole())
    self.jlc_th2 = self.Block(JlcToolingHole())
    self.jlc_th3 = self.Block(JlcToolingHole())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['reg_5v'], Tps54202h),
        (['reg_3v3'], Xc6209),
        (['reg_analog'], Ap2210),
        (['control', 'amp', 'amp'], Opa197),
        (['control', 'imeas', 'amp'], Opa197),
        (['control', 'vmeas', 'amp'], Opa197),
        (['control', 'isen', 'res', 'res'], ChipResistor),  # big one not from JLC
        (['control', 'int', 'c'], SmtCeramicCapacitorGeneric),  # no 1nF basic parts from JLC
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], ';'.join([
          'pd_int_net=28',
          'sw1_chain_0=43',
          'sw2_chain_0=44',
          'sw3_chain_0=45',
          'rgb_b_net=46',
          'rgb_g_net=47',
          'rgb_r_net=48',

          'dac_ldac_net=1',
          'dac_in_cs_net=2',
          'dac_ip_cs_net=3',
          'spi_net.mosi=4',
          'spi_net.miso=6',
          'spi_net.sck=7',
          'adc_v_cs_net=8',
          'adc_i_cs_net=12',
          'dac_v_cs_net=13',

          'lcd_reset_net=15',
          'lcd_rs_net=18',
          'lcd_cs_net=21',

          'low_en_net=22',
          'high_en_net=23',
        ])),
        # allow the regulator to go into tracking mode
        (['reg_5v', 'dutycycle_limit'], Range(0, float('inf'))),
        # NFET option: SQJ148EP-T1_GE3, NPN BJT option: PHPT60410NYX
        (['control', 'driver', 'high_fet', 'footprint_spec'], 'Package_SO:PowerPAK_SO-8_Single'),
        (['control', 'driver', 'high_fet', 'power'], Range(0, 0)),
        # PFET option: SQJ431EP-T1_GE3, PNP BJT option: PHPT60410PYX
        (['control', 'driver', 'low_fet', 'footprint_spec'], 'Package_SO:PowerPAK_SO-8_Single'),
        (['control', 'driver', 'low_fet', 'power'], Range(0, 0)),
        # TODO debug impedance for integrator
        (['control', 'int_link', 'sink_impedance'], RangeExpr.INF),
        (['control', 'int', 'c', 'footprint_spec'], 'Capacitor_SMD:C_0603_1608Metric'),

      ],
      class_refinements=[
        (SwdCortexTargetWithTdiConnector, SwdCortexTargetTc2050),
        (Opamp, Tlv9061),  # higher precision opamps
        (SolidStateRelay, G3VM_61GR2),
        (BananaSafetyJack, Ct3151),
        (Capacitor, JlcCapacitor),
        (Resistor, JlcResistor),
      ],
    )


class UsbTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(UsbSourceMeasureTest)
