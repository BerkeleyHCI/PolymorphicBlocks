import unittest

from edg import *


class CanAdapter(BoardTop):
  def contents(self) -> None:
    super().contents()

    # USB Domain
    self.usb = self.Block(UsbDeviceCReceptacle())

    self.vusb = self.connect(self.usb.pwr)
    self.gnd = self.connect(self.usb.gnd)

    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.usb_reg, ), _ = self.chain(
        self.usb.pwr,
        imp.Block(LinearRegulator(3.3*Volt(tol=0.05)))
      )

    self.v3v3 = self.connect(self.usb_reg.pwr_out)

    with self.implicit_connect(
        ImplicitConnect(self.v3v3, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())

      (self.usb_esd, ), _ = self.chain(self.usb.usb, imp.Block(UsbEsdDiode()), self.mcu.usb.allocate())
      (self.xcvr, ), self.can_chain = self.chain(self.mcu.can.allocate('can'), imp.Block(Iso1050dub()))

      (self.sw_usb, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.allocate('sw_usb'))
      (self.sw_can, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.allocate('sw_can'))

      self.lcd = imp.Block(Qt096t_if09())

      self.rgb_usb = imp.Block(IndicatorSinkRgbLed())
      self.rgb_can = imp.Block(IndicatorSinkRgbLed())

    self.connect(self.mcu.gpio.allocate('lcd_led'), self.lcd.led)
    self.connect(self.mcu.gpio.allocate('lcd_reset'), self.lcd.reset)
    self.connect(self.mcu.gpio.allocate('lcd_rs'), self.lcd.rs)
    self.connect(self.mcu.spi.allocate('lcd_spi'), self.lcd.spi)  # MISO unused
    self.connect(self.mcu.gpio.allocate('lcd_cs'), self.lcd.cs)

    self.connect(self.mcu.gpio.allocate_vector('rgb_usb'), self.rgb_usb.signals)
    self.connect(self.mcu.gpio.allocate_vector('rgb_can'), self.rgb_can.signals)

    # Isolated CAN Domain
    # self.can = self.Block(M12CanConnector())  # probably not a great idea for this particular application
    self.can = self.Block(CalSolCanConnectorRa())
    self.can_vcan = self.connect(self.can.pwr)
    self.can_gnd = self.connect(self.can.gnd)

    with self.implicit_connect(
        ImplicitConnect(self.can_gnd, [Common]),
    ) as imp:
      (self.can_reg, self.led_can), _ = self.chain(self.can_vcan,
                                                   imp.Block(LinearRegulator(5.0*Volt(tol=0.05))),
                                                   imp.Block(VoltageIndicatorLed()))
      (self.can_esd, ), _ = self.chain(self.xcvr.can, imp.Block(CanEsdDiode()), self.can.differential)

    self.can_v5v = self.connect(self.can_reg.pwr_out, self.xcvr.can_pwr)
    self.connect(self.can_gnd, self.xcvr.can_gnd)

    # Misc board
    self.duck = self.Block(DuckLogo())
    self.leadfree = self.Block(LeadFreeIndicator())
    self.id = self.Block(IdDots4())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Lpc1549_48),
        (['mcu', 'swd'], SwdCortexTargetTc2050Nl),
        (['sw_usb', 'package'], SmtSwitchRa),
        (['sw_can', 'package'], SmtSwitchRa),
        (['usb_reg'], Ap2204k),
        (['can_reg'], Ap2204k),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
          'can.txd=8',
          'can.rxd=12',
          'sw_usb=28',
          'sw_can=48',
          'lcd_led=23',
          'lcd_reset=13',
          'lcd_rs=15',
          'lcd_spi.sck=21',
          'lcd_spi.mosi=18',
          'lcd_spi.miso=NC',
          'lcd_cs=22',
          'rgb_usb_red=2',
          'rgb_usb_green=1',
          'rgb_usb_blue=3',
          'rgb_can_red=6',
          'rgb_can_green=4',
          'rgb_can_blue=7',
          'swd.swo=PIO0_8',
        ])
      ]
    )


class CanAdapterTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(CanAdapter)
