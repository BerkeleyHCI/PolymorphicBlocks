import unittest
from typing import List, Dict

from edg import *


class TofArrayTest(JlcBoardTop):
  """A ToF LiDAR array with application as emulating a laser harp and demonstrating another array topology.
  """
  def __init__(self):
    super().__init__()

    # design configuration variables
    self.tof_count = self.Parameter(IntExpr(5))

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

      (self.sw1, ), self.sw1_chain = self.chain(
        imp.Block(DigitalSwitch()), self.mcu.gpio.allocate('sw1'))
      (self.leds, ), self.leds_chain = self.chain(
        imp.Block(IndicatorLedArray(self.tof_count)), self.mcu.gpio.allocate_vector('leds'))
      (self.rgb, ), self.rgb_chain = self.chain(
        imp.Block(IndicatorSinkRgbLed()), self.mcu.gpio.allocate_vector('rgb'))

      self.tof = imp.Block(Vl53l0xArray(self.tof_count))
      (self.i2c_pull, ), self.i2c_chain = self.chain(
        self.mcu.i2c.allocate('i2c'), imp.Block(I2cPullup()), self.tof.i2c)
      self.connect(self.mcu.gpio.allocate_vector('tof_xshut'), self.tof.xshut)

      (self.usb_esd, ), self.usb_chain = self.chain(
        self.usb.usb, imp.Block(UsbEsdDiode()), self.mcu.usb.allocate())

    # 5V DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.spk_dac, self.spk_drv, self.spk), self.spk_chain = self.chain(
        self.mcu.gpio.allocate('spk'),
        imp.Block(LowPassRcDac(1*kOhm(tol=0.05), 5*kHertz(tol=0.5))),
        imp.Block(Tpa2005d1(gain=Range.from_tolerance(10, 0.2))),
        self.Block(Speaker()))

      # limit the power draw of the speaker to not overcurrent the USB source
      # this indicates that the device will only be run at partial power
      (self.spk_pwr, ), _ = self.chain(
        self.vusb,
        self.Block(ForcedVoltageCurrentDraw((0, 0.05)*Amp)),
        self.spk_drv.pwr
      )

    # Misc board
    self.duck = self.Block(DuckLogo())
    self.leadfree = self.Block(LeadFreeIndicator())
    self.id = self.Block(IdDots4())

  def multipack(self) -> None:
    pass  # TODO pack things interestingly
    # self.matrix_res1 = self.PackedBlock(ResistorArray())
    # self.pack(self.matrix_res1.elements.allocate('0'), ['matrix', 'res[0]'])
    # self.pack(self.matrix_res1.elements.allocate('1'), ['matrix', 'res[1]'])
    # self.pack(self.matrix_res1.elements.allocate('2'), ['matrix', 'res[2]'])
    #
    # self.matrix_res2 = self.PackedBlock(ResistorArray())
    # self.pack(self.matrix_res2.elements.allocate('0'), ['matrix', 'res[3]'])
    # self.pack(self.matrix_res2.elements.allocate('1'), ['matrix', 'res[4]'])

  def refinements(self) -> Refinements:
    from electronics_lib.Distance_Vl53l0x import Vl53l0x_Device

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
        (Vl53l0x_Device, ['require_basic_part'], False),
      ],
      class_refinements=[
        (SwdCortexTargetWithTdiConnector, SwdCortexTargetTc2050),
        (PassiveConnector, PinHeader254),
        (Speaker, ConnectorSpeaker),
      ],
    )


class TofArrayTestTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(TofArrayTest)
