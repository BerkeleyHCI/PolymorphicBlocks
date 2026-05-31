from typing import *

from typing_extensions import override

from ...circuits import *
from ...vendor_parts.jlc.JlcPart import JlcPart
from .EspCommon import HasEspProgramming


@non_library
class Esp32c3_Interfaces(
    IoControllerSpiPeripheral,
    IoControllerI2cTarget,
    IoControllerCan,
    IoControllerI2s,
    IoControllerWifi,
    IoControllerBle,
    BaseIoController,
):
    """Defines base interfaces for ESP32C3 microcontrollers"""


class Esp32c3_Device(Esp32c3_Interfaces, BaseIoControllerPinmapGenerator, InternalSubcircuit, FootprintBlock, JlcPart):

    RESOURCE_PIN_REMAP = {
        "GPIO0": "4",
        "GPIO1": "5",
        "GPIO3": "8",
        "MTMS": "9",  # GPIO4
        "MTDI": "10",  # GPIO5
        "MTCK": "12",  # GPIO6
        "MTDO": "13",  # GPIO7
        "GPIO10": "16",
        "GPIO18": "25",
        "GPIO19": "26",
    }

    @override
    def _system_pinmap(self) -> Dict[str, Union[Passive, HasPassivePort]]:
        return {
            "31": self.vdda,
            "32": self.vdda,
            "33": self.gnd,
            "6": self.io2,
            "7": self.en,
            "14": self.io8,
            "15": self.io9,
            "27": self.uart0.rx,
            "28": self.uart0.tx,
            "1": self.lna_in,
            "11": self.vdd3p3_rtc,
            "17": self.vdd3p3_cpu,
            "18": self.vdd_spi,
            "2": self.vdd3p3,
            "3": self.vdd3p3,
            "30": self.xtal.xtal_in,
            "29": self.xtal.xtal_out,
        }

    def __init__(self, _model: BoolLike = False, _allowed_pins: ArrayStringLike = [], **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self._model = self.ArgParameter(_model)
        self._allowed_pins = self.ArgParameter(_allowed_pins)
        self.generator_param(self._allowed_pins)

        self.gnd = self.Port(Ground(), [Common])
        self.vdda = self.Port(  # models total current draw
            VoltageSink(
                voltage_limits=(3.0, 3.6) * Volt,  # section 4.2
                current_draw=(0.001, 335) * mAmp
                + self.io_current_draw.upper(),  # section 4.6, from power off to RF active
            )
        )
        self.vdd3p3 = self.Port(
            VoltageSink(  # needs to be downstream of a filter
                voltage_limits=(3.0, 3.6) * Volt,  # section 4.2
            )
        )
        self.vdd3p3_rtc = self.Port(
            VoltageSink(
                voltage_limits=(3.0, 3.6) * Volt,  # section 4.2
            )
        )
        self.vdd3p3_cpu = self.Port(
            VoltageSink(
                voltage_limits=(3.0, 3.6) * Volt,  # section 4.2
            )
        )
        self.vdd_spi = self.Port(
            VoltageSink(
                voltage_limits=(3.0, 3.6) * Volt,  # section 4.2
            )
        )

        # 10ppm requirement from ESP32-C3-WROOM schematic, and in ESP32 hardware design guidelines
        self.xtal = self.Port(  # vdda domain assumed
            CrystalDriver(frequency_limits=40 * MHertz(tol=10e-6), voltage_out=self.vdda.link().voltage), optional=True
        )
        self.require((~self._model).implies(self.xtal.is_connected()))

        # section 2.4: strapping IOs that need a fixed value to boot, and currently can't be allocated as GPIO
        # TODO model from different 3.3v domains
        self._dio_model = DigitalBidir.from_supply(  # table 4.4
            self.gnd,
            self.vdd3p3_cpu,
            voltage_limit_tolerance=(-0.3, 0.3) * Volt,
            current_limits=(-28, 40) * mAmp,
            input_threshold_factor=(0.25, 0.75),
            pullup_capable=True,
            pulldown_capable=True,
        )
        self.en = self.Port(DigitalSink.from_bidir(self._dio_model), optional=True)  # needs external pullup
        self.io2 = self.Port(self._dio_model, optional=True)  # needs external pullup; affects IO glitching on boot
        self.io8 = self.Port(self._dio_model, optional=True)  # needs external pullup, required for download boot
        self.io9 = self.Port(
            self._dio_model, optional=True
        )  # internally pulled up for SPI boot, connect to GND for download
        self.require((~self._model).implies(self.en.is_connected() & self.io2.is_connected() & self.io8.is_connected()))

        # similarly, the programming UART is fixed and allocated separately
        self.uart0 = self.Port(UartPort(self._dio_model), optional=True)

        self.lna_in = self.Port(Passive(), optional=True)
        self.require((~self._model).implies(self.lna_in.is_connected()))

    @override
    def generate(self) -> None:
        super().generate()

        # this is the part with 4MB integrated flash
        # TODO: support other part numbers, including without integrated flash
        self.footprint(
            "U",
            "Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.65x3.65mm",
            self._make_pinning(),
            mfr="Espressif Systems",
            part="ESP32-C3FH4",
            datasheet="https://www.espressif.com/sites/default/files/documentation/esp32-c3-wroom-02_datasheet_en.pdf",
            pnp_rot=-90,
        )
        self.assign(self.lcsc_part, "C2858491")
        self.assign(self.actual_basic_part, False)

    @override
    def _io_pinmap(self) -> PinMapUtil:
        adc_model = AnalogSink.from_supply(
            self.gnd,
            self.vdda,  # assumed
            signal_limit_abs=(0, 2.5) * Volt,  # table 15, effective ADC range
            # TODO: impedance / leakage - not specified by datasheet
        )

        uart_model = UartPort(DigitalBidir.empty())
        spi_model = SpiController(
            DigitalBidir.empty(), (0, 60) * MHertz
        )  # section 3.4.2, max block in GP controller mode
        spi_peripheral_model = SpiPeripheral(DigitalBidir.empty(), (0, 60) * MHertz)
        i2c_model = I2cController(DigitalBidir.empty())  # section 3.4.4, supporting 100/400 and up to 800 kbit/s
        i2c_target_model = I2cTarget(DigitalBidir.empty())

        return (
            PinMapUtil(
                [  # section 2.2
                    PinResource("GPIO0", {"GPIO0": self._dio_model, "ADC1_CH0": adc_model}),  # also XTAL_32K_P
                    PinResource("GPIO1", {"GPIO1": self._dio_model, "ADC1_CH1": adc_model}),  # also XTAL_32K_N
                    # PinResource('GPIO2', {'GPIO2': self._dio_model, 'ADC1_CH2': adc_model}),  # boot pin, non-allocatable
                    PinResource("GPIO3", {"GPIO3": self._dio_model, "ADC1_CH3": adc_model}),
                    PinResource("MTMS", {"GPIO4": self._dio_model, "ADC1_CH4": adc_model}),
                    PinResource("MTDI", {"GPIO5": self._dio_model}),  # also ADC2_CH0, but unusable with WiFi
                    PinResource("MTCK", {"GPIO6": self._dio_model}),
                    PinResource("MTDO", {"GPIO7": self._dio_model}),
                    # PinResource('GPIO8', {'GPIO8': self._dio_model}),  # boot pin, non-allocatable
                    # PinResource('GPIO9', {'GPIO9': self._dio_model}),  # boot pin, non-allocatable
                    PinResource("GPIO10", {"GPIO10": self._dio_model}),
                    # not allowed for in-package flash
                    # PinResource("VDD_SPI", {"GPIO11": self._dio_model}),
                    # SPI pins skipped - internal to the modules supported so far
                    PinResource("GPIO18", {"GPIO18": self._dio_model}),
                    PinResource("GPIO19", {"GPIO19": self._dio_model}),
                    # PinResource('GPIO20', {'GPIO20': self._dio_model}),  # boot pin, non-allocatable
                    # PinResource('GPIO21', {'GPIO21': self._dio_model}),  # boot pin, non-allocatable
                    # peripherals in section 3.11
                    # PeripheralFixedResource('U0', uart_model, {  # programming pin, non-allocatable
                    #   'txd': ['GPIO21'], 'rxd': ['GPIO20']
                    # }),
                    PeripheralAnyResource("U1", uart_model),
                    PeripheralAnyResource("I2C", i2c_model),
                    PeripheralAnyResource("I2C_T", i2c_target_model),  # TODO shared resource w/ I2C controller
                    PeripheralAnyResource("SPI2", spi_model),
                    PeripheralAnyResource("SPI2_P", spi_peripheral_model),  # TODO shared resource w/ SPI controller
                    PeripheralAnyResource("I2S", I2sController.empty()),
                    PeripheralAnyResource("TWAI", CanControllerPort.empty()),
                ]
            )
            .remap_pins(self.RESOURCE_PIN_REMAP)
            .filter_pins(self.get(self._allowed_pins))
        )


class Esp32c3(
    Microcontroller,
    Radiofrequency,
    HasEspProgramming,
    Resettable,
    Esp32c3_Interfaces,
    WithCrystalGenerator,
    IoControllerPowerRequired,
    DiscreteRfWarning,
    GeneratorBlock,
):
    """ESP32-C3 application circuit, bare chip + RF circuits.
    NOT RECOMMENDED - you will need to do your own RF layout, instead consider using the WROOM module."""

    DEFAULT_CRYSTAL_FREQUENCY = 40 * MHertz(tol=10e-6)

    def __init__(self) -> None:
        super().__init__()
        self.ic: Esp32c3_Device
        self.generator_param(self.reset.is_connected(), self.pin_assigns, self.gpio.requested())

        self._io2_ext_connected: bool = False
        self._io8_ext_connected: bool = False

    @override
    def generate(self) -> None:
        super().generate()

        with self.implicit_connect(ImplicitConnect(self.pwr, [Power]), ImplicitConnect(self.gnd, [Common])) as imp:
            self.ic = imp.Block(Esp32c3_Device(pin_assigns=ArrayStringExpr()))
            self.connect(self.pwr, self.ic.vdda, self.ic.vdd3p3_rtc, self.ic.vdd3p3_cpu, self.ic.vdd_spi)

            def gpio_transform(self_io: BasePort, assign: Optional[str]) -> Optional[BasePort]:
                if assign == "_GPIO2_STRAP_EXT_PU":
                    self.connect(self_io, self.ic.io2)
                    self._io2_ext_connected = True
                    return None
                elif assign == "_GPIO8_STRAP_EXT_PU":
                    self.connect(self_io, self.ic.io8)
                    self._io8_ext_connected = True
                    return None
                elif assign == "_GPIO9_STRAP":
                    self.connect(self_io, self.ic.io9)
                    return None
                return self_io

            self._wrap_inner(self.ic, transforms={DigitalBidir: gpio_transform})

            self.connect(self.xtal_node, self.ic.xtal)
            self.connect(self.program_uart_node, self.ic.uart0)
            self.connect(self.program_en_node, self.ic.en)
            self.connect(self.program_boot_node, self.ic.io9)

            self.vdd_bulk_cap = imp.Block(DecouplingCapacitor(10 * uFarad(tol=0.2)))  # C5
            self.vdda_cap0 = imp.Block(DecouplingCapacitor(1 * uFarad(tol=0.2)))  # C3
            self.vdda_cap1 = imp.Block(DecouplingCapacitor(10 * nFarad(tol=0.2)))  # C3
            self.vddrtc_cap = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))  # C3
            self.vddcpu_cap = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))  # C10
            self.vddspi_cap = imp.Block(DecouplingCapacitor(1 * uFarad(tol=0.2)))  # C11

            self.ant = imp.Block(
                Antenna(frequency=(2402, 2484) * MHertz, impedance=50 * Ohm(tol=0.1), power=(0, 0.126) * Watt)
            )
            # expand the bandwidth to allow a lower Q and higher bandwidth
            # TODO: more principled calculation of Q / bandwidth, voltage, current and tolerance
            # 10% tolerance is roughly to support 5% off-nominal tolerance plus 5% component tolerance
            (self.pi,), _ = self.chain(
                self.ic.lna_in,
                imp.Block(
                    PiLowPassFilter(
                        (2402 - 200, 2484 + 200) * MHertz,
                        35 * Ohm,
                        10 * Ohm,
                        50 * Ohm,
                        0.10,
                        self.pwr.link().voltage,
                        (0, 0.1) * Amp,
                    )
                ),
                self.ant.a,
            )

        with self.implicit_connect(ImplicitConnect(self.gnd, [Common])) as imp:
            self.vdd3p3_l_cap = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2))).connected(pwr=self.pwr)  # C6
            self.vdd3p3_cap = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2))).connected(
                pwr=self.ic.vdd3p3
            )  # C7 - DNP on ESP32-C3-WROOM schematic but 0.1uF on hardware design guide
            self.vdd3p3_l = self.Block(
                SeriesPowerInductor(
                    inductance=2 * nHenry(tol=0.2),
                )
            ).connected(self.pwr, self.ic.vdd3p3)

        if self.get(self.reset.is_connected()):
            self.connect(self.reset, self.ic.en)
        else:
            self.en_pull = self.Block(PullupDelayRc(10 * kOhm(tol=0.05), 10 * mSecond(tol=0.2))).connected(
                gnd=self.gnd, pwr=self.pwr, io=self.ic.en
            )

        # Note strapping pins (section 3.3) IO2, 8, 9; IO9 is internally pulled up
        # IO9 (internally pulled up) is 1 for SPI boot and 0 for download boot
        # IO2 must be 1 for both SPI and download boot, while IO8 must be 1 for download boot
        if not self._io8_ext_connected:
            self.connect(self.ic.io8, self.pwr.as_digital_source())
        if not self._io2_ext_connected:
            self.connect(self.ic.io2, self.pwr.as_digital_source())

    @override
    def _crystal_required(self) -> bool:
        return True  # crystal oscillator always required


