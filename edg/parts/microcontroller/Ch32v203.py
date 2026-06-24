from typing import *

from typing_extensions import override

from ...circuits import *
from ...vendor_parts.jlc.JlcPart import JlcPart
from ..connector.Headers import PinHeader254
from ..connector.TagConnect import TagConnect


@abstract_block_default(lambda: Ch32vSdi2Header254)
class Ch32vSdi2Header(ProgrammingConnector):
    """Abstract programming header for the CH32V using the two-pin SDI interface."""

    def __init__(self) -> None:
        super().__init__()

        self.pwr = self.Port(VoltageSink.empty(), [Power])
        self.gnd = self.Port(Ground.empty(), [Common])
        self.swclk = self.Port(DigitalBidir.empty())  # despite similar naming, this is not ARM SWD
        self.swdio = self.Port(DigitalBidir.empty())
        self.reset = self.Port(DigitalBidir.empty(), optional=True)  # may not be connected internally


class Ch32vSdi2Header254(Ch32vSdi2Header):
    """4-pin minimal programming header for CH32V."""

    @override
    def contents(self) -> None:
        super().contents()

        self.gnd.init_from(Ground())
        self.pwr.init_from(VoltageSink())
        self.swclk.init_from(DigitalBidir())
        self.swdio.init_from(DigitalBidir())
        self.reset.init_from(DigitalBidir())  # not connected

        self.conn = self.Block(PinHeader254(4)).connected(
            {"1": self.pwr, "2": self.gnd, "3": self.swdio, "4": self.swclk}
        )


class Ch32vSdi2Tc2030(Ch32vSdi2Header):
    """UNOFFICIAL tag connect header, based on the SWD pinout."""

    @override
    def contents(self) -> None:
        super().contents()

        self.gnd.init_from(Ground())
        self.pwr.init_from(VoltageSink())
        self.swclk.init_from(DigitalBidir())
        self.swdio.init_from(DigitalBidir())
        self.reset.init_from(DigitalBidir())

        self.conn = self.Block(TagConnect(6)).connected(
            {"1": self.pwr, "5": self.gnd, "2": self.swdio, "4": self.swclk, "3": self.reset}
        )
        # unused: 6 = swo


