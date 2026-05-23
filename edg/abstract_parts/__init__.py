from ..electronics_interfaces import *

from .Categories import DiscreteComponent, DiscreteSemiconductor, PassiveComponent
from .Categories import DiscreteApplication
from .Categories import Analog, OpampApplication
from .Categories import Filter, AnalogFilter, RfFilter, DigitalFilter
from .Categories import Microcontroller, Fpga, Memory, RealtimeClock, Radiofrequency
from .Categories import Interface, AnalogToDigital, DigitalToAnalog, SpeakerDriver, IoExpander, BitBangAdapter
from .Categories import PowerConditioner, PowerSwitch, MotorDriver, BrushedMotorDriver, BldcDriver
from .Categories import PowerSource, Connector, ProgrammingConnector
from .Categories import HumanInterface, Display, Lcd, Oled, EInk, Light
from .Categories import (
    Sensor,
    CurrentSensor,
    Accelerometer,
    Gyroscope,
    MagneticSensor,
    MagneticSwitch,
    Magnetometer,
    DistanceSensor,
    Microphone,
    Camera,
    LightSensor,
)
from .Categories import EnvironmentalSensor, TemperatureSensor, HumiditySensor, PressureSensor, GasSensor
from .Categories import Label, Testing, TypedJumper, TypedTestPoint, InternalSubcircuit, DeprecatedBlock, Mechanical
from .Categories import MultipackDevice

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

from .AbstractDevices import Battery
from .AbstractConnector import (
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
from .AbstractResistor import Resistor, ResistorStandardFootprint, TableResistor, SeriesResistor, AnalogSeriesResistor
from .AbstractResistor import PulldownResistor, PullupResistor, PulldownResistorArray, PullupResistorArray
from .AbstractResistor import (
    SeriesPowerResistor,
    CurrentSenseResistor,
    AnalogClampResistor,
    DigitalSeriesResistor,
    DigitalBidirSeriesResistor,
    DigitalClampResistor,
    AnalogSetpointResistor,
    UsbSeriesResistor,
)
from .AbstractResistorArray import ResistorArray, ResistorArrayStandardFootprint, TableResistorArray
from .AbstractCapacitor import (
    UnpolarizedCapacitor,
    Capacitor,
    CeramicCapacitor,
    AluminumCapacitor,
    CapacitorStandardFootprint,
    TableCapacitor,
    TableDeratingCapacitor,
)
from .AbstractCapacitor import (
    DummyCapacitorFootprint,
    DecouplingCapacitor,
    AnalogCapacitor,
    AnalogSeriesCapacitor,
    DigitalCapacitor,
    CombinedCapacitor,
)
from .AbstractInductor import Inductor, TableInductor, SeriesPowerInductor
from .AbstractFerriteBead import FerriteBead, FerriteBeadStandardFootprint, TableFerriteBead, SeriesPowerFerriteBead
from .Resettable import Resettable

from .AbstractDiodes import BaseDiode, Diode, DiodeStandardFootprint, TableDiode
from .AbstractDiodes import ZenerDiode, TableZenerDiode, ProtectionZenerDiode, AnalogClampZenerDiode
from .AbstractTvsDiode import TvsDiode, ProtectionTvsDiode, DigitalTvsDiode
from .AbstractLed import Led, LedStandardFootprint, TableLed, RgbLedCommonAnode, LedColor, LedColorLike
from .AbstractLed import (
    IndicatorLed,
    IndicatorSinkLed,
    IndicatorSinkLedResistor,
    VoltageIndicatorLed,
    IndicatorSinkRgbLed,
)
from .AbstractLed import IndicatorSinkPackedRgbLed
from .AbstractLed import IndicatorLedArray, IndicatorSinkLedArray
from .AbstractBjt import Bjt, BjtStandardFootprint, TableBjt
from .AbstractFets import Fet, FetStandardFootprint, BaseTableFet, TableFet
from .AbstractFets import SwitchFet, TableSwitchFet

from .AbstractAntenna import Antenna, TableAntenna
from .AbstractSolidStateRelay import SolidStateRelay, VoltageIsolatedSwitch, AnalogIsolatedSwitch
from .AbstractAnalogSwitch import AnalogSwitch, AnalogSwitchTree, AnalogDemuxer, AnalogMuxer
from .AbstractSwitch import Switch, TactileSwitch, MechanicalKeyswitch, DigitalSwitch
from .AbstractSwitch import RotaryEncoder, RotaryEncoderSwitch, DigitalRotaryEncoder, DigitalRotaryEncoderSwitch
from .AbstractSwitch import DirectionSwitch, DirectionSwitchCenter, DigitalDirectionSwitch, DigitalDirectionSwitchCenter
from .AbstractComparator import Comparator, VoltageComparator
from .AbstractOpamp import Opamp, OpampElement, MultipackOpamp, MultipackOpampGenerator
from .AbstractSpiMemory import SpiMemory, SpiMemoryQspi
from .AbstractPowerConverters import VoltageRegulator, VoltageRegulatorEnableWrapper
from .AbstractPowerConverters import LinearRegulator, VoltageReference, LinearRegulatorDevice, SwitchingVoltageRegulator
from .AbstractPowerConverters import BootstrapCapacitor
from .AbstractPowerConverters import BuckConverter, DiscreteBuckConverter, BoostConverter, DiscreteBoostConverter
from .AbstractPowerConverters import BuckConverterPowerPath, BoostConverterPowerPath, BuckBoostConverterPowerPath
from .AbstractLedDriver import LedDriver, LedDriverPwm, LedDriverSwitchingConverter
from .AbstractFuse import Fuse, SeriesPowerFuse, PptcFuse, FuseStandardFootprint, TableFuse, SeriesPowerPptcFuse
from .AbstractCrystal import Crystal, TableCrystal, OscillatorReference, CeramicResonator
from .AbstractOscillator import Oscillator, TableOscillator
from .AbstractDebugHeaders import (
    SwdCortexTargetConnector,
    SwdCortexTargetConnectorReset,
    SwdCortexTargetConnectorSwo,
    SwdCortexTargetConnectorTdi,
)
from .AbstractTestPoint import (
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
from .AbstractTestPoint import AnalogCoaxTestPoint
from .AbstractJumper import Jumper, DigitalJumper
from .PassiveConnector import PassiveConnector, FootprintPassiveConnector
from .TouchPad import FootprintToucbPad

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