class Esp32c3_Wroom02_Footprint(
    Esp32c3_Interfaces, BaseIoControllerWrapped, InternalSubcircuit, GeneratorBlock, FootprintBlock, JlcPart
):

    _PIN_REMAPPING = {
        "MTMS": "3",  # GPIO4
        "MTDI": "4",  # GPIO5
        "MTCK": "5",  # GPIO6
        "MTDO": "6",  # GPIO7
        "GPIO10": "10",
        "GPIO18": "13",
        "GPIO19": "14",
        "GPIO3": "15",
        "GPIO1": "17",
        "GPIO0": "18",
    }

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.gnd = self.Port(Ground.empty(), [Common])
        self.v3v3 = self.Port(VoltageSink.empty(), [Power])

        self.en = self.Port(DigitalSink.empty())
        self.io2 = self.Port(DigitalBidir.empty())
        self.io8 = self.Port(DigitalBidir.empty())
        self.io9 = self.Port(DigitalBidir.empty())
        self.uart0 = self.Port(UartPort(DigitalBidir.empty()), optional=True)

        self.generator_param(self.pin_assigns)
        self._generator_param_all_ios()

    @override
    def generate(self) -> None:
        super().generate()

        self.footprint(
            "U",
            "RF_Module:ESP-WROOM-02",
            self._make_pinning(
                {
                    "1": self.v3v3,
                    "9": self.gnd,
                    "19": self.gnd,  # EP
                    "2": self.en,
                    "16": self.io2,
                    "7": self.io8,
                    "8": self.io9,
                    "11": self.uart0.rx,
                    "12": self.uart0.tx,
                },
                self._PIN_REMAPPING,
            ),
            mfr="Espressif Systems",
            part="ESP32-C3-WROOM-02",
            datasheet="https://www.espressif.com/sites/default/files/documentation/esp32-c3-wroom-02_datasheet_en.pdf",
        )
        self.assign(self.lcsc_part, "C2934560")
        self.assign(self.actual_basic_part, False)


