import unittest

from edg import *


class IronConnector(Connector, Block):
  """
  TODO REFERENCE LINK AND PINNING
  """
  @init_in_parent
  def __init__(self):
    super().__init__()
    self.conn = self.Block(PinHeader254(3))

    self.gnd = self.Export(self.conn.pins.request('1').adapt_to(Ground()),
                           [Common])
    self.pwr = self.Export(self.conn.pins.request('2').adapt_to(VoltageSink(
      current_draw=(0, 3.25)*Amp
    )))
    self.thermocouple = self.Export(self.conn.pins.request('3').adapt_to(AnalogSource(
      # TODO SPECS
    )), optional=True)


class IotIron(JlcBoardTop):
  """IoT soldering iron controller (ceramic heater type, not RF heating type) with USB-PD in,
  buck converter for maximum compatibility and reduced EMI, and builtin UI components (in addition
  to wireless connectivity).
  """
  def contents(self) -> None:
    super().contents()

    self.usb = self.Block(UsbCReceptacle(voltage_out=(4.5, 20)*Volt, current_limits=(0, 5)*Amp))

    self.vusb = self.connect(self.usb.pwr)
    self.gnd = self.connect(self.usb.gnd)

    self.tp_pwr = self.Block(VoltageTestPoint()).connected(self.usb.pwr)
    self.tp_gnd = self.Block(VoltageTestPoint()).connected(self.usb.gnd)

    # POWER
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.reg_3v3, self.tp_3v3, self.prot_3v3), _ = self.chain(
        self.vusb,
        imp.Block(VoltageRegulator(output_voltage=3.3*Volt(tol=0.05))),
        self.Block(VoltageTestPoint()),
        imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.9)*Volt))
      )
      self.v3v3 = self.connect(self.reg_3v3.pwr_out)

    # 3V3 DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.v3v3, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())
      self.mcu.with_mixin(IoControllerWifi())
      self.i2c = self.mcu.i2c.request()
      (self.i2c_pull, ), _ = self.chain(self.i2c, imp.Block(I2cPullup()))

      # power input
      self.pd = imp.Block(Fusb302b())
      self.connect(self.usb.pwr, self.pd.vbus)
      self.connect(self.usb.cc, self.pd.cc)
      self.connect(self.mcu.gpio.request('pd_int'), self.pd.int)
      self.connect(self.i2c, self.pd.i2c)

      (self.usb_esd, ), _ = self.chain(self.usb.usb, imp.Block(UsbEsdDiode()),
                                       self.mcu.usb.request())

      (self.vusb_sense, ), _ = self.chain(
        self.vusb,
        imp.Block(VoltageSenseDivider(full_scale_voltage=2.2*Volt(tol=0.1), impedance=(1, 10)*kOhm)),
        self.mcu.adc.request('vusb_sense')
      )

      # sensing
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
        self.mcu.with_mixin(IoControllerI2s()).i2s.request('speaker'),
        imp.Block(Max98357a()),
        self.Block(Speaker())
      )

      # debugging LEDs
      (self.ledr, ), _ = self.chain(imp.Block(IndicatorSinkLed(Led.Red)), self.mcu.gpio.request('led'))


    # IRON POWER SUPPLY
    with self.implicit_connect(
            ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.conv_force, self.conv), _ = self.chain(
        self.vusb,
        imp.Block(ForcedVoltage(20*Volt(tol=0))),
        imp.Block(CustomBuckConverter(output_voltage=(5, 5)*Volt, pwm_frequency=200*kHertz(tol=0),
                                                input_ripple_limit=0.25*Volt,
                                                output_ripple_limit=0.25*Volt))
      )
      self.conv_out = self.conv.pwr_out
      self.connect(self.conv.pwm, self.mcu.gpio.request('buck'))

      self.iron = imp.Block(IronConnector())
      self.connect(self.conv.pwr_out, self.iron.pwr)

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32s3_Wroom_1),
        (['reg_3v3'], Tps54202h),
      ],
      instance_values=[
        (['refdes_prefix'], 'I'),  # unique refdes for panelization
        (['mcu', 'pin_assigns'], [
          # 'v12_sense=4',
          # 'rgb=_GPIO2_STRAP',  # force using the strapping pin, since we're out of IOs
          # 'led=_GPIO9_STRAP',  # force using the strapping / boot mode pin
          #
          # 'fan_drv_0=5',
          # 'fan_ctl_0=8',
          # 'fan_sense_0=9',
          #
          # 'fan_drv_1=10',
          # 'fan_ctl_1=13',
          # 'fan_sense_1=12',
          #
          # 'enc_sw=25',
          # 'enc_b=16',
          # 'enc_a=26',
        ]),
        (['mcu', 'programming'], 'uart-auto'),

        # these will be enforced by the firmware control mechanism
        # (['conv', 'pwr_in', 'current_draw'], Range(0, 3)),  # max 3A input draw
        # force JLC frequency spec
        (['conv', 'power_path', 'inductor', 'part'], 'SLF12565T-150M4R2-PF'),
        (['conv', 'power_path', 'inductor', 'manual_frequency_rating'], Range(0, 1e6)),  # from charts, inductance constant up to 1MHz
        (['reg_3v3', 'power_path', 'inductor', 'part'], 'SWPA5040S220MT'),
        (['reg_3v3', 'power_path', 'inductor', 'manual_frequency_rating'], Range(0, 11e6)),
      ],
      class_refinements=[
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