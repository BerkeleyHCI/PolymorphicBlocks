import unittest
from typing import Mapping, Optional

from electronics_abstract_parts.ESeriesUtil import ESeriesRatioUtil
from electronics_abstract_parts.ResistiveDivider import DividerValues
from electronics_model.VoltagePorts import VoltageSinkAdapterAnalogSource  # needed by imported schematic
from edg import *


class EmitterFollower(InternalSubcircuit, KiCadSchematicBlock, KiCadImportableBlock, Block):
  """Emitter follower circuit
  """
  def symbol_pinning(self, symbol_name: str) -> Mapping[str, BasePort]:
    assert symbol_name == 'edg_importable:Opamp'  # this requires an schematic-modified symbol
    return {
      'IN': self.control, '3': self.out, 'V+': self.pwr, 'V-': self.gnd
    }

  @init_in_parent
  def __init__(self, current: RangeLike, rds_on: RangeLike):
    super().__init__()

    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.gnd = self.Port(Ground.empty(), [Common])
    self.out = self.Port(VoltageSource.empty())

    self.control = self.Port(AnalogSink.empty())

    self.current = self.ArgParameter(current)
    self.rds_on = self.ArgParameter(rds_on)

  def contents(self) -> None:
    super().contents()

    zener_model = ZenerDiode((8, 10)*Volt)
    self.clamp1 = self.Block(zener_model)
    self.clamp2 = self.Block(zener_model)

    gate_voltage = (-self.clamp1.actual_zener_voltage).hull(self.clamp2.actual_zener_voltage)
    self.high_fet = self.Block(Fet.NFet(
      drain_voltage=self.pwr.link().voltage,
      drain_current=self.current,
      gate_voltage=gate_voltage,
      rds_on=self.rds_on,
      gate_charge=RangeExpr.ALL,  # don't care, it's analog not switching
      power=self.pwr.link().voltage * self.current))
    self.low_fet = self.Block(Fet.PFet(
      drain_voltage=self.pwr.link().voltage,
      drain_current=self.current,
      gate_voltage=gate_voltage,
      rds_on=self.rds_on,
      gate_charge=RangeExpr.ALL,  # don't care, it's analog not switching
      power=self.pwr.link().voltage * self.current))

    self.import_kicad(self.file_path("resources", f"{self.__class__.__name__}.kicad_sch"),
      conversions={
        'gnd': Ground(),
        'pwr': VoltageSink(
          current_draw=self.current,
          voltage_limits=self.high_fet.actual_drain_voltage_rating.intersect(
            self.low_fet.actual_drain_voltage_rating)
        ),
        'out': VoltageSource(
          voltage_out=self.pwr.link().voltage,
          current_limits=self.high_fet.actual_drain_current_rating.intersect(self.low_fet.actual_drain_current_rating)
        ),
        'control': AnalogSink(),
      })


