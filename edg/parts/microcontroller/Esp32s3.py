from typing import *

from typing_extensions import override

from ...circuits import *
from ...vendor_parts.jlc.JlcPart import JlcPart
from .EspCommon import HasEspProgramming


@non_library
class Esp32s3_Interfaces(
    IoControllerSpiPeripheral,
    IoControllerI2cTarget,
    IoControllerTouchDriver,
    IoControllerCan,
    IoControllerUsb,
    IoControllerI2s,
    IoControllerDvp8,
    IoControllerWifi,
    IoControllerBle,
    BaseIoController,
):
    """Defines base interfaces for ESP32S3 microcontrollers"""


class Esp32s3_Wroom_1_Device(
    Esp32s3_Interfaces, BaseIoControllerPinmapGenerator, InternalSubcircuit, FootprintBlock, JlcPart
):
    _PIN_MAPPING = {
        "GPIO4": "4",
        "GPIO5": "5",
        "GPIO6": "6",
        "GPIO7": "7",
        "XTAL_32K_P": "8",  # GPIO15
        "XTAL_32K_N": "9",  # GPIO16
        "GPIO17": "10",
        "GPIO18": "11",
        "GPIO8": "12",
        "GPIO19": "13",
        "GPIO20": "14",
        "GPIO3": "15",
        # 'GPIO46': '16',  # strapping pin
        "GPIO9": "17",
        "GPIO10": "18",
        "GPIO11": "19",
        "GPIO12": "20",
        "GPIO13": "21",
        "GPIO14": "22",
        "GPIO21": "23",
        "SPICLK_P": "24",  # GPIO47
        "SPICLK_N": "25",  # GPIO48
        # 'GPIO45': '26',  # strapping pin
        # 'GPIO35': '28',  # not available on PSRAM variants
        # 'GPIO36': '29',  # not available on PSRAM variants
        # 'GPIO37': '30',  # not available on PSRAM variants
        "GPIO38": "31",
        "MTCK": "32",  # GPIO39
        "MTDO": "33",  # GPIO40
        "MTDI": "34",  # GPIO41
        "MTMS": "35",  # GPIO42
        "GPIO2": "38",
        "GPIO1": "39",
    }

    def __init__(self, _model: BoolLike = False, _allowed_pins: ArrayStringLike = [], **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self._model = self.ArgParameter(_model)
        self._allowed_pins = self.ArgParameter(_allowed_pins)
        self.generator_param(self._allowed_pins)

        self.pwr = self.Port(
            VoltageSink(  # assumes single-rail module
                voltage_limits=(3.0, 3.6) * Volt,  # table 4-2
                current_draw=(0.001, 355) * mAmp
                + self.io_current_draw.upper(),  # from power off (table 4-8) to RF working (table 12 on WROOM datasheet)
            ),
            [Power],
        )
        self.gnd = self.Port(Ground(), [Common])

        self._dio_model = DigitalBidir.from_supply(  # table 4-4
            self.gnd,
            self.pwr,
            voltage_limit_tolerance=(-0.3, 0.3) * Volt,
            current_limits=(-28, 40) * mAmp,
            input_threshold_factor=(0.25, 0.75),
            pullup_capable=True,
            pulldown_capable=True,
        )

        self.chip_pu = self.Port(self._dio_model, optional=True)
        self.require((~self._model).implies(self.chip_pu.is_connected()), "chip_pu must not be left floating")
        self.io0 = self.Port(
            self._dio_model, optional=True
        )  # table 2-11, default pullup (SPI boot), set low to download boot
        self.uart0 = self.Port(UartPort(self._dio_model), optional=True)  # programming

    @override
    def generate(self) -> None:
        super().generate()

        self.assign(self.lcsc_part, "C2913202")  # note standard only assembly
        self.assign(self.actual_basic_part, False)
        self.footprint(
            "U",
            "RF_Module:ESP32-S3-WROOM-1",
            self._make_pinning(),
            mfr="Espressif Systems",
            part="ESP32-S3-WROOM-1-N16R8",  # higher end variant
            datasheet="https://www.espressif.com/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf",
        )

    @override
    def _system_pinmap(self) -> Dict[str, Union[Passive, HasPassivePort]]:
        return {
            "2": self.pwr,  # including VDD3V3, VDD3P3_RTC, VDD_SPI, VDD3P3_CPU
            "1": self.gnd,
            "40": self.gnd,
            "41": self.gnd,  # EP
            "3": self.chip_pu,
            "27": self.io0,
            "36": self.uart0.rx,
            "37": self.uart0.tx,
        }

    @override
    def _io_pinmap(self) -> PinMapUtil:
        adc_model = AnalogSink.from_supply(
            self.gnd,
            self.pwr,
            signal_limit_abs=(0, 2.9) * Volt,  # table 4-5, effective ADC range at max attenuation
            # TODO: impedance / leakage - not specified by datasheet
        )

        uart_model = UartPort(DigitalBidir.empty())  # section 3.5.5, up to 5Mbps
        spi_model = SpiController(
            DigitalBidir.empty(), (0, 80) * MHertz
        )  # section 3.5.2, 80MHz in controller, 60MHz in peripheral
        spi_peripheral_model = SpiPeripheral(DigitalBidir.empty(), (0, 80) * MHertz)
        i2c_model = I2cController(DigitalBidir.empty())  # section 3.5.6, 100/400kHz and up to 800kbit/s
        i2c_target_model = I2cController(DigitalBidir.empty())
        touch_model = TouchDriver()
        can_model = CanControllerPort(DigitalBidir.empty())  # aka TWAI, up to 1Mbit/s
        i2s_model = I2sController(DigitalBidir.empty())
        dvp8_model = Dvp8Host(DigitalBidir.empty())

        return (
            PinMapUtil(
                [  # table 2-1 for overview, table 3-3 for remapping, table 2-4 for ADC
                    # VDD3P3_RTC domain
                    # PinResource('GPIO0', {'GPIO0': self._dio_model}),  # strapping pin, boot mode
                    PinResource("GPIO1", {"GPIO1": self._dio_model, "ADC1_CH0": adc_model, "TOUCH1": touch_model}),
                    PinResource("GPIO2", {"GPIO2": self._dio_model, "ADC1_CH1": adc_model, "TOUCH2": touch_model}),
                    # technically a strapping pin for JTAG control, but needs to be enabled by eFuse
                    PinResource("GPIO3", {"GPIO3": self._dio_model, "ADC1_CH2": adc_model, "TOUCH3": touch_model}),
                    PinResource("GPIO4", {"GPIO4": self._dio_model, "ADC1_CH3": adc_model, "TOUCH4": touch_model}),
                    PinResource("GPIO5", {"GPIO5": self._dio_model, "ADC1_CH4": adc_model, "TOUCH5": touch_model}),
                    PinResource("GPIO6", {"GPIO6": self._dio_model, "ADC1_CH5": adc_model, "TOUCH6": touch_model}),
                    PinResource("GPIO7", {"GPIO7": self._dio_model, "ADC1_CH6": adc_model, "TOUCH7": touch_model}),
                    PinResource("GPIO8", {"GPIO8": self._dio_model, "ADC1_CH7": adc_model, "TOUCH8": touch_model}),
                    PinResource("GPIO9", {"GPIO9": self._dio_model, "ADC1_CH8": adc_model, "TOUCH9": touch_model}),
                    PinResource("GPIO10", {"GPIO10": self._dio_model, "ADC1_CH9": adc_model, "TOUCH10": touch_model}),
                    # ADC2 pins can't be used simultaneously with WiFi (section 2.3.3) and are not allocatable
                    PinResource("GPIO11", {"GPIO11": self._dio_model, "TOUCH11": touch_model}),  # also ADC2_CH0
                    PinResource("GPIO12", {"GPIO12": self._dio_model, "TOUCH12": touch_model}),  # also ADC2_CH1
                    PinResource("GPIO13", {"GPIO13": self._dio_model, "TOUCH13": touch_model}),  # also ADC2_CH2
                    PinResource("GPIO14", {"GPIO14": self._dio_model, "TOUCH14": touch_model}),  # also ADC2_CH3
                    PinResource("XTAL_32K_P", {"GPIO15": self._dio_model}),  # also ADC2_CH4
                    PinResource("XTAL_32K_N", {"GPIO16": self._dio_model}),  # also ADC2_CH5
                    PinResource("GPIO17", {"GPIO17": self._dio_model}),  # also ADC2_CH6
                    PinResource("GPIO18", {"GPIO18": self._dio_model}),  # also ADC2_CH7
                    PinResource("GPIO19", {"GPIO19": self._dio_model}),  # also ADC2_CH8 / USB_D-
                    PinResource("GPIO20", {"GPIO20": self._dio_model}),  # also ADC2_CH9 / USB_D+
                    PinResource("GPIO21", {"GPIO21": self._dio_model}),
                    # VDD_SPI domain
                    # section 2.3.3, these are allocated for flash and should not be used
                    # PinResource('SPICS1', {'GPIO26': self._dio_model}),
                    # PinResource('SPIHD', {'GPIO27': self._dio_model}),
                    # PinResource('SPIWP', {'GPIO28': self._dio_model}),
                    # PinResource('SPICS0', {'GPIO29': self._dio_model}),
                    # PinResource('SPICLK', {'GPIO30': self._dio_model}),
                    # PinResource('SPIQ', {'GPIO31': self._dio_model}),
                    # PinResource('SPID', {'GPIO32': self._dio_model}),
                    # VDD_SPI / VDD3P3_CPU domain
                    PinResource("SPICLK_N", {"GPIO48": self._dio_model}),  # appendix A
                    PinResource("SPICLK_P", {"GPIO47": self._dio_model}),  # appendix A
                    # these may be allocated for PSRAM and should not be used
                    # PinResource('GPIO33', {'GPIO33': self._dio_model}),
                    # PinResource('GPIO34', {'GPIO34': self._dio_model}),
                    # PinResource('GPIO35', {'GPIO35': self._dio_model}),
                    # PinResource('GPIO36', {'GPIO36': self._dio_model}),
                    # PinResource('GPIO37', {'GPIO37': self._dio_model}),
                    # VDD3P3_CPU domain
                    PinResource("GPIO38", {"GPIO38": self._dio_model}),
                    PinResource("MTCK", {"GPIO39": self._dio_model}),
                    PinResource("MTDO", {"GPIO40": self._dio_model}),
                    PinResource("MTDI", {"GPIO41": self._dio_model}),
                    PinResource("MTMS", {"GPIO42": self._dio_model}),
                    # PinResource('U0TXD', {'GPIO43': self._dio_model}),  # for programming
                    # PinResource('U0RXD', {'GPIO44': self._dio_model}),  # for programming
                    # PeripheralFixedResource('U0', uart_model, {
                    #   'tx': ['GPIO43'], 'rx': ['GPIO44']
                    # }),
                    # PinResource('GPIO45', {'GPIO45': self._dio_model}),  # strapping pin, VDD_SPI power source
                    # PinResource('GPIO46', {'GPIO46': self._dio_model}),  # strapping pin, boot mode, keep low
                    PeripheralAnyResource("U1", uart_model),
                    PeripheralAnyResource("U2", uart_model),
                    PeripheralAnyResource("I2CEXT0", i2c_model),
                    PeripheralAnyResource("I2CEXT1", i2c_model),
                    PeripheralAnyResource("I2CEXT0_T", i2c_target_model),  # TODO shared resource w/ I2C controller
                    PeripheralAnyResource("I2CEXT1_T", i2c_target_model),  # TODO shared resource w/ I2C controller
                    # SPI0/1 may be used for (possibly on-chip) flash / PSRAM
                    PeripheralAnyResource("SPI2", spi_model),
                    PeripheralAnyResource("SPI3", spi_model),
                    PeripheralAnyResource("SPI2_P", spi_peripheral_model),  # TODO shared resource w/ SPI controller
                    PeripheralAnyResource("SPI3_P", spi_peripheral_model),  # TODO shared resource w/ SPI controller
                    PeripheralAnyResource("TWAI", can_model),
                    PeripheralAnyResource("I2S0", i2s_model),
                    PeripheralAnyResource("I2S1", i2s_model),
                    PeripheralAnyResource(
                        "DVP", dvp8_model
                    ),  # TODO this also eats an I2S port, also available as 16-bit
                    PeripheralFixedResource("USB", UsbDevicePort.empty(), {"dp": ["GPIO20"], "dm": ["GPIO19"]}),
                ]
            )
            .remap_pins(self._PIN_MAPPING)
            .filter_pins(self.get(self._allowed_pins))
        )


class Esp32s3_Wroom_1(
    Microcontroller,
    Radiofrequency,
    HasEspProgramming,
    Resettable,
    Esp32s3_Interfaces,
    IoControllerPowerRequired,
    GeneratorBlock,
):
    """ESP32-S3-WROOM-1 module"""

    def __init__(self) -> None:
        super().__init__()
        self.generator_param(self.reset.is_connected(), self.pin_assigns, self.gpio.requested())

    @override
    def generate(self) -> None:
        super().generate()

        def gpio_transform(self_io: BasePort, assign: Optional[str]) -> Optional[BasePort]:
            if assign == "_GPIO0_STRAP":
                self.connect(self_io, self.ic.io0)
                return None
            return self_io

        with self.implicit_connect(ImplicitConnect(self.pwr, [Power]), ImplicitConnect(self.gnd, [Common])) as imp:
            self.ic = imp.Block(Esp32s3_Wroom_1_Device(pin_assigns=ArrayStringExpr()))
            self._wrap_inner(self.ic, {DigitalBidir: gpio_transform})
            self.connect(self.program_uart_node, self.ic.uart0)
            self.connect(self.program_en_node, self.ic.chip_pu)
            self.connect(self.program_boot_node, self.ic.io0)

            self.vcc_cap0 = imp.Block(DecouplingCapacitor(22 * uFarad(tol=0.2)))  # C1
            self.vcc_cap1 = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))  # C2

        if self.get(self.reset.is_connected()):
            self.connect(self.reset, self.ic.chip_pu)
        else:
            self.en_pull = self.Block(PullupDelayRc(10 * kOhm(tol=0.05), 10 * mSecond(tol=0.2))).connected(
                gnd=self.gnd, pwr=self.pwr, io=self.ic.chip_pu
            )


