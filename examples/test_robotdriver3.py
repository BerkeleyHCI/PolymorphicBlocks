import unittest

from edg import *

from .test_robotdriver import LipoConnector
from .test_robotdriver import MotorConnector
from .test_robotdriver import PwmConnector


class RobotDriver3(JlcBoardTop):
  """Robot driver that uses a ESP32 w/ camera and has student-proofing
  """
  def contents(self) -> None:
    super().contents()

    self.batt = self.Block(LipoConnector(actual_voltage=(3.7, 4.2)*Volt))

    self.gnd = self.connect(self.batt.gnd)
    self.tp_gnd = self.Block(VoltageTestPoint()).connected(self.batt.gnd)

    # POWER
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.fuse, self.prot_in, self.tp_in, self.reg_3v3, self.tp_3v3, s2elf.prot_3v3), _ = self.chain(
        self.batt.pwr,
        imp.Block(SeriesPowerPptcFuse((2, 4)*Amp)),
        imp.Block(ProtectionZenerDiode(voltage=(4.5, 6.0)*Volt)),
        self.Block(VoltageTestPoint()),

        imp.Block(BuckConverter(output_voltage=3.3*Volt(tol=0.05))),
        imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.9)*Volt)),
        self.Block(VoltageTestPoint())
      )
      self.vbatt = self.connect(self.fuse.pwr_out)
      self.v3v3 = self.connect(self.reg_3v3.pwr_out)

    # 3V3 DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.v3v3, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())
      self.i2c = self.mcu.i2c.request('i2c')

      self.tof = imp.Block(Vl53l0xArray(4))
      (self.i2c_pull, self.i2c_tp), self.i2c_chain = self.chain(
        self.i2c,
        imp.Block(I2cPullup()), imp.Block(I2cTestPoint()),
        self.tof.i2c)
      self.connect(self.mcu.gpio.request_vector('tof_xshut'), self.tof.xshut)

      # IMU
      self.imu = imp.Block(Imu_Lsm6ds3trc())
      self.connect(self.i2c, self.imu.i2c)

      self.leds = imp.Block(IndicatorSinkLedArray(4))
      self.connect(self.mcu.gpio.request_vector('led'), self.leds.signals)

    # MOTORS AND SERVOS
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.motor_driver = imp.Block(Drv8833())
      self.connect(self.vbatt, self.motor_driver.pwr)
      self.connect(self.mcu.gpio.request('motor_1a1'), self.motor_driver.ain1)
      self.connect(self.mcu.gpio.request('motor_1a2'), self.motor_driver.ain2)
      self.connect(self.mcu.gpio.request('motor_1b1'), self.motor_driver.bin1)
      self.connect(self.mcu.gpio.request('motor_1b2'), self.motor_driver.bin2)
      self.connect(self.motor_driver.sleep, self.fuse.pwr_out.as_digital_source())

      self.motor_a = self.Block(MotorConnector((-500, 500) * mAmp))
      self.connect(self.motor_a.a, self.motor_driver.aout1)
      self.connect(self.motor_a.b, self.motor_driver.aout2)
      self.motor_b = self.Block(MotorConnector((-500, 500) * mAmp))
      self.connect(self.motor_b.a, self.motor_driver.bout1)
      self.connect(self.motor_b.b, self.motor_driver.bout2)

    self.servo = self.Block(PwmConnector((0, 200)*mAmp))
    self.connect(self.vbatt, self.servo.pwr)
    self.connect(self.gnd, self.servo.gnd)
    self.connect(self.mcu.gpio.request('pwm'), self.servo.pwm)

    # Misc board
    self.lemur = self.Block(LemurLogo())
    self.duck = self.Block(DuckLogo())
    self.id = self.Block(IdDots4())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32_Wrover_Dev),
        (['reg_3v3'], Ap3418),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [

        ]),

        # JLC does not have frequency specs, must be checked TODO
        (['reg_3v3', 'power_path', 'inductor', 'frequency'], Range(0, 0)),
        (['reg_3v3', 'power_path', 'efficiency'], Range(1.0, 1.0)),  # waive this check
      ],
      class_refinements=[
        (PassiveConnector, JstPhKVertical),  # default connector series unless otherwise specified
        (Vl53l0x, Vl53l0xConnector),
        (TestPoint, TeRc),
        (Speaker, ConnectorSpeaker),
        (Neopixel, Ws2812b),
      ],
    )


class RobotDriver3TestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(RobotDriver3)
