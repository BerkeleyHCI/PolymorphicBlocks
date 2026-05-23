from ..electronics_model import *

from .GroundPort import Ground, GroundSource, GroundReference, GroundLink, Common
from .VoltagePorts import VoltageSource, VoltageSink, Power, VoltageLink
from .DigitalPorts import DigitalSource, DigitalSink, DigitalBidir, DigitalSingleSource, DigitalLink
from .DigitalPorts import DigitalBidirNotConnected
from .AnalogPort import AnalogSource, AnalogSink, AnalogLink
from .TouchPort import TouchDriver, TouchPadPort
from .UartPort import UartPort, UartLink
from .SpiPort import SpiController, SpiPeripheral, SpiLink
from .SpiPort import SpiMaster, SpiSlave  # legacy names
from .I2cPort import I2cPullupPort, I2cController, I2cTarget, I2cLink
from .I2cPort import I2cMaster, I2cSlave  # legacy names
from .CanPort import CanControllerPort, CanTransceiverPort, CanLogicLink, CanPassivePort, CanDiffPort, CanDiffLink
from .DebugPorts import SwdHostPort, SwdTargetPort, SwdPullPort, SwdLink
from .SpeakerPort import SpeakerDriverPort, SpeakerPort, SpeakerLink
from .CrystalPort import CrystalPort, CrystalDriver, CrystalLink
from .UsbPort import UsbHostPort, UsbDevicePort, UsbPassivePort, UsbCcPort, UsbLink
from .DvpPort import Dvp8Host, Dvp8Camera, Dvp8Link
from .I2sPort import I2sController, I2sTargetReceiver, I2sLink

# model-breaking constructs, including for unit testing
from .GroundDummy import DummyGround
from .VoltageDummy import DummyVoltageSource, DummyVoltageSink

from .DummyDevices import DummyPassive, DummyDigitalSource, DummyDigitalSink, DummyAnalogSource, DummyAnalogSink
from .DummyDevices import (
    ForcedVoltageCurrentDraw,
    ForcedVoltageCurrentLimit,
    ForcedVoltage,
    ForcedVoltageCurrent,
    ForcedAnalogSignal,
    ForcedDigitalSinkCurrentDraw,
)

from .MergedBlocks import MergedVoltageSource, MergedDigitalSource, MergedAnalogSource, MergedSpiController

# packing constructs
from .CircuitPackingBlock import NetPackingBlock, PackedPassive, PackedGround, PackedVoltageSource

# utils
from .ConnectedGenerator import VoltageSourceConnected, DigitalSourceConnected
