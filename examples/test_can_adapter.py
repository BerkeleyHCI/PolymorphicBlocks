import os
import unittest

from edg import *
from .ExampleTestUtils import run_test


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
      (self.xcvr, ), _ = self.chain(self.mcu.new_io(CanControllerPort, pin=[8, 12]), imp.Block(Iso1050dub()))

      (self.sw_usb, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.new_io(DigitalBidir, pin=28))
      (self.sw_can, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.new_io(DigitalBidir, pin=48))

      self.lcd = imp.Block(Qt096t_if09())

      self.rgb_usb = imp.Block(IndicatorSinkRgbLed())
      self.rgb_can = imp.Block(IndicatorSinkRgbLed())

    # TODO all pin assignments
    self.connect(self.mcu.new_io(DigitalBidir, pin=23), self.lcd.led)
    self.connect(self.mcu.new_io(DigitalBidir, pin=13), self.lcd.reset)
    self.connect(self.mcu.new_io(DigitalBidir, pin=15), self.lcd.rs)
    self.connect(self.mcu.new_io(SpiMaster, pin=[21, 18, NotConnectedPin]), self.lcd.spi)  # MISO unused
    self.connect(self.mcu.new_io(DigitalBidir, pin=22), self.lcd.cs)

    self.connect(self.mcu.new_io(DigitalBidir, pin=2), self.rgb_usb.red)
    self.connect(self.mcu.new_io(DigitalBidir, pin=1), self.rgb_usb.green)
    self.connect(self.mcu.new_io(DigitalBidir, pin=3), self.rgb_usb.blue)

    self.connect(self.mcu.new_io(DigitalBidir, pin=6), self.rgb_can.red)
    self.connect(self.mcu.new_io(DigitalBidir, pin=4), self.rgb_can.green)
    self.connect(self.mcu.new_io(DigitalBidir, pin=7), self.rgb_can.blue)

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
      ]
    )
