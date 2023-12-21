import unittest

from edg import *
from .test_usb_uart import UartConnector


class SwitchController(JlcBoardTop):
  """Test board for an energy harvesting development project, that can control power to and
  communicate with the DUT.
  """
  def contents(self) -> None:
    super().contents()

    self.usb = self.Block(UsbCReceptacle(current_limits=(0, 3)*Amp))

    self.vusb = self.connect(self.usb.pwr)
    self.gnd = self.connect(self.usb.gnd)

    self.tp_vusb = self.Block(VoltageTestPoint()).connected(self.usb.pwr)
    self.tp_gnd = self.Block(VoltageTestPoint()).connected(self.usb.gnd)

    # POWER
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.reg_3v3, self.tp_3v3, self.prot_3v3), _ = self.chain(
        self.vusb,
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

      (self.sw1, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request('sw1'))

      (self.ledr, ), _ = self.chain(imp.Block(IndicatorLed(Led.Red)), self.mcu.gpio.request('ledr'))
      (self.ledg, ), _ = self.chain(imp.Block(IndicatorLed(Led.Green)), self.mcu.gpio.request('ledg'))
      (self.ledb, ), _ = self.chain(imp.Block(IndicatorLed(Led.Blue)), self.mcu.gpio.request('ledb'))

      self.lcd = imp.Block(Er_Oled_091_3())
      self.connect(self.mcu.spi.request('spi'), self.lcd.spi)
      self.connect(self.lcd.cs, self.mcu.gpio.request('lcd_cs'))
      self.connect(self.lcd.reset, self.mcu.gpio.request('lcd_reset'))
      self.connect(self.lcd.dc, self.mcu.gpio.request('lcd_dc'))

    # 5v DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.vusb, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.usb_uart = imp.Block(Cp2102())
      (self.usb_esd, ), _ = self.chain(self.usb.usb, imp.Block(UsbEsdDiode()), self.usb_uart.usb)
      self.connect(self.usb_uart.uart, self.mcu.uart.request('uart'))

    # Switched Domain
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.conn = imp.Block(UartConnector(pwr_current_draw=(0, 1)*Amp))
      self.connect(self.mcu.uart.request('dut'), self.conn.uart)

      self.isense = imp.Block(OpampCurrentSensor(
        resistance=100*mOhm(tol=0.05),
        ratio=Range.from_tolerance(50, 0.05),
        input_impedance=10*kOhm(tol=0.05)
      ))
      self.connect(self.vusb, self.isense.pwr_in)
      self.connect(self.v3v3, self.isense.pwr)
      self.connect(self.isense.out, self.mcu.adc.request('isense'))
      self.connect(self.isense.ref, self.isense.gnd.as_analog_source())
      self.sw = imp.Block(HighSideSwitch())
      self.connect(self.mcu.gpio.request('sw'), self.sw.control)
      self.connect(self.isense.pwr_out, self.sw.pwr)
      self.connect(self.sw.output, self.conn.pwr)

    # Misc board
    self.duck = self.Block(DuckLogo())
    self.id = self.Block(IdDots4())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32_Wroom_32),
        (['reg_3v3'], Ld1117),

        (['conn', 'conn'], PinHeader254),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
          'uart.tx=11',
          'uart.rx=10',

          'ledg=12',
          'ledr=13',
          'ledb=14',
          'sw1=16',

          'dut.tx=28',
          'dut.rx=27',
          'sw=26',
          'isense=23',

          'spi.mosi=36',
          'spi.sck=33',
          'spi.miso=NC',
          'lcd_dc=31',
          'lcd_reset=30',
          'lcd_cs=29',
        ]),
        (['isense', 'out', 'signal_out'], Range(0.1, 2.45)),  # trade range for resolution
      ],
      class_values=[
        (Er_Oled_091_3, ['device', 'vbat', 'voltage_limits'], Range(3.0, 4.2)),  # technically out of spec
        (Er_Oled_091_3, ['device', 'vdd', 'voltage_limits'], Range(1.65, 4.0)),  # use abs max rating
        (Esp32_Wroom_32, ['ic', 'lcsc_part'], 'C701341'),  # -N4 version which is economic PCBA compatible
        (Keystone5015, ['lcsc_part'], 'C5199798'),  # compatible RH-5015
        (Ld1117, ['ic', 'lcsc_part'], 'C115288'),  # LD1117A which is still in stock
      ]
    )


class SwitchControllerTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(SwitchController)