class ErrorAmplifier(InternalSubcircuit, KiCadSchematicBlock, KiCadImportableBlock, GeneratorBlock):
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
  def symbol_pinning(self, symbol_name: str) -> Mapping[str, BasePort]:
    assert symbol_name in ('Simulation_SPICE:OPAMP', 'edg_importable:Opamp')
    return {'+': self.actual, '-': self.target, '3': self.output, 'V+': self.pwr, 'V-': self.gnd}

  @init_in_parent
  def __init__(self, diode_spec: StringLike, output_resistance: RangeLike, input_resistance: RangeLike, *,
               series: IntLike = 24, tolerance: FloatLike = 0.01):
    super().__init__()

    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.gnd = self.Port(Ground.empty(), [Common])

    self.target = self.Port(AnalogSink.empty())
    self.actual = self.Port(AnalogSink.empty())
    self.output = self.Port(AnalogSource.empty())

    self.output_resistance = self.ArgParameter(output_resistance)
    self.input_resistance = self.ArgParameter(input_resistance)
    self.diode_spec = self.ArgParameter(diode_spec)
    self.series = self.ArgParameter(series)
    self.tolerance = self.ArgParameter(tolerance)
    self.generator_param(self.input_resistance, self.diode_spec, self.series, self.tolerance)

  def generate(self) -> None:
    super().generate()

    # The 1/4 factor is a way to specify the series resistance of the divider assuming both resistors are equal,
    # since the DividerValues util only takes the parallel resistance
    calculator = ESeriesRatioUtil(ESeriesUtil.SERIES[self.get(self.series)], self.get(self.tolerance), DividerValues)
    top_resistance, bottom_resistance = calculator.find(DividerValues(Range.from_tolerance(0.5, self.get(self.tolerance)),
                                                                      self.get(self.input_resistance) / 4))

    self.amp = self.Block(Opamp())
    self.rtop = self.Block(Resistor(resistance=Range.from_tolerance(top_resistance, self.get(self.tolerance))))
    self.rbot = self.Block(Resistor(resistance=Range.from_tolerance(bottom_resistance, self.get(self.tolerance))))
    self.rout = self.Block(Resistor(resistance=self.output_resistance))

    diode_spec = self.get(self.diode_spec)
    if diode_spec:
      self.diode = self.Block(Diode(  # TODO should be encoded as a voltage difference?
        reverse_voltage=self.amp.out.voltage_out,
        current=RangeExpr.ZERO,  # an approximation, current rating not significant here
        voltage_drop=(0, 0.5)*Volt,  # arbitrary low threshold
        reverse_recovery_time=(0, 500)*nSecond  # arbitrary for "fast recovery"
      ))
      # regardless of diode direction, the port model is the same on both ends
      amp_out_model = AnalogSink(
        impedance=self.rout.actual_resistance + self.output.link().sink_impedance
      )
      rout_in_model = AnalogSource(
        impedance=self.amp.out.link().source_impedance + self.rout.actual_resistance
      )
      if diode_spec == 'source':
        nodes: Mapping[str, Optional[BasePort]] = {
          'amp_out_node': self.diode.anode.adapt_to(amp_out_model),
          'rout_in_node': self.diode.cathode.adapt_to(rout_in_model)
        }
      elif diode_spec == 'sink':
        nodes = {
          'amp_out_node': self.diode.cathode.adapt_to(amp_out_model),
          'rout_in_node': self.diode.anode.adapt_to(rout_in_model)
        }
      else:
        raise ValueError(f"invalid diode spec '{diode_spec}', expected '', 'source', or 'sink'")
    else:
      nodes = {
        'rout_in_node': self.amp.out,
        'amp_out_node': None,  # must be marked as used, but don't want to double-connect to above
      }

    self.import_kicad(self.file_path("resources", f"{self.__class__.__name__}.kicad_sch"),
        conversions={
          'target': AnalogSink(
            impedance=self.rtop.actual_resistance + self.rbot.actual_resistance
          ),
          'actual': AnalogSink(
            impedance=self.rtop.actual_resistance + self.rbot.actual_resistance
          ),
          'rtop.2': AnalogSource(
            voltage_out=self.target.link().voltage.hull(self.actual.link().voltage),
            signal_out=self.target.link().voltage.hull(self.actual.link().voltage),
            impedance=1 / (1 / self.rtop.actual_resistance + 1 / self.rbot.actual_resistance)
          ),
          'rbot.2': AnalogSink(),  # ideal, rtop.2 contains the parameter model
          'rout.1': AnalogSink(),
          'rout.2': AnalogSource(
            voltage_out=self.amp.out.link().voltage,
            signal_out=self.amp.out.link().voltage,
            impedance=self.rout.actual_resistance
          ),
        }, nodes=nodes)


