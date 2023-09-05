from electronics_model import *
from .IoController import BaseIoController, IoController


class IoControllerSpiPeripheral(BlockInterfaceMixin[BaseIoController]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.spi_peripheral = self.Port(Vector(SpiPeripheral.empty()), optional=True)
        self.implementation(lambda base: base._io_ports.append(self.spi_peripheral))


class IoControllerI2cTarget(BlockInterfaceMixin[BaseIoController]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.i2c_target = self.Port(Vector(I2cTarget.empty()), optional=True)
        self.implementation(lambda base: base._io_ports.append(self.i2c_target))


class IoControllerDac(BlockInterfaceMixin[BaseIoController]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.dac = self.Port(Vector(AnalogSource.empty()), optional=True)
        self.implementation(lambda base: base._io_ports.insert(0, self.dac))  # allocate first


class IoControllerCan(BlockInterfaceMixin[BaseIoController]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.can = self.Port(Vector(CanControllerPort.empty()), optional=True)
        self.implementation(lambda base: base._io_ports.append(self.can))


class IoControllerUsb(BlockInterfaceMixin[BaseIoController]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.usb = self.Port(Vector(UsbDevicePort.empty()), optional=True)
        self.implementation(lambda base: base._io_ports.insert(0, self.usb))


class IoControllerI2s(BlockInterfaceMixin[BaseIoController]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.i2s = self.Port(Vector(I2sController.empty()), optional=True)
        self.implementation(lambda base: base._io_ports.append(self.i2s))


class IoControllerDvp8(BlockInterfaceMixin[BaseIoController]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.dvp8 = self.Port(Vector(Dvp8Host.empty()), optional=True)
        self.implementation(lambda base: base._io_ports.append(self.dvp8))


class IoControllerWifi(BlockInterfaceMixin[BaseIoController]):
    """Mixin indicating this IoController has programmable WiFi. Does not expose any ports."""


class IoControllerBluetooth(BlockInterfaceMixin[BaseIoController]):
    """Mixin indicating this IoController has programmable Bluetooth Classic. Does not expose any ports."""


class IoControllerBle(BlockInterfaceMixin[BaseIoController]):
    """Mixin indicating this IoController has programmable Bluetooth LE. Does not expose any ports."""


class IoControllerGroundOut(BlockInterfaceMixin[IoController]):
    """Base class for an IO controller that can act as a power output (e.g. dev boards),
     this only provides the ground source pin. Subclasses can define output power pins.
    Multiple power pin mixins can be used on the same class, but only one gnd_out can be connected."""
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.gnd_out = self.Port(GroundSource.empty(), optional=True)


class IoControllerPowerOut(IoControllerGroundOut):
    """IO controller mixin that provides an output of the IO controller's VddIO rail, commonly 3.3v."""
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.pwr_out = self.Port(VoltageSource.empty(), optional=True)


class IoControllerUsbOut(IoControllerGroundOut):
    """IO controller mixin that provides an output of the IO controller's USB Vbus.
    For devices without PD support, this should be 5v. For devices with PD support, this is whatever
    Vbus can be."""
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.vusb_out = self.Port(VoltageSource.empty(), optional=True)
