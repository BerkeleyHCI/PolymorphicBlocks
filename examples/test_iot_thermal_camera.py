import unittest

from edg import *


class IotThermalCamera(JlcBoardTop):
  """Dual-mode IR and RGB camera board with ESP32
  """
  def contents(self) -> None:
    super().contents()

    self.usb = self.Block(UsbCReceptacle())
    self.gnd = self.connect(self.usb.gnd)
    self.pwr = self.connect(self.usb.pwr)
    self.tp_gnd = self.Block(GroundTestPoint()).connected(self.usb.gnd)
    self.tp_pwr = self.Block(VoltageTestPoint()).connected(self.usb.pwr)

    with self.implicit_connect(  # POWER
            ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.reg_3v3, self.tp_3v3, self.prot_3v3), _ = self.chain(
        self.pwr,
        imp.Block(BuckConverter(output_voltage=3.3*Volt(tol=0.05))),
        self.Block(VoltageTestPoint()),
        imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.9)*Volt))
      )
      self.v3v3 = self.connect(self.reg_3v3.pwr_out)

      (self.reg_3v0, ), _ = self.chain(
        self.v3v3,
        imp.Block(LinearRegulator(output_voltage=3.0*Volt(tol=0.05)))
      )
      self.v3v0 = self.connect(self.reg_3v0.pwr_out)

      (self.reg_2v8, ), _ = self.chain(
        self.v3v3,
        imp.Block(LinearRegulator(output_voltage=2.8*Volt(tol=0.05)))
      )
      self.v2v8 = self.connect(self.reg_2v8.pwr_out)

      (self.reg_1v2, ), _ = self.chain(
        self.v3v3,
        imp.Block(LinearRegulator(output_voltage=1.2*Volt(tol=0.05)))
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
        imp.Block(I2cPullup()), imp.Block(I2cTestPoint()))

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

      self.flir = imp.Block(FlirLepton())
      self.connect(self.flir.pwr_io, self.v3v0)
      self.connect(self.flir.pwr, self.v2v8)
      self.connect(self.flir.pwr_core, self.v1v2)
      self.connect(self.flir.spi, self.mcu.spi.request('flir'))
      self.connect(self.flir.cci, self.i2c)
      self.connect(self.flir.reset, self.mcu.gpio.request('flir_rst'))
      self.connect(self.flir.cs, self.mcu.gpio.request('flir_cs'))


  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32s3_Wroom_1),
        (['reg_3v3'], Tps54202h),
      ],
      instance_values=[
        (['refdes_prefix'], 'T'),  # unique refdes for panelization
        (['mcu', 'pin_assigns'], [
        ]),
        (['mcu', 'programming'], 'uart-auto'),
        (['reg_2v8', 'ic', 'actual_dropout'], Range(0.0, 0.05)),  # 3.3V @ 100mA
        (['reg_3v0', 'ic', 'actual_dropout'], Range(0.0, 0.16)),  # 3.3V @ 400mA
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
