import unittest
import edg
from edg import *
from electronics_lib.BatteryProtector_S8200A import BatteryProtector_S8200A
from electronics_lib.DcDcConverters import Tps61023


class BatteryProtectorCircuit(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()
    self.battery_protector = self.Block(BatteryProtector_S8200A())
    self.li_ion_bat = self.Block(Li18650(voltage=(2.5, 4.2) * Volt))
    self.boost = self.Block(Tps61023(output_voltage=5.0 * Volt(tol=0.05)))
    self.led = self.Block(VoltageIndicatorLed())

    self.link_bat_neg = self.connect(self.li_ion_bat.gnd, self.battery_protector.gnd_in)
    self.link_bat_pos = self.connect(self.li_ion_bat.pwr, self.battery_protector.pwr_in)

    self.link_protect_neg = self.connect(self.battery_protector.gnd_out, self.boost.gnd, self.led.gnd)
    self.link_protect_pos = self.connect(self.battery_protector.pwr_out, self.boost.pwr_in)
    self.link_boost_pos = self.connect(self.boost.pwr_out, self.led.signal)

class BatteryProtectorCircuitTestCase(unittest.TestCase):
  def test_design_battery_protector(self) -> None:
    compile_board_inplace(BatteryProtectorCircuit)

if __name__ == "__main__":
  BoardCompiler.dump_examples(
    BatteryProtectorCircuit,
    base_library=edg,
    print_log=True)
