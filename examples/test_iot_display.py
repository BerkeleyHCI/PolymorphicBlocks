import unittest

from edg import *


class IotDisplay(JlcBoardTop):
  """IoT display with a WiFi microcontroller with connected display.
  """
  def contents(self) -> None:
    super().contents()

    self.usb = self.Block(UsbCReceptacle(current_limits=(0, 3)*Amp))
    self.batt = self.Block(LipoConnector(actual_voltage=(3.7, 4.2)*Volt))

    self.vusb = self.connect(self.usb.pwr)
    self.vbatt = self.connect(self.batt.pwr)
    self.gnd_merge = self.Block(MergedVoltageSource()).connected_from(
      self.usb.gnd, self.batt.gnd)
    self.gnd = self.connect(self.gnd_merge.pwr_out)

    self.pwr_or = self.Block(PriorityPowerOr(
      (0, 1)*Volt, (0, 0.1)*Ohm
    )).connected_from(self.gnd_merge.pwr_out, self.usb.pwr, self.batt.pwr)
    self.pwr = self.connect(self.pwr_or.pwr_out)

    self.tp_pwr = self.Block(VoltageTestPoint()).connected(self.pwr_or.pwr_out)
    self.tp_gnd = self.Block(VoltageTestPoint()).connected(self.gnd_merge.pwr_out)

    # POWER
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.charger, ), _ = self.chain(
        self.vusb, imp.Block(Mcp73831(200*mAmp(tol=0.2))), self.batt.chg
      )
      (self.charge_led, ), _ = self.chain(
        self.Block(IndicatorSinkLed(Led.Yellow)), self.charger.stat
      )
      self.connect(self.vusb, self.charge_led.pwr)

      (self.reg_3v3, self.tp_3v3, self.prot_3v3), _ = self.chain(
        self.pwr,
        imp.Block(LinearRegulator(output_voltage=3.3*Volt(tol=0.05))),
        self.Block(VoltageTestPoint()),
        imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.9)*Volt))
      )
      self.v3v3 = self.connect(self.reg_3v3.pwr_out)

      (self.reg_12v, self.tp_12v), _ = self.chain(
        self.pwr,
        imp.Block(BoostConverter(output_voltage=(12, 15)*Volt)),
        self.Block(VoltageTestPoint())
      )
      self.v12 = self.connect(self.reg_12v.pwr_out)

    # 3V3 DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.v3v3, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())
      self.mcu.with_mixin(IoControllerWifi())

      # need to name the USB chain so the USB net has the _N and _P postfix for differential traces
      (self.usb_esd, ), self.usb_chain = self.chain(self.usb.usb, imp.Block(UsbEsdDiode()),
                                                    self.mcu.with_mixin(IoControllerUsb()).usb.request())

      (self.ledr, ), _ = self.chain(imp.Block(IndicatorLed(Led.Red)), self.mcu.gpio.request('ledr'))
      (self.ledg, ), _ = self.chain(imp.Block(IndicatorLed(Led.Green)), self.mcu.gpio.request('ledg'))
      (self.ledb, ), _ = self.chain(imp.Block(IndicatorLed(Led.Blue)), self.mcu.gpio.request('ledb'))

      self.sw = ElementDict[DigitalSwitch]()
      for i in range(3):
        (self.sw[i], ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request(f'sw{i}'))

      self.oled28 = imp.Block(Er_Oled028_1())
      self.oled22 = imp.Block(Er_Oled022_1())
      self.epd = imp.Block(Er_Epd027_2())
      self.connect(self.v3v3, self.oled28.pwr, self.oled22.pwr, self.epd.pwr)
      self.connect(self.v12, self.oled28.vcc, self.oled22.vcc)
      self.connect(self.mcu.spi.request('spi'), self.oled28.spi, self.oled22.spi, self.epd.spi)
      self.connect(self.mcu.gpio.request('oled_rst'), self.oled28.reset, self.oled22.reset, self.epd.reset)
      self.connect(self.mcu.gpio.request('oled_dc'), self.oled28.dc, self.oled22.dc, self.epd.dc)
      self.connect(self.mcu.gpio.request('oled_cs'), self.oled28.cs, self.oled22.cs, self.epd.cs)
      self.connect(self.mcu.gpio.request('epd_busy'), self.epd.busy)

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32s3_Wroom_1),
        (['reg_3v3'], Ldl1117),
        (['reg_12v'], Ap3012),
        (['batt', 'conn'], JstPhKVertical),
      ],
      instance_values=[
        (['refdes_prefix'], 'D'),  # unique refdes for panelization
        (['mcu', 'pin_assigns'], [
          'ledr=7',
          'ledg=8',
          'ledb=9',
          'sw0=12',
          'sw1=11',
          'sw2=10',
          'oled_rst=38',
          'oled_cs=31',
          'oled_dc=32',
          'spi.sck=33',
          'spi.mosi=34',
          'spi.miso=NC',
          'epd_busy=35',
        ]),
        (['mcu', 'programming'], 'uart-auto'),
        (['reg_12v', 'power_path', 'inductor', 'part'], "CBC3225T470KR"),
        (['reg_12v', 'power_path', 'inductor', 'manual_frequency_rating'], Range(0, 7e6)),
        (['pwr_or', 'diode', 'part'], 'B5819W SL'),  # autopicked one is OOS
      ],
      class_refinements=[
        (EspProgrammingHeader, EspProgrammingTc2030),
        (TestPoint, CompactKeystone5015),
        (Fpc050Bottom, Fpc050BottomFlip),
      ],
      class_values=[
        (ZenerDiode, ['footprint_spec'], 'Diode_SMD:D_SOD-323'),  # for parts commonality w/ other zeners on panel
        (Diode, ['footprint_spec'], 'Diode_SMD:D_SOD-123'),
        (Diode, ['part'], 'B0520W'),  # autopicked one is OOS, use common one with other diode
        (CompactKeystone5015, ['lcsc_part'], 'C5199798'),  # RH-5015, which is actually in stock

        (Er_Oled028_1, ["device", "vcc", "voltage_limits"], Range(11.5, 16)),  # abs max ratings instead of recommended
        (Er_Oled022_1, ["device", "vcc", "voltage_limits"], Range(12, 15)),  # abs max ratings instead of recommended
        (Er_Oled022_1, ["device", "vcc", "current_draw"], Range(0, 0)),  # only one OLED will be active at any time
        (Er_Oled022_1, ["iref_res", "resistance"], Range.from_tolerance(820e3, 0.1)),  # use a basic part
      ]
    )


class IotDisplayTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(IotDisplay)
