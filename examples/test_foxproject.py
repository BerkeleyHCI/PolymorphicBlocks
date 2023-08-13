import unittest

from edg import *

from .test_robotdriver import LedConnector, PwmConnector


class FoxProject(JlcBoardTop):
  """Codename: fox"""
  SERVO_COUNT = 5
  def contents(self) -> None:
    super().contents()

    self.batt = self.Block(LipoConnector(actual_voltage=(3.7, 4.2)*Volt))

    self.pwr = self.connect(self.batt.pwr)
    self.gnd = self.connect(self.batt.gnd)

    self.tp_pwr = self.Block(VoltageTestPoint()).connected(self.batt.pwr)
    self.tp_gnd = self.Block(VoltageTestPoint()).connected(self.batt.gnd)

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

      (self.reg_2v5, ), _ = self.chain(
        self.pwr,
        imp.Block(VoltageRegulator(output_voltage=2.5*Volt(tol=0.05)))
      )
      self.v2v5 = self.connect(self.reg_2v5.pwr_out)

      (self.reg_1v2, ), _ = self.chain(
        self.pwr,
        imp.Block(VoltageRegulator(output_voltage=1.2*Volt(tol=0.05)))
      )
      self.v1v2 = self.connect(self.reg_1v2.pwr_out)

    # 3V3 DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.v3v3, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())
      self.mcu.with_mixin(IoControllerWifi())

      self.i2c = self.mcu.i2c.request('i2c')
      (self.i2c_pull, ), self.i2c_chain = self.chain(
        self.i2c, imp.Block(I2cPullup()))

      self.imu = imp.Block(Imu_Lsm6ds3trc())
      self.connect(self.i2c, self.imu.i2c)

      (self.led, ), _ = self.chain(imp.Block(IndicatorLed(Led.Yellow)), self.mcu.gpio.request('led'))
      (self.sw, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request(f'sw'))

      self.epd = imp.Block(Waveshare_Epd())
      self.connect(self.v3v3, self.epd.pwr)
      self.connect(self.mcu.spi.request('spi'), self.epd.spi)
      self.connect(self.mcu.gpio.request('epd_rst'), self.epd.reset)
      self.connect(self.mcu.gpio.request('epd_dc'), self.epd.dc)
      self.connect(self.mcu.gpio.request('epd_cs'), self.epd.cs)
      self.connect(self.mcu.gpio.request('epd_busy'), self.epd.busy)

    # VBATT DOMAIN
    with self.implicit_connect(
            ImplicitConnect(self.pwr, [Power]),
            ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.pixels = imp.Block(LedConnector())
      self.connect(self.mcu.gpio.request('pixels'), self.pixels.din)

      self.servos = ElementDict[PwmConnector]()
      for i in range(self.SERVO_COUNT):
        servo = self.servos[str(i)] = imp.Block(PwmConnector((5, 100)*mAmp))  # arbitrary low current draw
        self.connect(self.mcu.gpio.request(f'servo{i}'), servo.pwm)

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

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32s3_Wroom_1),
        (['reg_3v3'], Ap7215),
        (['reg_2v5'], Xc6206p),
        (['reg_1v2'], Xc6206p),
        (['batt', 'conn'], JstPhKVertical),
        (['pixels', 'conn'], JstPhKVertical),
      ],
      instance_values=[
        (['refdes_prefix'], 'F'),  # unique refdes for panelization
        (['mcu', 'pin_assigns'], [
          'spi.mosi=39',
          'spi.miso=NC',
          'spi.sck=38',
          'epd_cs=35',
          'epd_dc=34',
          'epd_rst=33',
          'epd_busy=32',

          'pixels=31',

          'cam.y2=13',
          'cam.y1=14',
          'cam.y3=15',
          'cam.y0=17',
          'cam.y4=18',
          'cam.pclk=19',
          'cam.y5=20',
          'cam.y6=21',
          'cam.xclk=22',
          'cam.y7=23',
          'cam.href=24',
          'cam.vsync=25',

          'servo0=8',
          'servo1=9',
          'servo2=10',
          'servo3=11',
          'servo4=12',

          'led=4',

          'i2c.sda=5',
          'i2c.scl=6',
        ]),
        (['mcu', 'programming'], 'uart-auto'),
      ],
      class_refinements=[
        (EspProgrammingHeader, EspProgrammingTc2030),
        (TestPoint, CompactKeystone5015),
        (PinHeader254, PinHeader254Horizontal),
      ],
      class_values=[
        (CompactKeystone5015, ['lcsc_part'], 'C5199798'),  # RH-5015, which is actually in stock
        # the camera recommended specs are excessively tight, so loosen them a bit
        (Ov2640_Fpc24, ['device', 'dovdd', 'voltage_limits'], Range(1.71, 4.5)),
        (Ov2640_Fpc24, ['device', 'dvdd', 'voltage_limits'], Range(1.1, 1.36)),  # allow 1v2
        (Ov2640_Fpc24, ['device', 'avdd', 'voltage_limits'], Range(2.3, 3.0)),  # allow 2v5
        (Diode, ['footprint_spec'], 'Diode_SMD:D_SOD-123'),
        (ZenerDiode, ['footprint_spec'], 'Diode_SMD:D_SOD-123'),
      ]
    )


class FoxProjectTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(FoxProject)
