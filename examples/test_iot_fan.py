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
      rgb_pin = self.mcu.gpio.request('rgb')  # multiplex RGB LED onto single debugging LED
      (self.ledr, ), _ = self.chain(imp.Block(IndicatorLed(Led.Red)), rgb_pin)

      self.enc = imp.Block(DigitalRotaryEncoder())
      self.connect(self.enc.a, self.mcu.gpio.request('enc_a'))
      self.connect(self.enc.b, self.mcu.gpio.request('enc_b'))
      self.connect(self.enc.with_mixin(DigitalRotaryEncoderSwitch()).sw, self.mcu.gpio.request('enc_sw'))

      (self.v12_sense, ), _ = self.chain(
        self.v12,
        imp.Block(VoltageSenseDivider(full_scale_voltage=2.2*Volt(tol=0.1), impedance=(1, 10)*kOhm)),
        self.mcu.adc.request('v12_sense')
      )

    # 5V DOMAIN
    with self.implicit_connect(
            ImplicitConnect(self.v5, [Power]),
            ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.rgb_ring, ), _ = self.chain(
        rgb_pin,
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
        (['mcu'], Esp32c3),
        (['reg_5v'], Tps54202h),
        (['reg_3v3'], Ap7215),
      ],
      instance_values=[
        (['refdes_prefix'], 'F'),  # unique refdes for panelization
        (['mcu', 'pin_assigns'], [
          # 'v12_sense=3',
          'rgb=_GPIO2_STRAP',  # force using the strapping pin, since we're out of IOs
          # 'enc_b=5',
          # 'enc_a=6',
          # 'fan_sense_1=18',
          # 'fan_ctl_1=17',
          # 'fan_drv_1=15',
          # 'fan_sense_0=14',
          # 'fan_ctl_0=13',
          # 'fan_drv_0=10',
        ]),
        (['mcu', 'programming'], 'uart-auto'),
        (['reg_5v', 'power_path', 'inductor', 'part'], "NR5040T220M"),
        (['reg_5v', 'power_path', 'inductor', 'manual_frequency_rating'], Range(0, 9e6)),
        (['fan_drv[0]', 'drv', 'footprint_spec'], "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"),
        (['fan_drv[0]', 'drv', 'part'], "AO4407A"),  # default DMG4407 is out of stock
        (['fan_drv[1]', 'drv', 'footprint_spec'], ParamValue(['fan_drv[0]', 'drv', 'footprint_spec'])),
        (['fan_drv[1]', 'drv', 'part'], ParamValue(['fan_drv[0]', 'drv', 'part'])),
      ],
      class_refinements=[
        (EspProgrammingHeader, EspProgrammingTc2030),
        (PowerBarrelJack, Pj_036ah),
        (Neopixel, Sk6805_Ec15),
        (TestPoint, CompactKeystone5015),
        (TagConnect, TagConnectNonLegged),
      ],
      class_values=[
        (Esp32c3, ['not_recommended'], True),
        (ZenerDiode, ['footprint_spec'], 'Diode_SMD:D_SOD-323'),
        (CompactKeystone5015, ['lcsc_part'], 'C5199798'),  # RH-5015, which is actually in stock
      ]
    )


class IotFanTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(IotFan)
