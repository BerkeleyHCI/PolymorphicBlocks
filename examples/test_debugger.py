import unittest

from edg import *


class SwdSourceBitBang(Internal, Block):
  def __init__(self) -> None:
    super().__init__()
    self.reset_in = self.Port(DigitalSink.empty())
    self.swclk_in = self.Port(DigitalSink.empty())
    self.swdio_in = self.Port(DigitalSink.empty())
    self.swdio_out = self.Port(DigitalSource.empty())
    self.swo_out = self.Port(DigitalSource.empty())

    self.swd = self.Port(SwdHostPort.empty(), [Output])
    self.swo_in = self.Port(DigitalSink.empty())

  def contents(self) -> None:
    super().contents()

    self.reset_res = self.Block(Resistor(resistance=22*Ohm(tol=0.05)))
    self.swclk_res = self.Block(Resistor(resistance=22*Ohm(tol=0.05)))
    self.swdio_res = self.Block(Resistor(resistance=22*Ohm(tol=0.05)))
    self.swdio_drv_res = self.Block(Resistor(resistance=100*Ohm(tol=0.05)))

    self.swo_res = self.Block(Resistor(resistance=22*Ohm(tol=0.05)))

    # TODO simplify using DigitalSeriesResistor(?) and chain
    self.connect(self.reset_res.a.adapt_to(DigitalSink()), self.reset_in)
    self.connect(self.reset_res.b.adapt_to(DigitalSource()), self.swd.reset)
    self.connect(self.swclk_res.a.adapt_to(DigitalSink()), self.swclk_in)
    self.connect(self.swclk_res.b.adapt_to(DigitalSource()), self.swd.swclk)
    self.connect(self.swdio_drv_res.a.adapt_to(DigitalSink()), self.swdio_in)
    self.connect(self.swdio_res.a.adapt_to(DigitalBidir()),
                 self.swdio_drv_res.b.adapt_to(DigitalBidir()),
                 self.swdio_out)
    self.connect(self.swdio_res.b.adapt_to(DigitalSink()), self.swd.swdio)
    self.connect(self.swo_res.a.adapt_to(DigitalSource()), self.swo_out)
    self.connect(self.swo_res.b.adapt_to(DigitalSink()), self.swo_in)


class Debugger(BoardTop):
  def contents(self) -> None:
    super().contents()

    self.usb = self.Block(UsbCReceptacle())

    self.vusb = self.connect(self.usb.pwr)
    self.gnd = self.connect(self.usb.gnd)

    with self.implicit_connect(
        ImplicitConnect(self.vusb, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.usb_reg = imp.Block(LinearRegulator(3.3*Volt(tol=0.05)))
      self.usb_esd = imp.Block(UsbEsdDiode())
      self.usb_net = self.connect(self.usb.usb, self.usb_esd.usb)

      self.target_reg = imp.Block(Ap2204k_Block(3.3*Volt(tol=0.05)))

    self.v3v3 = self.connect(self.usb_reg.pwr_out)
    self.vtarget = self.connect(self.target_reg.pwr_out)

    with self.implicit_connect(
        ImplicitConnect(self.vtarget, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.target = imp.Block(SwdCortexSourceHeaderHorizontal())
      self.led_target = imp.Block(VoltageIndicatorLed())

    with self.implicit_connect(
        ImplicitConnect(self.v3v3, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())

      self.target_drv = imp.Block(SwdSourceBitBang())
      self.tdi_res = imp.Block(Resistor(22*Ohm(tol=0.05)))

      self.connect(self.target_drv.swd, self.target.swd)
      self.connect(self.target_drv.swo_in, self.target.swo)
      self.connect(self.tdi_res.b.adapt_to(DigitalSource()), self.target.tdi)

      self.sw_usb = imp.Block(DigitalSwitch())

      self.lcd = imp.Block(Qt096t_if09())

      self.rgb_usb = imp.Block(IndicatorSinkRgbLed())
      self.rgb_tgt = imp.Block(IndicatorSinkRgbLed())

    self.connect(self.mcu.usb.request(), self.usb.usb)

    self.connect(self.mcu.gpio.request('target_reg_en'), self.target_reg.en)

    self.connect(self.mcu.gpio.request('target_swclk'), self.target_drv.swclk_in)  # TODO BMP uses pin 15
    self.connect(self.mcu.gpio.request('target_swdio_out'), self.target_drv.swdio_out)
    self.connect(self.mcu.gpio.request('target_swdio_in'), self.target_drv.swdio_in)
    self.connect(self.mcu.gpio.request('target_reset'), self.target_drv.reset_in)
    self.connect(self.mcu.gpio.request('target_swo'), self.target_drv.swo_out)
    self.connect(self.mcu.gpio.request('target_tdi'), self.tdi_res.a.adapt_to(DigitalSource()))

    self.connect(self.mcu.gpio.request('lcd_led'), self.lcd.led)
    self.connect(self.mcu.gpio.request('lcd_reset'), self.lcd.reset)
    self.connect(self.mcu.gpio.request('lcd_rs'), self.lcd.rs)
    self.connect(self.mcu.spi.request('lcd_spi'), self.lcd.spi)  # MISO unused
    self.connect(self.mcu.gpio.request('lcd_cs'), self.lcd.cs)

    self.connect(self.mcu.gpio.request_vector('rgb_usb'), self.rgb_usb.signals)
    self.connect(self.mcu.gpio.request_vector('rgb_tgt'), self.rgb_tgt.signals)

    self.connect(self.mcu.gpio.request('sw_usb'), self.sw_usb.out)

    # Misc board
    self.duck = self.Block(DuckLogo())
    self.leadfree = self.Block(LeadFreeIndicator())
    self.id = self.Block(IdDots4())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Stm32f103_48),
        (['mcu', 'swd'], SwdCortexTargetTc2050Nl),
        (['sw_usb', 'package'], SmtSwitchRa),
        (['sw_tgt', 'package'], SmtSwitchRa),
        (['usb_reg'], Ap2204k),
      ],
      instance_values=[
        (['mcu', 'crystal', 'frequency'], Range.from_tolerance(8000000, 0.005)),
        (['mcu', 'pin_assigns'], [
          'target_reg_en=16',
          'target_swclk=26',
          'target_swdio_out=27',
          'target_swdio_in=25',
          'target_reset=18',
          'target_swo=31',
          'target_tdi=21',
          'lcd_led=29',
          'lcd_reset=20',
          'lcd_rs=22',
          'lcd_spi.sck=15',
          'lcd_spi.mosi=17',
          'lcd_spi.miso=NC',
          'lcd_cs=28',
          'rgb_usb_red=14',
          'rgb_usb_green=12',
          'rgb_usb_blue=11',
          'rgb_tgt_red=13',
          'rgb_tgt_green=30',  # pinning on stock st-link
          'rgb_tgt_blue=10',
          'sw_usb=38',
        ]),
        (['mcu', 'swd_swo_pin'], 'PB3'),
      ]
    )


class DebuggerTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(Debugger)
