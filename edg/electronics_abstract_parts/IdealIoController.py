from ...electronics_model import *
from .Categories import IdealModel
from .IoController import IoController
from .IoControllerInterfaceMixins import IoControllerSpiPeripheral, IoControllerI2cTarget, IoControllerDac, \
    IoControllerCan, IoControllerUsb, IoControllerI2s, IoControllerWifi, IoControllerBluetooth, IoControllerBle


class IdealIoController(IoControllerSpiPeripheral, IoControllerI2cTarget, IoControllerDac, IoControllerCan,
                        IoControllerUsb, IoControllerI2s, IoControllerWifi, IoControllerBluetooth, IoControllerBle,
                        IoController, IdealModel, GeneratorBlock):
    """An ideal IO controller, with as many IOs as requested.
    Output have voltages at pwr/gnd, all other parameters are ideal."""
    def __init__(self) -> None:
        super().__init__()
        self.generator_param(self.adc.requested(), self.dac.requested(), self.gpio.requested(), self.spi.requested(),
                             self.spi_peripheral.requested(), self.i2c.requested(), self.i2c_target.requested(),
                             self.uart.requested(), self.usb.requested(), self.can.requested(), self.i2s.requested())

    def generate(self) -> None:
        self.pwr.init_from(VoltageSink(
            current_draw=RangeExpr()
        ))
        self.gnd.init_from(Ground())

        io_current_draw_builder = RangeExpr._to_expr_type(RangeExpr.ZERO)

        self.adc.defined()
        for elt in self.get(self.adc.requested()):
            self.adc.append_elt(AnalogSink(), elt)
        self.dac.defined()
        for elt in self.get(self.dac.requested()):
            aout = self.dac.append_elt(AnalogSource.from_supply(self.gnd, self.pwr), elt)
            io_current_draw_builder = io_current_draw_builder + (
                aout.link().current_drawn.lower().min(0), aout.link().current_drawn.upper().max(0)
            )

        dio_model = DigitalBidir.from_supply(
            self.gnd, self.pwr,
            pullup_capable=True, pulldown_capable=True
        )

        self.gpio.defined()
        for elt in self.get(self.gpio.requested()):
            dio = self.gpio.append_elt(dio_model, elt)
            io_current_draw_builder = io_current_draw_builder + (
                dio.link().current_drawn.lower().min(0), dio.link().current_drawn.upper().max(0)
            )

        self.spi.defined()
        for elt in self.get(self.spi.requested()):
            self.spi.append_elt(SpiController(dio_model), elt)
        self.spi_peripheral.defined()
        for elt in self.get(self.spi_peripheral.requested()):
            self.spi_peripheral.append_elt(SpiPeripheral(dio_model), elt)
        self.i2c.defined()
        for elt in self.get(self.i2c.requested()):
            self.i2c.append_elt(I2cController(dio_model), elt)
        self.i2c_target.defined()
        for elt in self.get(self.i2c_target.requested()):
            self.i2c_target.append_elt(I2cTarget(dio_model), elt)
        self.uart.defined()
        for elt in self.get(self.uart.requested()):
            self.uart.append_elt(UartPort(dio_model), elt)
        self.usb.defined()
        for elt in self.get(self.usb.requested()):
            self.usb.append_elt(UsbDevicePort(), elt)
        self.can.defined()
        for elt in self.get(self.can.requested()):
            self.can.append_elt(CanControllerPort(dio_model), elt)
        self.i2s.defined()
        for elt in self.get(self.i2s.requested()):
            self.i2s.append_elt(I2sController(dio_model), elt)

        self.assign(self.pwr.current_draw, io_current_draw_builder)
