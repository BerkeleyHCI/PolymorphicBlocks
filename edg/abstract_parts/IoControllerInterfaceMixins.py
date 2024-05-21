from ..electronics_model import *
from .IoController import BaseIoController, IoController


class IoControllerSpiPeripheral(BlockInterfaceMixin[BaseIoController]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.spi_peripheral = self.Port(Vector(SpiPeripheral.empty()), optional=True,
                                        doc="Microcontroller SPI peripherals (excluding CS pin, which must be handled separately), each element is an independent SPI peripheral")
        self.implementation(lambda base: base._io_ports.append(self.spi_peripheral))


class IoControllerI2cTarget(BlockInterfaceMixin[BaseIoController]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.i2c_target = self.Port(Vector(I2cTarget.empty()), optional=True,
                                    doc="Microcontroller I2C targets, each element is an independent I2C target")
        self.implementation(lambda base: base._io_ports.append(self.i2c_target))


class IoControllerTouchDriver(BlockInterfaceMixin[BaseIoController]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.touch = self.Port(Vector(TouchDriver.empty()), optional=True,
                               doc="Microcontroller touch input")
        self.implementation(lambda base: base._io_ports.insert(0, self.touch))  # allocate first


class IoControllerDac(BlockInterfaceMixin[BaseIoController]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.dac = self.Port(Vector(AnalogSource.empty()), optional=True,
                             doc="Microcontroller analog output pins")
        self.implementation(lambda base: base._io_ports.insert(0, self.dac))  # allocate first


class IoControllerCan(BlockInterfaceMixin[BaseIoController]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.can = self.Port(Vector(CanControllerPort.empty()), optional=True,
                             doc="Microcontroller CAN controller ports")
        self.implementation(lambda base: base._io_ports.append(self.can))


class IoControllerUsb(BlockInterfaceMixin[BaseIoController]):
    """Eventually, the USB device port will be an IoController mixin.
    For now, it's part of base, since it's common enough and there isn't GUI support for mixins.

    This class SHOULD BE mixed into IoController blocks, in preparation for the eventual move.
    This WILL NOT WORK when used in .with_mixin, since this defines no fields."""
    pass


class IoControllerI2s(BlockInterfaceMixin[BaseIoController]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.i2s = self.Port(Vector(I2sController.empty()), optional=True,
                             doc="Microcontroller I2S controller ports, each element is an independent I2S controller")
        self.implementation(lambda base: base._io_ports.append(self.i2s))


class IoControllerDvp8(BlockInterfaceMixin[BaseIoController]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.dvp8 = self.Port(Vector(Dvp8Host.empty()), optional=True,
                              doc="Microcontroller 8-bit DVP digital video ports")
        self.implementation(lambda base: base._io_ports.append(self.dvp8))


class IoControllerWifi(BlockInterfaceMixin[BaseIoController]):
    """Mixin indicating this IoController has programmable WiFi. Does not expose any ports."""


class IoControllerBluetooth(BlockInterfaceMixin[BaseIoController]):
    """Mixin indicating this IoController has programmable Bluetooth Classic. Does not expose any ports."""


class IoControllerBle(BlockInterfaceMixin[BaseIoController]):
    """Mixin indicating this IoController has programmable Bluetooth LE. Does not expose any ports."""


@non_library
class IoControllerGroundOut(BlockInterfaceMixin[IoController]):
    """Base mixin for an IoController that can act as a power output (e.g. dev boards),
    this only provides the ground source pin. Subclasses can define output power pins.
    Multiple power pin mixins can be used on the same class, but only one gnd_out can be connected."""
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.gnd_out = self.Port(GroundSource.empty(), optional=True,
                                 doc="Ground for power output ports, when the device is acting as a power source")


class IoControllerPowerOut(IoControllerGroundOut, BlockInterfaceMixin[IoController]):
    """IO controller mixin that provides an output of the IO controller's VddIO rail, commonly 3.3v."""
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.pwr_out = self.Port(VoltageSource.empty(), optional=True,
                                 doc="Power output port, typically of the device's Vdd or VddIO rail; must be used with gnd_out")


class IoControllerUsbOut(IoControllerGroundOut, BlockInterfaceMixin[IoController]):
    """IO controller mixin that provides an output of the IO controller's USB Vbus."""
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.vusb_out = self.Port(VoltageSource.empty(), optional=True,
                                  doc="Power output port of the device's Vbus, typically 5v; must be used with gnd_out")