class Freenove_Esp32s3_Wrover_Device(Esp32s3_Interfaces, BaseIoControllerWrapped, GeneratorBlock, FootprintBlock):
    _PIN_REMAPPING = {
        # 'GPIO4': '3',  # CAM_SIOD
        # 'GPIO5': '4',  # CAM_SIOC
        # 'GPIO6': '5',  # CAM_VYSNC
        # 'GPIO7': '6',  # CAM_HREF
        # 'GPIO15': '7',  # CAM_XCLK
        # 'GPIO16': '8',  # CAM_Y9
        # 'GPIO17': '9',  # CAM_Y8
        # 'GPIO18': '10',  # CAM_Y7
        # 'GPIO8': '11',  # CAM_Y4
        "GPIO3": "12",
        # 'GPIO46': '13',  # strapping pin, boot mode
        # 'GPIO9': '14',  # CAM_Y3
        # 'GPIO10': '15',  # CAM_Y5
        # 'GPIO11': '16',  # CAM_Y2
        # 'GPIO12': '17',  # CAM_Y6
        # 'GPIO13': '18',  # CAM_PCLK
        "GPIO14": "19",
        # 'GPIO19': '22',  # USB_D+
        # 'GPIO20': '23',  # USB_D-
        "GPIO21": "24",
        "SPICLK_P": "25",  # GPIO47
        "SPICLK_N": "26",  # GPIO48, internal WS2812
        # 'GPIO45': '27',  # strapping pin, VDD_SPI
        # 'GPIO35': '29',  # PSRAM
        # 'GPIO36': '30',  # PSRAM
        # 'GPIO37': '31',  # PSRAM
        # 'GPIO38': '32',  # SD_CMD
        # 'GPIO39': '33',  # SD_CLK
        # 'GPIO40': '34',  # SD_DATA
        "MTDI": "35",  # GPIO41
        "MTMS": "36",  # GPIO42
        "GPIO2": "37",  # internal LED
        "GPIO1": "38",
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
            "edg:Freenove_ESP32-WROVER",
            self._make_pinning(
                {
                    "1": self.v3v3,
                    "21": self.gnd,
                    "20": self.vusb,
                    "3": self.cam_sccb.sda,
                    "4": self.cam_sccb.scl,
                },
                self._PIN_REMAPPING,
            ),
            mfr="",
            part="Freenove ESP32S3-WROOM",
        )