class SourceMeasureControl(KiCadSchematicBlock, Block):
  """Analog feedback circuit for the source-measure unit
  """
  @init_in_parent
  def __init__(self, current: RangeLike, rds_on: RangeLike):
    super().__init__()

    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.pwr_logic = self.Port(VoltageSink.empty())
    self.gnd = self.Port(Ground.empty(), [Common])
    self.ref_center = self.Port(AnalogSink.empty())

    self.pwr_gate_pos = self.Port(VoltageSink.empty())
    self.pwr_gate_neg = self.Port(VoltageSink.empty())

    self.control_voltage = self.Port(AnalogSink.empty())
    self.control_current_source = self.Port(AnalogSink.empty())
    self.control_current_sink = self.Port(AnalogSink.empty())
    self.drv_en = self.Port(DigitalSink.empty())
    self.off = self.Port(Vector(DigitalSink.empty()))
    self.out = self.Port(VoltageSource.empty())

    self.measured_voltage = self.Port(AnalogSource.empty())
    self.measured_current = self.Port(AnalogSource.empty())

    self.current = self.ArgParameter(current)
    self.rds_on = self.ArgParameter(rds_on)

  def contents(self):
    super().contents()

    self.import_kicad(self.file_path("resources", f"{self.__class__.__name__}.kicad_sch"),
      locals={
        'err_volt': {
          'output_resistance': 4.7*kOhm(tol=0.05),
          'input_resistance': (10, 100)*kOhm
        },
        'err_current': {
          'output_resistance': 1*Ohm(tol=0.05),
          'input_resistance': (10, 100)*kOhm,
        },
        'int': {
          'factor': Range.from_tolerance(1 / 4.7e-6, 0.15),
          'capacitance': 1*nFarad(tol=0.1),
        },
        'amp': {
          'amplification': Range.from_tolerance(20, 0.05),
          'impedance': (1, 10)*kOhm
        },
        'driver': {
          'current': self.current,
          'rds_on': self.rds_on
        },
        'imeas': {
          'resistance': 0.1*Ohm(tol=0.01),
          'ratio': Range.from_tolerance(1, 0.05),
          'input_impedance': 10*kOhm(tol=0.05)
        },
        'vmeas': {
          'ratio': Range.from_tolerance(1/24, 0.05),
          'input_impedance': 220*kOhm(tol=0.05)
        },
        'clamp': {
          'voltage': (2.5, 3.0)*Volt
        }
      })


