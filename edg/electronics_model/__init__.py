# Contains the core netlist, netlister ports, and supporting utilities / interfaces.
# Excludes electronics interfaces (the higher level port and links models) which is in a separate package.
from ..core import *

from .CircuitBlock import (
    FootprintBlock,
    CircuitPortBridge,
    CircuitPortAdapter,
    NetBlock,
    CircuitPort,
)
from .SubboardBlock import SubboardBlock, WrapperSubboardBlock, SubboardConnectorPair

from .Units import Farad, uFarad, nFarad, pFarad, MOhm, kOhm, Ohm, mOhm, Henry, uHenry, nHenry
from .Units import Volt, mVolt, Watt, Amp, mAmp, uAmp, nAmp, pAmp
from .Units import Second, mSecond, uSecond, nSecond, Hertz, kHertz, MHertz, GHertz
from .Units import Bit, kiBit, MiBit
from .Units import Ratio
from .Units import UnitUtils

# Need to export link and bridge types for library auto-detection
from .PassivePort import Passive, PassiveLink, HasPassivePort

from .PartParserUtil import PartParserUtil

from .KiCadImportableBlock import KiCadImportableBlock, KiCadInstantiableBlock
from .KiCadSchematicBlock import KiCadSchematicBlock

# categories
from .Categories import DiscreteComponent, DiscreteSemiconductor, PassiveComponent
from .Categories import DummyDevice, DiscreteApplication
from .Categories import Analog, OpampApplication
from .Categories import Filter, AnalogFilter, RfFilter, DigitalFilter
from .Categories import ProgrammableController, Microcontroller, Fpga, Memory, RealtimeClock, Radiofrequency
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
from .Categories import Protection
from .Categories import Label, Testing, TypedJumper, TypedTestPoint, InternalSubcircuit, DeprecatedBlock, Mechanical
from .Categories import MultipackDevice
from .Categories import IdealModel

# model-breaking constructs, including for unit testing

# for power users to build custom blackbox handlers
from .KiCadSchematicParser import KiCadSymbol, KiCadLibSymbol
from .KiCadSchematicBlock import KiCadBlackbox, KiCadBlackboxBase
from .KicadFootprintData import FootprintDataTable

from .RefdesRefinementPass import RefdesRefinementPass
from .NetlistBackend import NetlistBackend
from .SvgPcbBackend import SvgPcbBackend
from .PinAssignmentUtil import PinAssignmentUtil, AnyPinAssign, PeripheralPinAssign, NotConnectedPin, AnyPin

from .SvgPcbTemplateBlock import SvgPcbTemplateBlock
