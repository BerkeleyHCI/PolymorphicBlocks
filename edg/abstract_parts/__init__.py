# Contains abstract part definitions, simple wrapper blocks / application circuits,
# and implementation helpers for abstract parts like part table utils.
from ..electronics_interfaces import *

from .ESeriesUtil import ESeriesUtil, ESeriesRatioUtil, ESeriesRatioValue

from .PartsTablePart import (
    PartsTableBase,
    PartsTablePart,
    PartsTableSelector,
    SelectorFootprint,
    PartsTableColumn,
    PartsTableRow,
    PartsTableFootprintFilter,
    PartsTableSelectorFootprint,
)
from .PartsTable import PartsTable
from .SelectorArea import PartsTableAreaSelector, SelectorArea
from .StandardFootprint import StandardFootprint

from .Battery import Battery
from .Connectors import (
    BananaJack,
    BananaSafetyJack,
    RfConnector,
    RfConnectorTestPoint,
    RfConnectorAntenna,
    UflConnector,
    SmaConnector,
    SmaMConnector,
    SmaFConnector,
)
from .Resistor import Resistor, ResistorStandardFootprint, TableResistor, SeriesResistor, AnalogSeriesResistor
from .Resistor import PulldownResistor, PullupResistor, PulldownResistorArray, PullupResistorArray
from .Resistor import (
    SeriesPowerResistor,
    CurrentSenseResistor,
    DigitalSeriesResistor,
    DigitalBidirSeriesResistor,
    AnalogSetpointResistor,
)
from .ResistorArray import ResistorArray, ResistorArrayStandardFootprint, TableResistorArray
from .Capacitor import (
    UnpolarizedCapacitor,
    Capacitor,
    CeramicCapacitor,
    AluminumCapacitor,
    CapacitorStandardFootprint,
    TableCapacitor,
    TableDeratingCapacitor,
)
from .Capacitor import (
    DummyCapacitorFootprint,
    DecouplingCapacitor,
    AnalogCapacitor,
    AnalogSeriesCapacitor,
    DigitalCapacitor,
    CombinedCapacitor,
)
from .Inductor import Inductor, TableInductor, SeriesPowerInductor
from .FerriteBead import FerriteBead, FerriteBeadStandardFootprint, TableFerriteBead, SeriesPowerFerriteBead
from .Resettable import Resettable

from .Diode import BaseDiode, Diode, DiodeStandardFootprint, TableDiode
from .ZenerDiode import ZenerDiode, TableZenerDiode, ProtectionZenerDiode, AnalogClampZenerDiode
from .TvsDiode import TvsDiode, ProtectionTvsDiode, DigitalTvsDiode
from .Led import Led, LedStandardFootprint, TableLed, RgbLedCommonAnode, LedColor, LedColorLike
from .Led import (
    IndicatorLed,
    IndicatorSinkLed,
    IndicatorSinkLedResistor,
    VoltageIndicatorLed,
    IndicatorSinkRgbLed,
)
from .Led import IndicatorSinkPackedRgbLed
from .Led import IndicatorLedArray, IndicatorSinkLedArray
from .Bjt import Bjt, BjtStandardFootprint, TableBjt
from .Fet import Fet, FetStandardFootprint, BaseTableFet, TableFet
from .Fet import SwitchFet, TableSwitchFet

from .Antenna import Antenna, TableAntenna
from .SolidStateRelay import SolidStateRelay, VoltageIsolatedSwitch, AnalogIsolatedSwitch
from .AnalogSwitch import AnalogSwitch, AnalogSwitchTree, AnalogDemuxer, AnalogMuxer
from .Switch import Switch, TactileSwitch, MechanicalKeyswitch, DigitalSwitch
from .Switch import RotaryEncoder, RotaryEncoderSwitch, DigitalRotaryEncoder, DigitalRotaryEncoderSwitch
from .Switch import DirectionSwitch, DirectionSwitchCenter, DigitalDirectionSwitch, DigitalDirectionSwitchCenter
from .Comparator import Comparator
from .Opamp import Opamp, OpampElement, MultipackOpamp, MultipackOpampGenerator
from .SpiMemory import SpiMemory, SpiMemoryQspi
from .PowerConverters import VoltageRegulator, VoltageRegulatorEnableWrapper
from .PowerConverters import LinearRegulator, VoltageReference, LinearRegulatorDevice, SwitchingVoltageRegulator
from .PowerConverters import BootstrapCapacitor
from .PowerConverters import BuckConverter, DiscreteBuckConverter, BoostConverter, DiscreteBoostConverter
from .PowerConverters import BuckConverterPowerPath, BoostConverterPowerPath, BuckBoostConverterPowerPath
from .LedDriver import LedDriver, LedDriverPwm, LedDriverSwitchingConverter
from .Fuse import Fuse, SeriesPowerFuse, PptcFuse, FuseStandardFootprint, TableFuse, SeriesPowerPptcFuse
from .Crystal import Crystal, TableCrystal, OscillatorReference, CeramicResonator
from .Oscillator import Oscillator, TableOscillator
from .SwdCortexConnectors import (
    SwdCortexTargetConnector,
    SwdCortexTargetConnectorReset,
    SwdCortexTargetConnectorSwo,
    SwdCortexTargetConnectorTdi,
)
from .TestPoint import (
    TestPoint,
    GroundTestPoint,
    VoltageTestPoint,
    DigitalTestPoint,
    DigitalArrayTestPoint,
    AnalogTestPoint,
    I2cTestPoint,
    SpiTestPoint,
    CanControllerTestPoint,
    CanDiffTestPoint,
)
from .TestPoint import AnalogCoaxTestPoint
from .Jumper import Jumper, DigitalJumper
from .PassiveConnector import PassiveConnector, FootprintPassiveConnector

from .UsbConnectors import UsbConnector, UsbHostConnector, UsbDeviceConnector, UsbEsdDiode
from .CanTransceiver import CanTransceiver, IsolatedCanTransceiver, CanEsdDiode
from .GateDrivers import HalfBridgeDriver, HalfBridgeDriverIndependent, HalfBridgeDriverPwm
from .DigitalIsolator import DigitalIsolator

from .IoController import BaseIoController, IoController, IoControllerPowerRequired, BaseIoControllerPinmapGenerator
from .IoControllerExportable import BaseIoControllerExportable
from .IoControllerInterfaceMixins import (
    IoControllerSpiPeripheral,
    IoControllerI2cTarget,
    IoControllerTouchDriver,
    IoControllerDac,
    IoControllerCan,
    IoControllerUsb,
    IoControllerI2s,
    IoControllerDvp8,
    IoControllerUsbCc,
)
from .IoControllerInterfaceMixins import IoControllerPowerOut, IoControllerUsbOut, IoControllerVin
from .IoControllerInterfaceMixins import IoControllerWifi, IoControllerBluetooth, IoControllerBle
from .IoControllerProgramming import IoControllerWithSwdTargetConnector
from .IoControllerMixins import WithCrystalGenerator
from .PinMappable import PinMappable, PinMapUtil
from .PinMappable import PinResource, PeripheralFixedPin, PeripheralAnyResource, PeripheralFixedResource
from .VariantPinRemapper import VariantPinRemapper

from .Nonstrict3v3Compatible import Nonstrict3v3Compatible
