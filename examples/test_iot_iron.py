import unittest

from edg import *


class IronConnector(Connector, Block):
  """See main design for details about pinning and compatibility.
  This assumes a common ground with heater+ and thermocouple+.
  TODO: support series heater and thermocouple, requires additional protection circuits on amps
  TODO: optional generation for isense_res, if not connected
  """
  @init_in_parent
  def __init__(self, *, isense_resistance: RangeLike = 22*mOhm(tol=0.05), current_draw: RangeLike=(0, 3.25)*Amp):
    super().__init__()
    self.conn = self.Block(PinHeader254(3))

    self.gnd = self.Port(Ground.empty(), [Common])
    self.pwr = self.Export(self.conn.pins.request('2').adapt_to(VoltageSink(
      current_draw=current_draw
    )))
    self.thermocouple = self.Export(self.conn.pins.request('3').adapt_to(AnalogSource(
      voltage_out=self.gnd.link().voltage + (0, 14.3)*mVolt,
      signal_out=self.gnd.link().voltage + (0, 14.3)*mVolt  # up to ~350 C
    )), optional=True)

    self.isense_res = self.Block(CurrentSenseResistor(resistance=isense_resistance, sense_in_reqd=False))
    self.isense = self.Export(self.isense_res.sense_out)
    self.connect(self.conn.pins.request('1').adapt_to(VoltageSink(current_draw=current_draw)),
                 self.isense_res.pwr_out)
    self.connect(self.gnd.as_voltage_source(), self.isense_res.pwr_in)


