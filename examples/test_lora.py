import unittest

from edg import *


class EspLora(JlcBoardTop):
  """ESP32 + discrete 915MHz LoRa via SX1262. USB-C powered.
  TODO: add RF TVS diode to avoid device damage
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
        imp.Block(LinearRegulator(output_voltage=3.3*Volt(tol=0.05))),
        self.Block(VoltageTestPoint()),
        imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.9)*Volt))
      )
      self.v3v3 = self.connect(self.reg_3v3.pwr_out)

    with self.implicit_connect(  # 3V3 DOMAIN
        ImplicitConnect(self.v3v3, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())
      self.mcu.with_mixin(IoControllerBle())

      (self.usb_esd, ), self.usb_chain = self.chain(self.usb.usb, imp.Block(UsbEsdDiode()),
                                                    self.mcu.usb.request())

      (self.ledr, ), _ = self.chain(self.mcu.gpio.request('ledr'), imp.Block(IndicatorLed(Led.Red)))
      (self.ledg, ), _ = self.chain(self.mcu.gpio.request('ledg'), imp.Block(IndicatorLed(Led.Green)))
      (self.ledb, ), _ = self.chain(self.mcu.gpio.request('ledb'), imp.Block(IndicatorLed(Led.Blue)))

      self.lora = imp.Block(Sx1262())
      (self.tp_lora_spi, ), _ = self.chain(self.mcu.spi.request('lora'), imp.Block(SpiTestPoint('lr')), self.lora.spi)
      (self.tp_lora_cs, ), _ = self.chain(self.mcu.gpio.request('lora_cs'), imp.Block(DigitalTestPoint('lr_cs')),
                                          self.lora.cs)
      (self.tp_lora_rst, ), _ = self.chain(self.mcu.gpio.request('lora_rst'), imp.Block(DigitalTestPoint('lr_rs')),
                                           self.lora.reset)
      (self.tp_lora_dio, ), _ = self.chain(self.mcu.gpio.request('lora_dio'), imp.Block(DigitalTestPoint('lr_di')),
                                           self.lora.dio1)

      self.oled = imp.Block(Er_Oled_096_1_1())
      self.i2c_pull = imp.Block(I2cPullup())
      self.connect(self.mcu.i2c.request('i2c'), self.i2c_pull.i2c, self.oled.i2c)
      (self.oled_rst, self.oled_pull), _ = self.chain(
        imp.Block(Apx803s()),  # -29 variant used on Adafruit boards
        imp.Block(PullupResistor(10*kOhm(tol=0.05))),
        self.oled.reset
      )

      self.sd = imp.Block(SdCard())
      self.connect(self.mcu.spi.request('sd'), self.sd.spi)
      self.connect(self.mcu.gpio.request('sd_cs'), self.sd.cs)

  def multipack(self) -> None:
    self.tx_cpack = self.PackedBlock(CombinedCapacitor())
    self.pack(self.tx_cpack.elements.request('0'), ['lora', 'tx_l', 'c'])
    self.pack(self.tx_cpack.elements.request('1'), ['lora', 'tx_pi', 'c1'])

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32s3_Wroom_1),
        (['reg_3v3'], Ldl1117),
        (['lora', 'ant'], RfConnectorAntenna),
        (['lora', 'ant', 'conn'], Amphenol901143),
      ],
      instance_values=[
        (['refdes_prefix'], 'L'),  # unique refdes for panelization
        (['mcu', 'pin_assigns'], [
          # LoRa and OLED pinnings consistent with Lilygo T3S3
          'lora.mosi=GPIO6',
          'lora.sck=GPIO5',
          'lora_cs=GPIO7',
          'lora_rst=GPIO8',
          'lora.miso=GPIO3',
          'lora_dio=GPIO38',  # IO33 on original, but is a PSRAM pin
          'i2c.sda=GPIO18',
          'i2c.scl=GPIO17',
          'sd_cs=GPIO13',
          'sd.mosi=GPIO11',
          'sd.sck=GPIO14',
          'sd.miso=GPIO2',

          'ledr=34',
          'ledg=35',
          'ledb=39',
        ]),
        (['mcu', 'programming'], 'uart-auto-button'),
        (['usb', 'conn', 'current_limits'], Range(0.0, 0.72)),  # fudge it a bit
        (['lora', 'balun', 'c', 'capacitance'], Range(2.8e-12 * 0.8, 2.8e-12 * 1.2))  # extend tolerance to find a part
      ],
      class_refinements=[
        (EspProgrammingHeader, EspProgrammingTc2030),
        (SdCard, Molex1040310811),
        (TestPoint, CompactKeystone5015),
      ],
      class_values=[
        (CompactKeystone5015, ['lcsc_part'], 'C5199798'),
        (Nonstrict3v3Compatible, ['nonstrict_3v3_compatible'], True),
      ]
    )


class EspLoraTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(EspLora)
