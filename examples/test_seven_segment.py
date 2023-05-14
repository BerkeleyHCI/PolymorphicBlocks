import unittest

from edg import *


class SevenSegment(JlcBoardTop):
  """RGB 7-segment clock using Neopixels.
  """
  def contents(self) -> None:
    super().contents()

    self.pwr_conn = self.Block(LipoConnector(voltage=(4.5, 5.5)*Volt, actual_voltage=(4.5, 5.5)*Volt))
    self.pwr = self.connect(self.pwr_conn.pwr)
    self.gnd = self.connect(self.pwr_conn.gnd)

    self.tp_pwr = self.Block(VoltageTestPoint()).connected(self.pwr_conn.pwr)
    self.tp_gnd = self.Block(VoltageTestPoint()).connected(self.pwr_conn.gnd)

    # POWER
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.reg_3v3, self.tp_3v3, self.prot_3v3), _ = self.chain(
        self.pwr,
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

      (self.sw1, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request('sw1'))

      (self.ledr, ), _ = self.chain(imp.Block(IndicatorLed(Led.Red)), self.mcu.gpio.request('ledr'))
      (self.ledg, ), _ = self.chain(imp.Block(IndicatorLed(Led.Green)), self.mcu.gpio.request('ledg'))
      (self.ledb, ), _ = self.chain(imp.Block(IndicatorLed(Led.Blue)), self.mcu.gpio.request('ledb'))


    # 5V DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.pwr, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.rgb_pull, self.rgb_tp, self.rgb, ), _ = self.chain(
        self.mcu.gpio.request('rgb').as_open_drain(),
        imp.Block(PullupResistor(10*kOhm(tol=0.05))),
        imp.Block(DigitalTestPoint()),
        imp.Block(NeopixelArray(4*7)))

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32_Wroom_32),
        (['reg_3v3'], Ld1117),
        (['pwr_conn', 'conn'], JstPhKVertical),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [

        ]),
        (['mcu', 'programming'], 'uart-auto')
      ],
      class_refinements=[
        (EspAutoProgrammingHeader, EspProgrammingTc2030),
        (Neopixel, Sk6805_Ec15),
      ],
      class_values=[
      ]
    )


class SevenSegmentTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(SevenSegment)
