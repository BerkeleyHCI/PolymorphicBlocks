import unittest

from edg import *


class IotThermalCamera(JlcBoardTop):
  """Dual-mode IR and RGB camera board with ESP32
  """
  def contents(self) -> None:
    super().contents()

    self.usb = self.Block(UsbCReceptacle())
    self.gnd = self.connect(self.usb.gnd)
    self.tp_gnd = self.Block(GroundTestPoint()).connected(self.usb.gnd)

    with self.implicit_connect(  # POWER
            ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.choke, self.tp_pwr), _ = self.chain(
        self.usb.pwr,
        self.Block(SeriesPowerFerriteBead()),
        self.Block(VoltageTestPoint())
      )
      self.pwr = self.connect(self.choke.pwr_out)

      (self.reg_3v3, self.tp_3v3, self.prot_3v3), _ = self.chain(
        self.pwr,
        imp.Block(BuckConverter(output_voltage=3.3*Volt(tol=0.05))),
        self.Block(VoltageTestPoint()),
        imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.9)*Volt))
      )
      self.v3v3 = self.connect(self.reg_3v3.pwr_out)

      (self.reg_3v0, ), _ = self.chain(
        self.v3v3,
        imp.Block(LinearRegulator(output_voltage=3.0*Volt(tol=0.03)))
      )
      self.v3v0 = self.connect(self.reg_3v0.pwr_out)

      (self.reg_2v8, ), _ = self.chain(
        self.v3v3,
        imp.Block(LinearRegulator(output_voltage=2.8*Volt(tol=0.03)))
      )
      self.v2v8 = self.connect(self.reg_2v8.pwr_out)

      (self.reg_1v2, ), _ = self.chain(
        self.v3v3,
        imp.Block(LinearRegulator(output_voltage=1.2*Volt(tol=0.03)))
      )
      self.v1v2 = self.connect(self.reg_1v2.pwr_out)

    # 3V3 DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.v3v3, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())
      self.mcu.with_mixin(IoControllerWifi())

      (self.usb_esd, ), self.usb_chain = self.chain(self.usb.usb, imp.Block(UsbEsdDiode()),
                                                    self.mcu.usb.request())

      self.i2c = self.mcu.i2c.request('i2c')
      (self.i2c_pull, self.i2c_tp), self.i2c_chain = self.chain(
        self.i2c,
        imp.Block(I2cPullup()), imp.Block(I2cTestPoint('i2c')))

      mcu_touch = self.mcu.with_mixin(IoControllerTouchDriver())
      (self.touch_duck, ), _ = self.chain(
        mcu_touch.touch.request('touch_duck'),
        imp.Block(FootprintToucbPad('edg:Symbol_DucklingSolid'))
      )

      # debugging LEDs
      (self.ledr, ), _ = self.chain(imp.Block(IndicatorLed(Led.Red)), self.mcu.gpio.request('ledr'))

    # CAMERA MULTI DOMAIN
    with self.implicit_connect(
            ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.cam = imp.Block(Ov2640_Fpc24())
      self.connect(self.cam.pwr, self.v3v0)
      self.connect(self.cam.pwr_analog, self.v2v8)
      self.connect(self.cam.pwr_digital, self.v1v2)
      self.connect(self.cam.dvp8, self.mcu.with_mixin(IoControllerDvp8()).dvp8.request('cam'))
      self.connect(self.cam.sio, self.i2c)
      self.connect(self.cam.reset, self.mcu.gpio.request('cam_rst'))

      self.flir = imp.Block(FlirLepton())
      self.connect(self.flir.pwr_io, self.v3v0)
      self.connect(self.flir.pwr, self.v2v8)
      self.connect(self.flir.pwr_core, self.v1v2)
      self.connect(self.flir.spi, self.mcu.spi.request('flir'))
      self.connect(self.flir.cci, self.i2c)
      self.connect(self.flir.reset, self.mcu.gpio.request('flir_rst'))
      self.connect(self.flir.shutdown, self.mcu.gpio.request('flir_pwrdn'))
      self.connect(self.flir.cs, self.mcu.gpio.request('flir_cs'))
      self.connect(self.flir.vsync, self.mcu.gpio.request('flir_vsync'))


  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32s3_Wroom_1),
        (['reg_3v3'], Tps54202h),
        (['cam', 'device', 'conn'], Fpc050BottomFlip),
      ],
      instance_values=[
        (['refdes_prefix'], 'T'),  # unique refdes for panelization
        (['mcu', 'pin_assigns'], [
          'cam.vsync=25',
          'cam.href=24',
          'cam_rst=23',
          'cam.y7=22',
          'cam.xclk=21',
          'cam.y6=20',
          'cam.y5=15',
          'cam.pclk=19',
          'cam.y4=12',
          'cam.y0=18',
          'cam.y3=10',
          'cam.y1=17',
          'cam.y2=11',

          'i2c.sda=31',
          'i2c.scl=32',

          'flir_pwrdn=33',
          'flir_rst=34',
          'flir_cs=38',
          'flir.sck=39',
          'flir.mosi=5',
          'flir.miso=4',
          'flir_vsync=7',

          'ledr=_GPIO0_STRAP',

          'touch_duck=6',
        ]),
        (['mcu', 'programming'], 'uart-auto'),
        (['reg_2v8', 'ic', 'actual_dropout'], Range(0.0, 0.05)),  # 3.3V @ 100mA
        (['reg_3v0', 'ic', 'actual_dropout'], Range(0.0, 0.16)),  # 3.3V @ 400mA
        (['reg_3v3', 'power_path', 'inductor', 'manual_frequency_rating'], Range(0, 21e6)),
        (['usb', 'pwr', 'current_limits'], Range(0.0, 0.8)),  # a bit over
      ],
      class_refinements=[
        (EspProgrammingHeader, EspProgrammingTc2030),
        (TestPoint, CompactKeystone5015),
        (LinearRegulator, Tlv757p),  # default type for all LDOs
      ],
      class_values=[
        (CompactKeystone5015, ['lcsc_part'], 'C5199798'),  # RH-5015, which is actually in stock
      ]
    )


class IotThermalCameraTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(IotThermalCamera)
