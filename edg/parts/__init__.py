from ..abstract_parts import *

from .analog import *
from .connector import *
from .display import *
from .interface import *
from .microcontroller import *
from .power import *
from .sensor import *

from .jlc import *

from .Leds import SmtLed, ThtLed, Smt0606RgbLed, Smt0404RgbLed, ThtRgbLed

from .Batteries import Cr2032, Li18650, AaBattery, AaBatteryStack
from .Switches import SmtSwitch, SmtSwitchRa, KailhSocket
from .Joystick_Xbox import XboxElite2Joystick
from .RotaryEncoder_Alps import Ec11eWithSwitch, Ec11j15WithSwitch, Ec05e
from .RotaryEncoder_Bourns import Pec11s
from .DirectionSwitch_Alps import Skrh

from .Speakers import Speaker, ConnectorSpeaker
from .SpeakerDriver_Analog import Lm4871, Tpa2005d1, Pam8302a
from .SpeakerDriver_Max98357a import Max98357a
from .Microphone_Sd18ob261 import Sd18ob261
from .Opamp_Mcp6001 import Mcp6001
from .Opamp_Tlv9061 import Tlv9061
from .Opamp_Tlv915x import Tlv9152
from .Opamp_Opax171 import Opa2171
from .Opamp_Opax197 import Opa197, Opa2197
from .Opamp_Opax189 import Opa189, Opa2189
from .Opamp_Opax333 import Opa2333
from .Opamp_Lmv321 import Lmv321
from .Inamp_Ina826 import Ina826
from .CeramicResonator_Cstne import Cstne


from .Jumpers import SolderJumperTriangular

from .DebugHeaders import SwdCortexTargetHeader
from .DebugHeaders import SwdCortexTargetTc2050, SwdCortexTargetTagConnect, SwdCortexTargetTc2050
from .SdCards import SdCard, SdSocket, MicroSdSocket, Dm3btDsfPejs, Molex1040310811


from .VoltageReferences import Ref30xx

from .PowerConditioning import (
    SingleDiodePowerMerge,
    DiodePowerMerge,
    PriorityPowerOr,
    SoftPowerGate,
    SoftPowerSwitch,
    PmosReverseProtection,
    PmosChargerReverseProtection,
)
from .LedDriver_Al8861 import Al8861
from .LedDriver_Tps92200 import Tps92200
from .ResetGenerator_Apx803s import Apx803s
from .BootstrapVoltageAdder import BootstrapVoltageAdder


from .IoExpander_Pcf8574 import Pcf8574
from .IoExpander_Pca9554 import Pca9554

from edg.parts.connector.Connectors import PowerBarrelJack, Pj_102ah, Pj_036ah, LipoConnector, QwiicTarget
from .Fuseholder_Nano2 import Nano2Fuseholder
from .FanConnector import CpuFanConnector, CpuFanPwmControl
from .CanBlocks import Pesd1can
from .UsbPorts import UsbAReceptacle, UsbCReceptacle, UsbAPlugPads, UsbMicroBReceptacle
from .UsbPorts import Tpd2e009, Pesd5v0x1bt, Pgb102st23
from .Fusb302b import Fusb302b
from edg.parts.connector.Banana import Ct3151, Fcr7350
from edg.parts.connector.Rf import Bwipx_1_001e, Amphenol901143

from .TestPoint_Keystone import Keystone5015, CompactKeystone5015, Keystone5000
from .TestPoint_Rc import TeRc

from .AdcSpi_Mcp3201 import Mcp3201
from .AdcSpi_Mcp3561 import Mcp3561
from .DacSpi_Mcp4901 import Mcp4921
from .DacI2c_Mcp47f import Mcp47f
from .DacI2c_Mcp4728 import Mcp4728

from .Rtc_Pcf2129 import Pcf2129
from .RfModules import Xbee_S3b, BlueSmirf
from .Neopixel import (
    Neopixel,
    Ws2812b,
    Sk6812Mini_E,
    Sk6805_Ec15,
    Ws2812c_2020,
    Sk6812_Side_A,
    NeopixelArray,
    NeopixelArrayCircular,
)