class Freenove_Esp32s3_Wroom(
    IoControllerUsbOut,
    IoControllerPowerOut,
    Esp32s3_Interfaces,
    IoController,
    BaseIoControllerWrapper,
    GeneratorBlock,
    WrapperSubboardBlock,
):
    """Freenove ESP32S3 WROOM breakout with camera.

    Board pinning: https://github.com/Freenove/Freenove_ESP32_S3_WROOM_Board/blob/main/ESP32S3_Pinout.png

    Top left is pin 1, going down the left side then up the right side.
    Up is defined from the text orientation (antenna is on top).
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
            Esp32s3_Wroom_1_Device(
                pin_assigns=self._make_model_pinning(
                    Freenove_Esp32s3_Wrover_Device._PIN_REMAPPING, self.get(self.pin_assigns)
                ),
                _model=True,
                _allowed_pins=list(Freenove_Esp32s3_Wrover_Device._PIN_REMAPPING.keys()),
            )
        )
        self._export_ios_inner(self.model)

        self.device = self.Block(
            Freenove_Esp32s3_Wrover_Device(pin_assigns=self.model.actual_pin_assigns), external=True
        )
        self._export_tap_ios_inner(self.device)
        self.assign(self.actual_pin_assigns, self.device.actual_pin_assigns)

        if self.get(self.gnd.is_connected()):
            self.connect(self.gnd, self.model.gnd)
            self.export_tap(self.gnd, self.device.gnd)
        else:
            self.gnd_model = self.Block(DummyGround())
            self.connect(self.gnd_model.gnd, self.model.gnd)

        if self.get(self.pwr.is_connected()):  # power supplied externally
            self.connect(self.pwr, self.model.pwr)
            self.export_tap(self.pwr.net, self.device.v3v3)
        else:  # board sources power from USB
            self.pwr_out_model = self.Block(
                DummyVoltageSource(
                    voltage_out=3.3 * Volt(tol=0.05),  # tolerance is a guess
                    current_limits=UsbConnector.USB2_CURRENT_LIMITS,
                )
            )
            self.connect(self.pwr_out_model.pwr, self.model.pwr)
            if self.get(self.pwr_out.is_connected()):
                self.connect(self.pwr_out, self.pwr_out_model.pwr)
            self.export_tap(self.pwr_out.net, self.device.v3v3)

        if self.get(self.vusb_out.is_connected()):
            self.export_tap(self.vusb_out.net, self.device.vusb)
