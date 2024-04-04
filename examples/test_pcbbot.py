import unittest

from edg import *

from .test_robotdriver import PwmConnector


class PcbBot(JlcBoardTop):
  """Robot driver that uses a ESP32 w/ camera and has student-proofing

  Key features:
  - USB-C receptacle for power input and battery charging.
  - LiPo battery connector with voltage regulation and protection circuits.
  - Power management with priority power selection, fuse protection, and gate control.
  - 3.3V voltage regulation for the main logic level power supply.
  - Integrated battery charging circuit with status indication.
  - I2C communication interface with pull-up resistors and test points.
  - Time-of-flight (ToF) sensor array for distance measurement.
  - Inertial Measurement Unit (IMU) and magnetometer for orientation sensing.
  - IO expander for additional GPIOs and a thru-hole RGB LED indicator.
  - OLED display
  - PWM Servo motor
  - Neopixel LED array for RGB lighting
  - Camera module with voltage regulation for image capture.
  - Digital switch for power control.
  - Keyboard mechanical switch with RGB LED
  - Ducky touch button

  Known issues:
  - Charging ic is not reverse protected
  - MCU does not get turned off with the gate when powered by the USB and battery, though the vbatt line turns off. (by design)
  """
  def contents(self) -> None:
    super().contents()

    self.usb = self.Block(UsbCReceptacle(current_limits=(0, 3)*Amp))
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
      (self.fuse, self.gate, self.prot_batt, self.tp_batt), _ = self.chain(
        self.batt.pwr,
        imp.Block(SeriesPowerPptcFuse((2, 4)*Amp)),
        imp.Block(SoftPowerSwitch()),
        imp.Block(ProtectionZenerDiode(voltage=(4.5, 6.0)*Volt)),
        self.Block(VoltageTestPoint()))
      self.vbatt = self.connect(self.gate.pwr_out)  # downstream of fuse

      self.pwr_or = self.Block(PriorityPowerOr(  # also does reverse protection
        (0, 1)*Volt, (0, 0.1)*Ohm
      )).connected_from(self.gnd_merge.pwr_out, self.usb.pwr, self.gate.pwr_out)
      self.pwr = self.connect(self.pwr_or.pwr_out)

      (self.reg_3v3, self.prot_3v3, self.tp_3v3), _ = self.chain(
        self.pwr,
        imp.Block(VoltageRegulator(output_voltage=3.3*Volt(tol=0.05))),
        imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.9)*Volt)),
        self.Block(VoltageTestPoint()),
      )
      self.v3v3 = self.connect(self.reg_3v3.pwr_out)

      (self.charger, ), _ = self.chain(
        self.vusb, imp.Block(Mcp73831(200*mAmp(tol=0.2))), self.batt.chg
      )
      (self.charge_led, ), _ = self.chain(
        self.Block(IndicatorSinkLed(Led.Yellow)), self.charger.stat
      )
      self.connect(self.vusb, self.charge_led.pwr)

    # 3V3 DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.v3v3, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())

      (self.usb_esd, ), self.usb_chain = self.chain(self.usb.usb, imp.Block(UsbEsdDiode()),
                                                    self.mcu.usb.request())

      # single onboard debugging LED
      (self.led, ), _ = self.chain(self.mcu.gpio.request('led'), imp.Block(IndicatorLed(Led.Red)))

      (self.touch_sink, ), self.touch = self.chain(self.mcu.gpio.request('touch'), imp.Block(DummyDigitalSink()))

      self.i2c = self.mcu.i2c.request('i2c')

      self.tof = imp.Block(Vl53l0xArray(4, first_xshut_fixed=True))
      (self.i2c_pull, self.i2c_tp), self.i2c_chain = self.chain(
        self.i2c,
        imp.Block(I2cPullup()), imp.Block(I2cTestPoint('i2c')),
        self.tof.i2c)

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
      self.connect(self.oled.reset, self.mcu.gpio.request("oled_reset"))

      (self.batt_sense, ), _ = self.chain(
        self.vbatt,
        imp.Block(VoltageSenseDivider(full_scale_voltage=2.2*Volt(tol=0.1), impedance=(1, 10)*kOhm)),
        self.mcu.adc.request('vbatt_sense')
      )

      self.chain(self.gate.btn_out, self.mcu.gpio.request('sw0'))
      self.chain(self.mcu.gpio.request('gate_control'), self.gate.control)

    # VBATT DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.vbatt, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.servo = ElementDict[PwmConnector]()
      for i in range(4):
        servo = self.servo[i] = imp.Block(PwmConnector((0, 200)*mAmp))
        self.connect(self.mcu.gpio.request(f'servo{i}'), servo.pwm)


      (self.npx, self.npx_key), _ = self.chain(self.mcu.gpio.request('npx'),  imp.Block(NeopixelArray(4*4)), imp.Block(Neopixel()))


    # CAMERA MULTI DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.reg_2v5, ), _ = self.chain(self.pwr, imp.Block(VoltageRegulator(output_voltage=2.5*Volt(tol=0.05))))
      self.v2v5 = self.connect(self.reg_2v5.pwr_out)
      (self.reg_1v2, ), _ = self.chain(self.pwr, imp.Block(VoltageRegulator(output_voltage=1.2*Volt(tol=0.05))))
      self.v1v2 = self.connect(self.reg_1v2.pwr_out)

      self.cam = imp.Block(Ov2640_Fpc24())
      self.connect(self.cam.pwr, self.v3v3)
      self.connect(self.cam.pwr_analog, self.v2v5)
      self.connect(self.cam.pwr_digital, self.v1v2)
      self.connect(self.mcu.with_mixin(IoControllerDvp8()).dvp8.request('cam'), self.cam.dvp8)
      self.connect(self.cam.sio, self.i2c)

    with self.implicit_connect(
            ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.switch = imp.Block(DigitalSwitch())
      self.connect(self.switch.out, self.mcu.gpio.request('pwr'))

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32s3_Wroom_1),
        (['reg_3v3'], Ldl1117),
        (['tof', 'elt[0]', 'conn'], PinSocket254),
        (['tof', 'elt[1]', 'conn'], PinSocket254),
        (['tof', 'elt[2]', 'conn'], PinSocket254),
        (['tof', 'elt[3]', 'conn'], PinSocket254),
        (['switch', 'package'], KailhSocket),

        (['reg_2v5'], Xc6206p),
        (['reg_1v2'], Xc6206p),
        (['rgb', 'package'], ThtRgbLed),
        (['npx_key'], Sk6812Mini_E),

      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
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
          'cam.href=12',
          'cam.vsync=11',

          "i2c=I2CEXT0",
          "i2c.scl=38",
          "i2c.sda=4",
          "0.dp=14",
          "0.dm=13",
          "servo0=5",
          "servo1=6",
          "servo2=8",
          "servo3=10",
          "npx=9",
          'led=_GPIO0_STRAP',
          'touch=GPIO7'
        ]),
        (['expander', 'pin_assigns'], [
        ]),

        (['prot_batt', 'diode', 'footprint_spec'], 'Diode_SMD:D_SMA'),  # big diodes to dissipate more power
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

        (Diode, ['footprint_spec'], 'Diode_SMD:D_SOD-323'),

        # the camera recommended specs are excessively tight, so loosen them a bit
        (Ov2640_Fpc24, ['device', 'dovdd', 'voltage_limits'], Range(1.71, 4.5)),
        (Ov2640_Fpc24, ['device', 'dvdd', 'voltage_limits'], Range(1.1, 1.36)),  # allow 1v2
        (Ov2640_Fpc24, ['device', 'avdd', 'voltage_limits'], Range(2.3, 3.0)),  # allow 2v5

        (Er_Oled_096_1_1, ['device', 'vbat', 'voltage_limits'], Range(3.0, 4.2)),  # technically out of spec
        (Er_Oled_096_1_1, ['device', 'vdd', 'voltage_limits'], Range(1.65, 4.0)),  # use abs max rating
      ],
    )


class PcbBotTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(PcbBot)
