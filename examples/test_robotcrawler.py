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
      voltage_out=(0.9, 2.1)*Volt,  # from https://www.pololu.com/blog/814/new-products-special-servos-with-position-feedback
      signal_out=(0.9, 2.1)*Volt
    )))


@abstract_block
class RobotCrawlerSpec(BoardTop):
  """Example spec for a robot crawler, that defines the needed interface blocks but no connections
  or infrastructure parts"""
  SERVO_COUNT = 12
  SERVO_CAM_COUNT = 2
  def __init__(self) -> None:
    super().__init__()
    self.batt = self.Block(LipoConnector(actual_voltage=(3.7, 4.2)*Volt))

    self.servos = ElementDict[ServoFeedbackConnector]()
    for i in range(self.SERVO_COUNT):
      self.servos[str(i)] = self.Block(ServoFeedbackConnector())
    self.imu = self.Block(Lsm6ds3trc())

    self.servos_cam = ElementDict[ServoFeedbackConnector]()
    for i in range(self.SERVO_CAM_COUNT):
      self.servos_cam[str(i)] = self.Block(ServoFeedbackConnector())

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
      self.mcu_servo = imp.Block(IoController())
      self.connect(self.mcu.gpio.request('srv_rst'), self.mcu_servo.with_mixin(Resettable()).reset)
      self.mcu_test = imp.Block(IoController())  # test revised subcircuit only

      self.i2c = self.mcu.i2c.request('i2c')
      (self.i2c_pull, self.i2c_tp), self.i2c_chain = self.chain(
        self.i2c,
        imp.Block(I2cPullup()), imp.Block(I2cTestPoint()))
      self.connect(self.i2c, self.imu.i2c,
                   self.mcu_servo.with_mixin(IoControllerI2cTarget()).i2c_target.request('i2c'),
                   self.mcu_test.with_mixin(IoControllerI2cTarget()).i2c_target.request('i2c'))

      self.connect(self.v3v3, self.imu.vdd, self.imu.vddio)
      self.connect(self.gnd, self.imu.gnd)

      (self.led, ), _ = self.chain(self.mcu.gpio.request('led'), imp.Block(IndicatorLed(Led.Yellow)))

      (self.servo_led, ), _ = self.chain(self.mcu_servo.gpio.request('led'), imp.Block(IndicatorLed(Led.Yellow)))
      (self.test_led, ), _ = self.chain(self.mcu_test.gpio.request_vector('led'), imp.Block(IndicatorLedArray(4, Led.Yellow)))

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
      self.cam = imp.Block(Ov2640_Fpc24())
      self.connect(self.cam.pwr, self.v3v3)
      self.connect(self.cam.pwr_analog, self.v2v5)
      self.connect(self.cam.pwr_digital, self.v1v2)
      self.connect(self.mcu.with_mixin(IoControllerDvp8()).dvp8.request('cam'), self.cam.dvp8)
      self.connect(self.cam.sio, self.i2c)

    # VBATT DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.vbatt, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      for (i, servo) in self.servos.items():
        self.connect(self.vbatt, servo.pwr)
        self.connect(self.gnd, servo.gnd)
        if int(i) < 4:  # 0-3 connected to ESP directly
          self.connect(self.mcu.gpio.request(f'servo{i}'), servo.pwm)
          self.connect(self.mcu.adc.request(f'servo{i}_fb'), servo.fb)
        else:  # rest connected to STM as IO expander
          self.connect(self.mcu_servo.gpio.request(f'servo{i}'), servo.pwm)
          self.connect(self.mcu_servo.adc.request(f'servo{i}_fb'), servo.fb)

      for (i, servo) in self.servos_cam.items():
        self.connect(self.vbatt, servo.pwr)
        self.connect(self.gnd, servo.gnd)
        self.connect(self.mcu_servo.gpio.request(f'servo_cam{i}'), servo.pwm)
        self.connect(self.mcu_servo.adc.request(f'servo_cam{i}_fb'), servo.fb)

      (self.rgbs, ), _ = self.chain(
        self.mcu.gpio.request('rgb'),
        imp.Block(NeopixelArray(10)))


  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32s3_Wroom_1),
        (['mcu_servo'], Stm32f103_48),
        (['mcu_test'], Rp2040),
        (['reg_3v3'], Ap7215),
        (['reg_2v5'], Xc6206p),
        (['reg_1v2'], Xc6206p),
        (['reg_14v'], Tps61040),
        (['batt', 'conn'], JstPhKVertical),
        (['mcu_servo', 'swd', 'conn'], TagConnectNonLegged),
        (['mcu_test', 'swd', 'conn'], TagConnectNonLegged),
      ],
      instance_values=[
        (['refdes_prefix'], 'R'),  # unique refdes for panelization
        (['mcu', 'pin_assigns'], [
          'servo0=34',
          'servo0_fb=38',
          'servo1=35',
          'servo1_fb=39',
          'servo2=4',
          'servo2_fb=5',
          'servo3=6',
          'servo3_fb=7',

          'i2c.scl=10',
          'i2c.sda=9',

          'rgb=32',

          'led=33',

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
        (['mcu_servo', 'pin_assigns'], [
          'servo4=41',
          'servo4_fb=10',
          'servo5=43',
          'servo5_fb=11',
          'servo6=45',
          'servo6_fb=12',
          'servo_cam0=46',
          'servo_cam0_fb=13',
          'servo7=26',
          'servo7_fb=14',

          'servo8=32',
          'servo8_fb=19',
          'servo9=31',
          'servo9_fb=18',
          'servo10=30',
          'servo10_fb=17',
          'servo_cam1=29',
          'servo_cam1_fb=16',
          'servo11=28',
          'servo11_fb=15',

          'led=33',

          'i2c.scl=21',
          'i2c.sda=22',
        ]),
        (['mcu_servo', 'swd_swo_pin'], 'PB6'),  # USART1_TX
        (['mcu_test', 'pin_assigns'], [
          'led_0=4',
          'led_1=12',
          'led_2=14',
          'led_3=16',

          'i2c.scl=37',
          'i2c.sda=36',
        ]),
        (['mcu_test', 'swd_swo_pin'], 'GPIO16'),  # UART0 TX
        (['mcu', 'programming'], 'uart-auto'),
        (['reg_14v', 'inductor', 'part'], "CBC3225T220KR"),
        (['reg_14v', 'inductor', 'manual_frequency_rating'], Range(0, 17e6)),  # 17MHz self-resonant
        (['reg_14v', 'out_cap', 'cap', 'voltage_rating_derating'], 0.85),
      ],
      class_refinements=[
        (EspProgrammingHeader, EspProgrammingTc2030),
        (SwdCortexTargetHeader, SwdCortexTargetTagConnect),
        (Neopixel, Sk6812_Side_A),
        (TestPoint, CompactKeystone5015),
      ],
      class_values=[
        (CompactKeystone5015, ['lcsc_part'], 'C5199798'),  # RH-5015, which is actually in stock
        # the camera recommended specs are excessively tight, so loosen them a bit
        (Ov2640_Fpc24, ['device', 'dovdd', 'voltage_limits'], Range(1.71, 4.5)),
        (Ov2640_Fpc24, ['device', 'dvdd', 'voltage_limits'], Range(1.1, 1.36)),  # allow 1v2
        (Ov2640_Fpc24, ['device', 'avdd', 'voltage_limits'], Range(2.3, 3.0)),  # allow 2v5
        (Er_Oled_096_1c, ['device', 'vcc', 'voltage_limits'], Range(8, 19)),  # abs maximum ratings
        (ServoFeedbackConnector, ['pwr', 'current_draw'], Range(0.005, 0.005)),  # ignore non-static draw
        (Diode, ['footprint_spec'], 'Diode_SMD:D_SOD-323'),
      ]
    )


class RobotCrawlerTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(RobotCrawler)
