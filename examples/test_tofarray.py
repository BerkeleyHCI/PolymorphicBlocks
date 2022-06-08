import unittest
from typing import List, Dict

from edg import *


class TofArrayTest(JlcBoardTop):
  """A ToF LiDAR array with application as emulating a laser harp and demonstrating another array topology.
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
      (self.leds, ), _ = self.chain(imp.Block(IndicatorLedArray(8)), self.mcu.gpio.allocate_vector('leds'))

      (self.usb_esd, ), _ = self.chain(self.usb.usb, imp.Block(UsbEsdDiode()), self.mcu.usb.allocate())

    # 5V DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.vusb, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.spk_dac, self.spk_tp, self.spk_drv, self.spk), self.spk_chain = self.chain(
        self.mcu.gpio.allocate('spk'),
        imp.Block(LowPassRcDac(1*kOhm(tol=0.05), 5*kHertz(tol=0.5))),
        self.Block(AnalogTestPoint()),
        imp.Block(Tpa2005d1(gain=Range.from_tolerance(10, 0.2))),
        self.Block(Speaker()))

    # Misc board
    self.duck = self.Block(DuckLogo())
    self.leadfree = self.Block(LeadFreeIndicator())
    self.id = self.Block(IdDots4())

  def multipack(self) -> None:
    pass  # TBD
    # self.matrix_res1 = self.PackedBlock(ResistorArray())
    # self.pack(self.matrix_res1.elements.allocate('0'), ['matrix', 'res[0]'])
    # self.pack(self.matrix_res1.elements.allocate('1'), ['matrix', 'res[1]'])
    # self.pack(self.matrix_res1.elements.allocate('2'), ['matrix', 'res[2]'])
    #
    # self.matrix_res2 = self.PackedBlock(ResistorArray())
    # self.pack(self.matrix_res2.elements.allocate('0'), ['matrix', 'res[3]'])
    # self.pack(self.matrix_res2.elements.allocate('1'), ['matrix', 'res[4]'])

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Stm32f103_48),
        (['reg_3v3'], Ldl1117),  # TBD find one that is in stock
        (['spk', 'conn'], JstPhK),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
          # TODO must assign speaker to PWM-capable pin
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
        (Speaker, ConnectorSpeaker),
      ],
    )


class TofArrayTestTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(TofArrayTest)
