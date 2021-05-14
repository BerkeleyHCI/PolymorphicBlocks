from edg import *
from electronics_lib.BatteryProtector_S8200A import BatteryProtector_S8200A
from electronics_lib.Microcontroller_Adafruit_ItsyBitsy_BLE import Adafruit_ItsyBitsy_BLE


class BLECircuit(SimpleBoardTop):
  def contents(self) -> None:
    super().contents()
    self.battery_voltage = (3.6, 4.2) * Volt
    self.mcu = self.Block(Adafruit_ItsyBitsy_BLE())
    self.battery_protector = self.Block(BatteryProtector_S8200A())
    self.li_ion_bat = self.Block(Li18650(voltage=self.battery_voltage))
    self.led = self.Block(IndicatorLed())

    self.link_protect_neg = self.connect(self.battery_protector.gnd_out, self.mcu.gnd)
    self.link_protect_pos = self.connect(self.battery_protector.pwr_out, self.mcu.pwr_bat)

    self.link_bat_neg = self.connect(self.li_ion_bat.gnd, self.battery_protector.gnd_in)
    self.link_bat_pos = self.connect(self.li_ion_bat.pwr, self.battery_protector.pwr_in)

    self.connect(self.mcu.gnd, self.led.gnd)
    self.connect(self.led.signal, self.mcu.digital[0])

if __name__ == "__main__":
  compile_board_inplace(BLECircuit)