class Esp32c3_Wroom02_Device(
    Esp32c3_Interfaces,
    BaseIoControllerWrapper,
    InternalSubcircuit,
    GeneratorBlock,
    WrapperSubboardBlock,
):

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.model = self.Block(
            Esp32c3_Device(
                pin_assigns=ArrayStringExpr(),
                _model=True,
                _allowed_pins=list(Esp32c3_Wroom02_Footprint._PIN_REMAPPING.keys()),
            )
        )
        self.gnd = self.Export(self.model.gnd, [Common])
        self.v3v3 = self.Export(self.model.vdd3p3, [Power])
        self.connect(self.v3v3, self.model.vdda, self.model.vdd3p3_rtc, self.model.vdd3p3_cpu, self.model.vdd_spi)
        self.en = self.Export(self.model.en)
        self.io2 = self.Export(self.model.io2)
        self.io8 = self.Export(self.model.io8)
        self.io9 = self.Export(self.model.io9, optional=True)
        self.uart0 = self.Export(self.model.uart0, optional=True)
        self.generator_param(self.pin_assigns)
        self._generator_param_all_ios()

    @override
    def generate(self) -> None:
        super().generate()

        self._export_ios_inner(self.model)
        self.assign(
            self.model.pin_assigns,
            self._make_model_pinning(Esp32c3_Wroom02_Footprint._PIN_REMAPPING, self.get(self.pin_assigns)),
        )

        self.device = self.Block(Esp32c3_Wroom02_Footprint(pin_assigns=self.model.actual_pin_assigns), external=True)
        self.assign(self.actual_pin_assigns, self.device.actual_pin_assigns)
        self._export_tap_ios_inner(self.device)
        self.export_tap(self.gnd, self.device.gnd)
        self.export_tap(self.v3v3, self.device.v3v3)
        self.export_tap(self.en, self.device.en)
        self.export_tap(self.io2, self.device.io2)
        self.export_tap(self.io8, self.device.io8)
        self.export_tap(self.io9, self.device.io9)
        self.export_tap(self.uart0, self.device.uart0)


