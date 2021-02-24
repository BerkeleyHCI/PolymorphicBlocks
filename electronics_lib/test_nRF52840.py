import unittest

from edg import *
from electronics_lib.Microcontroller_nRF52840 import Adafruit_ItsyBitsy_BLE
from examples.ExampleTestUtils import run_test


class TestnRF52840Basic(BoardTop):
  def contents(self):
    super().contents()
    self.mcu = self.Block(Adafruit_ItsyBitsy_BLE())

    self.led = self.Block(IndicatorLed())
    self.connect(self.mcu.gnd, self.led.gnd)
    self.connect(self.mcu.new_io(DigitalBidir), self.led.signal)

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_values=[
        (['mcu', 'pin_assigns'], "")
      ]
    )

class nRF52840TestCase(unittest.TestCase):
  def test_design_basic(self) -> None:
    run_test(TestnRF52840Basic)
