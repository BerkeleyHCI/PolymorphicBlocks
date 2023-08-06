import unittest

from edg import *


class ServoFeedbackConnector(Connector, Block):
  """4-pin connector modeling the FS90-FB micro servo with positional feedback,
  https://www.pololu.com/product/3436
  """
  @init_in_parent
  def __init__(self):
    super().__init__()
    self.conn = self.Block(PinHeader254(4))

    self.pwm = self.Export(self.conn.pins.request('1').adapt_to(DigitalSink()),  # no specs given
                           [Input])
    self.pwr = self.Export(self.conn.pins.request('2').adapt_to(VoltageSink(
      current_draw=(5, 800)*mAmp  # idle @ 4.8v to stall @ 6v
    )), [Power])
    self.gnd = self.Export(self.conn.pins.request('3').adapt_to(Ground()),
                           [Common])

    self.fb = self.Export(self.conn.pins.request('4').adapt_to(AnalogSource(  # no specs given
      voltage_out=(0.9, 2.1)*Volt  # from https://www.pololu.com/blog/814/new-products-special-servos-with-position-feedback
    )), [Common])


@abstract_block
class RobotCrawlerSpec(BoardTop):
  """Example spec for a robot crawler, that defines the needed interface blocks but no connections
  or infrastructure parts"""
  def __init__(self) -> None:
    super().__init__()
    self.batt = self.Block(LipoConnector(actual_voltage=(3.7, 4.2)*Volt))

    self.servo1 = self.Block(ServoFeedbackConnector())
    self.servo2 = self.Block(ServoFeedbackConnector())
    self.servo3 = self.Block(ServoFeedbackConnector())
    self.servo4 = self.Block(ServoFeedbackConnector())
    self.imu = self.Block(Imu_Lsm6ds3trc())
    self.compass = self.Block(Mag_Qmc5883l())


