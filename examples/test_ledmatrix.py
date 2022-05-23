import unittest
from typing import List

from edg import *


class LedMatrixTest(JlcBoardTop):
  """A USB-connected WiFi-enabled LED matrix that demonstrates a charlieplexing LEX matrix generator.
  """
  def contents(self) -> None:
    super().contents()

    self.usb = self.Block(UsbCReceptacle())

    self.vusb = self.connect(self.usb.pwr)
    self.gnd = self.connect(self.usb.gnd)

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

      self.rgb = imp.Block(IndicatorSinkRgbLed())  # status RGB
      self.connect(self.mcu.gpio.allocate_vector('rgb'), self.rgb.signals)

    # Misc board
    self.duck = self.Block(DuckLogo())
    self.leadfree = self.Block(LeadFreeIndicator())
    self.id = self.Block(IdDots4())


  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32c3_Wroom02),
        (['reg_3v3'], Lp5907),  # could be a cheaper LDO actually

        (['driver', 'fet'], DigikeyFet),
        (['driver', 'diode'], DigikeySmtDiode),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [

        ]),

        (['prot_3v3', 'diode', 'require_basic_part'], False),
        (['prot_analog', 'diode', 'require_basic_part'], False),

        (['usb_esd', 'require_basic_part'], False),
      ],
      class_values=[
        (TestPoint, ['require_basic_part'], False),
      ],
      class_refinements=[
        (PassiveConnector, PinHeader254),
      ],
    )


class LedMatrrixTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(LedMatrixTest)