class UsbSourceMeasure(JlcBoardTop):
  def contents(self) -> None:
    super().contents()

    # overall design parameters
    OUTPUT_CURRENT_RATING = (0, 1)*Amp

    # USB PD port that supplies power to the load
    # TODO the transistor is only rated at Vgs=+/-20V
    self.usb = self.Block(UsbCReceptacle(voltage_out=(9, 20)*Volt, current_limits=(0, 5)*Amp))

    self.gnd = self.connect(self.usb.gnd)
    self.vusb = self.connect(self.usb.pwr)

    self.tp_vusb = self.Block(VoltageTestPoint()).connected(self.usb.pwr)
    self.tp_gnd = self.Block(VoltageTestPoint()).connected(self.usb.gnd)

    # power supplies
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      # logic supplies
      (self.reg_6v, self.tp_6v, self.reg_3v3, self.tp_3v3), _ = self.chain(
        self.vusb,
        imp.Block(BuckConverter(output_voltage=6.0*Volt(tol=0.05))),  # high enough to power gate driver
        self.Block(VoltageTestPoint()),
        imp.Block(LinearRegulator(output_voltage=3.3*Volt(tol=0.05))),
        self.Block(VoltageTestPoint())
      )
      self.v6 = self.connect(self.reg_6v.pwr_out)
      self.v3v3 = self.connect(self.reg_3v3.pwr_out)

      # output power supplies
      (self.conv_force, self.conv, self.tp_conv), _ = self.chain(
        self.vusb,
        imp.Block(ForcedVoltage(20*Volt(tol=0))),
        imp.Block(CustomSyncBuckBoostConverter(output_voltage=(15, 32) * Volt,
                                               frequency=500*kHertz(tol=0),
                                               ripple_current_factor=(0.01, 0.9),
                                               input_ripple_limit=250*mVolt,
                                               )),
        self.Block(VoltageTestPoint())
      )
      self.connect(self.conv.pwr_logic, self.v6)
      self.vconv = self.connect(self.conv.pwr_out)

      # analog supplies
      (self.reg_analog, self.tp_analog), _ = self.chain(
        self.v6,
        imp.Block(LinearRegulator(output_voltage=3.3*Volt(tol=0.05))),
        self.Block(VoltageTestPoint())
      )
      self.vanalog = self.connect(self.reg_analog.pwr_out)

      (self.ref_div, self.ref_buf), _ = self.chain(
        self.vanalog,
        imp.Block(VoltageDivider(output_voltage=1.5*Volt(tol=0.05), impedance=(10, 100)*kOhm)),
        imp.Block(OpampFollower())
      )
      self.connect(self.vanalog, self.ref_buf.pwr)
      self.vcenter = self.connect(self.ref_buf.output)

    # power path domain
    with self.implicit_connect(
        ImplicitConnect(self.vconv, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      # zener shunt in case the boost converter goes crazy
      self.prot_conv = imp.Block(ProtectionZenerDiode(voltage=(32, 38)*Volt))
      self.control = imp.Block(SourceMeasureControl(
        current=OUTPUT_CURRENT_RATING,
        rds_on=(0, 0.2)*Ohm
      ))
      self.connect(self.vanalog, self.control.pwr_logic)
      self.connect(self.vcenter, self.control.ref_center)

      self.boot = self.Block(BootstrapVoltageAdder(frequency=1*MHertz(tol=0)))
      self.connect(self.boot.gnd, self.gnd)
      self.connect(self.boot.pwr, self.v3v3)
      self.connect(self.boot.pwr_neg, self.gnd)
      self.connect(self.boot.pwr_pos, self.conv.pwr_out)
      self.boot_neg_forced = self.Block(ForcedVoltage(0*Volt(tol=0)))  # TODO: support non-zero grounds
      self.connect(self.boot_neg_forced.pwr_in, self.boot.out_neg)
      self.connect(self.boot_neg_forced.pwr_out, self.control.pwr_gate_neg)
      self.connect(self.boot.out_pos, self.control.pwr_gate_pos)

      self.tp_boot_neg = self.Block(VoltageTestPoint("vb-")).connected(self.boot.out_neg)
      self.tp_boot_pos = self.Block(VoltageTestPoint("vb+")).connected(self.boot.out_pos)

    # logic domain
    with self.implicit_connect(
        ImplicitConnect(self.v3v3, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.prot_3v3 = imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.75)*Volt))

      # TODO next revision: optional clamping diode on CC lines (as present in PD buddy sink, but not OtterPill)
      self.pd = imp.Block(Fusb302b())
      self.connect(self.usb.pwr, self.pd.vbus)
      self.connect(self.usb.cc, self.pd.cc)

      self.mcu = imp.Block(IoController())
      (self.led, ), _ = self.chain(imp.Block(IndicatorSinkLed(Led.Red)), self.mcu.gpio.request('led'))  # debugging LED

      (self.usb_esd, ), self.usb_chain = self.chain(self.usb.usb, imp.Block(UsbEsdDiode()),
                                                    self.mcu.usb.request())

      shared_spi = self.mcu.spi.request('spi')
      shared_i2c = self.mcu.i2c.request('i2c')
      self.i2c_tp = self.Block(I2cTestPoint('i2c')).connected(shared_i2c)
      (self.i2c_pull, ), _ = self.chain(shared_i2c, imp.Block(I2cPullup()), self.pd.i2c)
      self.connect(self.mcu.gpio.request('pd_int'), self.pd.int)

      self.rgb = imp.Block(IndicatorSinkRgbLed())
      self.connect(self.mcu.gpio.request_vector('rgb'), self.rgb.signals)

      self.oled = imp.Block(Er_Oled_096_1_1())
      self.connect(shared_i2c, self.oled.i2c)
      self.connect(self.mcu.gpio.request('oled_reset'), self.oled.reset)

      self.connect(self.mcu.gpio.request('drv_en'), self.control.drv_en)
      self.connect(self.mcu.gpio.request_vector('off'), self.control.off)

      pull_model = PulldownResistor(10*kOhm(tol=0.05))
      rc_model = DigitalLowPassRc(150*Ohm(tol=0.05), 7*MHertz(tol=0.2))
      (self.buckl_pull, self.buckl_rc, self.buckl_tp), _ = self.chain(
        self.mcu.gpio.request('buck_pwm_low'),
        imp.Block(pull_model), imp.Block(rc_model),
        self.Block(DigitalTestPoint("bul")), self.conv.buck_pwm_low)
      (self.buckh_pull, self.buckh_rc, self.buckh_tp), _ = self.chain(
        self.mcu.gpio.request('buck_pwm_high'),
        imp.Block(pull_model), imp.Block(rc_model),
        self.Block(DigitalTestPoint("buh")), self.conv.buck_pwm_high)
      (self.boostl_pull, self.boostl_rc, self.boostl_tp), _ = self.chain(
        self.mcu.gpio.request('boost_pwm_low'),
        imp.Block(pull_model), imp.Block(rc_model),
        self.Block(DigitalTestPoint("bol")), self.conv.boost_pwm_low)
      (self.boosth_pull, self.boosth_rc, self.boosth_tp), _ = self.chain(
        self.mcu.gpio.request('boost_pwm_high'),
        imp.Block(pull_model), imp.Block(rc_model),
        self.Block(DigitalTestPoint("boh")), self.conv.boost_pwm_high)

      self.connect(self.mcu.gpio.request('boot_pwm'), self.boot.pwm)

      (self.pass_temp, ), _ = self.chain(shared_i2c, imp.Block(Tmp1075n(0)))
      (self.conv_temp, ), _ = self.chain(shared_i2c, imp.Block(Tmp1075n(1)))
      (self.conv_sense, ), _ = self.chain(
        self.vconv,
        imp.Block(VoltageSenseDivider(full_scale_voltage=2.2*Volt(tol=0.1), impedance=(1, 10)*kOhm)),
        self.mcu.adc.request('vconv_sense')
      )

      self.ioe = imp.Block(Pca9554())
      self.connect(self.ioe.i2c, shared_i2c)
      self.enc = imp.Block(DigitalRotaryEncoder())
      self.connect(self.enc.a, self.ioe.io.request('enc_a'))
      self.connect(self.enc.b, self.ioe.io.request('enc_b'))
      self.connect(self.enc.with_mixin(DigitalRotaryEncoderSwitch()).sw, self.ioe.io.request('enc_sw'))
      self.dir = imp.Block(DigitalDirectionSwitch())
      self.connect(self.dir.a, self.ioe.io.request('dir_a'))
      self.connect(self.dir.b, self.ioe.io.request('dir_b'))
      self.connect(self.dir.c, self.ioe.io.request('dir_c'))
      self.connect(self.dir.d, self.ioe.io.request('dir_d'))
      self.connect(self.dir.with_mixin(DigitalDirectionSwitchCenter()).center, self.ioe.io.request('dir_cen'))

    # analog domain
    with self.implicit_connect(
        ImplicitConnect(self.vanalog, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.dac = imp.Block(Mcp4728())
      self.connect(self.dac.out0, self.control.control_voltage)
      self.connect(self.dac.out1, self.control.control_current_sink)
      self.connect(self.dac.out2, self.control.control_current_source)
      self.connect(self.dac.i2c, shared_i2c)
      self.connect(self.dac.ldac, self.mcu.gpio.request('ldac'))

      self.adc = imp.Block(Mcp3561())
      self.connect(self.adc.pwra, self.vanalog)
      self.connect(self.adc.pwr, self.vanalog)  # TODO: digital rail
      self.connect(self.adc.spi, shared_spi)
      self.connect(self.adc.cs, self.mcu.gpio.request('adc_cs'))
      self.connect(self.adc.vins.request('0'), self.vcenter)
      self.connect(self.adc.vins.request('1'), self.control.measured_current)
      self.connect(self.adc.vins.request('2'), self.control.measured_voltage)

    self.outn = self.Block(BananaSafetyJack())
    self.connect(self.gnd, self.outn.port.adapt_to(Ground()))
    self.outp = self.Block(BananaSafetyJack())
    self.connect(self.outp.port.adapt_to(VoltageSink(
      current_draw=OUTPUT_CURRENT_RATING
    )), self.control.out)

  def multipack(self) -> None:
    self.vimeas_amps = self.PackedBlock(Opa2197())
    self.pack(self.vimeas_amps.elements.request('0'), ['control', 'vmeas', 'amp'])
    self.pack(self.vimeas_amps.elements.request('1'), ['control', 'imeas', 'amp', 'amp'])

    self.ampdmeas_amps = self.PackedBlock(Opa2197())
    self.pack(self.ampdmeas_amps.elements.request('0'), ['control', 'amp', 'amp'])
    self.pack(self.ampdmeas_amps.elements.request('1'), ['control', 'dmeas', 'amp'])

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32s3_Wroom_1),
        (['reg_6v'], Tps54202h),
        (['reg_3v3'], Ldl1117),
        (['reg_analog'], Ap2210),

        (['control', 'driver', 'low_fet'], CustomFet),
        (['control', 'driver', 'high_fet'], CustomFet),
      ],
      class_refinements=[
        (EspProgrammingHeader, EspProgrammingTc2030),
        (Opamp, Tlv9061),  # higher precision opamps
        (AnalogSwitch, Nlas4157),
        (SolidStateRelay, Tlp3545a),
        (BananaSafetyJack, Ct3151),
        (HalfBridgeDriver, Ucc27282),
        (DirectionSwitch, Skrh),
        (TestPoint, CompactKeystone5015),
        (RotaryEncoder, Pec11s),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
          # note: for ESP32-S3 compatibility: IO35/36/37 (pins 28-30) are used by PSRAM
          # note: for ESP32-C6 compatibility: pin 34 (22 on dedicated -C6 pattern) is NC
          'rgb_green=20',
          'rgb_red=21',
          'rgb_blue=22',
          'oled_reset=23',

          'adc_cs=4',
          'spi.sck=5',
          'spi.mosi=6',
          'spi.miso=7',
          'i2c.scl=8',
          'i2c.sda=9',
          'ldac=10',
          'drv_en=11',
          'off_0=12',
          'boost_pwm_high=31',
          'boost_pwm_low=32',
          'buck_pwm_high=33',
          'buck_pwm_low=35',
          'boot_pwm=38',
          'pd_int=39',

          'led=_GPIO0_STRAP',

          'vconv_sense=18',
        ]),
        (['mcu', 'programming'], 'uart-auto'),

        (['ioe', 'pin_assigns'], [
          'dir_a=5',
          'dir_cen=6',
          'dir_c=7',
          'dir_d=4',
          'dir_b=12',
          'enc_sw=11',
          'enc_a=9',
          'enc_b=10',
        ]),

        # allow the regulator to go into tracking mode
        (['reg_6v', 'power_path', 'dutycycle_limit'], Range(0, float('inf'))),
        (['reg_6v', 'power_path', 'inductor_current_ripple'], Range(0.01, 0.5)),  # trade higher Imax for lower L
        # JLC does not have frequency specs, must be checked TODO
        (['reg_6v', 'power_path', 'inductor', 'manual_frequency_rating'], Range.all()),
        (['conv', 'power_path', 'inductor', 'manual_frequency_rating'], Range.all()),

        # ignore derating on 20v - it's really broken =(
        (['reg_6v', 'power_path', 'in_cap', 'cap', 'exact_capacitance'], False),
        (['reg_6v', 'power_path', 'in_cap', 'cap', 'voltage_rating_derating'], 0.85),
        (['conv', 'power_path', 'in_cap', 'cap', 'exact_capacitance'], False),
        (['conv', 'power_path', 'in_cap', 'cap', 'voltage_rating_derating'], 0.85),
        (['conv', 'power_path', 'out_cap', 'cap', 'exact_capacitance'], False),
        (['conv', 'power_path', 'out_cap', 'cap', 'voltage_rating_derating'], 0.85),
        (['conv', 'boost_sw', 'high_fet', 'gate_voltage'], ParamValue(
          ['conv', 'boost_sw', 'low_fet', 'gate_voltage']
        )),  # TODO model is broken for unknown reasons
        (['boot', 'c_fly_pos', 'voltage_rating_derating'], 0.85),
        (['boot', 'c_fly_neg', 'voltage_rating_derating'], 0.85),
        (['conv', 'buck_sw', 'low_fet', 'manual_gate_charge'], Range.exact(100e-9)),  # reasonable worst case estimate
        (['conv', 'buck_sw', 'high_fet', 'manual_gate_charge'], ParamValue(['conv', 'buck_sw', 'low_fet', 'manual_gate_charge'])),
        (['conv', 'boost_sw', 'low_fet', 'manual_gate_charge'], ParamValue(['conv', 'buck_sw', 'low_fet', 'manual_gate_charge'])),
        (['conv', 'boost_sw', 'high_fet', 'manual_gate_charge'], ParamValue(['conv', 'buck_sw', 'low_fet', 'manual_gate_charge'])),
        (['conv', 'buck_sw', 'low_fet', 'part'], ParamValue(['conv', 'boost_sw', 'low_fet', 'actual_part'])),  # require all FETs the same
        (['conv', 'buck_sw', 'high_fet', 'part'], ParamValue(['conv', 'boost_sw', 'low_fet', 'actual_part'])),
        (['conv', 'boost_sw', 'high_fet', 'part'], ParamValue(['conv', 'boost_sw', 'low_fet', 'actual_part'])),
        (['conv', 'buck_sw', 'gate_res'], Range.from_tolerance(10, 0.05)),
        (['conv', 'boost_sw', 'gate_res'], ParamValue(['conv', 'buck_sw', 'gate_res'])),

        (['control', 'int_link', 'sink_impedance'], RangeExpr.INF),  # waive impedance check for integrator in

        (['control', 'imeas', 'sense', 'res', 'res', 'footprint_spec'], 'Resistor_SMD:R_2512_6332Metric'),
        (['control', 'imeas', 'sense', 'res', 'res', 'require_basic_part'], False),

        (['control', 'driver', 'high_fet', 'footprint_spec'], 'Package_TO_SOT_SMD:TO-252-2'),
        (['control', 'driver', 'high_fet', 'part_spec'], 'SQD50N10-8M9L_GE3'),
        (['control', 'driver', 'low_fet', 'footprint_spec'], 'Package_TO_SOT_SMD:TO-252-2'),
        (['control', 'driver', 'low_fet', 'part_spec'], 'SQD50P06-15L_GE3'),  # has a 30V/4A SOA

        (['prot_conv', 'diode', 'footprint_spec'], 'Diode_SMD:D_SMA'),
        (['conv', 'power_path', 'inductor', 'part'], 'SLF12575T-470M2R7-PF'),  # first auto pick is OOS
      ],
      class_values=[
        (Diode, ['footprint_spec'], 'Diode_SMD:D_SOD-323'),
        (ZenerDiode, ['footprint_spec'], 'Diode_SMD:D_SOD-323'),
        (CompactKeystone5015, ['lcsc_part'], 'C5199798'),  # RH-5015, which is actually in stock

        (Er_Oled_096_1_1, ['device', 'vbat', 'voltage_limits'], Range(3.0, 4.2)),  # technically out of spec
        (Er_Oled_096_1_1, ['device', 'vdd', 'voltage_limits'], Range(1.65, 4.0)),  # use abs max rating
      ]
    )


class UsbSourceMeasureTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(UsbSourceMeasure)