class Esp32c3_Wroom02(
    Microcontroller,
    Radiofrequency,
    HasEspProgramming,
    Resettable,
    Esp32c3_Interfaces,
    IoControllerPowerRequired,
    GeneratorBlock,
):
    """Wrapper around Esp32c3_Wroom02 with external capacitors and UART programming header."""

    def __init__(self) -> None:
        super().__init__()
        self.ic: Esp32c3_Wroom02_Device
        self.generator_param(self.reset.is_connected(), self.pin_assigns, self.gpio.requested())

        self.io2_ext_connected: bool = False
        self.io8_ext_connected: bool = False

    @override
    def generate(self) -> None:
        super().generate()

        with self.implicit_connect(ImplicitConnect(self.pwr, [Power]), ImplicitConnect(self.gnd, [Common])) as imp:
            self.ic = imp.Block(Esp32c3_Wroom02_Device(pin_assigns=ArrayStringExpr()))

            def gpio_transform(self_io: BasePort, assign: Optional[str]) -> Optional[BasePort]:
                if assign == "_GPIO2_STRAP_EXT_PU":
                    self.connect(self_io, self.ic.io2)
                    self._io2_ext_connected = True
                    return None
                elif assign == "_GPIO8_STRAP_EXT_PU":
                    self.connect(self_io, self.ic.io8)
                    self._io8_ext_connected = True
                    return None
                elif assign == "_GPIO9_STRAP":
                    self.connect(self_io, self.ic.io9)
                    return None
                return self_io

            self._wrap_inner(self.ic, transforms={DigitalBidir: gpio_transform})

            self.connect(self.program_uart_node, self.ic.uart0)
            self.connect(self.program_en_node, self.ic.en)
            self.connect(self.program_boot_node, self.ic.io9)

            self.vcc_cap0 = imp.Block(DecouplingCapacitor(10 * uFarad(tol=0.2)))  # C1
            self.vcc_cap1 = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))  # C2

        if self.get(self.reset.is_connected()):
            self.connect(self.reset, self.ic.en)
        else:
            self.en_pull = self.Block(PullupDelayRc(10 * kOhm(tol=0.05), 10 * mSecond(tol=0.2))).connected(
                gnd=self.gnd, pwr=self.pwr, io=self.ic.en
            )

        # Note strapping pins (section 3.3) IO2, 8, 9; IO9 is internally pulled up
        # IO9 (internally pulled up) is 1 for SPI boot and 0 for download boot
        # IO2 must be 1 for both SPI and download boot, while IO8 must be 1 for download boot
        if not self.io8_ext_connected:
            self.connect(self.ic.io8, self.pwr.as_digital_source())
            self.io8_ext_connected = True  # set to ensure this runs after external connections
        if not self.io2_ext_connected:
            self.connect(self.ic.io2, self.pwr.as_digital_source())
            self.io2_ext_connected = True  # set to ensure this runs after external connections


