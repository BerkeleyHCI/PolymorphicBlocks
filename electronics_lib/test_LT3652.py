import unittest

from edg import *
from electronics_lib.ChargeTracker_LT3652 import ChargeTracker_LT3652
from electronics_lib.Microcontroller_nRF52840 import Adafruit_ItsyBitsy_BLE
from examples.ExampleTestUtils import run_test


class TestLT3652Basic(BoardTop):
  def contents(self):
    super().contents()
    self.mppt = self.Block(ChargeTracker_LT3652())

    # self.led = self.Block(IndicatorLed())
    # self.connect(self.mppt.gnd, self.led.gnd)
    # self.connect(self.mcu.new_io(DigitalBidir), self.led.signal)

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_values=[
        (['mppt', 'pin_assigns'], "")
      ]
    )

class LT3652TestCase(unittest.TestCase):
  def test_design_basic(self) -> None:
    run_test(TestLT3652Basic)
