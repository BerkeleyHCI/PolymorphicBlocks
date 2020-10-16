import os
import unittest
import sys

from edg import *
import edg_core.TransformUtil as tfu


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


class Debugger(Block):
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
      self.connect(self.target_reg.pwr_out, self.led_target.signal)

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

    # TODO all pin assignments
    # self.connect(self.mcu.new_io(UsbDevicePort, pin=[33, 32]), self.usb.usb)  # TODO once works in MCU def
    self.connect(self.mcu.usb_0, self.usb.usb)

    self.connect(self.mcu.new_io(DigitalBidir, pin=16), self.target_reg.en)

    self.connect(self.mcu.new_io(DigitalBidir, pin=26), self.target_drv.swclk_in)  # TODO BMP uses pin 15
    self.connect(self.mcu.new_io(DigitalBidir, pin=27), self.target_drv.swdio_out)
    self.connect(self.mcu.new_io(DigitalBidir, pin=25), self.target_drv.swdio_in)
    self.connect(self.mcu.new_io(DigitalBidir, pin=18), self.target_drv.reset_in)
    self.connect(self.mcu.new_io(DigitalBidir, pin=31), self.target_drv.swo_out)
    self.connect(self.mcu.new_io(DigitalBidir, pin=21), self.tdi_res.a.as_digital_source())

    self.connect(self.mcu.new_io(DigitalBidir, pin=29), self.lcd.led)
    self.connect(self.mcu.new_io(DigitalBidir, pin=20), self.lcd.reset)
    self.connect(self.mcu.new_io(DigitalBidir, pin=22), self.lcd.rs)
    self.connect(self.mcu.new_io(SpiMaster, pin=[15, 17, NotConnectedPin]), self.lcd.spi)  # MISO unused
    self.connect(self.mcu.new_io(DigitalBidir, pin=28), self.lcd.cs)

    self.connect(self.mcu.new_io(DigitalBidir, pin=14), self.rgb_usb.red)
    self.connect(self.mcu.new_io(DigitalBidir, pin=12), self.rgb_usb.green)
    self.connect(self.mcu.new_io(DigitalBidir, pin=11), self.rgb_usb.blue)

    self.connect(self.mcu.new_io(DigitalBidir, pin=13), self.rgb_tgt.red)
    self.connect(self.mcu.new_io(DigitalBidir, pin=30), self.rgb_tgt.green)  # pinning on stock ST-Link
    self.connect(self.mcu.new_io(DigitalBidir, pin=10), self.rgb_tgt.blue)

    self.connect(self.mcu.new_io(DigitalBidir, pin=38), self.sw_usb.out)

    # Misc board
    self.duck = self.Block(DuckLogo())
    self.leadfree = self.Block(LeadFreeIndicator())
    self.id = self.Block(IdDots4())


class DebuggerTestCase(unittest.TestCase):
  def test_design(self) -> None:
    ElectronicsDriver([sys.modules[__name__]]).generate_write_block(
      Debugger(),
      os.path.splitext(__file__)[0],
      instance_refinements={
        tfu.Path.empty().append_block('sw_usb').append_block('package'): SmtSwitchRa,
        tfu.Path.empty().append_block('sw_tgt').append_block('package'): SmtSwitchRa,
        tfu.Path.empty().append_block('usb_reg'): Ap2204k,
      }
    )