class Xiao_Esp32c3_Device(Esp32c3_Interfaces, BaseIoControllerWrapped, GeneratorBlock, FootprintBlock):

    _PIN_REMAPPING = {
        # 'GPIO2': '1',  # boot pin, non-allocatable
        "GPIO3": "2",
        "MTMS": "3",
        "MTDI": "4",
        "MTCK": "5",
        "MTDO": "6",
        # 'GPIO21': '7',  # boot pin, non-allocatable
        # 'GPIO20': '8',  # boot pin, non-allocatable
        # 'GPIO8': '9',  # boot pin, non-allocatable
        # 'GPIO9': '10',  # boot pin, non-allocatable
        "GPIO10": "11",
    }

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.gnd = self.Port(Ground.empty(), optional=True)
        self.v3v3 = self.Port(Passive.empty(), optional=True)
        self.vusb = self.Port(Passive.empty(), optional=True)  # VUsb
        self.cam_sccb = self.Port(I2cController.empty(), optional=True)  # internally connected to camera
        self.generator_param(self.pin_assigns)
        self._generator_param_all_ios()

    @override
    def generate(self) -> None:
        super().generate()

        self.footprint(
            "U",
            "Seeed Studio XIAO Series Library:XIAO-ESP32C3-SMD",
            self._make_pinning(
                {"13": self.gnd, "12": self.v3v3, "14": self.vusb},
                self._PIN_REMAPPING,
            ),
            mfr="",
            part="XIAO ESP32C3",
            datasheet="https://www.seeedstudio.com/Seeed-XIAO-ESP32C3-p-5431.html",
        )


