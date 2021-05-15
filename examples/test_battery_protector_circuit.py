import unittest

from edg import *
from electronics_lib.BatteryProtector_S8200A import BatteryProtector_S8200A
from electronics_lib.DcDcConverters import Tps61023


class BatteryProtectorCircuit(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()
    self.battery_voltage = (1, 1.5) * Volt
    self.mcu = self.Block(Stm32f103_48())
    self.battery_protector = self.Block(BatteryProtector_S8200A())
    self.li_ion_bat = self.Block(Li18650(voltage=self.battery_voltage))
    self.led = self.Block(VoltageIndicatorLed())
    self.boost = self.Block(Tps61023(output_voltage=3.3 * Volt(tol=0.07)))
    self.swd = self.Block(SwdCortexTargetHeader())

    self.link_bat_neg = self.connect(self.li_ion_bat.gnd, self.battery_protector.gnd_in)
    self.link_bat_pos = self.connect(self.li_ion_bat.pwr, self.battery_protector.pwr_in)

    self.link_protect_neg = self.connect(self.battery_protector.gnd_out, self.boost.gnd)
    self.link_protect_pos = self.connect(self.battery_protector.pwr_out, self.boost.pwr_in)

    self.link_boost_neg = self.connect(self.boost.gnd, self.mcu.gnd)
    self.link_boost_pos = self.connect(self.boost.pwr_out, self.mcu.pwr)

    self.connect(self.mcu.gnd, self.led.gnd)
    self.connect(self.led.signal, self.mcu.pwr)

    self.connect(self.swd.swd, self.mcu.swd)
    self.connect(self.mcu.gnd, self.swd.gnd)
    self.connect(self.mcu.pwr, self.swd.pwr)


if __name__ == "__main__":
  compile_board_inplace(BatteryProtectorCircuit)

class BatteryProtectorCircuitTestCase(unittest.TestCase):
  def test_design_battery_protector(self) -> None:
    compile_board_inplace(BatteryProtectorCircuit)
