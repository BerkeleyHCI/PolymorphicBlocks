from edg import *
from electronics_lib.BatteryProtector_S8200A import BatteryProtector_S8200A
from electronics_lib.Microcontroller_nRF52840 import Adafruit_ItsyBitsy_BLE
from electronics_model.VoltagePorts import VoltageSourceBridge


class BLECircuit(Block):
  def contents(self) -> None:
    super().contents()
    self.mcu = self.Block(Adafruit_ItsyBitsy_BLE())
    self.battery_protector = self.Block(BatteryProtector_S8200A())
    self.li_ion_bat = self.Block(Li18650())

    self.link_protect_neg = self.connect(self.battery_protector.ebm, self.mcu.gnd)
    self.link_protect_pos = self.connect(self.battery_protector.ebp, self.mcu.pwr_bat)

    self.link_bat_neg = self.connect(self.li_ion_bat.gnd, self.battery_protector.vss)
    self.link_bat_pos = self.connect(self.li_ion_bat.pwr, self.battery_protector.vdd)



  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['battery_protector', 'co_fet'], SmtNFet),
        (['battery_protector', 'do_fet'], SmtNFet),
        (['battery_protector', 'vm_res'], ChipResistor),
        (['battery_protector', 'vdd_res'], ChipResistor),
        (['battery_protector', 'vdd_vss_cap'], SmtCeramicCapacitor),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], "")
      ])

if __name__ == "__main__":
  compile_board_inplace(BLECircuit)
