import unittest

from edg import *


class EspLora(JlcBoardTop):
  """ESP32 + discrete 915MHz LoRa via SX1262. USB-C powered.
  TODO: add RF TVS diode to avoid device damage
  """
  def contents(self) -> None:
    super().contents()

    self.usb = self.Block(UsbCReceptacle())
    self.pwr = self.connect(self.usb.pwr)
    self.gnd = self.connect(self.usb.gnd)

    self.tp_pwr = self.Block(VoltageTestPoint()).connected(self.usb.pwr)
    self.tp_gnd = self.Block(GroundTestPoint()).connected(self.usb.gnd)

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

    # 3V3 DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.v3v3, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())
      self.mcu.with_mixin(IoControllerBle())

      (self.ledr, ), _ = self.chain(self.mcu.gpio.request('ledr'), imp.Block(IndicatorLed(Led.Red)))
      (self.ledg, ), _ = self.chain(self.mcu.gpio.request('ledg'), imp.Block(IndicatorLed(Led.Green)))
      (self.ledb, ), _ = self.chain(self.mcu.gpio.request('ledb'), imp.Block(IndicatorLed(Led.Blue)))

      self.sw = ElementDict[DigitalSwitch]()
      for i in range(4):
        (self.sw[i], ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request(f'sw{i}'))

      self.lora = imp.Block(Sx1262())
      self.connect(self.mcu.spi.request('lora'), self.lora.spi)
      self.connect(self.mcu.gpio.request('lora_cs'), self.lora.cs)
      self.connect(self.mcu.gpio.request('lora_rst'), self.lora.reset)

      self.oled = imp.Block(Er_Oled_096_1_1())
      self.i2c_pull = imp.Block(I2cPullup())
      self.connect(self.mcu.i2c.request('i2c'), self.i2c_pull.i2c, self.oled.i2c)
      self.connect(self.mcu.gpio.request('oled_rst'), self.oled.reset)

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32s3_Wroom_1),
        (['reg_3v3'], Ldl1117),
      ],
      instance_values=[
        # (['refdes_prefix'], 'C'),  # unique refdes for panelization
        (['mcu', 'pin_assigns'], [
          # LoRa and OLED pinnings consistent with Lilygo T3S3
          'lora.mosi=GPIO6',
          'lora.sck=GPIO5',
          'lora_cs=GPIO7',
          'lora_rst=GPIO8',
          'lora.miso=GPIO3',
          # TODO LORA_DIO = GPIO33
          'i2c.sda=GPIO18',
          'i2c.scl=GPIO17',
        ]),
        (['mcu', 'programming'], 'uart-auto')
      ],
      class_refinements=[
        (EspProgrammingHeader, EspProgrammingTc2030),
        (TestPoint, CompactKeystone5015),
      ],
      class_values=[
        (CompactKeystone5015, ['lcsc_part'], 'C5199798'),  # RH-5015, which is actually in stock
        (Nonstrict3v3Compatible, ['nonstrict_3v3_compatible'], True),
      ]
    )


class EspLoraTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(EspLora)
