import unittest

from edg import *

from .test_robotdriver import PwmConnector


class RobotOwl(JlcBoardTop):
  """Controller for a robot owl with a ESP32S3 dev board w/ camera, audio, and peripherals.
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

        imp.Block(LinearRegulator(output_voltage=3.3*Volt(tol=0.05))),
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
      self.mcu = imp.Block(Freenove_Esp32_Wrover())  # allows us to use IO2
      self.i2c = self.mcu.i2c.request('i2c')

      # IMU
      self.imu = imp.Block(Imu_Lsm6ds3trc())
      self.mag = imp.Block(Mag_Qmc5883l())
      self.connect(self.i2c, self.imu.i2c, self.mag.i2c)

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
        (['mcu'], Freenove_Esp32_Wrover),
        (['reg_3v3'], Ap3418),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
        ]),
        (['expander', 'pin_assigns'], [
        ]),
        (['mcu', 'ic', 'fp_footprint'], 'edg:Freenove_ESP32S3-WROOM_Expansion'),
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


class RobotOwlTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(RobotOwl)
