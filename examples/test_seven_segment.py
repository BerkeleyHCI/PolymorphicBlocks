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

      (self.ledr, ), _ = self.chain(self.mcu.gpio.request('ledr'), imp.Block(IndicatorLed(Led.Red)))
      (self.ledg, ), _ = self.chain(self.mcu.gpio.request('ledg'), imp.Block(IndicatorLed(Led.Green)))
      (self.ledb, ), _ = self.chain(self.mcu.gpio.request('ledb'), imp.Block(IndicatorLed(Led.Blue)))

      self.sw = ElementDict[DigitalSwitch]()
      for i in range(4):
        (self.sw[i], ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request(f'sw{i}'))

      self.i2c = self.mcu.i2c.request('i2c')
      (self.i2c_pull, self.i2c_tp), self.i2c_chain = self.chain(
        self.i2c,
        imp.Block(I2cPullup()), imp.Block(I2cTestPoint()))

      self.env = imp.Block(Bme680())
      self.connect(self.i2c, self.env.i2c)
      self.als = imp.Block(Bh1750())
      self.connect(self.i2c, self.als.i2c)

    # 5V DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.pwr, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.rgb_shift, self.rgb_tp), _ = self.chain(
        self.mcu.gpio.request('rgb'),
        imp.Block(L74Ahct1g125()),
        imp.Block(DigitalTestPoint()))

      self.digit = ElementDict[NeopixelArray]()
      for i in range(4):
        self.digit[i] = imp.Block(NeopixelArray(2*7))
      self.center = imp.Block(NeopixelArray(2))
      self.meta = imp.Block(NeopixelArray(2))

      self.connect(self.rgb_shift.output, self.digit[0].din)
      self.connect(self.digit[0].dout, self.digit[1].din)
      self.connect(self.digit[1].dout, self.meta.din)
      self.connect(self.meta.dout, self.center.din)
      self.connect(self.center.dout, self.digit[2].din)
      self.connect(self.digit[2].dout, self.digit[3].din)

      (self.spk_dac, self.spk_tp, self.spk_drv, self.spk), self.spk_chain = self.chain(
        self.mcu.gpio.request('spk'),
        imp.Block(LowPassRcDac(1*kOhm(tol=0.05), 5*kHertz(tol=0.5))),
        self.Block(AnalogTestPoint()),
        imp.Block(Tpa2005d1(gain=Range.from_tolerance(10, 0.2))),
        self.Block(Speaker()))

      self.v5v_sense = imp.Block(VoltageSenseDivider(full_scale_voltage=3.0*Volt(tol=0.1), impedance=(1, 10)*kOhm))
      self.connect(self.v5v_sense.input, self.pwr)
      self.connect(self.v5v_sense.output, self.mcu.adc.request('v5v_sense'))

    self.mount = ElementDict[MountingHole]()
    for i in range(2):
      self.mount[i] = self.Block(MountingHole_M2_5())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32s3_Wroom_1),
        (['reg_3v3'], Ldl1117),
        (['pwr_conn', 'conn'], JstPhKVertical),
        (['spk', 'conn'], JstPhKVertical),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
          'ledr=4',
          'ledg=5',
          'ledb=6',
          'i2c.sda=8',
          'i2c.scl=9',
          'rgb=12',

          'sw0=32',
          'sw1=33',
          'sw2=34',
          'sw3=35',

          'v5v_sense=7',
          'spk=31',
        ]),
        (['mcu', 'programming'], 'uart-auto')
      ],
      class_refinements=[
        (EspAutoProgrammingHeader, EspProgrammingTc2030),
        (Neopixel, Sk6805_Ec15),
        (Switch, Skrtlae010),
        (Speaker, ConnectorSpeaker),
        (TestPoint, CompactKeystone5015),
      ],
      class_values=[
        (CompactKeystone5015, ['lcsc_part'], 'C5199798'),  # RH-5015, which is actually in stock
      ]
    )


class SevenSegmentTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(SevenSegment)
