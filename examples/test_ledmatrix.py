import unittest

from edg import *


class LedMatrix(JlcBoardTop):
  """A USB-connected WiFi-enabled LED matrix that demonstrates a charlieplexing LED matrix generator.
  """
  def contents(self) -> None:
    super().contents()

    self.usb = self.Block(UsbCReceptacle())

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

      # maximum current draw that is still within the column sink capability of the ESP32
      self.matrix = imp.Block(CharlieplexedLedMatrix(6, 5, current_draw=(3.5, 5)*mAmp, color=Led.Yellow))
      self.connect(self.mcu.gpio.request_vector('led'), self.matrix.ios)

    # Misc board
    self.duck = self.Block(DuckLogo())
    self.leadfree = self.Block(LeadFreeIndicator())
    self.id = self.Block(IdDots4())

  def multipack(self) -> None:
    self.matrix_res1 = self.PackedBlock(ResistorArray())
    self.pack(self.matrix_res1.elements.request('0'), ['matrix', 'res[0]'])
    self.pack(self.matrix_res1.elements.request('1'), ['matrix', 'res[1]'])
    self.pack(self.matrix_res1.elements.request('2'), ['matrix', 'res[2]'])

    self.matrix_res2 = self.PackedBlock(ResistorArray())
    self.pack(self.matrix_res2.elements.request('0'), ['matrix', 'res[3]'])
    self.pack(self.matrix_res2.elements.request('1'), ['matrix', 'res[4]'])

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32c3_Wroom02),
        (['reg_3v3'], Ldl1117),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
          'led_0=3',
          'led_1=4',
          'led_2=5',
          'led_3=6',
          'led_4=17',
          'led_5=15',
          'led_6=10',
          'sw1=18',
        ]),
      ],
    )


class LedMatrixTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(LedMatrix)
