import unittest
from typing import List, Dict

from edg import *

class LipoConnector(Battery, FootprintBlock):
  @init_in_parent
  def __init__(self, voltage: RangeLike = Default((2.5, 4.2)*Volt), *args,
               actual_voltage: RangeLike = Default((2.5, 4.2)*Volt), **kwargs):
    super().__init__(voltage, *args, **kwargs)
    self.conn = self.Block(PassiveConnector())

    self.connect(self.gnd, self.conn.pins.allocate('1').adapt_to(GroundSource()))
    self.connect(self.pwr, self.conn.pins.allocate('2').adapt_to(VoltageSource(
      voltage_out=actual_voltage,  # arbitrary from https://www.mouser.com/catalog/additional/Adafruit_3262.pdf
      current_limits=(0, 2)*Amp,  # arbitrary assuming low capacity, 1 C discharge
    )))
    self.assign(self.actual_capacity, (2, 3.6)*Amp)


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

      self.tof = imp.Block(Vl53l0xArray(3))
      (self.i2c_pull, self.i2c_tp), self.i2c_chain = self.chain(
        self.mcu.i2c.allocate('i2c'),
        imp.Block(I2cPullup()), imp.Block(I2cTestPoint()),
        self.tof.i2c)
      self.connect(self.mcu.gpio.allocate_vector('tof_xshut'), self.tof.xshut)

      self.lcd = imp.Block(Er_Oled_091_3())

    self.motor_driver = self.Block(L293dd())
    self.connect(self.vbatt, self.motor_driver.vss)
    self.connect(self.vbatt, self.motor_driver.vs)
    self.connect(self.mcu.gnd, self.motor_driver.gnd)

    # self.connect(self.mcu.gpio.allocate('enable1'), self.motor_driver.en1)
    # self.connect(self.mcu.gpio.allocate('enable2'), self.motor_driver.en2)
    # self.connect(self.mcu.gpio.allocate('motor1'), self.motor_driver.in1)
    # self.connect(self.mcu.gpio.allocate('motor2'), self.motor_driver.in2)
    # self.connect(self.mcu.gpio.allocate('motor3'), self.motor_driver.in3)
    # self.connect(self.mcu.gpio.allocate('motor4'), self.motor_driver.in4)

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
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32c3_Wroom02),
        (['reg_3v3'], Ap3418),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
          'sw1=18',
        ]),

        (['mcu', 'ic', 'require_basic_part'], False),
        (['reg_3v3', 'ic', 'require_basic_part'], False),
        (['prot_3v3', 'diode', 'require_basic_part'], False),

        # JLC does not have frequency specs, must be checked TODO
        (['reg_3v3', 'power_path', 'inductor', 'frequency'], Range(0, 0)),
        (['reg_3v3', 'power_path', 'inductor', 'require_basic_part'], False),
      ],
      class_values=[
        (TestPoint, ['require_basic_part'], False),
        (ResistorArray, ['require_basic_part'], False),
        (Vl53l0x_Device, ['require_basic_part'], False),
      ],
      class_refinements=[
        (PassiveConnector, PinHeader254),
      ],
    )


class RobotDriverTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(RobotDriver)