class RobotCrawler(RobotCrawlerSpec, JlcBoardTop):
  """Implementation of the crawler robot, that implements what is needed to connect the interface blocks
  as well as optional additional blocks.
  """
  def contents(self) -> None:
    super().contents()

    self.vbatt = self.connect(self.batt.pwr)
    self.gnd = self.connect(self.batt.gnd)

    self.tp_vbatt = self.Block(VoltageTestPoint()).connected(self.batt.pwr)
    self.tp_gnd = self.Block(VoltageTestPoint()).connected(self.batt.gnd)

    # POWER
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.reg_3v3, self.tp_3v3), _ = self.chain(
        self.vbatt,
        imp.Block(VoltageRegulator(output_voltage=3.3*Volt(tol=0.05))),
        self.Block(VoltageTestPoint())
      )
      self.v3v3 = self.connect(self.reg_3v3.pwr_out)

      (self.reg_14v, self.tp_14v), _ = self.chain(
        self.vbatt,
        imp.Block(VoltageRegulator(output_voltage=(13, 16)*Volt)),
        self.Block(VoltageTestPoint())
      )
      self.v14 = self.connect(self.reg_14v.pwr_out)

      (self.reg_2v5, ), _ = self.chain(
        self.vbatt,
        imp.Block(VoltageRegulator(output_voltage=2.5*Volt(tol=0.05)))
      )
      self.v2v5 = self.connect(self.reg_2v5.pwr_out)

      (self.reg_1v2, ), _ = self.chain(
        self.vbatt,
        imp.Block(VoltageRegulator(output_voltage=1.2*Volt(tol=0.05)))
      )
      self.v1v2 = self.connect(self.reg_1v2.pwr_out)

    # 3V3 DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.v3v3, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())

      self.i2c = self.mcu.i2c.request('i2c')
      (self.i2c_pull, self.i2c_tp), self.i2c_chain = self.chain(
        self.i2c,
        imp.Block(I2cPullup()), imp.Block(I2cTestPoint()))
      self.connect(self.i2c, self.imu.i2c, self.compass.i2c)

      self.connect(self.v3v3, self.imu.vdd, self.imu.vddio, self.compass.vdd)
      self.connect(self.gnd, self.imu.gnd, self.compass.gnd)

      (self.ledr, ), _ = self.chain(self.mcu.gpio.request('ledr'), imp.Block(IndicatorLed(Led.Red)))
      (self.ledg, ), _ = self.chain(self.mcu.gpio.request('ledg'), imp.Block(IndicatorLed(Led.Green)))
      (self.ledb, ), _ = self.chain(self.mcu.gpio.request('ledb'), imp.Block(IndicatorLed(Led.Blue)))

    # OLED MULTI DOMAIN
    with self.implicit_connect(
           ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.oled = imp.Block(Er_Oled_096_1c())
      self.connect(self.oled.vcc, self.v14)
      self.connect(self.oled.pwr, self.v3v3)
      self.connect(self.i2c, self.oled.i2c)
      self.connect(self.mcu.gpio.request('oled_reset'), self.oled.reset)

    # CAMERA MULTI DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      mcu_dvp = self.mcu.with_mixin(IoControllerDvp8())

      self.cam = imp.Block(Ov2640_Fpc24())
      self.connect(self.cam.pwr, self.v3v3)
      self.connect(self.cam.pwr_analog, self.v2v5)
      self.connect(self.cam.pwr_digital, self.v1v2)

      self.connect(mcu_dvp.dvp8.request('cam'), self.cam.dvp8)

      self.connect(self.cam.sio, self.i2c)

    # VBATT DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.vbatt, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.connect(self.vbatt, self.servo1.pwr, self.servo2.pwr, self.servo3.pwr, self.servo4.pwr)
      self.connect(self.gnd, self.servo1.gnd, self.servo2.gnd, self.servo3.gnd, self.servo4.gnd)
      self.connect(self.mcu.gpio.request('servo1'), self.servo1.pwm)
      self.connect(self.mcu.gpio.request('servo2'), self.servo2.pwm)
      self.connect(self.mcu.gpio.request('servo3'), self.servo3.pwm)
      self.connect(self.mcu.gpio.request('servo4'), self.servo4.pwm)

      self.connect(self.mcu.adc.request('servo1_fb'), self.servo1.fb)
      self.connect(self.mcu.adc.request('servo2_fb'), self.servo2.fb)
      self.connect(self.mcu.adc.request('servo3_fb'), self.servo3.fb)
      self.connect(self.mcu.adc.request('servo4_fb'), self.servo4.fb)

      (self.rgbs, ), _ = self.chain(
        self.mcu.gpio.request('rgb'),
        imp.Block(NeopixelArray(4)))


  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32s3_Wroom_1),
        (['reg_3v3'], Ldl1117),
        (['reg_2v5'], Xc6206p),
        (['reg_1v2'], Xc6206p),
        (['reg_14v'], Tps61040),
        (['batt', 'conn'], JstPhKVertical),
      ],
      instance_values=[
        (['refdes_prefix'], 'R'),  # unique refdes for panelization
        (['mcu', 'pin_assigns'], [
          'servo1=31',
          'servo1_fb=4',
          'servo2=32',
          'servo2_fb=5',
          'servo3=12',
          'servo3_fb=6',
          'servo4=11',
          'servo4_fb=7',

          'i2c.scl=10',
          'i2c.sda=9',

          'rgb=38',

          'ledr=33',
          'ledg=34',
          'ledb=35',

          'cam.y2=25',
          'cam.y1=24',
          'cam.y3=23',
          'cam.y0=22',
          'cam.y4=21',
          'cam.pclk=20',
          'cam.y5=19',
          'cam.y6=18',
          'cam.xclk=17',
          'cam.y7=15',
          'cam.href=14',
          'cam.vsync=13',

          'oled_reset=8',
        ]),
        (['mcu', 'programming'], 'uart-auto'),
        (['reg_14v', 'inductor', 'part'], "CBC3225T220KR"),
        (['reg_14v', 'inductor', 'manual_frequency_rating'], Range(0, 17e6))  # 17MHz self-resonant
      ],
      class_refinements=[
        (EspProgrammingHeader, EspProgrammingTc2030),
        (Neopixel, Sk6805_Ec15),
        (TestPoint, CompactKeystone5015),
      ],
      class_values=[
        (CompactKeystone5015, ['lcsc_part'], 'C5199798'),  # RH-5015, which is actually in stock
        # the camera recommended specs are excessively tight, so loosen them a bit
        (Ov2640_Fpc24, ['device', 'dovdd', 'voltage_limits'], Range(1.71, 4.5)),
        (Ov2640_Fpc24, ['device', 'dvdd', 'voltage_limits'], Range(1.1, 1.36)),  # allow 1v2
        (Ov2640_Fpc24, ['device', 'avdd', 'voltage_limits'], Range(2.3, 3.0)),  # allow 2v5
        (Er_Oled_096_1c, ['device', 'vcc', 'voltage_limits'], Range(8, 19)),  # abs maximum ratings
      ]
    )


class RobotCrawlerTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(RobotCrawler)
