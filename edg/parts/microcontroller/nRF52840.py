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


@non_library
class Nrf52840_Ios(Nrf52840_Interfaces, BaseIoControllerPinmapGenerator, GeneratorBlock, FootprintBlock):
    """nRF52840 IO mappings
    https://infocenter.nordicsemi.com/pdf/nRF52840_PS_v1.7.pdf"""

    RESOURCE_PIN_REMAP: Dict[str, str]  # resource name in base -> pin name

    @abstractmethod
    def _vddio(self) -> Port[VoltageLink]: ...

    def _vdd_model(self) -> VoltageSink:
        return VoltageSink(
            voltage_limits=(1.75, 3.6) * Volt,  # 1.75 minimum for power-on reset
            current_draw=(0, 212 / 64 + 4.8) * mAmp
            + self.io_current_draw.upper(),  # CPU @ max 212 Coremarks + 4.8mA in RF transmit
        )

    def _dio_model(self, pwr: Port[VoltageLink]) -> DigitalBidir:
        return DigitalBidir.from_supply(
            self.gnd,
            pwr,
            voltage_limit_tolerance=(-0.3, 0.3) * Volt,
            current_limits=(-6, 6) * mAmp,  # minimum current, high drive, Vdd>2.7
            input_threshold_factor=(0.3, 0.7),
            pullup_capable=True,
            pulldown_capable=True,
        )

    @override
    def _io_pinmap(self) -> PinMapUtil:
        """Returns the mappable for given the input power and ground references.
        This separates the system pins definition from the IO pins definition."""
        pwr = self._vddio()
        dio_model = self._dio_model(pwr)
        dio_lf_model = dio_model  # "standard drive, low frequency IO only" (differences not modeled)

        adc_model = AnalogSink.from_supply(
            self.gnd,
            pwr,
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

        return PinMapUtil(
            [  # Section 7.1.2 with QIAA aQFN73 & QFAA QFN48 pins only
                PinResource("P0.31", {"P0.31": dio_lf_model, "AIN7": adc_model}),
                PinResource("P0.29", {"P0.29": dio_lf_model, "AIN5": adc_model}),
                PinResource("P0.02", {"P0.02": dio_lf_model, "AIN0": adc_model}),
                PinResource("P1.15", {"P1.15": dio_lf_model}),
                PinResource("P1.13", {"P1.13": dio_lf_model}),
                PinResource("P1.10", {"P1.10": dio_lf_model}),
                PinResource("P0.30", {"P0.30": dio_lf_model, "AIN6": adc_model}),
                PinResource("P0.28", {"P0.28": dio_lf_model, "AIN4": adc_model}),
                PinResource("P0.03", {"P0.03": dio_lf_model, "AIN1": adc_model}),
                PinResource("P1.14", {"P1.14": dio_lf_model}),
                PinResource("P1.12", {"P1.12": dio_lf_model}),
                PinResource("P1.11", {"P1.11": dio_lf_model}),
                PinResource("P0.00", {"P0.00": dio_model}),  # TODO also 32.768 kHz crystal in
                PinResource("P0.01", {"P0.01": dio_model}),  # TODO also 32.768 kHz crystal in
                PinResource("P0.26", {"P0.26": dio_model}),
                PinResource("P0.27", {"P0.27": dio_model}),
                PinResource("P0.04", {"P0.04": dio_model, "AIN2": adc_model}),
                PinResource("P0.10", {"P0.10": dio_lf_model}),  # TODO also NFC2
                PinResource("P0.05", {"P0.05": dio_model, "AIN3": adc_model}),
                PinResource("P0.06", {"P0.06": dio_model}),
                PinResource("P0.09", {"P0.09": dio_lf_model}),  # TODO also NFC1
                PinResource("P0.07", {"P0.07": dio_model}),
                PinResource("P0.08", {"P0.08": dio_model}),
                PinResource("P1.08", {"P1.08": dio_model}),
                PinResource("P1.07", {"P1.07": dio_lf_model}),
                PinResource("P1.09", {"P1.09": dio_model}),
                PinResource("P1.06", {"P1.06": dio_lf_model}),
                PinResource("P0.11", {"P0.11": dio_model}),
                PinResource("P1.05", {"P1.05": dio_lf_model}),
                PinResource("P0.12", {"P0.12": dio_model}),
                PinResource("P1.04", {"P1.04": dio_lf_model}),
                PinResource("P1.03", {"P1.03": dio_lf_model}),
                PinResource("P1.02", {"P1.02": dio_lf_model}),
                PinResource("P1.01", {"P1.01": dio_lf_model}),
                PinResource("P0.14", {"P0.14": dio_model}),
                PinResource("P0.16", {"P0.16": dio_model}),
                # PinResource('P0.18', {'P0.18': dio_model}),  # configurable as RESET, mappable
                PinResource("P0.19", {"P0.19": dio_model}),
                PinResource("P0.21", {"P0.21": dio_model}),
                PinResource("P0.23", {"P0.23": dio_model}),
                PinResource("P0.25", {"P0.25": dio_model}),
                PinResource("P0.13", {"P0.13": dio_model}),
                PinResource("P0.15", {"P0.15": dio_model}),
                PinResource("P0.17", {"P0.17": dio_model}),
                PinResource("P0.20", {"P0.20": dio_model}),
                PinResource("P0.22", {"P0.22": dio_model}),
                PinResource("P0.24", {"P0.24": dio_model}),
                PinResource(
                    "P1.00", {"P1.00": dio_model}
                ),  # TRACEDATA[0] and SWO, if used as IO must clear TRACECONFIG reg
                PeripheralFixedPin(
                    "SWD",
                    SwdTargetPort(dio_model),
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
        ).remap_pins(self.RESOURCE_PIN_REMAP)


@abstract_block
class Nrf52840_Base(Nrf52840_Ios, GeneratorBlock):
    SYSTEM_PIN_REMAP: Dict[str, Union[str, List[str]]]  # pin name in base -> pin name(s)

    @override
    def _vddio(self) -> Port[VoltageLink]:
        return self.pwr

    @override
    def _system_pinmap(self) -> Dict[str, Union[Passive, HasPassivePort]]:
        return VariantPinRemapper(
            {
                "Vdd": self.pwr,
                "Vss": self.gnd,
                "Vbus": self.pwr_usb,
                "nRESET": self.nreset,
            }
        ).remap(self.SYSTEM_PIN_REMAP)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.gnd = self.Port(Ground(), [Common])
        self.pwr = self.Port(self._vdd_model(), [Power])

        self.pwr_usb = self.Port(
            VoltageSink(
                voltage_limits=(4.35, 5.5) * Volt,
                current_draw=(0.262, 7.73) * mAmp,  # CPU/USB sleeping to everything active
            ),
            optional=True,
        )
        self.require((self.usb.length() > 0).implies(self.pwr_usb.is_connected()), "USB require Vbus connected")

        # Additional ports (on top of IoController)
        # Crystals from table 15, 32, 33
        # TODO Table 32, model crystal load capacitance and series resistance ratings
        self.xtal = self.Port(
            CrystalDriver(frequency_limits=(1, 25) * MHertz, voltage_out=self.pwr.link().voltage), optional=True
        )
        # Assumed from "32kHz crystal" in 14.5
        self.xtal_rtc = self.Port(
            CrystalDriver(frequency_limits=(32, 33) * kHertz, voltage_out=self.pwr.link().voltage), optional=True
        )

        self.swd = self.Port(SwdTargetPort.empty())
        self.nreset = self.Port(DigitalSink.from_bidir(self._dio_model(self.pwr)), optional=True)
        self._io_ports.insert(0, self.swd)


class Mdbt50q_1mv2_Device(
    Nrf52840_Interfaces, BaseIoControllerPinmapGenerator, InternalSubcircuit, JlcPart, GeneratorBlock, FootprintBlock
):
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

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

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

        # Additional ports (on top of IoController)
        # Crystals from table 15, 32, 33
        # TODO Table 32, model crystal load capacitance and series resistance ratings
        self.xtal = self.Port(
            CrystalDriver(frequency_limits=(1, 25) * MHertz, voltage_out=self.pwr.link().voltage), optional=True
        )
        # Assumed from "32kHz crystal" in 14.5
        self.xtal_rtc = self.Port(
            CrystalDriver(frequency_limits=(32, 33) * kHertz, voltage_out=self.pwr.link().voltage), optional=True
        )

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
        self.swd = self.Port(SwdTargetPort.empty())
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
    def _system_pinmap(self) -> Dict[str, Union[Passive, HasPassivePort]]:
        return {
            "28": self.pwr,  # Vdd
            "30": self.pwr,  # VddH
            # "31": DccH is disconnected - from section 8.3 for input voltage <3.6v
            "1": self.gnd,
            "2": self.gnd,
            "15": self.gnd,
            "33": self.gnd,
            "55": self.gnd,
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

        return PinMapUtil(
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
        ).remap_pins(self._PIN_MAPPING)


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

    # in the absence of a chip-level subcircuit, this is used as the authoritative base device model
    # that other modules should wrap

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


class Holyiot_18010_Device(
    Nrf52840_Interfaces, IoControllerWrapped, InternalSubcircuit, GeneratorBlock, FootprintBlock
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

    SYSTEM_PIN_REMAP: Dict[str, Union[str, List[str]]] = {
        "Vdd": "14",
        "Vss": ["1", "25", "37"],
        "Vbus": "22",
        "nRESET": "21",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gnd = self.Port(Ground.empty())
        self.vdd_nrf = self.Port(VoltageSink.empty(), optional=True)
        self.vbus = self.Port(VoltageSink.empty(), optional=True)
        self.p0_18 = self.Port(DigitalSink.empty(), optional=True)  # nRESET
        self.swd = self.Port(SwdTargetPort.empty())
        self._io_ports.insert(0, self.swd)
        self.generator_param(self.pin_assigns)

        # TODO MOVE TO INFRASTRUCTURE
        for io_port in self._io_ports:
            if isinstance(io_port, Vector):
                self.generator_param(io_port.requested())
            elif isinstance(io_port, Port):
                self.generator_param(io_port.is_connected())
            else:
                raise NotImplementedError(f"unknown port type {io_port}")

    @override
    def generate(self) -> None:
        super().generate()

        pinning: Dict[str, HasPassivePort] = {
            "14": self.vdd_nrf,
            "1": self.gnd,
            "25": self.gnd,
            "37": self.gnd,
            "22": self.vbus,
            "21": self.p0_18,
        }
        remap_pinnings, remap_pin_assigns = self._remap_pinning_assigns(self.get(self.pin_assigns), self._PIN_REMAPPING)
        pinning.update(remap_pinnings)
        self.assign(self.actual_pin_assigns, self._remap_assigns_to_value(remap_pin_assigns))

        self.footprint(
            "U",
            "edg:Holyiot-18010-NRF52840",
            self._make_pinning(),
            mfr="Holyiot",
            part="18010",
            datasheet="http://www.holyiot.com/tp/2019042516322180424.pdf",
        )


class Holyiot_18010_Subcircuit(
    Nrf52840_Interfaces,
    IoControllerWithSwdTargetConnector,
    InternalSubcircuit,
    GeneratorBlock,
):
    """Wrapper around the Mdbt50q_1mv2 that includes the reference schematic."""

    # in the absence of a chip-level subcircuit, this is used as the authoritative base device model
    # that other modules should wrap

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.ic = self.Block(Holyiot_18010_Device(pin_assigns=self.pin_assigns))
        self.pwr_usb = self.Export(self.ic.vbus, optional=True)
        self.reset = self.Export(self.ic.p0_18, optional=True)
        self.generator_param(self.reset.is_connected(), self.pin_assigns, self.gpio.requested(), self.usb.requested())

    @override
    def contents(self) -> None:
        super().contents()
        self.connect(self.pwr, self.ic.vdd_nrf)
        self.connect(self.gnd, self.ic.gnd)

        self.connect(self.swd_node, self.ic.swd)

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


class Holyiot_18010(
    Microcontroller,
    Radiofrequency,
    Resettable,
    Nrf52840_Interfaces,
    IoControllerPowerRequired,
    GeneratorBlock,
    WrapperSubboardBlock,
):
    """Wrapper around the Holyiot 18010 that includes supporting components (programming port)"""

    def __init__(
        self,
        swd_connect_swo: BoolLike = False,  # TODO SwdTargetConnector should only define the interface
        swd_connect_tdi: BoolLike = False,
        swd_connect_reset: BoolLike = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        self.swd_connect_swo = self.ArgParameter(swd_connect_swo)
        self.swd_connect_tdi = self.ArgParameter(swd_connect_tdi)
        self.swd_connect_reset = self.ArgParameter(swd_connect_reset)

        self.model = self.Block(
            Mdbt50q_1mv2(
                pin_assigns=ArrayStringExpr(),
                swd_connect_swo=self.swd_connect_swo,
                swd_connect_tdi=self.swd_connect_tdi,
                swd_connect_reset=self.swd_connect_reset,
            )
        )
        self.pwr_usb = self.Export(self.model.pwr_usb, optional=True)

        self.generator_param(self.reset.is_connected())

    @override
    def contents(self) -> None:
        super().contents()

        model_pin_assigns = self._export_ios_inner(self.model)
        self.assign(self.model.pin_assigns, model_pin_assigns)
        self.connect(self.pwr, self.model.pwr)
        self.connect(self.gnd, self.model.gnd)

        self.device = self.Block(
            Holyiot_18010_Subcircuit(
                pin_assigns=self.model.actual_pin_assigns,
                swd_connect_swo=self.swd_connect_swo,
                swd_connect_tdi=self.swd_connect_tdi,
                swd_connect_reset=self.swd_connect_reset,
            ),
            external=True,
        )
        self.assign(self.actual_pin_assigns, self.device.actual_pin_assigns)
        self._export_tap_ios_inner(self.device)
        self.export_tap(self.gnd, self.device.gnd)
        self.export_tap(self.pwr, self.device.pwr)
        self.export_tap(self.pwr_usb, self.device.pwr_usb)

    @override
    def generate(self) -> None:
        super().generate()

        if self.get(self.reset.is_connected()):
            self.connect(self.reset, self.model.nreset)
            self.export_tap(self.reset, self.device.reset)


class Feather_Nrf52840(
    IoControllerUsbOut, IoControllerPowerOut, Nrf52840_Ios, IoController, GeneratorBlock, FootprintBlock
):
    """Feather nRF52840 socketed dev board as either power source or sink"""

    SYSTEM_PIN_REMAP: Dict[str, Union[str, List[str]]] = {
        "Vdd": "2",  # 3v3
        "Vss": "4",
        # 'reset': '1',
        "Vbus": "26",
        # 'EN': '27',  # controls the onboard 3.3 LDO, internally pulled up
        # 'Vbat': '28',
    }
    RESOURCE_PIN_REMAP = {  # boundary pins only, inner pins ignored
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

    @override
    def _vddio(self) -> Port[VoltageLink]:
        if self.get(self.pwr.is_connected()):  # board sinks power
            return self.pwr
        else:
            return self.pwr_out

    @override
    def _system_pinmap(self) -> Dict[str, Union[Passive, HasPassivePort]]:
        if self.get(self.pwr.is_connected()):  # board sinks power
            self.require(~self.vusb_out.is_connected(), "can't source USB power if power input connected")
            self.require(~self.pwr_out.is_connected(), "can't source 3v3 power if power input connected")
            return VariantPinRemapper(
                {
                    "Vdd": self.pwr,
                    "Vss": self.gnd,
                }
            ).remap(self.SYSTEM_PIN_REMAP)
        else:  # board sources power (default)
            return VariantPinRemapper(
                {
                    "Vdd": self.pwr_out,
                    "Vss": self.gnd,
                    "Vbus": self.vusb_out,
                }
            ).remap(self.SYSTEM_PIN_REMAP)

    @override
    def contents(self) -> None:
        super().contents()

        self.gnd.init_from(Ground())
        self.pwr.init_from(self._vdd_model())

        mbr120_drop = (0, 0.340) * Volt
        ap2112_3v3_out = 3.3 * Volt(tol=0.015)  # note dropout voltage up to 400mV, current up to 600mA
        self.vusb_out.init_from(
            VoltageSource(
                voltage_out=UsbConnector.USB2_VOLTAGE_RANGE - mbr120_drop,
                current_limits=UsbConnector.USB2_CURRENT_LIMITS,
            )
        )
        self.pwr_out.init_from(
            VoltageSource(voltage_out=ap2112_3v3_out, current_limits=UsbConnector.USB2_CURRENT_LIMITS)
        )

        self.generator_param(self.pwr.is_connected())

    @override
    def generate(self) -> None:
        super().generate()

        self.footprint(
            "U",
            "bldc:FEATHERWING_NODIM",
            self._make_pinning(),
            mfr="Adafruit",
            part="Feather nRF52840 Express",
            datasheet="https://learn.adafruit.com/assets/68545",
        )
