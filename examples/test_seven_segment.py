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

      (self.ledr, ), _ = self.chain(imp.Block(IndicatorLed(Led.Red)), self.mcu.gpio.request('ledr'))
      (self.ledg, ), _ = self.chain(imp.Block(IndicatorLed(Led.Green)), self.mcu.gpio.request('ledg'))
      (self.ledb, ), _ = self.chain(imp.Block(IndicatorLed(Led.Blue)), self.mcu.gpio.request('ledb'))

      self.sw = ElementDict[DigitalSwitch]()
      for i in range(4):
        (self.sw[i], ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request(f'sw{i}'))

      self.i2c = self.mcu.i2c.request('i2c')
      (self.i2c_pull, self.i2c_tp), self.i2c_chain = self.chain(
        self.i2c,
        imp.Block(I2cPullup()), imp.Block(I2cTestPoint()))

      self.env = imp.Block(EnvironmentalSensor_Bme680())
      self.connect(self.i2c, self.env.i2c)
      self.als = imp.Block(LightSensor_Bh1750())
      self.connect(self.i2c, self.als.i2c)

    # 5V DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.pwr, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.rgb_tp, self.rgb_shift), _ = self.chain(
        self.mcu.gpio.request('rgb'),
        imp.Block(DigitalTestPoint()),
        imp.Block(L74Ahct1g125()))

      last_digit = self.rgb_shift.output
      self.digit = ElementDict[NeopixelArray]()
      for i in range(4):
        self.digit[i] = digit = imp.Block(NeopixelArray(2*7))
        self.connect(last_digit, digit.din)
        last_digit = digit.dout

      (self.center, ), _ = self.chain(last_digit, imp.Block(NeopixelArray(2)))
      (self.meta, ), _ = self.chain(self.center.dout, imp.Block(NeopixelArray(2)))

      (self.spk_tp, self.spk_drv, self.spk), self.spk_chain = self.chain(
        self.mcu.dac.request('spk'),
        self.Block(AnalogTestPoint()),
        imp.Block(Tpa2005d1(gain=Range.from_tolerance(10, 0.2))),
        self.Block(Speaker()))

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32_Wroom_32),
        (['reg_3v3'], Ld1117),
        (['pwr_conn', 'conn'], JstPhKVertical),
        (['spk', 'conn'], JstPhKVertical),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [

        ]),
        (['mcu', 'programming'], 'uart-auto')
      ],
      class_refinements=[
        (EspAutoProgrammingHeader, EspProgrammingTc2030),
        (Neopixel, Sk6805_Ec15),
        (Speaker, ConnectorSpeaker),
        (TactileSwitch, Skrtlae010),
      ],
      class_values=[
      ]
    )


class SevenSegmentTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(SevenSegment)
