import unittest
import edg
from edg import *


class CanAdapter(BoardTop):
  def contents(self) -> None:
    super().contents()

    # USB Domain
    self.usb = self.Block(UsbDeviceCReceptacle())

    self.vusb = self.connect(self.usb.pwr)
    self.gnd = self.connect(self.usb.gnd)

    with self.implicit_connect(
        ImplicitConnect(self.usb.gnd, [Common]),
    ) as imp:
      (self.usb_reg, ), _ = self.chain(
        self.usb.pwr,
        imp.Block(LinearRegulator(3.3*Volt(tol=0.05)))
      )

    self.v3v3 = self.connect(self.usb_reg.pwr_out)

    with self.implicit_connect(
        ImplicitConnect(self.usb_reg.pwr_out, [Power]),
        ImplicitConnect(self.usb.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(Lpc1549_48(frequency=12 * MHertz(tol=0.005)))
      (self.swd, ), _ = self.chain(imp.Block(SwdCortexTargetTc2050Nl()), self.mcu.swd)
      (self.crystal, ), _ = self.chain(self.mcu.xtal, imp.Block(OscillatorCrystal(frequency=12 * MHertz(tol=0.005))))  # TODO can we not specify this and instead infer from MCU specs?

      (self.usb_esd, ), _ = self.chain(self.usb.usb, imp.Block(UsbEsdDiode()), self.mcu.usb_0)
      (self.xcvr, ), self.can_chain = self.chain(self.mcu.new_io(CanControllerPort), imp.Block(Iso1050dub()))

      (self.sw_usb, ), self.sw_usb_chain = self.chain(imp.Block(DigitalSwitch()), self.mcu.new_io(DigitalBidir))
      (self.sw_can, ), self.sw_can_chain = self.chain(imp.Block(DigitalSwitch()), self.mcu.new_io(DigitalBidir))

      self.lcd = imp.Block(Qt096t_if09())

      self.rgb_usb = imp.Block(IndicatorSinkRgbLed())
      self.rgb_can = imp.Block(IndicatorSinkRgbLed())

    self.lcd_led_net = self.connect(self.mcu.new_io(DigitalBidir), self.lcd.led)
    self.lcd_reset_net = self.connect(self.mcu.new_io(DigitalBidir), self.lcd.reset)
    self.lcd_rs_net = self.connect(self.mcu.new_io(DigitalBidir), self.lcd.rs)
    self.lcd_spi_net = self.connect(self.mcu.new_io(SpiMaster), self.lcd.spi)  # MISO unused
    self.lcd_cs_net = self.connect(self.mcu.new_io(DigitalBidir), self.lcd.cs)

    self.rgb_usb_red_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb_usb.red)
    self.rgb_usb_grn_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb_usb.green)
    self.rgb_usb_blue_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb_usb.blue)

    self.rgb_can_red_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb_can.red)
    self.rgb_can_grn_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb_can.green)
    self.rgb_can_blue_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb_can.blue)

    # Isolated CAN Domain
    # self.can = self.Block(M12CanConnector())  # probably not a great idea for this particular application
    self.can = self.Block(CalSolCanConnectorRa())
    self.can_vcan = self.connect(self.can.pwr)
    self.can_gnd = self.connect(self.can.gnd)

    with self.implicit_connect(
        ImplicitConnect(self.can.gnd, [Common]),
    ) as imp:
      (self.can_reg, self.led_can), _ = self.chain(self.can.pwr,
                                                   imp.Block(LinearRegulator(5.0*Volt(tol=0.05))),
                                                   imp.Block(VoltageIndicatorLed()))
      (self.can_esd, ), _ = self.chain(self.xcvr.can, imp.Block(CanEsdDiode()), self.can.differential)

    self.can_v5v = self.connect(self.can_reg.pwr_out, self.xcvr.can_pwr)
    self.connect(self.can.gnd, self.xcvr.can_gnd)

    # Misc board
    self.duck = self.Block(DuckLogo())
    self.leadfree = self.Block(LeadFreeIndicator())
    self.id = self.Block(IdDots4())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['sw_usb', 'package'], SmtSwitchRa),
        (['sw_can', 'package'], SmtSwitchRa),
        (['usb_reg'], Ap2204k),
        (['can_reg'], Ap2204k),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], ';'.join([
          'can_chain_0.txd=8',
          'can_chain_0.rxd=12',
          'sw_usb_chain_0=28',
          'sw_can_chain_0=48',
          'lcd_led_net=23',
          'lcd_reset_net=13',
          'lcd_rs_net=15',
          'lcd_spi_net.sck=21',
          'lcd_spi_net.mosi=18',
          'lcd_spi_net.miso=NC',
          'lcd_cs_net=22',
          'rgb_usb_red_net=2',
          'rgb_usb_grn_net=1',
          'rgb_usb_blue_net=3',
          'rgb_can_red_net=6',
          'rgb_can_grn_net=4',
          'rgb_can_blue_net=7',
        ]))
      ]
    )


class CanAdapterTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(CanAdapter)

if __name__ == "__main__":
  BoardCompiler.dump_examples(
    CanAdapter,
    base_library=edg,
    print_log=True)
