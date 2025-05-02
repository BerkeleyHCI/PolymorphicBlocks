import unittest

from edg import *


class PowerInConnector(Connector):
  def __init__(self):
    super().__init__()
    self.conn = self.Block(JstPh())
    self.gnd = self.Export(self.conn.pins.request('1').adapt_to(Ground()))
    self.pwr = self.Export(self.conn.pins.request('2').adapt_to(VoltageSource(
      voltage_out=(10, 24)*Volt,
      current_limits=(0, 5)*Amp,
    )))


class IotLedDriver(JlcBoardTop):
  """Multichannel IoT high-power external LED driver with a 12v barrel jack input.
  """
  def contents(self) -> None:
    super().contents()

    self.pwr = self.Block(PowerInConnector())

    self.v12 = self.connect(self.pwr.pwr)
    self.gnd = self.connect(self.pwr.gnd)

    # POWER
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.reg_3v3, self.tp_3v3, self.prot_3v3), _ = self.chain(
        self.v12,
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

      (self.v12_sense, ), _ = self.chain(
        self.v12,
        imp.Block(VoltageSenseDivider(full_scale_voltage=2.2*Volt(tol=0.1), impedance=(1, 10)*kOhm)),
        self.mcu.adc.request('v12_sense')
      )

    # 12V DOMAIN
    self.led_drv = ElementDict[LedDriver]()
    with self.implicit_connect(
            ImplicitConnect(self.v12, [Power]),
            ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      for i in range(4):
        led_drv = self.led_drv[i] = imp.Block(LedDriver(max_current=700*mAmp(tol=0.1)))
        # led_drv.with_mixin(LedDriverSwitchingConverter(ripple_limit=500*mAmp))
        self.connect(self.mcu.gpio.request(f'led_pwm_{i}'), led_drv.with_mixin(LedDriverPwm()).pwm)

    self.led_conn = self.Block(JstPhKHorizontal(2))
    self.connect(self.led_drv[0].leda, self.led_conn.pins.request('1'))
    self.connect(self.led_drv[0].ledk, self.led_conn.pins.request('2'))

    self.rgb_conn = self.Block(JstPhKHorizontal(6))
    self.connect(self.led_drv[1].leda, self.rgb_conn.pins.request('1'))
    self.connect(self.led_drv[1].ledk, self.rgb_conn.pins.request('2'))
    self.connect(self.led_drv[2].leda, self.rgb_conn.pins.request('3'))
    self.connect(self.led_drv[2].ledk, self.rgb_conn.pins.request('4'))
    self.connect(self.led_drv[3].leda, self.rgb_conn.pins.request('5'))
    self.connect(self.led_drv[3].ledk, self.rgb_conn.pins.request('6'))

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32c3),
        (['reg_3v3'], Tps54202h),
      ],
      instance_values=[
        (['refdes_prefix'], 'L'),  # unique refdes for panelization
        (['mcu', 'pin_assigns'], [
          # also designed to be compatible w/ ESP32C6
          # https://www.espressif.com/sites/default/files/documentation/esp32-c6-wroom-1_wroom-1u_datasheet_en.pdf
          # note: pin 34 NC, GPIO8 (pin 10) is strapping and should be PUR
          # bottom row doesn't exist
          # 'v12_sense=4',
          # 'enc_a=8',
          # 'enc_b=7',
          # 'enc_sw=6',
          # 'rgb=5',
          # 'ledr=14',
          # 'led_pwm_0=39',
          # 'led_pwm_1=38',
          # 'led_pwm_2=35',
          # 'led_pwm_3=33',
        ]),
        (['mcu', 'programming'], 'uart-auto'),
        (['reg_3v3', 'power_path', 'inductor', 'manual_frequency_rating'], Range(0, 9e6)),

        (['led_drv[0]', 'diode_voltage_drop'], Range(0, 0.5)),
        (['led_drv[1]', 'diode_voltage_drop'], ParamValue(['led_drv[0]', 'diode_voltage_drop'])),
        (['led_drv[2]', 'diode_voltage_drop'], ParamValue(['led_drv[0]', 'diode_voltage_drop'])),
        (['led_drv[3]', 'diode_voltage_drop'], ParamValue(['led_drv[0]', 'diode_voltage_drop'])),

        (['led_drv[0]', 'rsense', 'res', 'res', 'require_basic_part'], False),
        (['led_drv[1]', 'rsense', 'res', 'res', 'require_basic_part'], ParamValue(['led_drv[0]', 'rsense', 'res', 'res', 'require_basic_part'])),
        (['led_drv[2]', 'rsense', 'res', 'res', 'require_basic_part'], ParamValue(['led_drv[0]', 'rsense', 'res', 'res', 'require_basic_part'])),
        (['led_drv[3]', 'rsense', 'res', 'res', 'require_basic_part'], ParamValue(['led_drv[0]', 'rsense', 'res', 'res', 'require_basic_part'])),
        # (['led_drv[0]', 'ind', 'part'], "SWPA6045S680MT"),
        (['led_drv[0]', 'power_path', 'inductor', 'manual_frequency_rating'], Range(0, 6.4e6)),
        (['led_drv[1]', 'power_path', 'inductor', 'part'], ParamValue(['led_drv[0]', 'power_path', 'inductor', 'part'])),
        (['led_drv[1]', 'power_path', 'inductor', 'manual_frequency_rating'], ParamValue(['led_drv[0]', 'power_path', 'inductor', 'manual_frequency_rating'])),
        (['led_drv[2]', 'power_path', 'inductor', 'part'], ParamValue(['led_drv[0]', 'power_path', 'inductor', 'part'])),
        (['led_drv[2]', 'power_path', 'inductor', 'manual_frequency_rating'], ParamValue(['led_drv[0]', 'power_path', 'inductor', 'manual_frequency_rating'])),
        (['led_drv[3]', 'power_path', 'inductor', 'part'], ParamValue(['led_drv[0]', 'power_path', 'inductor', 'part'])),
        (['led_drv[3]', 'power_path', 'inductor', 'manual_frequency_rating'], ParamValue(['led_drv[0]', 'power_path', 'inductor', 'manual_frequency_rating'])),
        (['reg_3v3', 'power_path', 'in_cap', 'cap', 'voltage_rating_derating'], 0.98),  # use a 1206 25 oe 35v part
      ],
      class_refinements=[
        (EspProgrammingHeader, EspProgrammingTc2030),
        (PowerBarrelJack, Pj_036ah),
        (Neopixel, Sk6805_Ec15),
        (LedDriver, Tps92200),
        (TestPoint, CompactKeystone5015),
        (TagConnect, TagConnectNonLegged),
      ],
      class_values=[
        (SelectorArea, ['footprint_area'], Range.from_lower(1.5)),  # at least 0402
        (CompactKeystone5015, ['lcsc_part'], 'C5199798'),  # RH-5015, which is actually in stock
      ]
    )


class IotLedDriverTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(IotLedDriver)
