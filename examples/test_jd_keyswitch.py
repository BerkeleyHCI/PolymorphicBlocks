import unittest

from edg import *


class JacdacKeyswitch(JacdacDeviceTop, JlcBoardTop):
  """A Jacdac socketed mechanical keyswitch with RGB, for the gamer-maker in all of us.
  """
  def contents(self) -> None:
    super().contents()



  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Stm32g031_G),
        # (['reg_3v3'], Ldl1117),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
        ]),
      ],
    )


class JacdacKeyswitchTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(JacdacKeyswitch)