class Ch32v203_Device(
    IoControllerI2cTarget,
    IoControllerUsb,
    IoControllerCan,
    InternalSubcircuit,
    BaseIoControllerPinmapGenerator,
    GeneratorBlock,
    JlcPart,
    FootprintBlock,
):
    _PIN_MAPPING = {  # -K6/K8 version, LQFP-32 package
        # "PD0": "2",  # OSCI
        # "PD1": "3",  # OSCO
        "PA0-WKUP": "6",
        "PA1": "7",
        "PA2": "8",
        "PA3": "9",
        "PA4": "10",
        "PA5": "11",
        "PA6": "12",
        "PA7": "13",
        "PB0": "14",
        "PB1": "15",
        "PA8": "18",
        "PA9": "19",
        "PA10": "20",
        "PA11": "21",
        "PA12": "22",
        # "PA13": "23",  # SWDIO
        # "PA14": "24",  # SWCLK
        "PA15": "25",
        "PB3": "26",
        "PB4": "27",
        "PB5": "28",
        "PB6": "29",
        "PB7": "30",
        # "PB8": "31",  # BOOT0
    }

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # Additional ports (on top of BaseIoController)
        self.vdd = self.Port(
            VoltageSink(
                voltage_limits=(3.0, 3.6) * Volt,  # stricter range when USB used, otherwise down to 2.7
                current_draw=(0.0005, 23.37) * mAmp + self.io_current_draw.upper(),  # standby min to 144MHz run max
            ),
            [Power],
        )
        self.vss = self.Port(Ground(), [Common])

        self.nrst = self.Port(  # Table 3-19
            DigitalSink.from_supply(
                self.vss,
                self.vdd,
                voltage_limit_tolerance=(-0.3, 0.3) * Volt,
                input_threshold_abs=(
                    0.28 * (self.vdd.link().voltage.lower() - 1.8) + 0.6 + self.vss.link().voltage.lower(),
                    0.41 * (self.vdd.link().voltage.upper() - 1.8) + 1.3 + self.vss.link().voltage.upper(),
                ),
                pullup_capable=True,
            ),
            optional=True,
        )  # note, switched internal pull-up resistor, 30-50 kOhm

        self.osc = self.Port(
            CrystalDriver(frequency_limits=(3, 25) * MHertz, voltage_out=self.vdd.link().voltage), optional=True
        )  # Table 4-11 crystal / resonator specs, typ 8 MHz

        self._dio_ft_model = DigitalBidir.from_supply(
            self.vss,
            self.vdd,
            voltage_limit_abs=(-0.3, 5.5) * Volt,  # table 4-1
            current_limits=(-20, 20) * mAmp,  # 4.3.10 output drive current characteristics
            input_threshold_abs=(  # table 3-16
                0.32 * (self.vdd.link().voltage.lower() - 1.8) + 0.55 + self.vss.link().voltage.lower(),
                0.42 * (self.vdd.link().voltage.upper() - 1.8) + 1.3 + self.vss.link().voltage.upper(),
            ),
            pullup_capable=True,  # 30-50 kOhm
            pulldown_capable=True,  # 30-50 kOhm
        )
        self._dio_std_model = DigitalBidir.from_supply(
            self.vss,
            self.vdd,
            voltage_limit_tolerance=(-0.3, 0.3) * Volt,  # table 4-1
            current_limits=(-20, 20) * mAmp,  # 4.3.10 output drive current characteristics
            input_threshold_abs=(  # table 3-16
                0.28 * (self.vdd.link().voltage.lower() - 1.8) + 0.6 + self.vss.link().voltage.lower(),
                0.42 * (self.vdd.link().voltage.upper() - 1.8) + 1 + self.vss.link().voltage.upper(),
            ),
            pullup_capable=True,  # 30-50 kOhm
            pulldown_capable=True,  # 30-50 kOhm
        )

        self.swdio = self.Port(self._dio_ft_model)
        self.swclk = self.Port(self._dio_ft_model)

    @override
    def _system_pinmap(self) -> Mapping[Union[Iterable[str], str], Union[Passive, HasPassivePort]]:
        return {
            ("16", "32"): self.vss,
            "5": self.vdd,  # VddA
            ("17", "1"): self.vdd,
            "2": self.osc.xtal_in,  # TODO remappable to PD0
            "3": self.osc.xtal_out,  # TODO remappable to PD1
            "4": self.nrst,
            "23": self.swdio,  # TODO remappable to PA13
            "24": self.swclk,  # TODO remappable to PA14
            "31": self.vss,  # BOOT0, TODO theoretically usable as output-only PB8
        }

    @override
    def _io_pinmap(self) -> PinMapUtil:
        # Port models
        adc_model = AnalogSink.from_supply(
            self.vss,
            self.vdd,
            voltage_limit_tolerance=(-0.3, 0.3) * Volt,  # table 4-1
            signal_limit_tolerance=(0, 0) * Volt,  # table 4-27 conversion range, up to Vref+ up to VddA
            # impedance depends on sampling rate
        )

        uart_model = UartPort(DigitalBidir.empty())
        spi_model = SpiController(DigitalBidir.empty())
        # TODO SPI peripherals, which have fixed-pin CS lines
        i2c_model = I2cController(DigitalBidir.empty())
        i2c_target_model = I2cTarget(DigitalBidir.empty())

        return PinMapUtil(
            [  # table 2-1
                PinResource("PC13-TAMPER-RTC", {"PC13": self._dio_std_model}),
                PinResource("PC14-OSC32_IN", {"PC14": self._dio_std_model}),
                PinResource("PC15-OSC32_OUT", {"PC15": self._dio_std_model}),
                PinResource("OSC_IN", {"PD0": self._dio_std_model}),
                PinResource("OSC_OUT", {"PD1": self._dio_std_model}),
                PinResource("PA0-WKUP", {"PA0": self._dio_std_model, "ADC_IN0": adc_model}),
                PinResource("PA1", {"PA1": self._dio_std_model, "ADC_IN1": adc_model}),
                PinResource("PA2", {"PA2": self._dio_std_model, "ADC_IN2": adc_model}),
                PinResource("PA3", {"PA3": self._dio_std_model, "ADC_IN3": adc_model}),
                PinResource("PA4", {"PA4": self._dio_std_model, "ADC_IN4": adc_model}),
                PinResource("PA5", {"PA5": self._dio_std_model, "ADC_IN5": adc_model}),
                PinResource("PA6", {"PA6": self._dio_std_model, "ADC_IN6": adc_model}),
                PinResource("PA7", {"PA7": self._dio_std_model, "ADC_IN7": adc_model}),
                PinResource("PB0", {"PB0": self._dio_std_model, "ADC_IN8": adc_model}),
                PinResource("PB1", {"PB1": self._dio_std_model, "ADC_IN9": adc_model}),
                PinResource("PB2", {"PB2": self._dio_ft_model}),  # BOOT1
                PinResource("PB10", {"PB10": self._dio_ft_model}),
                PinResource("PB11", {"PB11": self._dio_ft_model}),
                PinResource("PB12", {"PB12": self._dio_ft_model}),
                PinResource("PB13", {"PB13": self._dio_ft_model}),
                PinResource("PB14", {"PB14": self._dio_ft_model}),
                PinResource("PB15", {"PB15": self._dio_ft_model}),
                PinResource("PA8", {"PA8": self._dio_ft_model}),
                PinResource("PA9", {"PA9": self._dio_ft_model}),
                PinResource("PA10", {"PA10": self._dio_ft_model}),
                PinResource("PA11", {"PA11": self._dio_ft_model, "USB1DM": Passive()}),
                PinResource(
                    "PA12", {"PA12": self._dio_ft_model, "USB1DP": Passive()}
                ),  # merged w/ SWDIO on some devices
                PinResource("PA13", {"PA13": self._dio_ft_model}),  # SWDIO
                PinResource("PA14", {"PA14": self._dio_ft_model}),  # SWCLK
                PinResource("PA15", {"PA15": self._dio_ft_model}),
                PinResource("PB3", {"PB3": self._dio_ft_model}),
                PinResource("PB4", {"PB4": self._dio_ft_model}),
                PinResource("PB5", {"PB5": self._dio_ft_model}),
                PinResource("PB6", {"PB6": self._dio_ft_model}),
                PinResource("PB7", {"PB7": self._dio_ft_model}),
                PinResource("PB8", {"PB8": self._dio_ft_model}),  # merged w/ BOOT0 on some devices
                PinResource("PB9", {"PB9": self._dio_ft_model}),
                PeripheralFixedResource(
                    "USART1", uart_model, {"tx": ["PA9", "PB6", "PB15", "PA6"], "rx": ["PA10", "PB7", "PA8", "PA7"]}
                ),
                PeripheralFixedResource("USART2", uart_model, {"tx": ["PA2"], "rx": ["PA3"]}),
                # unavailable on K8
                # PeripheralFixedResource("USART3", uart_model, {"tx": ["PB10"], "rx": ["PB11"]}),
                # PeripheralFixedResource("USART4", uart_model, {"tx": ["PB0", "PA5"], "rx": ["PB1", "PB5"]}),
                PeripheralFixedResource("USB", UsbDevicePort(), {"dm": ["PA11"], "dp": ["PA12"]}),
                # PeripheralFixedResource("USBFS", UsbDevicePort(DigitalBidir.empty()), {"dm": ["PB6"], "dp": ["PB7"]}),
                PeripheralFixedResource("I2C1", i2c_model, {"scl": ["PB6", "PB8"], "sda": ["PB7", "PB9"]}),
                PeripheralFixedResource("I2C1_T", i2c_target_model, {"scl": ["PB6", "PB8"], "sda": ["PB7", "PB9"]}),
                # PeripheralFixedResource("I2C2", i2c_model, {"scl": ["PB10"], "sda": ["PB11"]}),
                # PeripheralFixedResource("I2C2_T", i2c_target_model, {"scl": ["PB10"], "sda": ["PB11"]}),
                PeripheralFixedResource(
                    "SPI1", spi_model, {"sck": ["PA5", "PB3"], "miso": ["PA6", "PB4"], "mosi": ["PA7", "PB5"]}
                ),
                # PeripheralFixedResource("SPI2", spi_model, {"sck": ["PB13"], "miso": ["PB14"], "mosi": ["PB15"]}),
                PeripheralFixedResource(
                    "CAN",
                    CanControllerPort(DigitalBidir.empty()),
                    {"rxd": ["PA11", "PB8"], "txd": ["PA12", "PB9"]},
                ),
            ]
        ).remap_pins(self._PIN_MAPPING)

    @override
    def generate(self) -> None:
        super().generate()

        self.footprint(
            "U",
            "Package_QFP:LQFP-32_7x7mm_P0.8mm",
            self._make_pinning(),
            mfr="WCH",
            part="CH32V203K8T6",
            datasheet="https://www.wch-ic.com/downloads/CH32V203DS0_PDF.html",
            pnp_rot=-90,
        )
        self.assign(self.lcsc_part, "C5372188")
        self.assign(self.actual_basic_part, False)


