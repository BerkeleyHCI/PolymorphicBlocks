"""
Simple mechanical keyboard example design, using a socketed dev board

Relies on footprints from external libraries.
In the KiCad Plugin and Content Manager, install the Keyswitch Kicad Library,
also on GitHub here https://github.com/perigoso/keyswitch-kicad-library
The project is set up to reference the third party library as installed by the KiCad
Plugin Manager, it does not need to be in your global library table.
"""

import unittest

from edg import *


class BasicKeyboard(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()

    self.mcu = self.Block(Xiao_Rp2040())

    self.sw = self.Block(SwitchMatrix(nrows=3, ncols=2))
    self.connect(self.sw.cols, self.mcu.gpio.request_vector())
    self.connect(self.sw.rows, self.mcu.gpio.request_vector())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      class_refinements=[
        (Switch, KailhSocket),
      ],
    )


class BasicKeyboardTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(BasicKeyboard)