class IotIron(JlcBoardTop):
  """IoT soldering iron controller (ceramic heater type, not RF heating type) with USB-PD in,
  buck converter for maximum compatibility and reduced EMI, and builtin UI components (in addition
  to wireless connectivity).

  Inspired by https://github.com/AxxAxx/AxxSolder/tree/main, see repo README for links on connector pinning.
  """
  def contents(self) -> None:
    super().contents()

    # assume minimum power input of 12v from PD, you probably don't want a 5v USB 15W soldering iron
    self.usb = self.Block(UsbCReceptacle(voltage_out=(12, 20)*Volt, current_limits=(0, 5)*Amp))

    self.vusb = self.connect(self.usb.pwr)
    self.gnd = self.connect(self.usb.gnd)

    self.tp_pwr = self.Block(VoltageTestPoint()).connected(self.usb.pwr)
    self.tp_gnd = self.Block(GroundTestPoint()).connected(self.usb.gnd)

    # POWER
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.reg_3v3, self.tp_3v3, self.prot_3v3), _ = self.chain(
        self.vusb,
        imp.Block(BuckConverter(output_voltage=3.3*Volt(tol=0.05),
                                input_ripple_limit=100*mVolt)),
        self.Block(VoltageTestPoint()),
        imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.9)*Volt))
      )
      self.v3v3 = self.connect(self.reg_3v3.pwr_out)

      # set gate driver at 9v to allow power from USB-PD 9v
      (self.reg_gate, self.tp_gate), _ = self.chain(
        self.vusb,
        imp.Block(VoltageRegulator(output_voltage=12*Volt(tol=0.06))),
        self.Block(VoltageTestPoint())
      )
      self.vgate = self.connect(self.reg_gate.pwr_out)

    # 3V3 DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.v3v3, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())
      self.mcu.with_mixin(IoControllerWifi())
      self.i2c = self.mcu.i2c.request('i2c')
      (self.i2c_pull, ), _ = self.chain(self.i2c, imp.Block(I2cPullup()))

      # power input
      self.pd = imp.Block(Fusb302b())
      self.connect(self.usb.pwr, self.pd.vbus)
      self.connect(self.usb.cc, self.pd.cc)
      self.connect(self.mcu.gpio.request('pd_int'), self.pd.int)
      self.connect(self.i2c, self.pd.i2c)

      (self.usb_esd, ), self.usb_chain = self.chain(self.usb.usb, imp.Block(UsbEsdDiode()),
                                                    self.mcu.usb.request())

      (self.vusb_sense, ), _ = self.chain(
        self.vusb,
        imp.Block(VoltageSenseDivider(full_scale_voltage=2.2*Volt(tol=0.1), impedance=(1, 10)*kOhm)),
        self.mcu.adc.request('vusb_sense')
      )

      # sensing - cold junction compensation
      (self.temp, ), _ = self.chain(self.i2c, imp.Block(Hdc1080()))

      # onboard user interface
      self.enc = imp.Block(DigitalRotaryEncoder())
      self.connect(self.enc.a, self.mcu.gpio.request('enc_a'))
      self.connect(self.enc.b, self.mcu.gpio.request('enc_b'))
      self.connect(self.enc.with_mixin(DigitalRotaryEncoderSwitch()).sw, self.mcu.gpio.request('enc_sw'))

      self.oled = imp.Block(Er_Oled_096_1_1())
      self.connect(self.i2c, self.oled.i2c)
      self.connect(self.mcu.gpio.request('oled_reset'), self.oled.reset)

      (self.spk_drv, self.spk), _ = self.chain(
        self.mcu.with_mixin(IoControllerI2s()).i2s.request('spk'),
        imp.Block(Max98357a()),
        self.Block(Speaker())
      )

      # debugging LEDs
      (self.ledr, ), _ = self.chain(imp.Block(IndicatorSinkLed(Led.Red)), self.mcu.gpio.request('led'))


    # IRON POWER SUPPLY
    with self.implicit_connect(
            ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.conv_force, self.conv, self.tp_conv), _ = self.chain(
        self.vusb,
        imp.Block(ForcedVoltage(20*Volt(tol=0))),
        # want a high output ripple limit so the converter turns off fast to read the thermocouple
        imp.Block(CustomSyncBuckConverterIndependent(output_voltage=(5, 5) * Volt, frequency=200 * kHertz(tol=0),
                                                     input_ripple_limit=1*Volt,
                                                     output_ripple_limit=0.25*Volt)),
        self.Block(VoltageTestPoint())
      )
      self.conv_out = self.connect(self.conv.pwr_out)
      self.connect(self.conv.pwr_logic, self.vgate)
      pull_model = PulldownResistor(10*kOhm(tol=0.05))
      rc_model = DigitalLowPassRc(150*Ohm(tol=0.05), 7*MHertz(tol=0.2))
      (self.low_pull, self.low_rc), _ = self.chain(self.mcu.gpio.request('pwm_low'),
                                                   imp.Block(pull_model),
                                                   imp.Block(rc_model),
                                                   self.conv.pwm_low)
      (self.high_pull, self.high_rc), _ = self.chain(self.mcu.gpio.request('pwm_high'),
                                                    imp.Block(pull_model),
                                                    imp.Block(rc_model),
                                                    self.conv.pwm_high)
      self.tp_pwm_l = self.Block(DigitalTestPoint()).connected(self.conv.pwm_low)
      self.tp_pwm_h = self.Block(DigitalTestPoint()).connected(self.conv.pwm_high)

      mcu_touch = self.mcu.with_mixin(IoControllerTouchDriver())
      (self.touch_sink, ), _ = self.chain(
        mcu_touch.touch.request('touch'),
        imp.Block(FootprintToucbPad('edg:Symbol_DucklingSolid'))
      )

    self.iron = self.Block(IronConnector())
    self.connect(self.conv.pwr_out, self.iron.pwr)

    # IRON SENSE AMPS - 3v3 DOMAIN
    with self.implicit_connect(
            ImplicitConnect(self.v3v3, [Power]),
            ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      rc_filter_model = AnalogLowPassRc(impedance=1*kOhm(tol=0.1), cutoff_freq=(1, 10)*kHertz)
      (self.vsense, self.tp_v, self.vfilt), _ = self.chain(
        self.conv.pwr_out,
        imp.Block(VoltageSenseDivider(full_scale_voltage=2.2*Volt(tol=0.1), impedance=(1, 10)*kOhm)),
        self.Block(AnalogTestPoint()),
        imp.Block(rc_filter_model),
        self.mcu.adc.request('iron_vsense')
      )
      (self.ifilt, self.tp_i, self.iamp), _ = self.chain(
        self.iron.sense_out,
        imp.Block(Amplifier((18, 25))),
        imp.Block(rc_filter_model),
        self.Block(AnalogTestPoint()),
        self.mcu.adc.request('iron_isense')
      )

      self.tamp = imp.Block(DifferentialAmplifier(
        ratio=(150, 165),
        input_impedance=(0.9, 5)*kOhm
      ))
      self.connect(self.tamp.input_negative, self.iron.gnd.as_analog_source())
      self.connect(self.tamp.input_positive, self.iron.thermocouple)
      self.connect(self.tamp.output, self.mcu.adc.request('thermocouple'))
      self.tp_t = self.Block(AnalogTestPoint()).connected(self.iron.thermocouple)

  def multipack(self) -> None:
    self.packed_opamp = self.PackedBlock(Opa2333())
    self.pack(self.packed_opamp.elements.request('0'), ['ifilt', 'amp'])
    self.pack(self.packed_opamp.elements.request('1'), ['tamp', 'amp'])

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32s3_Wroom_1),
        (['reg_3v3'], Tps54202h),
        (['reg_gate'], L78l),
      ],
      instance_values=[
        (['refdes_prefix'], 'I'),  # unique refdes for panelization
        (['mcu', 'pin_assigns'], [
          'vusb_sense=39',
          'i2c.sda=34',
          'i2c.scl=35',
          'pd_int=38',

          'spk.sd=33',
          'spk.sck=32',
          'spk.ws=31',

          'pwm_low=4',
          'pwm_high=5',

          'iron_vsense=6',
          'iron_isense=7',
          'thermocouple=12',

          'enc_a=10',
          'enc_b=9',
          'enc_sw=8',
          'oled_reset=11',

          'led=_GPIO0_STRAP',
          'touch=GPIO3',  # experimental
        ]),
        (['mcu', 'programming'], 'uart-auto'),

        (['isense', 'res', 'res', 'smd_min_package'], '2512'),  # more power headroom
        (['isense', 'res', 'res', 'require_basic_part'], False),

        # these will be enforced by the firmware control mechanism
        # (['conv', 'pwr_in', 'current_draw'], Range(0, 3)),  # max 3A input draw
        # force JLC frequency spec
        (['conv', 'power_path', 'inductor', 'part'], 'SLF12565T-150M4R2-PF'),
        (['conv', 'power_path', 'inductor', 'manual_frequency_rating'], Range(0, 1e6)),  # from charts, inductance constant up to 1MHz
        (['reg_3v3', 'power_path', 'inductor', 'part'], 'SWPA5040S220MT'),
        (['reg_3v3', 'power_path', 'inductor', 'manual_frequency_rating'], Range(0, 11e6)),

        (['reg_gate', 'ic', 'actual_dropout'], Range.exact(0)),  # allow tracking

        (['conv', 'sw', 'high_fet', 'part'], ParamValue(['conv', 'sw', 'low_fet', 'part'])),
        (['conv', 'sw', 'low_fet', 'manual_gate_charge'], Range.exact(100e-9)),  # reasonable worst case estimate
        (['conv', 'sw', 'high_fet', 'manual_gate_charge'], ParamValue(['conv', 'sw', 'low_fet', 'manual_gate_charge'])),
      ],
      class_refinements=[
        (HalfBridgeDriver, Ucc27282),
        (Speaker, ConnectorSpeaker),
        (PassiveConnector, JstPhKVertical),  # default connector series unless otherwise specified
        (EspProgrammingHeader, EspProgrammingTc2030),
        (TagConnect, TagConnectNonLegged),
        (TestPoint, CompactKeystone5015),
      ],
      class_values=[
        (ZenerDiode, ['footprint_spec'], 'Diode_SMD:D_SOD-323'),
        (CompactKeystone5015, ['lcsc_part'], 'C5199798'),  # RH-5015, which is actually in stock

        (Er_Oled_096_1_1, ['device', 'vbat', 'voltage_limits'], Range(3.0, 4.2)),  # technically out of spec
        (Er_Oled_096_1_1, ['device', 'vdd', 'voltage_limits'], Range(1.65, 4.0)),  # use abs max rating
      ]
    )


class IotIronTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(IotIron)
