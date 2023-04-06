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

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
      ],
      instance_values=[
      ],
    )


class KeyboardTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(Keyboard, False)
