import unittest

from edg import *


class IotDisplay(JlcBoardTop):
  """IoT display with a WiFi microcontroller with connected display.
  """
  def contents(self) -> None:
    super().contents()

    self.usb = self.Block(UsbCReceptacle(current_limits=(0, 3)*Amp))
    self.pwr = self.connect(self.usb.pwr)
    self.gnd = self.connect(self.usb.gnd)

    self.tp_pwr = self.Block(VoltageTestPoint()).connected(self.usb.pwr)
    self.tp_gnd = self.Block(VoltageTestPoint()).connected(self.usb.gnd)

    # POWER
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
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

      (self.ledr, ), _ = self.chain(imp.Block(IndicatorLed(Led.Red)), self.mcu.gpio.request('ledr'))
      (self.ledg, ), _ = self.chain(imp.Block(IndicatorLed(Led.Green)), self.mcu.gpio.request('ledg'))
      (self.ledb, ), _ = self.chain(imp.Block(IndicatorLed(Led.Blue)), self.mcu.gpio.request('ledb'))

      self.sw = ElementDict[DigitalSwitch]()
      for i in range(4):
        (self.sw[i], ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request(f'sw{i}'))

      self.oled28 = imp.Block(Er_Oled028_1())
      self.oled22 = imp.Block(Er_Oled022_1())
      self.connect(self.v3v3, self.oled28.pwr, self.oled22.pwr)
      self.connect(self.v12, self.oled28.vcc, self.oled22.vcc)
      self.connect(self.mcu.spi.request('oled'), self.oled28.spi, self.oled22.spi)
      self.connect(self.mcu.gpio.request('oled_rst'), self.oled28.reset, self.oled22.reset)
      self.connect(self.mcu.gpio.request('oled_dc'), self.oled28.dc, self.oled22.dc)
      self.connect(self.mcu.gpio.request('oled_cs'), self.oled28.cs, self.oled22.cs)

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32_Wroom_32),
        (['reg_3v3'], Ld1117),
        (['reg_12v'], Ap3012),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [

        ]),
        (['mcu', 'programming'], 'uart-auto')
      ],
      class_refinements=[
        (EspAutoProgrammingHeader, EspProgrammingTc2030),
      ],
      class_values=[
        (Er_Oled028_1, ["device", "vcc", "voltage_limits"], Range(11.5, 16)),  # abs max ratings instead of recommended
        (Er_Oled022_1, ["device", "vcc", "voltage_limits"], Range(12, 15)),  # abs max ratings instead of recommended
      ]
    )


class IotDisplayTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(IotDisplay)
