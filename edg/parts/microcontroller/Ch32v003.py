from typing import *

from typing_extensions import override

from ...circuits import *
from ...vendor_parts.jlc.JlcPart import JlcPart
from ..connector.Headers import PinHeader254
from ..connector.TagConnect import TagConnect


@abstract_block_default(lambda: Ch32VSdiHeader254)
class Ch32vSdiHeader(ProgrammingConnector):
    """Abstract programming header for the CH32V using the one-pin SDI interface with SWIO pin.."""

    def __init__(self) -> None:
        super().__init__()

        self.pwr = self.Port(VoltageSink.empty(), [Power])
        self.gnd = self.Port(Ground.empty(), [Common])
        self.swio = self.Port(DigitalBidir.empty())
        self.reset = self.Port(DigitalBidir.empty(), optional=True)  # may not be connected internally


class Ch32VSdiHeader254(Ch32vSdiHeader):
    """3-pin minimal programming header for CH32V."""

    @override
    def contents(self) -> None:
        super().contents()

        self.gnd.init_from(Ground())
        self.pwr.init_from(VoltageSink())
        self.swio.init_from(DigitalBidir())
        self.reset.init_from(DigitalBidir())

        self.conn = self.Block(PinHeader254()).connected({"1": self.pwr, "2": self.gnd, "3": self.swio})


class Ch32VSdiTc2030(Ch32vSdiHeader):
    """UNOFFICIAL tag connect header, based on the SWD pinout and mapping SWDIO to SWIO."""

    @override
    def contents(self) -> None:
        super().contents()

        self.gnd.init_from(Ground())
        self.pwr.init_from(VoltageSink())
        self.swio.init_from(DigitalBidir())
        self.reset.init_from(DigitalBidir())

        self.conn = self.Block(TagConnect(6)).connected({"1": self.pwr, "5": self.gnd, "2": self.swio, "3": self.reset})
        # unused: 4 = swclk, 6 = swo


