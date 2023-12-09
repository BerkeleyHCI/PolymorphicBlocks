"""
Mechanical keyboard example design.

Relies on footprints from external libraries.
In the KiCad Plugin and Content Manager, install the Keyswitch Kicad Library,
also on GitHub here https://github.com/perigoso/keyswitch-kicad-library
The project is set up to reference the third party library as installed by the KiCad
Plugin Manager, it does not need to be in your global library table.
"""

import unittest

from edg import *


class Keyboard(JlcBoardTop):
  def contents(self) -> None:
    super().contents()
    self.mcu = self.Block(IoController())
    self.mcu_pwr = self.mcu.with_mixin(IoControllerPowerOut())

    self.pwr_led = self.Block(IndicatorLed())
    self.connect(self.pwr_led.gnd, self.mcu_pwr.gnd_out)
    self.connect(self.pwr_led.signal, self.mcu_pwr.pwr_out.as_digital_source())

    self.led = self.Block(IndicatorLed())
    self.connect(self.led.gnd, self.mcu_pwr.gnd_out)
    self.connect(self.led.signal, self.mcu.gpio.request())

    self.sw = self.Block(SwitchMatrix(2, 2))
    self.connect(self.sw.cols, self.mcu.gpio.request_vector('cols'))
    self.connect(self.sw.rows, self.mcu.gpio.request_vector('rows'))

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Xiao_Rp2040),
      ],
      instance_values=[
      ],
      class_refinements=[
        (Switch, KailhSocket),
      ],
      class_values=[
        (Diode, ['footprint_spec'], 'Diode_SMD:D_SMA')
      ]
    )


class KeyboardTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(Keyboard)
