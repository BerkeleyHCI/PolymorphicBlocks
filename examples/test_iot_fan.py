import unittest

from edg import *


class IotFan(JlcBoardTop):
  """IoT fan controller with a 12v barrel jack input and a CPU fan connector.
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
    self.fan = ElementDict[CpuFanConnector]()
    self.fan_drv = ElementDict[HighSideSwitch]()
    self.fan_sense = ElementDict[OpenDrainDriver]()
    self.fan_ctl = ElementDict[OpenDrainDriver]()

    with self.implicit_connect(
            ImplicitConnect(self.v12, [Power]),
            ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      for i in range(2):
        fan = self.fan[i] = self.Block(CpuFanConnector())
        fan_drv = self.fan_drv[i] = imp.Block(HighSideSwitch(pull_resistance=4.7*kOhm(tol=0.05), max_rds=0.3*Ohm))
        self.connect(fan.pwr, fan_drv.output.as_voltage_source())
        self.connect(fan.gnd, self.gnd)
        self.connect(self.mcu.gpio.request(f'fan_drv_{i}'), fan_drv.control)

        self.connect(fan.sense, self.mcu.gpio.request(f'fan_sense_{i}'))
        (self.fan_ctl[i], ), _ = self.chain(
          self.mcu.gpio.request(f'fan_ctl_{i}'),
          imp.Block(OpenDrainDriver()),
          fan.with_mixin(CpuFanPwmControl()).control
        )

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32s3_Wroom_1),
        (['reg_5v'], Tps54202h),
        (['reg_3v3'], Ldl1117),
      ],
      instance_values=[
        (['refdes_prefix'], 'F'),  # unique refdes for panelization
        (['mcu', 'pin_assigns'], [
          # also designed to be compatible w/ ESP32C6
          # https://www.espressif.com/sites/default/files/documentation/esp32-c6-wroom-1_wroom-1u_datasheet_en.pdf
          # note: pin 34 NC, GPIO8 (pin 10) is strapping and should be PUR
          # bottom row doesn't exist
          'v12_sense=4',
          'enc_a=8',
          'enc_b=7',
          'rgb=5',
          'ledr=14',
          'fan_drv_1=35',
          'fan_sense_1=39',
          'fan_ctl_1=38',
          'fan_drv_0=31',
          'fan_sense_0=33',
          'fan_ctl_0=32',
        ]),
        (['mcu', 'programming'], 'uart-auto'),
        (['reg_5v', 'power_path', 'inductor', 'part'], "NR5040T220M"),
        (['reg_5v', 'power_path', 'inductor', 'manual_frequency_rating'], Range(0, 9e6)),
      ],
      class_refinements=[
        (EspAutoProgrammingHeader, EspProgrammingTc2030),
        (PowerBarrelJack, Pj_036ah),
        (Neopixel, Sk6805_Ec15),
        (TestPoint, CompactKeystone5015),
        (TagConnect, TagConnectNonLegged),
        (RotaryEncoder, Ec05e),
      ],
      class_values=[
        (ZenerDiode, ['footprint_spec'], 'Diode_SMD:D_SOD-123'),
        (Diode, ['footprint_spec'], 'Diode_SMD:D_SOD-123'),
        (CompactKeystone5015, ['lcsc_part'], 'C5199798'),  # RH-5015, which is actually in stock
      ]
    )


class IotFanTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(IotFan)
