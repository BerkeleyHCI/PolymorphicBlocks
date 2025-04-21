import unittest

from edg import *
from .test_iot_blinds import PowerInConnector


class IotLedDriver(JlcBoardTop):
  """Multichannel IoT high-power external LED driver with external power input.
  """
  def contents(self) -> None:
    super().contents()

    self.pwr = self.Block(PowerInConnector())

    self.vin = self.connect(self.pwr.pwr)
    self.gnd = self.connect(self.pwr.gnd)

    self.tp_pwr = self.Block(VoltageTestPoint()).connected(self.pwr.pwr)
    self.tp_gnd = self.Block(GroundTestPoint()).connected(self.pwr.gnd)

    # POWER
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.reg_3v3, self.tp_3v3, self.prot_3v3), _ = self.chain(
        self.vin,
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

      (self.vin_sense, ), _ = self.chain(
        self.vin,
        imp.Block(VoltageSenseDivider(full_scale_voltage=2.2*Volt(tol=0.1), impedance=(1, 10)*kOhm)),
        self.mcu.adc.request('vin_sense')
      )

      # generic expansion
      self.i2c = self.mcu.i2c.request('i2c')
      (self.i2c_pull, self.i2c_tp), self.i2c_chain = self.chain(
        self.i2c,
        imp.Block(I2cPullup()), imp.Block(I2cTestPoint()))
      self.als = imp.Block(Bh1750())
      self.tof = imp.Block(Vl53l0x())
      self.connect(self.i2c, self.als.i2c, self.tof.i2c)

    # Vin DOMAIN
    self.led_drv = ElementDict[LedDriver]()
    self.led_conn = ElementDict[PassiveConnector]()
    with self.implicit_connect(
            ImplicitConnect(self.vin, [Power]),
            ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      for i in range(4):
        led_drv = self.led_drv[i] = imp.Block(LedDriver(max_current=700*mAmp(tol=0.1)))
        led_drv.with_mixin(LedDriverSwitchingConverter(ripple_limit=500*mAmp))
        self.connect(self.mcu.gpio.request(f'led_pwm_{i}'), led_drv.with_mixin(LedDriverPwm()).pwm)

        led_conn = self.led_conn[i] = self.Block(JstPhKHorizontal(2))
        self.connect(led_drv.leda, led_conn.pins.request('1'))
        self.connect(led_drv.ledk, led_conn.pins.request('2'))

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32c3),
        (['reg_3v3'], Tps54202h),
        (['pwr', 'conn'], JstPhKHorizontal),
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
        (['reg_3v3', 'power_path', 'inductor', 'part'], "NR5040T220M"),
        (['reg_3v3', 'power_path', 'inductor', 'manual_frequency_rating'], Range(0, 9e6)),

        (['led_drv[0]', 'diode_voltage_drop'], Range(0, 0.5)),
        (['led_drv[1]', 'diode_voltage_drop'], ParamValue(['led_drv[0]', 'diode_voltage_drop'])),
        (['led_drv[2]', 'diode_voltage_drop'], ParamValue(['led_drv[0]', 'diode_voltage_drop'])),
        (['led_drv[3]', 'diode_voltage_drop'], ParamValue(['led_drv[0]', 'diode_voltage_drop'])),

        (['led_drv[0]', 'rsense', 'res', 'res', 'require_basic_part'], False),
        (['led_drv[1]', 'rsense', 'res', 'res', 'require_basic_part'], ParamValue(['led_drv[0]', 'rsense', 'res', 'res', 'require_basic_part'])),
        (['led_drv[2]', 'rsense', 'res', 'res', 'require_basic_part'], ParamValue(['led_drv[0]', 'rsense', 'res', 'res', 'require_basic_part'])),
        (['led_drv[3]', 'rsense', 'res', 'res', 'require_basic_part'], ParamValue(['led_drv[0]', 'rsense', 'res', 'res', 'require_basic_part'])),
        (['led_drv[0]', 'ind', 'part'], "SWPA6045S680MT"),
        (['led_drv[0]', 'ind', 'manual_frequency_rating'], Range(0, 6.4e6)),
        (['led_drv[1]', 'ind', 'part'], ParamValue(['led_drv[0]', 'ind', 'part'])),
        (['led_drv[1]', 'ind', 'manual_frequency_rating'], ParamValue(['led_drv[0]', 'ind', 'manual_frequency_rating'])),
        (['led_drv[2]', 'ind', 'part'], ParamValue(['led_drv[0]', 'ind', 'part'])),
        (['led_drv[2]', 'ind', 'manual_frequency_rating'], ParamValue(['led_drv[0]', 'ind', 'manual_frequency_rating'])),
        (['led_drv[3]', 'ind', 'part'], ParamValue(['led_drv[0]', 'ind', 'part'])),
        (['led_drv[3]', 'ind', 'manual_frequency_rating'], ParamValue(['led_drv[0]', 'ind', 'manual_frequency_rating'])),
      ],
      class_refinements=[
        (EspProgrammingHeader, EspProgrammingTc2030),
        (LedDriver, Al8861),
        (TestPoint, CompactKeystone5015),
      ],
      class_values=[
        (CompactKeystone5015, ['lcsc_part'], 'C5199798'),
      ]
    )


class IotLedDriverTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(IotLedDriver)
