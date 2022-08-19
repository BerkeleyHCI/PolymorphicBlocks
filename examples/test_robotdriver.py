import unittest

from edg import *


class LipoConnector(Battery):
  @init_in_parent
  def __init__(self, voltage: RangeLike = Default((2.5, 4.2)*Volt), *args,
               actual_voltage: RangeLike = Default((2.5, 4.2)*Volt), **kwargs):
    super().__init__(voltage, *args, **kwargs)
    self.conn = self.Block(PassiveConnector())

    self.connect(self.gnd, self.conn.pins.allocate('1').adapt_to(GroundSource()))
    self.connect(self.pwr, self.conn.pins.allocate('2').adapt_to(VoltageSource(
      voltage_out=actual_voltage,  # arbitrary from https://www.mouser.com/catalog/additional/Adafruit_3262.pdf
      current_limits=(0, 5.5)*Amp,  # arbitrary assuming low capacity, 10 C discharge
    )))
    self.assign(self.actual_capacity, (500, 600)*mAmp)  # arbitrary


class MotorConnector(Block):
  def __init__(self):
    super().__init__()
    self.conn = self.Block(PassiveConnector())

    self.a = self.Export(self.conn.pins.allocate('1').adapt_to(DigitalSink(
      current_draw=(-600, 600)*mAmp
    )))
    self.b = self.Export(self.conn.pins.allocate('2').adapt_to(DigitalSink(
      current_draw=(-600, 600)*mAmp
    )))


class PwmConnector(Block):
  def __init__(self):
    super().__init__()
    self.conn = self.Block(PinHeader254())

    self.pwm = self.Export(self.conn.pins.allocate('1').adapt_to(DigitalSink()),
                           [Input])
    self.pwr = self.Export(self.conn.pins.allocate('2').adapt_to(VoltageSink()),
                           [Power])
    self.gnd = self.Export(self.conn.pins.allocate('3').adapt_to(Ground()),
                           [Common])


class RobotDriver(JlcBoardTop):
  """A USB-connected WiFi-enabled LED matrix that demonstrates a charlieplexing LEX matrix generator.
  """
  def contents(self) -> None:
    super().contents()

    self.batt = self.Block(LipoConnector(actual_voltage=(3.7, 4.2)*Volt))

    self.vbatt = self.connect(self.batt.pwr)
    self.gnd = self.connect(self.batt.gnd)

    self.tp_vbatt = self.Block(VoltageTestPoint()).connected(self.batt.pwr)
    self.tp_gnd = self.Block(VoltageTestPoint()).connected(self.batt.gnd)

    # POWER
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.reg_3v3, self.tp_3v3, self.prot_3v3), _ = self.chain(
        self.vbatt,
        imp.Block(BuckConverter(output_voltage=3.3*Volt(tol=0.05))),
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
      self.i2c = self.mcu.i2c.allocate('i2c')

      self.tof = imp.Block(Vl53l0xArray(3))
      (self.i2c_pull, self.i2c_tp), self.i2c_chain = self.chain(
        self.i2c,
        imp.Block(I2cPullup()), imp.Block(I2cTestPoint()),
        self.tof.i2c)

      self.expander = imp.Block(Pcf8574())
      self.connect(self.i2c, self.expander.i2c)
      # TODO use pin assign util for IO expanders
      self.connect(self.expander.io.allocate_vector('tof_xshut'), self.tof.xshut)

      self.lcd = imp.Block(Er_Oled_091_3())
      self.connect(self.mcu.spi.allocate('spi'), self.lcd.spi)
      self.connect(self.lcd.cs, self.expander.io.allocate('lcd_cs'))
      self.connect(self.lcd.reset, self.expander.io.allocate('lcd_reset'))
      self.connect(self.lcd.dc, self.expander.io.allocate('lcd_dc'))

    self.motor_driver = self.Block(Drv8833())
    self.connect(self.vbatt, self.motor_driver.pwr)
    self.connect(self.gnd, self.motor_driver.gnd)
    self.connect(self.mcu.gpio.allocate('motor_ain1'), self.motor_driver.ain1)
    self.connect(self.mcu.gpio.allocate('motor_ain2'), self.motor_driver.ain2)
    self.connect(self.mcu.gpio.allocate('motor_bin1'), self.motor_driver.bin1)
    self.connect(self.mcu.gpio.allocate('motor_bin2'), self.motor_driver.bin2)
    self.connect(self.motor_driver.sleep, self.batt.pwr.as_digital_source())

    self.m1 = self.Block(MotorConnector())
    self.connect(self.m1.a, self.motor_driver.aout1)
    self.connect(self.m1.b, self.motor_driver.aout2)
    self.m2 = self.Block(MotorConnector())
    self.connect(self.m2.a, self.motor_driver.bout1)
    self.connect(self.m2.b, self.motor_driver.bout2)

    self.servo = self.Block(PwmConnector())
    self.connect(self.vbatt, self.servo.pwr)
    self.connect(self.gnd, self.servo.gnd)
    self.connect(self.mcu.gpio.allocate(), self.servo.pwm)

    self.ws2812bArray = self.Block(Ws2812bArray(5))
    self.connect(self.ws2812bArray.vdd, self.vbatt)
    self.connect(self.ws2812bArray.gnd, self.gnd)
    self.connect(self.mcu.gpio.allocate('ledArray'), self.ws2812bArray.din)


    # Misc board
    self.duck = self.Block(DuckLogo())
    self.leadfree = self.Block(LeadFreeIndicator())
    self.id = self.Block(IdDots4())

  def refinements(self) -> Refinements:
    from electronics_lib.Distance_Vl53l0x import Vl53l0x_Device
    from electronics_lib.MotorDriver_Drv8833 import Drv8833_Device
    from electronics_lib.IoExpander_Pcf8574 import Pcf8574_Device
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32c3_Wroom02),
        (['reg_3v3'], Ap3418),

        (['batt', 'conn'], JstPhK),
        (['m1', 'conn'], JstPhK),
        (['m2', 'conn'], JstPhK),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
          'spi.miso=NC',
        ]),

        (['mcu', 'ic', 'require_basic_part'], False),
        (['reg_3v3', 'ic', 'require_basic_part'], False),
        (['prot_3v3', 'diode', 'require_basic_part'], False),

        # JLC does not have frequency specs, must be checked TODO
        (['reg_3v3', 'power_path', 'inductor', 'frequency'], Range(0, 0)),
        (['reg_3v3', 'power_path', 'inductor', 'require_basic_part'], False),
        (['reg_3v3', 'power_path', 'efficiency'], Range(1.0, 1.0)),  # waive this check
        (['lcd', 'device', 'vbat_min'], 3.0),  # datasheet seems to be overly pessimistic
      ],
      class_values=[
        (TestPoint, ['require_basic_part'], False),
        (ResistorArray, ['require_basic_part'], False),
        (Vl53l0x_Device, ['require_basic_part'], False),
        (Drv8833_Device, ['require_basic_part'], False),
        (Pcf8574_Device, ['require_basic_part'], False),
      ],
      class_refinements=[
        (PassiveConnector, PinHeader254),
      ],
    )


class RobotDriverTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(RobotDriver)