class Xiao_Esp32c3(
    IoControllerUsbOut,
    IoControllerPowerOut,
    Esp32c3_Interfaces,
    IoController,
    BaseIoControllerWrapper,
    GeneratorBlock,
    WrapperSubboardBlock,
):
    """ESP32-C3 development board, a tiny development (21x17.5mm) daughterboard with a RISC-V microcontroller
    supporting WiFi and BLE. Has an onboard USB connector, so this can also source power.

    Limited pins (only 11 for IOs, of which 6 are usable as the other 5 have boot requirements).

    Requires Seeed Studio's KiCad library for the footprint: https://github.com/Seeed-Studio/OPL_Kicad_Library
    The 'Seeed Studio XIAO Series Library' must have been added as a footprint library of the same name.

    Pinning data: https://www.seeedstudio.com/blog/wp-content/uploads/2022/08/Seeed-Studio-XIAO-Series-Package-and-PCB-Design.pdf
    """

    @override
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.vusb_out.init_from(
            VoltageSource(voltage_out=UsbConnector.USB2_VOLTAGE_RANGE, current_limits=UsbConnector.USB2_CURRENT_LIMITS)
        )

        self.generator_param(
            self.gnd.is_connected(),
            self.pwr.is_connected(),
            self.pwr_out.is_connected(),
            self.vusb_out.is_connected(),
            self.pin_assigns,
        )
        self._generator_param_all_ios()

    @override
    def generate(self) -> None:
        super().generate()

        self.model = self.Block(
            Esp32c3_Device(
                pin_assigns=self._make_model_pinning(Xiao_Esp32c3_Device._PIN_REMAPPING, self.get(self.pin_assigns)),
                _model=True,
                _allowed_pins=list(Xiao_Esp32c3_Device._PIN_REMAPPING.keys()),
            )
        )
        self._export_ios_inner(self.model)

        self.device = self.Block(Xiao_Esp32c3_Device(pin_assigns=self.model.actual_pin_assigns), external=True)
        self._export_tap_ios_inner(self.device)
        self.assign(self.actual_pin_assigns, self.device.actual_pin_assigns)

        if self.get(self.gnd.is_connected()):
            self.connect(self.gnd, self.model.gnd)
            self.export_tap(self.gnd, self.device.gnd)
        else:
            self.gnd_model = self.Block(DummyGround())
            self.connect(self.gnd_model.gnd, self.model.gnd)

        self.connect(
            self.model.vdda, self.model.vdd3p3, self.model.vdd3p3_rtc, self.model.vdd3p3_cpu, self.model.vdd_spi
        )
        if self.get(self.pwr.is_connected()):  # power supplied externally
            self.connect(self.pwr, self.model.vdd3p3)
            self.export_tap(self.pwr.net, self.device.v3v3)
        else:  # board sources power from USB
            self.pwr_out_model = self.Block(
                DummyVoltageSource(
                    voltage_out=3.3 * Volt(tol=0.05),  # tolerance is a guess
                    current_limits=UsbConnector.USB2_CURRENT_LIMITS,
                )
            )
            self.connect(self.pwr_out_model.pwr, self.model.vdd3p3)
            if self.get(self.pwr_out.is_connected()):
                self.connect(self.pwr_out, self.pwr_out_model.pwr)
            self.export_tap(self.pwr_out.net, self.device.v3v3)

        if self.get(self.vusb_out.is_connected()):
            self.export_tap(self.vusb_out.net, self.device.vusb)
