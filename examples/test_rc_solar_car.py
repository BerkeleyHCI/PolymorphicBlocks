from edg import *
from electronics_abstract_parts.AbstractDevices import SolarPanel
from electronics_lib.BatteryProtector_S8200A import BatteryProtector_S8200A_Module
from electronics_lib.DcDcConverterModules import Tps61023_Device_Module
from electronics_lib.SolarCharger_LT3652 import SolarCharger_LT3652_Module
from electronics_lib.Microcontroller_nRF52840 import Adafruit_ItsyBitsy_BLE


class RCSolarCar(Block):
  def contents(self) -> None:
    super().contents()
    self.mcu = self.Block(Adafruit_ItsyBitsy_BLE())
    self.boost = self.Block(Tps61023_Device_Module())
    self.solar_charger = self.Block(SolarCharger_LT3652_Module())
    self.battery_protector = self.Block(BatteryProtector_S8200A_Module())
    self.li_ion_bat = self.Block(Battery())
    self.solar_panel = self.Block(SolarPanel())

    # grounds
    self.connect(self.battery_protector.gnd, self.boost.gnd, self.mcu.gnd, self.solar_charger.gnd)
    #
    self.connect(self.battery_protector.vss, self.li_ion_bat.gnd)
    self.connect(self.battery_protector.vdd, self.boost.vin)
    self.connect(self.boost.vout, self.mcu.pwr_bat)
    self.connect(self.solar_panel.pwr, self.solar_charger.vin)
    # self.connect(self.solar_panel.gnd, self.battery_protector.gnd)


if __name__ == "__main__":
  compile_board_inplace(RCSolarCar)
