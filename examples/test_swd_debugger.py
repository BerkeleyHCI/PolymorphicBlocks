import unittest

from edg import *


class SwdSourceBitBang(InternalSubcircuit, Block):
  def __init__(self) -> None:
    super().__init__()
    self.reset_in = self.Port(DigitalSink.empty())
    self.swclk_in = self.Port(DigitalSink.empty())
    self.swdio_in = self.Port(DigitalSink.empty())  # driving side
    self.swdio_out = self.Port(DigitalSource.empty())  # target side
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


class SwdDebugger(JlcBoardTop):
  def contents(self) -> None:
    super().contents()

    self.usb = self.Block(UsbCReceptacle())

    self.vusb = self.connect(self.usb.pwr)
    self.gnd = self.connect(self.usb.gnd)

    with self.implicit_connect(
        ImplicitConnect(self.vusb, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.vusb_protect = imp.Block(ProtectionZenerDiode(voltage=(5.25, 6)*Volt))

      self.usb_reg = imp.Block(LinearRegulator(3.3*Volt(tol=0.05)))
      self.v3v3 = self.connect(self.usb_reg.pwr_out)

      self.target_reg = imp.Block(Ap2204k(3.3*Volt(tol=0.05)))
      self.vtarget = self.connect(self.target_reg.pwr_out)

    with self.implicit_connect(
        ImplicitConnect(self.v3v3, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())

      (self.usb_esd, ), _ = self.chain(self.usb.usb, imp.Block(UsbEsdDiode()), self.mcu.usb.request())
      (self.sw, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request('sw'))

      (self.led_tgt, ), _ = self.chain(self.mcu.gpio.request(f'led_target'),
                                       imp.Block(IndicatorLed(Led.Yellow)))
      (self.led_usb, ), _ = self.chain(self.mcu.gpio.request(f'led_usb'),
                                       imp.Block(IndicatorLed(Led.White)))

      (self.en_pull, ), _ = self.chain(self.mcu.gpio.request('target_reg_en'),
                                      imp.Block(PullupResistor(4.7*kOhm(tol=0.1))),
                                      self.target_reg.en)

      self.target_drv = imp.Block(SwdSourceBitBang())
      self.connect(self.mcu.gpio.request('target_swclk'), self.target_drv.swclk_in)  # TODO BMP uses pin 15
      self.connect(self.mcu.gpio.request('target_swdio_out'), self.target_drv.swdio_out)
      self.connect(self.mcu.gpio.request('target_swdio_in'), self.target_drv.swdio_in)
      self.connect(self.mcu.gpio.request('target_reset'), self.target_drv.reset_in)
      self.connect(self.mcu.gpio.request('target_swo'), self.target_drv.swo_out)

    with self.implicit_connect(
            ImplicitConnect(self.vtarget, [Power]),
            ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.target = imp.Block(SwdCortexSourceHeaderHorizontal())
      self.connect(self.target_drv.swd, self.target.swd)
      self.connect(self.target_drv.swo_in, self.target.swo)

      self.led_target = imp.Block(VoltageIndicatorLed(Led.Green))
      (self.target_sense, ), _ = self.chain(
        self.vtarget,
        imp.Block(VoltageDivider(output_voltage=1.65*Volt(tol=0.05), impedance=4.7/2*kOhm(tol=0.05))),
        self.mcu.adc.request('target_vsense')
      )

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Stm32f103_48),
        (['mcu', 'swd'], SwdCortexTargetTagConnect),
        (['mcu', 'swd', 'conn'], TagConnectNonLegged),
        (['sw', 'package'], SmtSwitchRa),
        (['usb_reg'], Ap2204k),
      ],
      instance_values=[
        (['refdes_prefix'], 'S'),  # unique refdes for panelization
        (['vusb_protect', 'diode', 'footprint_spec'], 'Diode_SMD:D_SOD-323'),

        (['mcu', 'crystal', 'frequency'], Range.from_tolerance(8000000, 0.005)),
        (['mcu', 'pin_assigns'], [
          # these are pinnings on stock st-link
          'target_vsense=PA0',
          'target_swclk=PB13',
          'target_swdio_out=PB14',
          'target_swdio_in=PB12',
          'target_reset=PB0',
          'target_swo=PA10',
          'led_target=PA9',
          # these are custom additional parts
          'led_usb=14',
          'target_reg_en=16',
          'sw=38',
        ]),
        (['mcu', 'swd_swo_pin'], 'PB3'),
      ],
      class_values=[
        (SmdStandardPackage, ["smd_min_package"], "0402"),
      ],
    )


class SwdDebuggerTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(SwdDebugger)
