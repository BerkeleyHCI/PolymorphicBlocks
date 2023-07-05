import unittest

from edg import *


class IotLedDriver(JlcBoardTop):
  """Multichannel IoT high-power external LED driver with a 12v barrel jack input.
  """
  def contents(self) -> None:
    super().contents()

    RING_LEDS = 18  # number of RGBs for the ring indicator

    self.pwr = self.Block(PowerBarrelJack(voltage_out=12*Volt(tol=0.05), current_limits=(0, 5)*Amp))

    self.v12 = self.connect(self.pwr.pwr)
    self.gnd = self.connect(self.pwr.gnd)

    self.tp_pwr = self.Block(VoltageTestPoint()).connected(self.pwr.pwr)
    self.tp_gnd = self.Block(VoltageTestPoint()).connected(self.pwr.gnd)

    # POWER
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.reg_5v, self.tp_5v, self.prot_5v), _ = self.chain(
        self.v12,
        imp.Block(VoltageRegulator(output_voltage=4*Volt(tol=0.05))),
        self.Block(VoltageTestPoint()),
        imp.Block(ProtectionZenerDiode(voltage=(5.5, 6.8)*Volt))
      )
      self.v5 = self.connect(self.reg_5v.pwr_out)

      (self.reg_3v3, self.tp_3v3, self.prot_3v3), _ = self.chain(
        self.v5,
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

      # debugging LEDs
      (self.ledr, ), _ = self.chain(imp.Block(IndicatorLed(Led.Red)), self.mcu.gpio.request('ledr'))

      self.enc = imp.Block(DigitalRotaryEncoder())
      self.connect(self.enc.a, self.mcu.gpio.request('enc_a'))
      self.connect(self.enc.b, self.mcu.gpio.request('enc_b'))
      self.connect(self.enc.with_mixin(DigitalRotaryEncoderSwitch()).sw, self.mcu.gpio.request('enc_sw'))

      (self.v12_sense, ), _ = self.chain(
        self.v12,
        imp.Block(VoltageSenseDivider(full_scale_voltage=3.0*Volt(tol=0.1), impedance=(1, 10)*kOhm)),
        self.mcu.adc.request('v12_sense')
      )

    # 5V DOMAIN
    with self.implicit_connect(
            ImplicitConnect(self.v5, [Power]),
            ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.rgb_ring, ), _ = self.chain(
        self.mcu.gpio.request('rgb'),
        imp.Block(NeopixelArray(RING_LEDS)))

    # 12V DOMAIN
    self.led_drv = ElementDict[Al8861]()
    with self.implicit_connect(
            ImplicitConnect(self.v12, [Power]),
            ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      for i in range(3):
        led_drv = self.led_drv[i] = imp.Block(Al8861(max_current=700*mAmp(tol=0.1), ripple_limit=400*mAmp,
                                                     diode_voltage_drop=(0, 0.5)*Volt))
        self.connect(self.mcu.gpio.request(f'led_pwm_{i}'), led_drv.pwm)

    self.led_conn = self.Block(JstPhKHorizontal(6))
    self.connect(self.led_drv[0].leda, self.led_conn.pins.request('1'))
    self.connect(self.led_drv[0].ledk, self.led_conn.pins.request('2'))
    self.connect(self.led_drv[1].leda, self.led_conn.pins.request('3'))
    self.connect(self.led_drv[1].ledk, self.led_conn.pins.request('4'))
    self.connect(self.led_drv[2].leda, self.led_conn.pins.request('5'))
    self.connect(self.led_drv[2].ledk, self.led_conn.pins.request('6'))

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32s3_Wroom_1),
        (['reg_5v'], Tps54202h),
        (['reg_3v3'], Ldl1117),
      ],
      instance_values=[
        (['refdes_prefix'], 'L'),  # unique refdes for panelization
        (['mcu', 'pin_assigns'], [
          # also designed to be compatible w/ ESP32C6
          # https://www.espressif.com/sites/default/files/documentation/esp32-c6-wroom-1_wroom-1u_datasheet_en.pdf
          # note: pin 34 NC, GPIO8 (pin 10) is strapping and should be PUR
          # bottom row doesn't exist
          'v12_sense=4',
          'enc_a=8',
          'enc_b=7',
          'enc_sw=6',
          'rgb=5',
          'ledr=14',
          'led_pwm_0=39',
          'led_pwm_1=38',
          'led_pwm_2=35',
        ]),
        (['mcu', 'programming'], 'uart-auto'),
        (['reg_5v', 'power_path', 'inductor', 'part'], "NR5040T220M"),
        (['reg_5v', 'power_path', 'inductor', 'manual_frequency_rating'], Range(0, 9e6)),

        (['led_drv[0]', 'rsense', 'res', 'res', 'require_basic_part'], False),
        (['led_drv[1]', 'rsense', 'res', 'res', 'require_basic_part'], ParamValue(['led_drv[0]', 'rsense', 'res', 'res', 'require_basic_part'])),
        (['led_drv[2]', 'rsense', 'res', 'res', 'require_basic_part'], ParamValue(['led_drv[0]', 'rsense', 'res', 'res', 'require_basic_part'])),
        (['led_drv[3]', 'rsense', 'res', 'res', 'require_basic_part'], ParamValue(['led_drv[0]', 'rsense', 'res', 'res', 'require_basic_part'])),
        (['led_drv[0]', 'ind', 'part'], "SWPA8040S680MT"),
        (['led_drv[0]', 'ind', 'manual_frequency_rating'], Range(0, 4.9e6)),
        (['led_drv[1]', 'ind', 'part'], ParamValue(['led_drv[0]', 'ind', 'part'])),
        (['led_drv[1]', 'ind', 'manual_frequency_rating'], ParamValue(['led_drv[0]', 'ind', 'manual_frequency_rating'])),
        (['led_drv[2]', 'ind', 'part'], ParamValue(['led_drv[0]', 'ind', 'part'])),
        (['led_drv[2]', 'ind', 'manual_frequency_rating'], ParamValue(['led_drv[0]', 'ind', 'manual_frequency_rating'])),
        (['led_drv[3]', 'ind', 'part'], ParamValue(['led_drv[0]', 'ind', 'part'])),
        (['led_drv[3]', 'ind', 'manual_frequency_rating'], ParamValue(['led_drv[0]', 'ind', 'manual_frequency_rating'])),
      ],
      class_refinements=[
        (EspAutoProgrammingHeader, EspProgrammingTc2030),
        (PowerBarrelJack, Pj_036ah),
        (Neopixel, Sk6805_Ec15),
        (TestPoint, CompactKeystone5015),
        (TagConnect, TagConnectNonLegged),
      ],
      class_values=[
        (ZenerDiode, ['footprint_spec'], 'Diode_SMD:D_SOD-123'),
        (Diode, ['footprint_spec'], 'Diode_SMD:D_SOD-123'),
        (CompactKeystone5015, ['lcsc_part'], 'C5199798'),  # RH-5015, which is actually in stock
      ]
    )


class IotLedDriverTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(IotLedDriver)
