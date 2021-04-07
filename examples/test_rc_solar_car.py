from edg import *
from electronics_abstract_parts.AbstractDevices import SolarPanel
from electronics_lib.BatteryProtector_S8200A import BatteryProtector_S8200A_Module
from electronics_lib.DcDcConverterModules import Tps61023_Device_Module
from electronics_lib.SolarCharger_LT3652 import SolarCharger_LT3652_Module
from electronics_lib.Microcontroller_nRF52840 import Adafruit_ItsyBitsy_BLE
from electronics_model.PassivePort import PassiveAdapterVoltageSource, PassiveAdapterVoltageSink


class RCSolarCar(Block):
  def contents(self) -> None:
    super().contents()
    self.mcu = self.Block(Adafruit_ItsyBitsy_BLE())
    self.boost = self.Block(Tps61023_Device_Module())
    self.solar_charger = self.Block(SolarCharger_LT3652_Module())
    self.battery_protector = self.Block(BatteryProtector_S8200A_Module())
    self.li_ion_bat = self.Block(Battery())
    self.solar_panel = self.Block(SolarPanel())
    self.battery_and_protector = self.Block(MergedVoltageSource())
    self.solar_panel_passive_gnd = self.Block(PassiveAdapterVoltageSink())

    # ground
    self.connect(self.solar_panel_passive_gnd.dst, self.solar_panel.gnd)
    self.link_gnd = self.connect(self.battery_protector.gnd, self.boost.gnd, self.mcu.gnd, self.solar_charger.gnd, self.solar_panel_passive_gnd.src.as_ground())

    # 6v
    self.connect(self.solar_panel.pwr, self.solar_charger.vin)

    # 4.2v
    self.connect(self.battery_and_protector.sink1, self.li_ion_bat.pwr)
    self.connect(self.battery_and_protector.sink2, self.solar_charger.vout)
    self.link_42v = self.connect(self.battery_and_protector.source, self.battery_protector.vdd, self.boost.vin)
    # self.connect(self.li_ion_bat.pwr, self.battery_protector.vdd)

    # 5v
    self.link_5v = self.connect(self.boost.vout, self.mcu.pwr_bat)

    self.connect(self.battery_protector.vss, self.li_ion_bat.gnd)

if __name__ == "__main__":
  compile_board_inplace(RCSolarCar)
