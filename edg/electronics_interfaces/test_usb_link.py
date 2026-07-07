import unittest

from ..electronics_model import *
from .UsbPort import UsbLink, UsbHostPort, UsbDevicePort, UsbPassivePort


class DummyUsbHost(Block):
    def __init__(self, speed: RangeLike = UsbLink.AllUsb2Speeds) -> None:
        super().__init__()
        self.io = self.Port(UsbHostPort(speed=speed))


class DummyUsbDevice(Block):
    def __init__(self, speed: RangeLike = UsbLink.AllUsb2Speeds) -> None:
        super().__init__()
        self.io = self.Port(UsbDevicePort(speed=speed))


class DummyUsbPassive(Block):
    def __init__(self, speed: RangeLike = UsbLink.AllUsb2Speeds) -> None:
        super().__init__()
        self.io = self.Port(UsbPassivePort(speed=speed))


class SimpleUsbTestTop(DesignTop):
    """Test design with host and device and default operating ranges"""

    def __init__(self) -> None:
        super().__init__()
        self.host = self.Block(DummyUsbHost())
        self.device = self.Block(DummyUsbDevice())
        self.connect(self.host.io, self.device.io)


class PassiveUsbTestTop(DesignTop):
    """Test design with host, device, and passive and default operating ranges"""

    def __init__(self) -> None:
        super().__init__()
        self.host = self.Block(DummyUsbHost())
        self.device = self.Block(DummyUsbDevice())
        self.passive = self.Block(DummyUsbPassive())
        self.connect(self.host.io, self.device.io, self.passive.io)


class FullSpeedDeviceTestTop(DesignTop):
    """Test design with unlimited host (eg, upstream-facing connector) and full-speed device (eg, microcontroller)"""

    def __init__(self) -> None:
        super().__init__()
        self.host = self.Block(DummyUsbHost())
        self.device = self.Block(DummyUsbDevice(speed=(UsbLink.UsbLowSpeed, UsbLink.UsbFullSpeed)))
        self.connect(self.host.io, self.device.io)


class IncompatibleSpeedTestTop(DesignTop):
    """Test design with incompatible speeds (high speed only host, full speed device)"""

    def __init__(self) -> None:
        super().__init__()
        self.host = self.Block(DummyUsbHost(speed=(UsbLink.UsbHighSpeed, UsbLink.UsbHighSpeed)))
        self.device = self.Block(DummyUsbDevice(speed=(UsbLink.UsbLowSpeed, UsbLink.UsbFullSpeed)))
        self.connect(self.host.io, self.device.io)


class LimitingPassiveUsbTestTop(DesignTop):
    """Test design with passive that limits the link speed, eg low-speed / high-capacitance ESD diode"""

    def __init__(self) -> None:
        super().__init__()
        self.host = self.Block(DummyUsbHost())
        self.device = self.Block(DummyUsbDevice())
        self.passive = self.Block(DummyUsbPassive(speed=(UsbLink.UsbLowSpeed, UsbLink.UsbFullSpeed)))
        self.connect(self.host.io, self.device.io, self.passive.io)


class VoltageLinkTestCase(unittest.TestCase):
    def test_simple(self) -> None:
        ScalaCompiler.compile(SimpleUsbTestTop)

    def test_passive(self) -> None:
        ScalaCompiler.compile(PassiveUsbTestTop)

    def test_full_speed_device(self) -> None:
        ScalaCompiler.compile(FullSpeedDeviceTestTop)

    def test_incompatible_speed(self) -> None:
        with self.assertRaises(CompilerCheckError):
            ScalaCompiler.compile(IncompatibleSpeedTestTop)

    def test_limiting_passive(self) -> None:
        with self.assertRaises(CompilerCheckError):
            ScalaCompiler.compile(LimitingPassiveUsbTestTop)
