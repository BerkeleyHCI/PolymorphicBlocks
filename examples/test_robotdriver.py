import unittest
from typing import List, Dict

from edg import *
from electronics_lib.Ws2812b import Ws2812b, Ws2812bArray


class RobotDriver(JlcBoardTop):
  """A USB-connected WiFi-enabled LED matrix that demonstrates a charlieplexing LEX matrix generator.
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

      (self.sw1, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.allocate('sw1'))

      # maximum current draw that is still within the column sink capability of the ESP32

      (self.usb_esd, ), _ = self.chain(self.usb.usb, imp.Block(UsbEsdDiode()), self.mcu.usb.allocate())

    self.motor_driver = self.Block(L293dd())
    self.connect(self.vusb, self.motor_driver.vss)
    self.connect(self.vusb, self.motor_driver.vs)
    self.connect(self.mcu.gnd, self.motor_driver.gnd)

    self.connect(self.mcu.gpio.allocate('enable1'), self.motor_driver.en1)
    self.connect(self.mcu.gpio.allocate('enable2'), self.motor_driver.en2)
    self.connect(self.mcu.gpio.allocate('motor1'), self.motor_driver.in1)
    self.connect(self.mcu.gpio.allocate('motor2'), self.motor_driver.in2)
    self.connect(self.mcu.gpio.allocate('motor3'), self.motor_driver.in3)
    self.connect(self.mcu.gpio.allocate('motor4'), self.motor_driver.in4)

    self.ws2812bArray = self.Block(Ws2812bArray(5))
    self.connect(self.ws2812bArray.vdd, self.vusb)
    self.connect(self.ws2812bArray.gnd, self.gnd)
    self.connect(self.mcu.gpio.allocate('ledArray'), self.ws2812bArray.din)


    # Misc board
    self.duck = self.Block(DuckLogo())
    self.leadfree = self.Block(LeadFreeIndicator())
    self.id = self.Block(IdDots4())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32c3_Wroom02),
        (['reg_3v3'], Ldl1117),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
          'sw1=18',
        ]),

        (['mcu', 'ic', 'require_basic_part'], False),
        (['reg_3v3', 'ic', 'require_basic_part'], False),
        (['prot_3v3', 'diode', 'require_basic_part'], False),
        (['usb_esd', 'require_basic_part'], False),
        (['usb', 'require_basic_part'], False),
      ],
      class_values=[
        (TestPoint, ['require_basic_part'], False),
        (ResistorArray, ['require_basic_part'], False),
      ],
      class_refinements=[
        (PassiveConnector, PinHeader254),
      ],
    )


class RobotDriverTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(RobotDriver)
