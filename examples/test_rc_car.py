import unittest

from edg import *
from electronics_lib.BatteryProtector_S8200A import BatteryProtector_S8200A_Module, BatteryProtector_S8200A
from electronics_lib.DcDcConverterModules import Tps61023_Device_Module
from electronics_lib.SolarCharger_LT3652 import SolarCharger_LT3652, SolarCharger_LT3652_Module
from electronics_lib.DcDcConverters import Tps61023_Device
from electronics_lib.Microcontroller_nRF52840 import Adafruit_ItsyBitsy_BLE
from .ExampleTestUtils import run_test


class RcCarTest(Block):
  def contents(self) -> None:
    super().contents()
    # self.battery_protector = self.Block(BatteryProtector_S8200A())
    self.mcu = self.Block(Adafruit_ItsyBitsy_BLE())
    self.boost = self.Block(Tps61023_Device_Module())
    self.solar_charger = self.Block(SolarCharger_LT3652_Module())
    self.battery_protector = self.Block(BatteryProtector_S8200A_Module())
    self.li_ion_bat = self.Block(Battery())
    #
    # self.connect(self.solar_charger.vout, self.battery_protector.vdd)

    # grounds
    # self.connect(self.solar_charger.gnd, self.battery_protector.gnd)
    self.connect(self.battery_protector.gnd, self.boost.gnd, self.mcu.gnd, self.solar_charger.gnd)
    self.connect(self.battery_protector.vss, self.li_ion_bat.gnd)
    self.connect(self.battery_protector.vdd, self.boost.vin)
    self.connect(self.boost.vout, self.mcu.pwr_bat)


class RcCarTestCase(unittest.TestCase):
  @unittest.skip("needs to be completed")
  def test_design_basic(self) -> None:
    run_test(RcCarTest)
