import unittest

from edg import *


class SwdSourceBitBang(Block):
  def __init__(self) -> None:
    super().__init__()
    self.reset_in = self.Port(DigitalSink())
    self.swclk_in = self.Port(DigitalSink())
    self.swdio_in = self.Port(DigitalSink())
    self.swdio_out = self.Port(DigitalSource())
    self.swo_out = self.Port(DigitalSource())  # TODO is this directionality coreect?

    self.swd = self.Port(SwdHostPort(), [Output])

  def contents(self) -> None:
    super().contents()

    self.reset_res = self.Block(Resistor(resistance=22*Ohm(tol=0.05)))
    self.swclk_res = self.Block(Resistor(resistance=22*Ohm(tol=0.05)))
    self.swdio_res = self.Block(Resistor(resistance=22*Ohm(tol=0.05)))
    self.swdio_drv_res = self.Block(Resistor(resistance=100*Ohm(tol=0.05)))
    self.swo_res = self.Block(Resistor(resistance=22*Ohm(tol=0.05)))

    # TODO simplify using DigitalSeriesResistor(?) and chain
    self.connect(self.reset_res.a.as_digital_sink(), self.reset_in)
    self.connect(self.reset_res.b.as_digital_source(), self.swd.reset)
    self.connect(self.swclk_res.a.as_digital_sink(), self.swclk_in)
    self.connect(self.swclk_res.b.as_digital_source(), self.swd.swclk)
    self.connect(self.swdio_drv_res.a.as_digital_sink(), self.swdio_in)
    self.connect(self.swdio_res.a.as_digital_bidir(), self.swdio_drv_res.b.as_digital_bidir(), self.swdio_out)
    self.connect(self.swdio_res.b.as_digital_sink(), self.swd.swdio)
    self.connect(self.swo_res.a.as_digital_source(), self.swo_out)
    self.connect(self.swo_res.b.as_digital_sink(), self.swd.swo)


class Debugger(BoardTop):
  def contents(self) -> None:
    super().contents()

    self.usb = self.Block(UsbDeviceCReceptacle())

    self.vusb = self.connect(self.usb.pwr)
    self.gnd = self.connect(self.usb.gnd)

    with self.implicit_connect(
        ImplicitConnect(self.usb.pwr, [Power]),
        ImplicitConnect(self.usb.gnd, [Common]),
    ) as imp:
      self.usb_reg = imp.Block(LinearRegulator(3.3*Volt(tol=0.05)))
      self.usb_esd = imp.Block(UsbEsdDiode())
      self.usb_net = self.connect(self.usb.usb, self.usb_esd.usb)

      self.target_reg = imp.Block(Ap2204k_Block(3.3*Volt(tol=0.05)))

    self.v3v3 = self.connect(self.usb_reg.pwr_out)

    with self.implicit_connect(
        ImplicitConnect(self.target_reg.pwr_out, [Power]),
        ImplicitConnect(self.usb.gnd, [Common]),
    ) as imp:
      self.target = imp.Block(SwdCortexSourceHeaderHorizontal())
      self.led_target = imp.Block(VoltageIndicatorLed())

    with self.implicit_connect(
        ImplicitConnect(self.usb_reg.pwr_out, [Power]),
        ImplicitConnect(self.usb.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(Stm32f103_48())
      self.swd = imp.Block(SwdCortexTargetTc2050Nl())
      self.connect(self.mcu.swd, self.swd.swd)
      self.crystal = imp.Block(OscillatorCrystal(frequency=8 * MHertz(tol=0.0025)))  # tolerance needed for USB  # TODO infer from presence of SB?
      self.connect(self.mcu.xtal, self.crystal.crystal)

      self.target_drv = imp.Block(SwdSourceBitBang())
      self.tdi_res = imp.Block(Resistor(22*Ohm(tol=0.05)))

      self.connect(self.target_drv.swd, self.target.swd)
      self.connect(self.tdi_res.b.as_digital_source(), self.target.tdi)

      self.sw_usb = imp.Block(DigitalSwitch())

      self.lcd = imp.Block(Qt096t_if09())

      self.rgb_usb = imp.Block(IndicatorSinkRgbLed())
      self.rgb_tgt = imp.Block(IndicatorSinkRgbLed())

    # self.connect(self.mcu.new_io(UsbDevicePort, pin=[33, 32]), self.usb.usb)  # TODO once works in MCU def
    self.connect(self.mcu.usb_0, self.usb.usb)

    self.target_reg_en_net = self.connect(self.mcu.new_io(DigitalBidir), self.target_reg.en)

    self.target_swclk_net = self.connect(self.mcu.new_io(DigitalBidir), self.target_drv.swclk_in)  # TODO BMP uses pin 15
    self.target_swdio_out_net = self.connect(self.mcu.new_io(DigitalBidir), self.target_drv.swdio_out)
    self.target_swdio_in_net = self.connect(self.mcu.new_io(DigitalBidir), self.target_drv.swdio_in)
    self.target_reset_net = self.connect(self.mcu.new_io(DigitalBidir), self.target_drv.reset_in)
    self.target_swo_net = self.connect(self.mcu.new_io(DigitalBidir), self.target_drv.swo_out)
    self.target_tdi_net = self.connect(self.mcu.new_io(DigitalBidir), self.tdi_res.a.as_digital_source())

    self.lcd_led_net = self.connect(self.mcu.new_io(DigitalBidir), self.lcd.led)
    self.lcd_reset_net = self.connect(self.mcu.new_io(DigitalBidir), self.lcd.reset)
    self.lcd_rs_net = self.connect(self.mcu.new_io(DigitalBidir), self.lcd.rs)
    self.lcd_spi_net = self.connect(self.mcu.new_io(SpiMaster), self.lcd.spi)  # MISO unused
    self.lcd_cs_net = self.connect(self.mcu.new_io(DigitalBidir), self.lcd.cs)

    self.rgb_usb_red_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb_usb.red)
    self.rgb_usb_grn_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb_usb.green)
    self.rgb_usb_blue_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb_usb.blue)

    self.rgb_tgt_red_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb_tgt.red)
    self.rgb_tgt_grn_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb_tgt.green)  # pinning on stock ST-Link
    self.rgb_tgt_blue_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb_tgt.blue)

    self.sw_usb_net = self.connect(self.mcu.new_io(DigitalBidir), self.sw_usb.out)

    # Misc board
    self.duck = self.Block(DuckLogo())
    self.leadfree = self.Block(LeadFreeIndicator())
    self.id = self.Block(IdDots4())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['sw_usb', 'package'], SmtSwitchRa),
        (['sw_tgt', 'package'], SmtSwitchRa),
        (['usb_reg'], Ap2204k),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], ';'.join([
          'target_reg_en_net=16',
          'target_swclk_net=26',
          'target_swdio_out_net=27',
          'target_swdio_in_net=25',
          'target_reset_net=18',
          'target_swo_net=31',
          'target_tdi_net=21',
          'lcd_led_net=29',
          'lcd_reset_net=20',
          'lcd_rs_net=22',
          'lcd_spi_net.sck=15',
          'lcd_spi_net.mosi=17',
          'lcd_spi_net.miso=NC',
          'lcd_cs_net=28',
          'rgb_usb_red_net=14',
          'rgb_usb_grn_net=12',
          'rgb_usb_blue_net=11',
          'rgb_tgt_red_net=13',
          'rgb_tgt_grn_net=30',
          'rgb_tgt_blue_net=10',
          'sw_usb_net=38',
        ]))
      ]
    )


class DebuggerTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(Debugger)
