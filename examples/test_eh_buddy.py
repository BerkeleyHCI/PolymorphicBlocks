import unittest

from edg import *
from .test_usb_uart import UartConnector


class EhBuddyTest(JlcBoardTop):
  """Test board for an energy harvesting development project, that can control power to and
  communicate with the DUT.
  """
  def contents(self) -> None:
    super().contents()

    self.usb = self.Block(UsbCReceptacle())

    self.vusb = self.connect(self.usb.pwr)
    self.gnd = self.connect(self.usb.gnd)

    self.tp_vusb = self.Block(VoltageTestPoint()).connected(self.usb.pwr)
    self.tp_gnd = self.Block(VoltageTestPoint()).connected(self.usb.gnd)

    # POWER
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.reg_3v3, self.tp_3v3, self.prot_3v3), _ = self.chain(
        self.vusb,
        imp.Block(LinearRegulator(output_voltage=3.3*Volt(tol=0.05))),
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
      (self.usb_esd, ), _ = self.chain(self.usb.usb, imp.Block(UsbEsdDiode()), self.mcu.usb.request())

      (self.sw1, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request('sw1'))

      (self.ledr, ), _ = self.chain(imp.Block(IndicatorLed(Led.Red)), self.mcu.gpio.request('ledr'))
      (self.ledg, ), _ = self.chain(imp.Block(IndicatorLed(Led.Green)), self.mcu.gpio.request('ledg'))
      (self.ledb, ), _ = self.chain(imp.Block(IndicatorLed(Led.Blue)), self.mcu.gpio.request('ledb'))

    # Switched Domain
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.conn = imp.Block(UartConnector(pwr_current_draw=(0, 150)*mAmp))
      self.connect(self.mcu.uart.request('dut'), self.conn.uart)

      self.isense = imp.Block(OpampCurrentSensor(
        resistance=(0, 100)*mOhm,
        ratio=Range.from_tolerance(50, 0.05),
        input_impedance=10*kOhm(tol=0.05)
      ))
      self.connect(self.vusb, self.isense.pwr_in)
      self.connect(self.v3v3, self.isense.pwr)
      self.connect(self.isense.out, self.mcu.adc.request('isense'))
      self.connect(self.isense.ref, self.isense.gnd.as_analog_source())
      self.sw = imp.Block(HighSideSwitch())
      self.connect(self.mcu.gpio.request('sw'), self.sw.control)
      self.connect(self.isense.pwr_out, self.sw.pwr)
      self.connect(self.sw.output.as_voltage_source(), self.conn.pwr)

    # Misc board
    self.duck = self.Block(DuckLogo())
    self.id = self.Block(IdDots4())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32c3_Wroom02),
        (['reg_3v3'], Ldl1117),

        (['target', 'conn'], PinHeader254),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
        ]),
      ],
      class_refinements=[
        (PassiveConnector, PinHeader254),
      ],
    )


class EhBuddyTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(EhBuddyTest)
