from edg import *
from electronics_lib.BatteryProtector_S8200A import BatteryProtector_S8200A
from electronics_lib.Microcontroller_nRF52840 import Adafruit_ItsyBitsy_BLE
from electronics_model.VoltagePorts import VoltageSourceBridge


class BLECircuit(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()
    self.battery_voltage = (3.5, 4.2) * Volt
    self.mcu = self.Block(Adafruit_ItsyBitsy_BLE())
    self.battery_protector = self.Block(BatteryProtector_S8200A(battery_voltage=self.battery_voltage))
    self.li_ion_bat = self.Block(Li18650(voltage=self.battery_voltage))

    self.link_protect_neg = self.connect(self.battery_protector.ebm, self.mcu.gnd)
    self.link_protect_pos = self.connect(self.battery_protector.ebp, self.mcu.pwr_bat)

    self.link_bat_neg = self.connect(self.li_ion_bat.gnd, self.battery_protector.vss)
    self.link_bat_pos = self.connect(self.li_ion_bat.pwr, self.battery_protector.vdd)

if __name__ == "__main__":
  compile_board_inplace(BLECircuit)
