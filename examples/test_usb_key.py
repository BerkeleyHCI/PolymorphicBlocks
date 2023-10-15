import unittest

from edg import *


class UsbKey(JlcBoardTop):
  """USB dongle with the PCB as the USB-A contact surface and a microcontroller on the opposite side.
  Similar circuitry and same pinning as the Solokeys Somu: https://github.com/solokeys/solo-hw/tree/master/solo
  """
  def contents(self) -> None:
    super().contents()

    self.usb = self.Block(UsbAPlugPads())

    self.gnd = self.connect(self.usb.gnd)

    # POWER
    with self.implicit_connect(
            ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.reg_3v3, ), _ = self.chain(
        self.usb.pwr,
        imp.Block(LinearRegulator(output_voltage=3.3*Volt(tol=0.05))),
      )
      self.v3v3 = self.connect(self.reg_3v3.pwr_out)

    # 3V3 DOMAIN
    with self.implicit_connect(
            ImplicitConnect(self.v3v3, [Power]),
            ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())

      self.connect(self.mcu.usb.request('usb'), self.usb.usb)

      (self.rgb, ), _ = self.chain(imp.Block(IndicatorSinkRgbLed()), self.mcu.gpio.request_vector('rgb'))


  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Stm32l432k),
        (['reg_3v3'], Lp5907),
      ],
      class_refinements=[
        (RgbLedCommonAnode, Smt0404RgbLed),
        (SwdCortexTargetHeader, SwdCortexTargetTagConnect),
        (TagConnect, TagConnectNonLegged),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
          # 'touch1=PB4',
          # 'touch2=PB5',
          'rgb_red=PA3',
          'rgb_green=PA2',
          'rgb_blue=PA1',

          # TODO: PB1 is tied low, PC15 is grounded, PH3 is tied high (boot select), PB6 has cap connected
        ]),
      ],
      class_values=[
        (Diode, ['footprint_spec'], 'Diode_SMD:D_SOD-323'),
        (SmdStandardPackage, ["smd_min_package"], "0402"),
        (Lp5907, ['ic', 'footprint_spec'], 'Package_DFN_QFN:UDFN-4-1EP_1x1mm_P0.65mm_EP0.48x0.48mm'),
      ]
    )


class UsbKeyTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(UsbKey)
