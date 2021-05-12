from typing import *
from itertools import chain

from electronics_abstract_parts import *

class Adafruit_ItsyBitsy_BLE(Microcontroller, FootprintBlock, AssignablePinBlock):
    """
    nRF52840 configured as power source from USB.

    Documentation: https://learn.adafruit.com/adafruit-itsybitsy-nrf52840-express
    """

    @init_in_parent
    def __init__(self) -> None:
        super().__init__()

        self.pwr_bat = self.Port(VoltageSink(
            voltage_limits=(3.5, 6) * Volt
        ), optional=True)
        self.pwr_vhi = self.Port(VoltageSource(
            voltage_out=(3.5, 6) * Volt,
            current_limits=(0, 0.5) * Amp
        ), optional=True)
        self.pwr_3v = self.Port(VoltageSource(
            voltage_out=3.3 * Volt(tol=0.10),
            current_limits=(0, 0.5) * Amp
        ), optional=True)
        self.pwr_usb = self.Port(VoltageSource(
            voltage_out=5 * Volt(tol=0.10),
            current_limits=(0, 0.5) * Amp
        ), optional=True)
        self.gnd = self.Port(Ground(), optional=True)

        io_model = DigitalBidir(  # TODO no specs
            voltage_limits=(-0.3, 3.6) * Volt,
            current_draw=(0, 0) * Amp,
            voltage_out=(0 * Volt, 3.3 * Volt),
            current_limits=(-25, 25) * mAmp,
            input_thresholds=(0.3 * 3.3*0.97,
                              0.7 * 3.3*1.03),
            output_thresholds=(0 * Volt, 3.3 * 0.97 * Volt),
            pullup_capable=True, pulldown_capable=True
        )

        adc_model = AnalogSink(
            voltage_limits=(-0.3, 3.6) * Volt,
            current_draw=(0, 0) * Amp,
            impedance=100*kOhm  # TODO no specs
        )

        self.digital = ElementDict[DigitalBidir]()
        for i in [0, 1, 2, 5, 7, 9, 10, 11, 12, 13]:
            self.digital[i] = self.Port(io_model, optional=True)
            self._add_assignable_io(self.digital[i])

        self.adc = ElementDict[AnalogSink]()
        for i in range(6):
            self.adc[i] = self.Port(adc_model, optional=True)
            self._add_assignable_io(self.adc[i])

        self.uart_0 = self.Port(UartPort(io_model), optional=True)
        self._add_assignable_io(self.uart_0)

        self.spi_0 = self.Port(SpiMaster(io_model), optional=True)
        self._add_assignable_io(self.spi_0)

        self.usb_0 = self.Port(UsbDevicePort(), optional=True)

        self.swd_swdio = self.Port(DigitalBidir(io_model), optional=True)
        self.swd_swclk = self.Port(DigitalSink(io_model), optional=True)
        self.swd_reset = self.Port(DigitalSink(io_model), optional=True)

        self.generator(self.pin_assign, self.pin_assigns,
                       req_ports=list(chain(self.digital.values(), self.adc.values(),
                                            [self.uart_0, self.spi_0])))

    def pin_assign(self, pin_assigns_str: str) -> None:
        system_pins: Dict[str, CircuitPort]
        system_pins = {}

        assigned_pins = PinAssignmentUtil(
            AnyPinAssign([port for port in self._all_assignable_ios if isinstance(port, AnalogSink)],
                         [0, 1, 2, 3, 4, 5]),
            AnyPinAssign([port for port in self._all_assignable_ios if isinstance(port, DigitalBidir)],
                         [0, 1, 2, 5, 7, 9, 10, 11, 12, 13]),
        ).assign(
            [port for port in self._all_assignable_ios if self.get(port.is_connected())],
            self._get_suggested_pin_maps(pin_assigns_str))

        overassigned_pins = set(assigned_pins.keys()).intersection(set(system_pins.keys()))
        assert not overassigned_pins, f"over-assigned pins {overassigned_pins}"

        all_pins = {
            **{str(pin): port for pin, port in assigned_pins.items()},
            **{str(pin): port for pin, port in system_pins.items()}
        }

        self.footprint(
            'U', 'Adafruit ItsyBitsy nRF52840 Express - Bluetooth LE',
            all_pins,
            mfr='Adafruit', part='ItsyBitsy nRF52840 Express - Bluetooth LE',
            datasheet='https://learn.adafruit.com/adafruit-itsybitsy-nrf52840-express',
        )
