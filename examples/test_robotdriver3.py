import unittest

from edg import *

from .test_robotdriver import LipoConnector
from .test_robotdriver import PwmConnector


class RobotDriver3(JlcBoardTop):
  """Robot driver that uses a ESP32 w/ camera and has student-proofing
  """
  def contents(self) -> None:
    super().contents()

    self.batt = self.Block(LipoConnector(actual_voltage=(3.7, 4.2)*Volt))

    self.gnd = self.connect(self.batt.gnd)
    self.tp_gnd = self.Block(VoltageTestPoint()).connected(self.batt.gnd)
    self.tp_gnd2 = self.Block(VoltageTestPoint()).connected(self.batt.gnd)

    # POWER
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.fuse, self.prot_in, self.tp_in, self.tp_in2,
       self.reg_3v3, self.prot_3v3, self.tp_3v3, self.tp_3v32), _ = self.chain(
        self.batt.pwr,
        imp.Block(SeriesPowerPptcFuse((2, 4)*Amp)),
        imp.Block(ProtectionZenerDiode(voltage=(4.5, 6.0)*Volt)),
        self.Block(VoltageTestPoint()),
        self.Block(VoltageTestPoint()),

        imp.Block(BuckConverter(output_voltage=3.3*Volt(tol=0.05))),
        imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.9)*Volt)),
        self.Block(VoltageTestPoint()),
      self.Block(VoltageTestPoint()),
      )
      self.vbatt = self.connect(self.fuse.pwr_out)
      self.v3v3 = self.connect(self.reg_3v3.pwr_out)

    # 3V3 DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.v3v3, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(Esp32_Wrover_Dev())  # allows us to use IO2
      self.i2c = self.mcu.i2c.request('i2c')

      self.tof = imp.Block(Vl53l0xArray(4, first_xshut_fixed=True))
      (self.i2c_pull, self.i2c_tp), self.i2c_chain = self.chain(
        self.i2c,
        imp.Block(I2cPullup()), imp.Block(I2cTestPoint()),
        self.tof.i2c)

      # IMU
      self.imu = imp.Block(Imu_Lsm6ds3trc())
      self.mag = imp.Block(Mag_Qmc5883l())
      self.connect(self.i2c, self.imu.i2c, self.mag.i2c)

      # IO EXPANDER
      self.expander = imp.Block(Pcf8574(0))
      self.connect(self.i2c, self.expander.i2c)

      self.leds = imp.Block(IndicatorSinkLedArray(4))
      self.connect(self.expander.io.request_vector('led'), self.leds.signals)

      self.connect(self.expander.io.request_vector('tof_xshut'), self.tof.xshut)

    # VBATT DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.vbatt, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.servo = ElementDict[PwmConnector]()
      for i in range(4):
        servo = self.servo[i] = imp.Block(PwmConnector((0, 200)*mAmp))
        self.connect(self.mcu.gpio.request(f'servo{i}'), servo.pwm)

      self.ws2812bArray = imp.Block(NeopixelArray(6))
      self.connect(self.mcu.io2, self.ws2812bArray.din)

    # Mounting holes
    self.m = ElementDict[MountingHole]()
    for i in range(2):
      self.m[i] = self.Block(MountingHole())

    # Misc board
    self.lemur = self.Block(LemurLogo())
    self.duck = self.Block(DuckLogo())
    self.id = self.Block(IdDots4())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32_Wrover_Dev),
        (['reg_3v3'], Ap3418),
        (['tof', 'elt[0]', 'conn'], PinSocket254),
        (['tof', 'elt[1]', 'conn'], PinSocket254),
        (['tof', 'elt[2]', 'conn'], PinSocket254),
        (['tof', 'elt[3]', 'conn'], PinSocket254),

        (['tp_in2', 'tp'], Keystone5000),
        (['tp_3v32', 'tp'], Keystone5000),
        (['tp_gnd2', 'tp'], Keystone5000),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
        ]),
        (['expander', 'pin_assigns'], [
        ]),
        (['mcu', 'ic', 'fp_footprint'], 'edg:ESP32-WROVER-DEV_Chicken'),

        # JLC does not have frequency specs, must be checked TODO
        (['reg_3v3', 'power_path', 'inductor', 'frequency'], Range(0, 0)),
        (['reg_3v3', 'power_path', 'efficiency'], Range(1.0, 1.0)),  # waive this check
      ],
      class_refinements=[
        (PassiveConnector, JstPhKVertical),  # default connector series unless otherwise specified
        (TestPoint, CompactKeystone5015),
        (Vl53l0x, Vl53l0xConnector),
        (Speaker, ConnectorSpeaker),
        (Neopixel, Ws2812b),
        (MountingHole, MountingHole_M3),
      ],
      class_values=[
        (CompactKeystone5015, ['lcsc_part'], 'C5199798'),  # RH-5015, which is actually in stock
      ],
    )


class RobotDriver3TestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(RobotDriver3)
