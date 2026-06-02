from abc import abstractmethod
from typing import *

from typing_extensions import override

from ...circuits import *
from ...vendor_parts.jlc.JlcPart import JlcPart


@non_library
class Nrf52840_Interfaces(
    IoControllerSpiPeripheral, IoControllerI2cTarget, IoControllerUsb, IoControllerI2s, IoControllerBle
):
    """Defines base interfaces for nRF52840 microcontrollers"""


class Mdbt50q_1mv2_Device(
    Nrf52840_Interfaces, BaseIoControllerPinmapGenerator, InternalSubcircuit, JlcPart, GeneratorBlock, FootprintBlock
):
    # in the absence of a chip-level subcircuit, this is used as the authoritative base device model
    # that other modules should wrap

    _PIN_MAPPING = {  # boundary pins only, inner pins ignored
        "P1.10": "3",
        "P1.11": "4",
        "P1.12": "5",
        "P1.13": "6",
        "P1.14": "7",
        "P1.15": "8",
        "P0.03": "9",
        "P0.29": "10",
        "P0.02": "11",
        "P0.31": "12",
        "P0.28": "13",
        "P0.30": "14",
        "P0.27": "16",
        "P0.00": "17",
        "P0.01": "18",
        "P0.26": "19",
        "P0.04": "20",
        "P0.05": "21",
        "P0.06": "22",
        "P0.07": "23",
        "P0.08": "24",
        "P1.08": "25",
        "P1.09": "26",
        "P0.11": "27",
        "P0.12": "29",
        "D-": "34",
        "D+": "35",
        "P0.14": "36",
        "P0.13": "37",
        "P0.16": "38",
        "P0.15": "39",
        "P0.17": "41",
        "P0.19": "42",
        "P0.21": "43",
        "P0.20": "44",
        "P0.23": "45",
        "P0.22": "46",
        "P1.00": "47",
        "P0.24": "48",
        "P0.25": "49",
        "P1.02": "50",
        "SWDIO": "51",
        "P0.09": "52",
        "SWCLK": "53",
        "P0.10": "54",
        "P1.04": "56",
        "P1.06": "57",
        "P1.07": "58",
        "P1.05": "59",
        "P1.03": "60",
        "P1.01": "61",
    }

    def __init__(self, _allowed_pins: ArrayStringLike = [], **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self._allowed_pins = self.ArgParameter(_allowed_pins)
        self.generator_param(self._allowed_pins)

        self.gnd = self.Port(Ground(), [Common])
        self.pwr = self.Port(
            VoltageSink(
                voltage_limits=(1.75, 3.6) * Volt,  # 1.75 minimum for power-on reset
                current_draw=(0, 212 / 64 + 4.8) * mAmp
                + self.io_current_draw.upper(),  # CPU @ max 212 Coremarks + 4.8mA in RF transmit
            ),
            [Power],
        )

        self.pwr_usb = self.Port(
            VoltageSink(
                voltage_limits=(4.35, 5.5) * Volt,
                current_draw=(0.262, 7.73) * mAmp,  # CPU/USB sleeping to everything active
            ),
            optional=True,
        )
        self.require((self.usb.length() > 0).implies(self.pwr_usb.is_connected()), "USB require Vbus connected")

        self._dio_model = DigitalBidir.from_supply(
            self.gnd,
            self.pwr,
            voltage_limit_tolerance=(-0.3, 0.3) * Volt,
            current_limits=(-6, 6) * mAmp,  # minimum current, high drive, Vdd>2.7
            input_threshold_factor=(0.3, 0.7),
            pullup_capable=True,
            pulldown_capable=True,
        )
        self._dio_lf_model = self._dio_model  # "standard drive, low frequency IO only" (differences not modeled)
        self.swd = self.Port(SwdTargetPort.empty(), optional=True)
        self.nreset = self.Port(DigitalSink.from_bidir(self._dio_model), optional=True)
        self._io_ports.insert(0, self.swd)

    @override
    def generate(self) -> None:
        super().generate()

        self.assign(self.lcsc_part, "C5118826")
        self.assign(self.actual_basic_part, False)
        self.footprint(
            "U",
            "RF_Module:Raytac_MDBT50Q",
            self._make_pinning(),
            mfr="Raytac",
            part="MDBT50Q-1MV2",
            datasheet="https://www.raytac.com/download/index.php?index_id=43",
        )

    @override
    def _system_pinmap(self) -> Mapping[Union[Iterable[str], str], Union[Passive, HasPassivePort]]:
        return {
            "28": self.pwr,  # Vdd
            "30": self.pwr,  # VddH
            # "31": DccH is disconnected - from section 8.3 for input voltage <3.6v
            ("1", "2", "15", "33", "55"): self.gnd,
            "32": self.pwr_usb,
            "40": self.nreset,
        }

    @override
    def _io_pinmap(self) -> PinMapUtil:
        """Returns the mappable for given the input power and ground references.
        This separates the system pins definition from the IO pins definition."""
        adc_model = AnalogSink.from_supply(
            self.gnd,
            self.pwr,
            voltage_limit_tolerance=(0, 0),  # datasheet 6.23.2, analog inputs cannot exceed Vdd or be lower than Vss
            signal_limit_tolerance=(0, 0),
            impedance=Range.from_lower(1) * MOhm,
        )

        uart_model = UartPort(DigitalBidir.empty())
        spi_model = SpiController(DigitalBidir.empty(), (125, 32000) * kHertz)
        spi_peripheral_model = SpiPeripheral(DigitalBidir.empty(), (125, 32000) * kHertz)  # tristated by CS pin
        i2c_model = I2cController(DigitalBidir.empty())
        i2c_target_model = I2cTarget(DigitalBidir.empty())
        i2s_model = I2sController(DigitalBidir.empty())

        hf_io_pins = [
            "P0.00",
            "P0.01",
            "P0.26",
            "P0.27",
            "P0.04",
            "P0.05",
            "P0.06",
            "P0.07",
            "P0.08",
            "P1.08",
            "P1.09",
            "P0.11",
            "P0.12",
            "P0.14",
            "P0.16",
            "P0.19",
            "P0.21",
            "P0.23",
            "P0.25",  # 'P0.18'
            "P0.13",
            "P0.15",
            "P0.17",
            "P0.20",
            "P0.22",
            "P0.24",
            "P1.00",
        ]

        return (
            PinMapUtil(
                [  # Section 7.1.2 with QIAA aQFN73 & QFAA QFN48 pins only
                    PinResource("P0.31", {"P0.31": self._dio_lf_model, "AIN7": adc_model}),
                    PinResource("P0.29", {"P0.29": self._dio_lf_model, "AIN5": adc_model}),
                    PinResource("P0.02", {"P0.02": self._dio_lf_model, "AIN0": adc_model}),
                    PinResource("P1.15", {"P1.15": self._dio_lf_model}),
                    PinResource("P1.13", {"P1.13": self._dio_lf_model}),
                    PinResource("P1.10", {"P1.10": self._dio_lf_model}),
                    PinResource("P0.30", {"P0.30": self._dio_lf_model, "AIN6": adc_model}),
                    PinResource("P0.28", {"P0.28": self._dio_lf_model, "AIN4": adc_model}),
                    PinResource("P0.03", {"P0.03": self._dio_lf_model, "AIN1": adc_model}),
                    PinResource("P1.14", {"P1.14": self._dio_lf_model}),
                    PinResource("P1.12", {"P1.12": self._dio_lf_model}),
                    PinResource("P1.11", {"P1.11": self._dio_lf_model}),
                    PinResource("P0.00", {"P0.00": self._dio_model}),  # TODO also 32.768 kHz crystal in
                    PinResource("P0.01", {"P0.01": self._dio_model}),  # TODO also 32.768 kHz crystal in
                    PinResource("P0.26", {"P0.26": self._dio_model}),
                    PinResource("P0.27", {"P0.27": self._dio_model}),
                    PinResource("P0.04", {"P0.04": self._dio_model, "AIN2": adc_model}),
                    PinResource("P0.10", {"P0.10": self._dio_lf_model}),  # TODO also NFC2
                    PinResource("P0.05", {"P0.05": self._dio_model, "AIN3": adc_model}),
                    PinResource("P0.06", {"P0.06": self._dio_model}),
                    PinResource("P0.09", {"P0.09": self._dio_lf_model}),  # TODO also NFC1
                    PinResource("P0.07", {"P0.07": self._dio_model}),
                    PinResource("P0.08", {"P0.08": self._dio_model}),
                    PinResource("P1.08", {"P1.08": self._dio_model}),
                    PinResource("P1.07", {"P1.07": self._dio_lf_model}),
                    PinResource("P1.09", {"P1.09": self._dio_model}),
                    PinResource("P1.06", {"P1.06": self._dio_lf_model}),
                    PinResource("P0.11", {"P0.11": self._dio_model}),
                    PinResource("P1.05", {"P1.05": self._dio_lf_model}),
                    PinResource("P0.12", {"P0.12": self._dio_model}),
                    PinResource("P1.04", {"P1.04": self._dio_lf_model}),
                    PinResource("P1.03", {"P1.03": self._dio_lf_model}),
                    PinResource("P1.02", {"P1.02": self._dio_lf_model}),
                    PinResource("P1.01", {"P1.01": self._dio_lf_model}),
                    PinResource("P0.14", {"P0.14": self._dio_model}),
                    PinResource("P0.16", {"P0.16": self._dio_model}),
                    # PinResource('P0.18', {'P0.18': dio_model}),  # configurable as RESET, mappable
                    PinResource("P0.19", {"P0.19": self._dio_model}),
                    PinResource("P0.21", {"P0.21": self._dio_model}),
                    PinResource("P0.23", {"P0.23": self._dio_model}),
                    PinResource("P0.25", {"P0.25": self._dio_model}),
                    PinResource("P0.13", {"P0.13": self._dio_model}),
                    PinResource("P0.15", {"P0.15": self._dio_model}),
                    PinResource("P0.17", {"P0.17": self._dio_model}),
                    PinResource("P0.20", {"P0.20": self._dio_model}),
                    PinResource("P0.22", {"P0.22": self._dio_model}),
                    PinResource("P0.24", {"P0.24": self._dio_model}),
                    PinResource(
                        "P1.00", {"P1.00": self._dio_model}
                    ),  # TRACEDATA[0] and SWO, if used as IO must clear TRACECONFIG reg
                    PeripheralFixedPin(
                        "SWD",
                        SwdTargetPort(self._dio_model),
                        {
                            "swclk": "SWCLK",
                            "swdio": "SWDIO",
                        },
                    ),
                    PeripheralFixedPin("USBD", UsbDevicePort(), {"dp": "D+", "dm": "D-"}),
                    PeripheralFixedResource(
                        "SPIM0",
                        spi_model,
                        {
                            "sck": hf_io_pins,
                            "miso": hf_io_pins,
                            "mosi": hf_io_pins,
                        },
                    ),
                    PeripheralFixedResource(
                        "SPIM1",
                        spi_model,
                        {
                            "sck": hf_io_pins,
                            "miso": hf_io_pins,
                            "mosi": hf_io_pins,
                        },
                    ),
                    PeripheralFixedResource(
                        "SPIM2",
                        spi_model,
                        {
                            "sck": hf_io_pins,
                            "miso": hf_io_pins,
                            "mosi": hf_io_pins,
                        },
                    ),
                    PeripheralFixedResource(
                        "SPIM3",
                        spi_model,
                        {
                            "sck": hf_io_pins,
                            "miso": hf_io_pins,
                            "mosi": hf_io_pins,
                        },
                    ),
                    PeripheralFixedResource(
                        "SPIS0",
                        spi_peripheral_model,
                        {  # TODO shared resource w/ SPI controller
                            "sck": hf_io_pins,
                            "miso": hf_io_pins,
                            "mosi": hf_io_pins,
                        },
                    ),
                    PeripheralFixedResource(
                        "SPIS1",
                        spi_peripheral_model,
                        {  # TODO shared resource w/ SPI controller
                            "sck": hf_io_pins,
                            "miso": hf_io_pins,
                            "mosi": hf_io_pins,
                        },
                    ),
                    PeripheralFixedResource(
                        "SPIS2",
                        spi_peripheral_model,
                        {  # TODO shared resource w/ SPI controller
                            "sck": hf_io_pins,
                            "miso": hf_io_pins,
                            "mosi": hf_io_pins,
                        },
                    ),
                    PeripheralFixedResource(
                        "TWIM0",
                        i2c_model,
                        {
                            "scl": hf_io_pins,
                            "sda": hf_io_pins,
                        },
                    ),
                    PeripheralFixedResource(
                        "TWIM1",
                        i2c_model,
                        {
                            "scl": hf_io_pins,
                            "sda": hf_io_pins,
                        },
                    ),
                    PeripheralFixedResource(
                        "TWIS0",
                        i2c_target_model,
                        {  # TODO shared resource w/ I2C controller
                            "scl": hf_io_pins,
                            "sda": hf_io_pins,
                        },
                    ),
                    PeripheralFixedResource(
                        "TWIS1",
                        i2c_target_model,
                        {  # TODO shared resource w/ I2C controller
                            "scl": hf_io_pins,
                            "sda": hf_io_pins,
                        },
                    ),
                    PeripheralFixedResource(
                        "UARTE0",
                        uart_model,
                        {
                            "tx": hf_io_pins,
                            "rx": hf_io_pins,
                        },
                    ),
                    PeripheralFixedResource(
                        "UARTE1",
                        uart_model,
                        {
                            "tx": hf_io_pins,
                            "rx": hf_io_pins,
                        },
                    ),
                    PeripheralFixedResource(
                        "I2S",
                        i2s_model,
                        {
                            "sck": hf_io_pins,
                            "ws": hf_io_pins,
                            "sd": hf_io_pins,
                        },
                    ),
                ]
            )
            .remap_pins(self._PIN_MAPPING)
            .filter_pins(self.get(self._allowed_pins))
        )


class Mdbt50q_1mv2(
    Microcontroller,
    Radiofrequency,
    Resettable,
    Nrf52840_Interfaces,
    IoControllerWithSwdTargetConnector,
    IoControllerPowerRequired,
    GeneratorBlock,
):
    """Wrapper around the Mdbt50q_1mv2 that includes the reference schematic."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.ic = self.Block(Mdbt50q_1mv2_Device(pin_assigns=ArrayStringExpr()))
        self.pwr_usb = self.Export(self.ic.pwr_usb, optional=True)
        self.generator_param(self.reset.is_connected(), self.pin_assigns, self.gpio.requested(), self.usb.requested())

    @override
    def contents(self) -> None:
        super().contents()
        self.connect(self.pwr, self.ic.pwr)
        self.connect(self.gnd, self.ic.gnd)

        self.connect(self.swd_node, self.ic.swd)
        self.connect(self.reset_node, self.ic.nreset)

        with self.implicit_connect(ImplicitConnect(self.pwr, [Power]), ImplicitConnect(self.gnd, [Common])) as imp:
            self.vcc_cap = imp.Block(DecouplingCapacitor(10 * uFarad(tol=0.2)))

    @override
    def generate(self) -> None:
        super().generate()

        def usb_export_transform(self_io: BasePort, assign: Optional[str]) -> Optional[BasePort]:
            self.vbus_cap = self.Block(DecouplingCapacitor(10 * uFarad(tol=0.2))).connected(self.gnd, self.pwr_usb)
            self.usb_res = self.Block(UsbSeriesResistor(27 * Ohm(tol=0.05)))
            self.connect(self_io, self.usb_res.exterior)
            return self.usb_res.interior

        # add a passthrough for gpio (DigitalBidir) to allow the SWD pins to be attached, if using
        self._wrap_inner(self.ic, {UsbDevicePort: usb_export_transform, DigitalBidir: lambda port, assign: port})

        if self.get(self.reset.is_connected()):
            self.connect(self.reset, self.ic.nreset)


class Holyiot_18010_Footprint(
    Nrf52840_Interfaces, BaseIoControllerWrapped, InternalSubcircuit, GeneratorBlock, FootprintBlock
):
    _PIN_REMAPPING = {  # boundary pins only, inner pins ignored
        "P1.11": "2",
        "P1.10": "3",
        "P1.13": "4",
        "P1.15": "5",
        "P0.03": "6",
        "P0.02": "7",
        "P0.28": "8",
        "P0.29": "9",
        "P0.30": "10",
        "P0.31": "11",
        "P0.04": "12",
        "P0.05": "13",
        "P0.07": "15",
        "P1.09": "16",
        "P0.12": "17",
        "P0.23": "18",
        "P0.21": "19",
        "P0.19": "20",
        "D-": "23",
        "D+": "24",
        "P0.22": "26",
        "P1.00": "27",
        "P1.03": "28",
        "P1.01": "29",
        "P1.02": "30",
        "SWCLK": "31",
        "SWDIO": "32",
        "P1.04": "33",
        "P1.06": "34",
        "P0.09": "35",
        "P0.10": "36",
    }

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.gnd = self.Port(Ground.empty())
        self.vdd_nrf = self.Port(VoltageSink.empty(), optional=True)
        self.vbus = self.Port(VoltageSink.empty(), optional=True)
        self.p0_18 = self.Port(DigitalSink.empty(), optional=True)  # nRESET
        self.swd = self.Port(SwdTargetPort.empty())
        self._io_ports.insert(0, self.swd)
        self.generator_param(self.pin_assigns)
        self._generator_param_all_ios()

    @override
    def generate(self) -> None:
        super().generate()

        self.footprint(
            "U",
            "edg:Holyiot-18010-NRF52840",
            self._make_pinning(
                {
                    "14": self.vdd_nrf,
                    ("1", "25", "37"): self.gnd,
                    "22": self.vbus,
                    "21": self.p0_18,
                },
                self._PIN_REMAPPING,
            ),
            mfr="Holyiot",
            part="18010",
            datasheet="http://www.holyiot.com/tp/2019042516322180424.pdf",
        )


class Holyiot_18010_Device(
    Nrf52840_Interfaces,
    BaseIoControllerWrapper,
    InternalSubcircuit,
    GeneratorBlock,
    WrapperSubboardBlock,
):

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.model = self.Block(
            Mdbt50q_1mv2_Device(
                pin_assigns=ArrayStringExpr(), _allowed_pins=list(Holyiot_18010_Footprint._PIN_REMAPPING.keys())
            )
        )
        self.gnd = self.Export(self.model.gnd)
        self.pwr = self.Export(self.model.pwr)
        self.pwr_usb = self.Export(self.model.pwr_usb, optional=True)
        self.reset = self.Export(self.model.nreset, optional=True)
        self.swd = self.Export(self.model.swd, optional=True)
        self.generator_param(self.pin_assigns)
        self._generator_param_all_ios()

    @override
    def generate(self) -> None:
        super().generate()

        self._export_ios_inner(self.model)
        self.assign(
            self.model.pin_assigns,
            self._make_model_pinning(Holyiot_18010_Footprint._PIN_REMAPPING, self.get(self.pin_assigns)),
        )

        self.device = self.Block(Holyiot_18010_Footprint(pin_assigns=self.model.actual_pin_assigns, external=True))
        self.assign(self.actual_pin_assigns, self.device.actual_pin_assigns)
        self._export_tap_ios_inner(self.device)
        self.export_tap(self.gnd, self.device.gnd)
        self.export_tap(self.pwr, self.device.vdd_nrf)
        self.export_tap(self.pwr_usb, self.device.vbus)
        self.export_tap(self.reset, self.device.p0_18)
        self.export_tap(self.swd, self.device.swd)


class Holyiot_18010(
    Microcontroller,
    Radiofrequency,
    Resettable,
    Nrf52840_Interfaces,
    IoControllerPowerRequired,
    IoControllerWithSwdTargetConnector,
    GeneratorBlock,
):
    """Wrapper around the Holyiot 18010 that includes supporting components (programming port)"""

    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        self.ic = self.Block(Holyiot_18010_Device(pin_assigns=ArrayStringExpr()))
        self.pwr_usb = self.Export(self.ic.pwr_usb, optional=True)

        self.generator_param(self.reset.is_connected(), self.pin_assigns, self.gpio.requested(), self.usb.requested())

    @override
    def contents(self) -> None:
        super().contents()

        self.connect(self.gnd, self.ic.gnd)
        self.connect(self.pwr, self.ic.pwr)

        self.connect(self.swd_node, self.ic.swd)
        self.connect(self.reset_node, self.ic.reset)

        with self.implicit_connect(ImplicitConnect(self.pwr, [Power]), ImplicitConnect(self.gnd, [Common])) as imp:
            self.vcc_cap = imp.Block(DecouplingCapacitor(10 * uFarad(tol=0.2)))

    @override
    def generate(self) -> None:
        super().generate()

        def usb_export_transform(self_io: BasePort, assign: Optional[str]) -> Optional[BasePort]:
            self.vbus_cap = self.Block(DecouplingCapacitor(10 * uFarad(tol=0.2))).connected(self.gnd, self.pwr_usb)
            self.usb_res = self.Block(UsbSeriesResistor(27 * Ohm(tol=0.05)))
            self.connect(self_io, self.usb_res.exterior)
            return self.usb_res.interior

        # add a passthrough for gpio (DigitalBidir) to allow the SWD pins to be attached, if using
        self._wrap_inner(self.ic, {UsbDevicePort: usb_export_transform, DigitalBidir: lambda port, assign: port})

        if self.get(self.reset.is_connected()):
            self.connect(self.reset, self.ic.reset)


class Feather_Nrf52840_Device(Nrf52840_Interfaces, BaseIoControllerWrapped, GeneratorBlock, FootprintBlock):

    _PIN_REMAPPING = {  # boundary pins only, inner pins ignored
        "P0.31": "3",  # AREF
        "P0.04": "5",  # A0
        "P0.05": "6",  # A1
        "P0.30": "7",  # A2
        "P0.28": "8",  # A3
        "P0.02": "9",  # A4
        "P0.03": "10",  # A5
        "P0.14": "11",  # SCK
        "P0.13": "12",  # MOSI
        "P0.15": "13",  # MISO
        "P0.24": "14",  # RXD
        "P0.25": "15",  # TXD
        "P0.10": "16",  # D2
        "P0.12": "17",  # SDA
        "P0.11": "18",  # SCL
        "P1.08": "19",  # D5
        "P0.07": "20",  # D6
        "P0.26": "21",  # D9
        "P0.27": "22",  # D10
        "P0.06": "23",  # D11
        "P0.08": "24",  # D12
        "P1.09": "25",  # D13
        # note onboard LED1 at P1.15, LED2 at P1.10
        # note onboard switch at P1.02, reset switch at P0.18
        # note onboard neopixel at P0.16 (data out not broken out)
        # note onboard VBAT sense divider at P0.29
    }

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.gnd = self.Port(Ground.empty(), optional=True)
        # power ports are passive so directionality and concrete types can be resolved at the higher modeling level
        self.pwr = self.Port(Passive.empty(), optional=True)
        self.vusb = self.Port(Passive.empty(), optional=True)

        self.generator_param(self.pin_assigns)
        self._generator_param_all_ios()

    @override
    def generate(self) -> None:
        super().generate()

        self.footprint(
            "U",
            "bldc:FEATHERWING_NODIM",
            self._make_pinning(
                {
                    "2": self.pwr,
                    "4": self.gnd,
                    # "1": reset,
                    "26": self.vusb,
                    # 'EN': '27',  # controls the onboard 3.3 LDO, internally pulled up
                    # 'Vbat': '28',
                },
                self._PIN_REMAPPING,
            ),
            mfr="Adafruit",
            part="Feather nRF52840 Express",
            datasheet="https://learn.adafruit.com/assets/68545",
        )


class Feather_Nrf52840(
    IoControllerUsbOut,
    IoControllerPowerOut,
    Nrf52840_Interfaces,
    BaseIoControllerWrapper,
    IoController,
    WrapperSubboardBlock,
    GeneratorBlock,
    FootprintBlock,
):
    """Feather nRF52840 socketed dev board as either power source or sink"""

    _MBR120_DROP = (0, 0.340) * Volt
    _AP2112_3V3_OUT = 3.3 * Volt(tol=0.015)  # note dropout voltage up to 400mV, current up to 600mA

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.generator_param(
            self.pin_assigns,
            self.gnd.is_connected(),
            self.pwr.is_connected(),
            self.pwr_out.is_connected(),
            self.vusb_out.is_connected(),
        )
        self._generator_param_all_ios()

    @override
    def generate(self) -> None:
        super().generate()

        self.model = self.Block(
            Mdbt50q_1mv2_Device(
                pin_assigns=ArrayStringExpr(),
                _allowed_pins=list(Feather_Nrf52840_Device._PIN_REMAPPING.keys()),
            )
        )
        self.device = self.Block(Feather_Nrf52840_Device(pin_assigns=ArrayStringExpr()), external=True)
        self._wrap_inner_model_device(self.model, self.device, Feather_Nrf52840_Device._PIN_REMAPPING)

        self.connect(self._generate_gnd_node(), self.model.gnd)
        self.export_tap(self.gnd, self.device.gnd)

        self.connect(
            self._generate_pwr_node(voltage_out=self._AP2112_3V3_OUT, current_limits=UsbConnector.USB2_CURRENT_LIMITS),
            self.model.pwr,
        )
        self.export_tap((self.pwr if self.get(self.pwr.is_connected()) else self.pwr_out).net, self.device.pwr)

        self.vusb_out.init_from(
            VoltageSource(
                voltage_out=UsbConnector.USB2_VOLTAGE_RANGE - self._MBR120_DROP,
                current_limits=UsbConnector.USB2_CURRENT_LIMITS,
            )
        )
        self.export_tap(self.vusb_out.net, self.device.vusb)