class Ch32v203(
    Resettable,
    IoControllerI2cTarget,
    IoControllerUsb,
    IoControllerCan,
    Microcontroller,
    WithCrystalGenerator,
    IoControllerPowerRequired,
    GeneratorBlock,
):
    """General-purpose RISC-V (RV32IMAC) microcontroller with USB"""

    DEFAULT_CRYSTAL_FREQUENCY = 8 * MHertz(tol=0.005)  # 8 MHz as typical in datasheet

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.generator_param(self.reset.is_connected(), self.usb.requested(), self.can.requested())

    @override
    def generate(self) -> None:
        super().generate()

        with self.implicit_connect(ImplicitConnect(self.pwr, [Power]), ImplicitConnect(self.gnd, [Common])) as imp:
            self.ic = imp.Block(Ch32v203_Device(pin_assigns=ArrayStringExpr()))
            self._wrap_inner(self.ic)

            self.sdi = imp.Block(Ch32vSdi2Header())
            self.connect(self.ic.swclk, self.sdi.swclk)
            self.connect(self.ic.swdio, self.sdi.swdio)
            self.connect(self.ic.nrst, self.sdi.reset)

            self.connect(self.xtal_node, self.ic.osc)

            self.vdd_cap = ElementDict[DecouplingCapacitor]()  # assume one 0.1uF cap per power pair
            for i in range(2):
                self.vdd_cap[i] = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))
            self.vdda_cap = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))

        self.reset_cap = self.Block(DigitalCapacitor(0.1 * uFarad(tol=0.2))).connected(self.gnd, self.ic.nrst)

        if self.get(self.reset.is_connected()):
            self.connect(self.reset, self.ic.nrst)

    @override
    def _crystal_required(self) -> bool:  # crystal needed for CAN or USB b/c tighter freq tolerance
        return (
            len(self.get(self.can.requested())) > 0
            or len(self.get(self.usb.requested())) > 0
            or super()._crystal_required()
        )
