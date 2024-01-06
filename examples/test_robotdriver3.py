import unittest

from edg import *

from .test_robotdriver import PwmConnector


class RobotDriver3(JlcBoardTop):
  """Robot driver that uses a ESP32 w/ camera and has student-proofing
  """
  def contents(self) -> None:
    super().contents()

    self.usb = self.Block(UsbCReceptacle(voltage_out=(9, 20)*Volt, current_limits=(0, 5)*Amp))
    self.vusb = self.connect(self.usb.pwr)

    self.batt = self.Block(LipoConnector(actual_voltage=(3.7, 4.2)*Volt))

    self.gnd_merge = self.Block(MergedVoltageSource()).connected_from(
      self.usb.gnd, self.batt.gnd
    )
    self.gnd = self.connect(self.gnd_merge.pwr_out)
    self.tp_gnd = self.Block(VoltageTestPoint()).connected(self.gnd_merge.pwr_out)

    # POWER
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.fuse, self.prot_in, self.tp_in,
       self.reg_3v3, self.prot_3v3, self.tp_3v3), _ = self.chain(
        self.batt.pwr,
        imp.Block(SeriesPowerPptcFuse((2, 4)*Amp)),
        imp.Block(ProtectionZenerDiode(voltage=(4.5, 6.0)*Volt)),
        self.Block(VoltageTestPoint()),

        imp.Block(VoltageRegulator(output_voltage=3.3*Volt(tol=0.05))),
        imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.9)*Volt)),
        self.Block(VoltageTestPoint()),
      )
      self.vbatt = self.connect(self.fuse.pwr_out)
      self.v3v3 = self.connect(self.reg_3v3.pwr_out)

      (self.charger, ), _ = self.chain(
        self.vusb, imp.Block(Mcp73831(200*mAmp(tol=0.2))), self.batt.chg
      )
      (self.charge_led, ), _ = self.chain(
        self.Block(IndicatorSinkLed(Led.Yellow)), self.charger.stat
      )
      self.connect(self.vusb, self.charge_led.pwr)

      self.pwr_or = self.Block(PriorityPowerOr(
        (0, 1)*Volt, (0, 0.1)*Ohm
      )).connected_from(self.gnd_merge.pwr_out, self.usb.pwr, self.batt.pwr)
      self.pwr = self.connect(self.pwr_or.pwr_out)

    # 3V3 DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.v3v3, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())

      self.connect(self.mcu.usb.request(), self.usb.usb)

      self.i2c = self.mcu.i2c.request('i2c')

      self.tof = imp.Block(Vl53l0xArray(4, first_xshut_fixed=True))
      (self.i2c_pull, self.i2c_tp), self.i2c_chain = self.chain(
        self.i2c,
        imp.Block(I2cPullup()), imp.Block(I2cTestPoint()),
        self.tof.i2c)

      # single onboard debugging LED
      (self.led, ), _ = self.chain(self.mcu.gpio.request('led'), imp.Block(IndicatorLed(Led.Red)))

      # IMU
      self.imu = imp.Block(Imu_Lsm6ds3trc())
      self.mag = imp.Block(Mag_Qmc5883l())
      self.connect(self.i2c, self.imu.i2c, self.mag.i2c)

      # IO EXPANDER
      self.expander = imp.Block(Pca9554())
      self.connect(self.i2c, self.expander.i2c)

      self.connect(self.expander.io.request_vector('tof_xshut'), self.tof.xshut)

      (self.rgb, ), _ = self.chain(self.expander.io.request_vector('rgb'), imp.Block(IndicatorSinkRgbLed()))

      self.oled = imp.Block(Er_Oled_096_1_1())
      self.connect(self.i2c, self.oled.i2c)
      (self.oled_rst, self.oled_pull), _ = self.chain(
        imp.Block(Apx803s(reset_threshold=(2.88, 2.98)*Volt)),  # -29 variant used on Adafruit boards
        imp.Block(PullupResistor(10*kOhm(tol=0.05))),
        self.oled.reset
      )

      (self.batt_sense, ), _ = self.chain(
        self.vbatt,
        imp.Block(VoltageSenseDivider(full_scale_voltage=2.2*Volt(tol=0.1), impedance=(1, 10)*kOhm)),
        self.mcu.adc.request('vbatt_sense')
      )

    # VBATT DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.vbatt, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.servo = ElementDict[PwmConnector]()
      for i in range(4):
        servo = self.servo[i] = imp.Block(PwmConnector((0, 200)*mAmp))
        self.connect(self.mcu.gpio.request(f'servo{i}'), servo.pwm)

      (self.npx, ), _ = self.chain(self.mcu.gpio.request('npx'), imp.Block(NeopixelArray(4*4)))

    # CAMERA MULTI DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
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

      self.cam = imp.Block(Ov2640_Fpc24())
      self.connect(self.cam.pwr, self.v3v3)
      self.connect(self.cam.pwr_analog, self.v2v5)
      self.connect(self.cam.pwr_digital, self.v1v2)
      self.connect(self.mcu.with_mixin(IoControllerDvp8()).dvp8.request('cam'), self.cam.dvp8)
      self.connect(self.cam.sio, self.i2c)

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
        (['mcu'], Esp32s3_Wroom_1),
        (['reg_3v3'], Ldl1117),
        (['tof', 'elt[0]', 'conn'], PinSocket254),
        (['tof', 'elt[1]', 'conn'], PinSocket254),
        (['tof', 'elt[2]', 'conn'], PinSocket254),
        (['tof', 'elt[3]', 'conn'], PinSocket254),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
        ]),
        (['expander', 'pin_assigns'], [
        ]),

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
