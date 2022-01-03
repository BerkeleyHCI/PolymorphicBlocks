import unittest
import edg
from edg import *
from electronics_lib.Batteries import AABattery
from electronics_lib.DcDcConverters import Tps61023


class AABatteryCircuit(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()
    self.mcu = self.Block(Stm32f103_48())
    self.bat = self.Block(AABattery())
    self.led = self.Block(VoltageIndicatorLed())
    self.boost = self.Block(Tps61023(output_voltage=3.3 * Volt(tol=0.07)))
    self.swd = self.Block(SwdCortexTargetHeader())

    self.link_bat_neg = self.connect(self.bat.gnd, self.boost.gnd)
    self.link_bat_pos = self.connect(self.bat.pwr, self.boost.pwr_in)

    self.link_boost_neg = self.connect(self.boost.gnd, self.mcu.gnd)
    self.link_boost_pos = self.connect(self.boost.pwr_out, self.mcu.pwr)

    self.connect(self.mcu.gnd, self.led.gnd)
    self.connect(self.led.signal, self.mcu.pwr)

    self.connect(self.swd.swd, self.mcu.swd)
    self.connect(self.mcu.gnd, self.swd.gnd)
    self.connect(self.mcu.pwr, self.swd.pwr)


class AABatteryCircuitTestCase(unittest.TestCase):
  def test_design_aa_battery(self) -> None:
    compile_board_inplace(AABatteryCircuit)

if __name__ == "__main__":
  BoardCompiler.dump_examples(
    AABatteryCircuit,
    base_library=edg,
    print_log=True)
