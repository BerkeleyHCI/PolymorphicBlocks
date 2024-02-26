import unittest

from edg import *


class IotDisplay(JlcBoardTop):
  """IoT display with a WiFi microcontroller with connected display.
  """
  def contents(self) -> None:
    super().contents()

    BATTERY_VOLTAGE = (4*1.0, 6*1.6)*Volt

    self.usb = self.Block(UsbCReceptacle(current_limits=(0, 3)*Amp))
    self.batt = self.Block(LipoConnector(voltage=BATTERY_VOLTAGE, actual_voltage=BATTERY_VOLTAGE))  # 2-6 AA

    self.vbat = self.connect(self.batt.pwr)
    self.gnd_merge = self.Block(MergedVoltageSource()).connected_from(
      self.usb.gnd, self.batt.gnd)
    self.gnd = self.connect(self.gnd_merge.pwr_out)

    self.tp_pwr = self.Block(VoltageTestPoint()).connected(self.batt.pwr)
    self.tp_gnd = self.Block(VoltageTestPoint()).connected(self.gnd_merge.pwr_out)

    # POWER
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.reg_3v3, self.tp_3v3, self.prot_3v3), _ = self.chain(
        self.pwr,
        imp.Block(BuckConverter(output_voltage=3.3*Volt(tol=0.05))),
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

      # need to name the USB chain so the USB net has the _N and _P postfix for differential traces
      (self.usb_esd, ), self.usb_chain = self.chain(self.usb.usb, imp.Block(UsbEsdDiode()),
                                                    self.mcu.usb.request())

      (self.ledr, ), _ = self.chain(imp.Block(IndicatorLed(Led.Red)), self.mcu.gpio.request('ledr'))
      (self.ledg, ), _ = self.chain(imp.Block(IndicatorLed(Led.Green)), self.mcu.gpio.request('ledg'))
      (self.ledb, ), _ = self.chain(imp.Block(IndicatorLed(Led.Blue)), self.mcu.gpio.request('ledb'))

      self.sw = ElementDict[DigitalSwitch]()
      for i in range(3):
        (self.sw[i], ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request(f'sw{i}'))
      self.epd = imp.Block(Er_Epd027_2())
      self.connect(self.v3v3, self.epd.pwr)
      self.connect(self.mcu.spi.request('spi'), self.epd.spi)
      self.connect(self.mcu.gpio.request('epd_rst'), self.epd.reset)
      self.connect(self.mcu.gpio.request('epd_dc'), self.epd.dc)
      self.connect(self.mcu.gpio.request('epd_cs'), self.epd.cs)
      self.connect(self.mcu.gpio.request('epd_busy'), self.epd.busy)

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32s3_Wroom_1),
        (['reg_3v3'], Tps54202h),
        (['batt', 'conn'], JstPhKVertical),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
          # 'ledr=7',
          # 'ledg=8',
          # 'ledb=9',
          # 'sw0=12',
          # 'sw1=11',
          # 'sw2=10',
          # 'oled_rst=38',
          # 'oled_cs=31',
          # 'oled_dc=32',
          # 'spi.sck=33',
          # 'spi.mosi=34',
          # 'spi.miso=NC',
          # 'epd_busy=35',
        ]),
        (['mcu', 'programming'], 'uart-auto'),
        (['reg_12v', 'power_path', 'inductor', 'part'], "CBC3225T470KR"),
        (['reg_12v', 'power_path', 'inductor', 'manual_frequency_rating'], Range(0, 7e6)),
        (['pwr_or', 'diode', 'part'], 'B5819W SL'),  # autopicked one is OOS
      ],
      class_refinements=[
        (EspProgrammingHeader, EspProgrammingTc2030),
        (TestPoint, CompactKeystone5015),
      ],
      class_values=[
        (ZenerDiode, ['footprint_spec'], 'Diode_SMD:D_SOD-323'),  # for parts commonality w/ other zeners on panel
        (Diode, ['footprint_spec'], 'Diode_SMD:D_SOD-123'),
        (Diode, ['part'], 'B0520W'),  # autopicked one is OOS, use common one with other diode
        (CompactKeystone5015, ['lcsc_part'], 'C5199798'),  # RH-5015, which is actually in stock
      ]
    )


class IotDisplayTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(IotDisplay)