from .SolidStateRelay_G3VM_61GR2 import G3VM_61GR2
from .SolidStateRelay_Toshiba import Tlp3545a, Tlp170am
from .AnalogSwitch_7400 import Sn74lvc1g3157
from .AnalogSwitch_Nlas4157 import Nlas4157
from .AnalogSwitch_Dg468 import Dg468
from .CanTransceiver_Iso1050 import Iso1050dub
from .CanTransceiver_Sn65hvd230 import Sn65hvd230
from .CurrentSense_Ad8418 import Ad8418a
from .Ina219 import Ina219
from .FuelGauge_Max17048 import Max17048
from .BatteryProtector_S8261A import S8261A
from .BatteryCharger_Mcp73831 import Mcp73831
from .Distance_Vl53l0x import Vl53l0x, Vl53l0xConnector, Vl53l0xArray
from .Isolator_Cbmud1200 import Cbmud1200l
from .GateDriver_Ir2301 import Ir2301
from .GateDriver_Ucc27282 import Ucc27282
from .GateDriver_Ncp3420 import Ncp3420
from .SpiMemory_W25q import W25q
from .SpiMemory_93Lc import E93Lc_B
from .UsbUart_Cp2102 import Cp2102
from .UsbInterface_Ft232h import Ft232hl
from .Logic_74Ahct import L74Ahct1g125
from .Logic_74Lvc import Sn74lvc1g74, Sn74lvc2g02
from .Rf_Sx1262 import Sx1262
from .Rf_Pn7160 import Pn7160
from .Comparator_Lmv331 import Lmv331
from .Camera_Ov2640_Fpc24 import Ov2640, Ov2640_Fpc24

from .Labels import DuckLogo, LeadFreeIndicator, IdDots4, LemurLogo
from .Mechanicals import Outline_Pn1332
from .Mechanicals import MountingHole, MountingHole_M2_5, MountingHole_M3, MountingHole_M4, MountingHole_NoPad_M2_5

from .MotorDriver_L293dd import L293dd
from .MotorDriver_Drv8833 import Drv8833
from .MotorDriver_Drv8870 import Drv8870
from .Bldc_Drv8313 import Drv8313
from .StepperDriver_A4988 import A4988, PololuA4988

from .Imu_Lsm6ds3trc import Lsm6ds3trc
from .Lsm6dsv16x import Lsm6dsv16x
from .MagneticSensor_A1304 import A1304
from .MagneticSwitch_Ah1806 import Ah1806
from .Mag_Qmc5883l import Qmc5883l
from .EnvironmentalSensor_Sensirion import Shtc3
from .EnvironmentalSensor_Bme680 import Bme680
from .EnvironmentalSensor_Ti import Hdc1080, Tmp1075n
from .LightSensor_Bh1750 import Bh1750
from .LightSensor_As7341 import As7341
from .ThermalSensor_FlirLepton import FlirLepton

from .LedMatrix import CharlieplexedLedMatrix
from .SwitchMatrix import SwitchMatrix
from .ResistiveSensor import ConnectorResistiveSensor

from .Jacdac import JacdacDataPort, JacdacPassivePort
from .Jacdac import JacdacEdgeConnector, JacdacDataInterface, Rclamp0521p
from .Jacdac import JacdacMountingData1, JacdacMountingGnd2, JacdacMountingGnd4, JacdacMountingPwr3
from .Jacdac import JacdacDeviceTop

# compatibility shims
import deprecated as __deprecated  # not to be exported


@__deprecated.deprecated("new naming convention")
class Vl53l0xApplication(Vl53l0x, DeprecatedBlock):
    pass


@__deprecated.deprecated("new naming convention")
class Imu_Lsm6ds3trc(Lsm6ds3trc, DeprecatedBlock):
    pass


@__deprecated.deprecated("new naming convention")
class Mag_Qmc5883l(Qmc5883l, DeprecatedBlock):
    pass
