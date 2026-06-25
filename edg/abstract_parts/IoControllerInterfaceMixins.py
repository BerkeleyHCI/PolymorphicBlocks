from typing import Any, Union

from typing_extensions import override

from ..electronics_interfaces import *
from .IoController import BaseIoController, IoController
from ..util import deprecated_param_remap


class IoControllerSpiPeripheral(BlockInterfaceMixin[BaseIoController]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.spi_peripheral = self.Port(
            Vector(SpiPeripheral.empty()),
            optional=True,
            doc="Microcontroller SPI peripherals (excluding CS pin, which must be handled separately), each element is an independent SPI peripheral",
        )
        self.implementation(lambda base: base._io_ports.append(self.spi_peripheral))


class IoControllerI2cTarget(BlockInterfaceMixin[BaseIoController]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.i2c_target = self.Port(
            Vector(I2cTarget.empty()),
            optional=True,
            doc="Microcontroller I2C targets, each element is an independent I2C target",
        )
        self.implementation(lambda base: base._io_ports.append(self.i2c_target))


class IoControllerTouchDriver(BlockInterfaceMixin[BaseIoController]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.touch = self.Port(Vector(TouchDriver.empty()), optional=True, doc="Microcontroller touch input")
        self.implementation(lambda base: base._io_ports.insert(0, self.touch))  # allocate first


class IoControllerDac(BlockInterfaceMixin[BaseIoController]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.dac = self.Port(Vector(AnalogSource.empty()), optional=True, doc="Microcontroller analog output pins")
        self.implementation(lambda base: base._io_ports.insert(0, self.dac))  # allocate first


class IoControllerCan(BlockInterfaceMixin[BaseIoController]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.can = self.Port(
            Vector(CanControllerPort.empty()), optional=True, doc="Microcontroller CAN controller ports"
        )
        self.implementation(lambda base: base._io_ports.append(self.can))


class IoControllerUsb(BlockInterfaceMixin[BaseIoController]):
    """Eventually, the USB device port will be an IoController mixin.
    For now, it's part of base, since it's common enough and there isn't GUI support for mixins.

    This class SHOULD BE mixed into IoController blocks, in preparation for the eventual move.
    This WILL NOT WORK when used in .with_mixin, since this defines no fields."""

    pass


class IoControllerUsbCc(BlockInterfaceMixin[BaseIoController]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.cc = self.Port(Vector(UsbCcPort.empty()), optional=True, doc="Microcontroller USB Power delivery CC pins")
        self.implementation(lambda base: base._io_ports.append(self.cc))


class IoControllerI2s(BlockInterfaceMixin[BaseIoController]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.i2s = self.Port(
            Vector(I2sController.empty()),
            optional=True,
            doc="Microcontroller I2S controller ports, each element is an independent I2S controller",
        )
        self.implementation(lambda base: base._io_ports.append(self.i2s))


class IoControllerDvp8(BlockInterfaceMixin[BaseIoController]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.dvp8 = self.Port(
            Vector(Dvp8Host.empty()), optional=True, doc="Microcontroller 8-bit DVP digital video ports"
        )
        self.implementation(lambda base: base._io_ports.append(self.dvp8))


class IoControllerWifi(BlockInterfaceMixin[BaseIoController]):
    """Mixin indicating this IoController has programmable WiFi. Does not expose any ports."""


class IoControllerBluetooth(BlockInterfaceMixin[BaseIoController]):
    """Mixin indicating this IoController has programmable Bluetooth Classic. Does not expose any ports."""


class IoControllerBle(BlockInterfaceMixin[BaseIoController]):
    """Mixin indicating this IoController has programmable Bluetooth LE. Does not expose any ports."""


class IoControllerPowerOut(BlockInterfaceMixin[IoController]):
    """IO controller mixin that provides an output of the IO controller's VddIO rail, commonly 3.3v."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.pwr_out = self.Port(
            VoltageSource.empty(),
            optional=True,
            doc="Power output port, typically of the device's Vdd or VddIO rail at 3.3v",
        )

    @override
    def contents(self) -> None:
        super().contents()
        if isinstance(self, IoController):
            self.require(
                self.pwr_out.is_connected().implies(~self.pwr.is_connected()),
                "can only connect one of pwr and pwr_out (same physical pin)",
            )
            self.require(
                self.pwr_out.is_connected().implies(self.gnd.is_connected()),
                "gnd must be connected if pwr_out connected",
            )

    def _generate_gnd_node(self) -> Ground:
        """Helper function that returns a ground node, either directly taking the gnd port if available,
        or generating an internal ground node.

        Requires self.gnd.is_connected() as a generator param.
        """
        assert isinstance(self, IoController)
        if self.get(self.gnd.is_connected()):  # gnd connected externally
            return self.gnd
        else:
            self.gnd_model = self.Block(DummyGround())
            return self.gnd_model.io

    @deprecated_param_remap(("voltage_out", "voltage"))
    def _generate_pwr_node(self, voltage: RangeLike, current_limits: RangeLike) -> Union[VoltageSink, VoltageSource]:
        """Helper function that returns a power node, either directly taking the pwr port if available,
        or generating an internal voltage node and optionally connecting it to pwr_out (if used).

        Requires self.pwr.is_connected(), self.pwr_out.is_connected as generator params.
        """
        assert isinstance(self, IoController)
        if self.get(self.pwr.is_connected()):  # power supplied externally
            return self.pwr
        else:
            self.pwr_out_model = self.Block(
                DummyVoltageSource(
                    voltage=voltage,  # tolerance is a guess
                    current_limits=current_limits,
                )
            )
            if self.get(self.pwr_out.is_connected()):
                self.connect(self.pwr_out, self.pwr_out_model.io)
            return self.pwr_out_model.io


class IoControllerUsbOut(BlockInterfaceMixin[IoController]):
    """IO controller mixin that provides an output of the IO controller's USB Vbus.

    If also used with IoControllerVin, it is assumed that pwr_vin is the same physical pin as vusb_out.
    TODO: support devices with separate Vin and Vbus"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.vusb_out = self.Port(
            VoltageSource.empty(), optional=True, doc="Power output port of the device's Vbus, typically 5v"
        )

    @override
    def contents(self) -> None:
        super().contents()
        if isinstance(self, IoController):
            self.require(
                self.vusb_out.is_connected().implies(self.gnd.is_connected()),
                "gnd must be connected if vusb_out connected",
            )
            self.require(
                self.vusb_out.is_connected().implies(~self.pwr.is_connected()),
                "can't sink logic-level pwr if sourcing power from USB",
            )

        if isinstance(self, IoControllerVin):
            self.require(
                self.vusb_out.is_connected().implies(~self.pwr_vin.is_connected()),
                "can only connect one of pwr_vin and vusb_out (same physical pin)",
            )


class IoControllerVin(BlockInterfaceMixin[IoController]):
    """IO controller mixin that provides a >=5v input to the device, typically upstream of the Vbus-to-3.3 regulator."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.pwr_vin = self.Port(
            VoltageSink.empty(), optional=True, doc="Power input pin, typically rated for 5v or a bit beyond."
        )

    @override
    def contents(self) -> None:
        super().contents()
        if isinstance(self, IoController):
            self.require(
                self.pwr_vin.is_connected().implies(self.gnd.is_connected()),
                "gnd must be connected if pwr_vin connected",
            )
            self.require(
                self.pwr_vin.is_connected().implies(~self.pwr.is_connected()),
                "can't sink logic-level pwr if powered from external vin",
            )