class Ch32v003_Device(
    IoControllerI2cTarget,
    InternalSubcircuit,
    BaseIoControllerPinmapGenerator,
    GeneratorBlock,
    JlcPart,
    FootprintBlock,
):
    _PIN_MAPPING = {  # F4P6 version, TSSOP-20
        "PD4": "1",
        "PD5": "2",
        "PD6": "3",
        # "PD7": "4",  # NRST
        # "PA1": "5",  # OSCI
        # "PA2": "6",  # OSCO
        "PD0": "8",
        "PC0": "10",
        "PC1": "11",
        "PC2": "12",
        "PC3": "13",
        "PC4": "14",
        "PC5": "15",
        "PC6": "16",
        "PC7": "17",
        # "PD1": "18",  # SWIO
        "PD2": "19",
        "PD3": "20",
    }

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # Additional ports (on top of BaseIoController)
        self.vdd = self.Port(
            VoltageSink(
                voltage_limits=(2.8, 5.5) * Volt,  # stricter range when ADC used
                current_draw=(0.009, 8.0) * mAmp + self.io_current_draw.upper(),  # standby min to 48MHz run max
            ),
            [Power],
        )
        self.vss = self.Port(Ground(), [Common])

        self.nrst = self.Port(  # Table 3-19
            DigitalSink.from_supply(
                self.gnd,
                self.pwr,
                voltage_limit_tolerance=(-0.3, 0.3) * Volt,
                input_threshold_abs=(
                    0.28 * (self.vdd.link().voltage.lower() - 1.8) + 0.6 + self.vss.link().voltage.lower(),
                    0.41 * (self.vdd.link().voltage.upper() - 1.8) + 1.3 + self.vss.link().voltage.upper(),
                ),
                pullup_capable=True,
            ),
            optional=True,
        )  # note, switched internal pull-up resistor, 35-55 kOhm

        self.osc = self.Port(
            CrystalDriver(frequency_limits=(4, 25) * MHertz, voltage_out=self.pwr.link().voltage), optional=True
        )  # Table 3-10 crystal / resonator specs, typ 24 MHz

        self.swio = self.Port(DigitalBidir.empty())

    @override
    def _system_pinmap(self) -> Mapping[Union[Iterable[str], str], Union[Passive, HasPassivePort]]:
        return {
            "7": self.vss,
            "9": self.vdd,
            "5": self.osc.xtal_in,  # TODO remappable to PA1
            "6": self.osc.xtal_out,  # TODO remappable to PA2
            "4": self.nrst,
            "18": self.swio,
        }

    @override
    def _io_pinmap(self) -> PinMapUtil:
        # Port models
        dio_ft_model = DigitalBidir.from_supply(
            self.gnd,
            self.pwr,
            voltage_limit_abs=(-0.3, 5.5) * Volt,  # table 3.1
            current_limits=(-20, 20) * mAmp,  # table 3.1
            input_threshold_abs=(  # table 3-16
                0.19 * (self.vdd.link().voltage.lower() - 2.7) + 0.65 + self.vss.link().voltage.lower(),
                0.22 * (self.vdd.link().voltage.upper() - 2.7) + 1.55 + self.vss.link().voltage.upper(),
            ),
            pullup_capable=True,  # 35-55 kOhm
            pulldown_capable=True,  # 35-55 kOhm
        )
        dio_std_model = DigitalBidir.from_supply(
            self.gnd,
            self.pwr,
            voltage_limit_tolerance=(-0.3, 0.3) * Volt,  # table 3.1
            current_limits=(-20, 20) * mAmp,  # table 3.1
            input_threshold_abs=(  # table 3-16
                0.19 * (self.vdd.link().voltage.lower() - 2.7) + 0.65 + self.vss.link().voltage.lower(),
                0.22 * (self.vdd.link().voltage.upper() - 2.7) + 1.55 + self.vss.link().voltage.upper(),
            ),
            pullup_capable=True,  # 35-55 kOhm
            pulldown_capable=True,  # 35-55 kOhm
        )

        adc_model = AnalogSink.from_supply(
            self.gnd,
            self.pwr,
            voltage_limit_tolerance=(-0.3, 0.3) * Volt,  # table 3.1
            signal_limit_tolerance=(0, 0),  # conversion voltage range, 0 to Vref+ (assumed VddA)
            impedance=(100, float("inf")) * kOhm,
        )

        uart_model = UartPort(DigitalBidir.empty())
        spi_model = SpiController(DigitalBidir.empty())
        # TODO SPI peripherals, which have fixed-pin CS lines
        i2c_model = I2cController(DigitalBidir.empty())
        i2c_target_model = I2cTarget(DigitalBidir.empty())

        # return PinMapUtil(
        #     [  # Table 5, partial table for 48-pin only
        #         PinResource("PA0", {"PA0": dio_std_model, "ADC12_IN0": adc_model}),
        #         PinResource("PA1", {"PA1": dio_std_model, "ADC12_IN1": adc_model}),
        #         PinResource("PA2", {"PA2": dio_std_model, "ADC12_IN2": adc_model}),
        #         PinResource("PA3", {"PA3": dio_std_model, "ADC12_IN3": adc_model}),
        #         PinResource("PA4", {"PA4": dio_std_model, "ADC12_IN4": adc_model}),
        #         PinResource("PA5", {"PA5": dio_std_model, "ADC12_IN5": adc_model}),
        #         PinResource("PA6", {"PA6": dio_std_model, "ADC12_IN6": adc_model}),
        #         PinResource("PA7", {"PA7": dio_std_model, "ADC12_IN7": adc_model}),
        #         PinResource("PB0", {"PB0": dio_std_model, "ADC12_IN8": adc_model}),
        #         PinResource("PB1", {"PB1": dio_std_model, "ADC12_IN9": adc_model}),
        #         PinResource("PB2", {"PB2": dio_ft_model}),  # BOOT1
        #         PinResource("PB10", {"PB10": dio_ft_model}),
        #         PinResource("PB11", {"PB11": dio_ft_model}),
        #         PinResource("PB12", {"PB12": dio_ft_model}),
        #         PinResource("PB13", {"PB13": dio_ft_model}),
        #         PinResource("PB14", {"PB14": dio_ft_model}),
        #         PinResource("PB15", {"PB15": dio_ft_model}),
        #         PinResource("PA8", {"PA8": dio_ft_model}),
        #         PinResource("PA9", {"PA9": dio_ft_model}),
        #         PinResource("PA10", {"PA10": dio_ft_model}),
        #         PinResource("PA11", {"PA11": dio_ft_model}),
        #         PinResource("PA12", {"PA12": dio_ft_model}),
        #         # PinResource('PA13', {'PA13': dio_ft_model}),  # forced SWDIO default is JTMS/SWDIO
        #         # PinResource('PA14', {'PA14': dio_ft_model}),  # forced SWCLK, default is JTCK/SWCLK
        #         PinResource("PA15", {"PA15": dio_ft_model}),  # default is JTDI
        #         PinResource("PB3", {"PB3": dio_ft_model}),  # SWO, default is JTDO
        #         PinResource("PB4", {"PB4": dio_ft_model}),  # default is JNTRST
        #         PinResource("PB5", {"PB5": dio_std_model}),
        #         PinResource("PB6", {"PB6": dio_ft_model}),
        #         PinResource("PB7", {"PB7": dio_ft_model}),
        #         PinResource("PB8", {"PB8": dio_ft_model}),
        #         PinResource("PB9", {"PB9": dio_ft_model}),
        #         # PinResource('NRST', {'NRST': dio_std_model}),  # non-mappable to IO!
        #         # de-prioritize these for auto-assignment since they're low-current
        #         PinResource("PC13", {"PC13": dio_pc_13_14_15_model}),
        #         PinResource("PC14", {"PC14": dio_pc_13_14_15_model, "OSC32_IN": Passive()}),
        #         PinResource("PC15", {"PC15": dio_pc_13_14_15_model, "OSC32_OUT": Passive()}),
        #         PeripheralFixedResource("USART2", uart_model, {"tx": ["PA2", "PD5"], "rx": ["PA3", "PD6"]}),
        #         PeripheralFixedResource(
        #             "SPI1", spi_model, {"sck": ["PA5", "PB3"], "miso": ["PA6", "PB4"], "mosi": ["PA7", "PB5"]}
        #         ),
        #         PeripheralFixedResource(
        #             "USART3", uart_model, {"tx": ["PB10", "PD8", "PC10"], "rx": ["PB11", "PD9", "PC11"]}
        #         ),
        #         PeripheralFixedResource("I2C2", i2c_model, {"scl": ["PB10"], "sda": ["PB11"]}),
        #         PeripheralFixedResource(
        #             "I2C2_T",
        #             i2c_target_model,
        #             {"scl": ["PB10"], "sda": ["PB11"]},  # TODO shared resource w/ I2C controller
        #         ),
        #         PeripheralFixedResource("SPI2", spi_model, {"sck": ["PB13"], "miso": ["PB14"], "mosi": ["PB15"]}),
        #         PeripheralFixedResource("USART1", uart_model, {"tx": ["PA9", "PB6"], "rx": ["PA10", "PB7"]}),
        #         PeripheralFixedResource(
        #             "CAN",
        #             CanControllerPort(DigitalBidir.empty()),
        #             {"txd": ["PA12", "PD1", "PB9"], "rxd": ["PA11", "PD0", "PB8"]},
        #         ),
        #         PeripheralFixedResource("USB", UsbDevicePort(DigitalBidir.empty()), {"dm": ["PA11"], "dp": ["PA12"]}),
        #         PeripheralFixedPin(
        #             "SWD",
        #             SwdTargetPort(dio_std_model),
        #             {  # TODO most are FT pins
        #                 "swdio": "PA13",
        #                 "swclk": "PA14",  # note: SWO is PB3
        #             },
        #         ),
        #         PeripheralFixedResource("I2C1", i2c_model, {"scl": ["PB6", "PB8"], "sda": ["PB7", "PB9"]}),
        #         PeripheralFixedResource(
        #             "I2C1_T",
        #             i2c_target_model,
        #             {"scl": ["PB6", "PB8"], "sda": ["PB7", "PB9"]},  # TODO shared resource w/ I2C controller
        #         ),
        #     ]
        # ).remap_pins(self._PIN_MAPPING)

    @override
    def generate(self) -> None:
        super().generate()

        self.footprint(
            "U",
            "Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm",
            self._make_pinning(),
            mfr="WCH",
            part="CH32V003F4P6",
            datasheet="https://www.wch-ic.com/downloads/CH32V003DS0_PDF.html",
        )
        self.assign(self.lcsc_part, "C5187096")
        self.assign(self.actual_basic_part, False)


class Ch32v003(
    Resettable,
    IoControllerI2cTarget,
    Microcontroller,
    IoControllerWithSwdTargetConnector,
    WithCrystalGenerator,
    IoControllerPowerRequired,
    GeneratorBlock,
):
    """Low-cost, bare bones RISC-V (RV32EC) microcontroller"""

    DEFAULT_CRYSTAL_FREQUENCY = 24 * MHertz(tol=0.005)  # 24 MHz as typical in datasheet

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.generator_param(self.reset.is_connected())

    @override
    def generate(self) -> None:
        super().generate()

        with self.implicit_connect(ImplicitConnect(self.pwr, [Power]), ImplicitConnect(self.gnd, [Common])) as imp:
            self.ic = imp.Block(Ch32v003_Device(pin_assigns=ArrayStringExpr()))
            self._wrap_inner(self.ic)

            self.sdi = imp.Block(Ch32vSdiHeader())
            self.connect(self.ic.swio, self.sdi.swio)
            self.connect(self.ic.nrst, self.sdi.reset)

            self.connect(self.xtal_node, self.ic.osc)

            self.vdd_cap = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))

        if self.get(self.reset.is_connected()):
            self.connect(self.reset, self.ic.nrst)
