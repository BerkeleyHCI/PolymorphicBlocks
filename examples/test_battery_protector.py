import unittest

from edg import *


class BatteryProtectorCircuit(BoardTop):
  def contents(self) -> None:
    super().contents()
    self.battery_protector = self.Block(BatteryProtector_S8261A())
    self.li_ion_bat = self.Block(Li18650(voltage=(2.5, 4.2) * Volt))
    self.led = self.Block(VoltageIndicatorLed())

    self.link_bat_neg = self.connect(self.li_ion_bat.gnd, self.battery_protector.gnd_in)
    self.link_bat_pos = self.connect(self.li_ion_bat.pwr, self.battery_protector.pwr_in)

    self.link_protect_neg = self.connect(self.battery_protector.gnd_out, self.led.gnd)
    self.link_protect_pos = self.connect(self.battery_protector.pwr_out, self.led.signal)


class BatteryProtectorCircuitTestCase(unittest.TestCase):
  def test_design_battery_protector(self) -> None:
    compile_board_inplace(BatteryProtectorCircuit)
