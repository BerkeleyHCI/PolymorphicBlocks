import unittest

from edg import *


class IotKnob(JlcBoardTop):
  """IoT knob with lights, buttons, and a screen.
  """
  def contents(self) -> None:
    super().contents()

    KNOB_LEDS = 4  # number of RGBs for knob underglow
    RING_LEDS = 24  # number of RGBs for the ring indicator
    NUM_SECTIONS = 6  # number of buttons

    self.usb = self.Block(UsbCReceptacle(current_limits=(0, 3)*Amp))

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
        imp.Block(LinearRegulator(output_voltage=3.3*Volt(tol=0.05))),
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

      self.i2c = self.mcu.i2c.request('i2c')
      (self.i2c_pull, self.i2c_tp), self.i2c_chain = self.chain(
        self.i2c,
        imp.Block(I2cPullup()), imp.Block(I2cTestPoint()))

      # need to name the USB chain so the USB net has the _N and _P postfix for differential traces
      (self.usb_esd, ), self.usb_chain = self.chain(self.usb.usb, imp.Block(UsbEsdDiode()), self.mcu.usb.request())

      (self.ledr, ), _ = self.chain(imp.Block(IndicatorLed(Led.Red)), self.mcu.gpio.request('ledr'))
      (self.ledg, ), _ = self.chain(imp.Block(IndicatorLed(Led.Green)), self.mcu.gpio.request('ledg'))
      (self.ledb, ), _ = self.chain(imp.Block(IndicatorLed(Led.Blue)), self.mcu.gpio.request('ledb'))

      self.knob = imp.Block(DigitalRotaryEncoder())
      self.connect(self.knob.a, self.mcu.gpio.request('knob_a'))
      self.connect(self.knob.b, self.mcu.gpio.request('knob_b'))
      self.connect(self.knob.with_mixin(DigitalRotaryEncoderSwitch()).sw, self.mcu.gpio.request('knob_sw'))

      self.sw = ElementDict[DigitalSwitch]()
      for i in range(NUM_SECTIONS):
        (self.sw[i], ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request(f'sw{i}'))

      self.dist = imp.Block(Vl53l0x())
      self.connect(self.i2c, self.dist.i2c)

      self.env = imp.Block(Bme680())  # TODO replace with cheaper BME280
      self.connect(self.i2c, self.env.i2c)

      self.oled = imp.Block(Er_Oled_096_1_1())
      self.connect(self.i2c, self.oled.i2c)
      self.connect(self.mcu.gpio.request('oled_reset'), self.oled.reset)

    # 5V DOMAIN
    with self.implicit_connect(
            ImplicitConnect(self.vusb, [Power]),
            ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.rgb_shift, self.rgb_tp, self.rgb_knob, self.rgb_ring, self.rgb_sw), _ = self.chain(
        self.mcu.gpio.request('rgb'),
        imp.Block(L74Ahct1g125()),
        imp.Block(DigitalTestPoint()),
        imp.Block(NeopixelArray(KNOB_LEDS)),
        imp.Block(NeopixelArray(RING_LEDS)),
        imp.Block(NeopixelArray(NUM_SECTIONS)))

      (self.spk_drv, self.spk), _ = self.chain(
        self.mcu.with_mixin(IoControllerI2s()).i2s.request('speaker'),
        imp.Block(Max98357a()),
        self.Block(Speaker())
      )


  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32s3_Wroom_1),
        (['reg_3v3'], Ldl1117),
      ],
      instance_values=[
        (['refdes_prefix'], 'K'),  # unique refdes for panelization
        (['mcu', 'pin_assigns'], [

        ]),
        (['mcu', 'programming'], 'uart-auto'),
        # (['reg_12v', 'power_path', 'inductor', 'part'], "CBC3225T470KR"),
        # (['reg_12v', 'power_path', 'inductor', 'manual_frequency_rating'], Range(0, 7e6)),
        # (['pwr_or', 'diode', 'part'], 'B5819W SL'),  # autopicked one is OOS
      ],
      class_refinements=[
        (EspAutoProgrammingHeader, EspProgrammingTc2030),
        (Neopixel, Sk6805_Ec15),
        (Speaker, ConnectorSpeaker),
        (PassiveConnector, JstPhKVertical),  # default connector series unless otherwise specified
        (TestPoint, CompactKeystone5015),
      ],
      class_values=[
        (ZenerDiode, ['footprint_spec'], 'Diode_SMD:D_SOD-123'),
        (Diode, ['footprint_spec'], 'Diode_SMD:D_SOD-123'),
        (CompactKeystone5015, ['lcsc_part'], 'C5199798'),  # RH-5015, which is actually in stock

        (Er_Oled_096_1_1, ['device', 'vbat', 'voltage_limits'], Range(3.0, 4.2)),  # technically out of spec
        (Er_Oled_096_1_1, ['device', 'vdd', 'voltage_limits'], Range(1.65, 4.0)),  # use abs max rating
      ]
    )


class IotKnobTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(IotKnob)
