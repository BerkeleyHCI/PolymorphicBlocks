from typing import *

from deprecated import deprecated
from typing_extensions import override

from ...circuits import *
from ...vendor_parts.jlc.JlcPart import JlcPart


class Stm32f103_Device(
    IoControllerI2cTarget,
    IoControllerCan,
    IoControllerUsb,
    InternalSubcircuit,
    BaseIoControllerPinmapGenerator,
    GeneratorBlock,
    JlcPart,
    FootprintBlock,
):
    _PIN_MAPPING = {
        "PC13": "2",
        "PC14": "3",
        "PC15": "4",
        "PA0": "10",
        "PA1": "11",
        "PA2": "12",
        "PA3": "13",
        "PA4": "14",
        "PA5": "15",
        "PA6": "16",
        "PA7": "17",
        "PB0": "18",
        "PB1": "19",
        "PB2": "20",
        "PB10": "21",
        "PB11": "22",
        "PB12": "25",
        "PB13": "26",
        "PB14": "27",
        "PB15": "28",
        "PA8": "29",
        "PA9": "30",
        "PA10": "31",
        "PA11": "32",
        "PA12": "33",
        "PA13": "34",
        "PA14": "37",
        "PA15": "38",
        "PB3": "39",
        "PB4": "40",
        "PB5": "41",
        "PB6": "42",
        "PB7": "43",
        "PB8": "45",
        "PB9": "46",
    }

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # Additional ports (on top of BaseIoController)
        self.pwr = self.Port(
            VoltageSink(
                voltage_limits=(3.0, 3.6)
                * Volt,  # TODO relaxed range down to 2.0 if ADC not used, or 2.4 if USB not used
                current_draw=(0, 50.3) * mAmp + self.io_current_draw.upper(),  # Table 13
            ),
            [Power],
        )
        self.gnd = self.Port(Ground(), [Common])

        self.nrst = self.Port(
            DigitalSink.from_supply(
                self.gnd,
                self.pwr,
                voltage_limit_tolerance=(-0.3, 0.3)
                * Volt,  # Table 5.3.1, general operating conditions  TODO: FT IO, BOOT0 IO
                input_threshold_abs=(0.8, 2) * Volt,
                pullup_capable=True,
            ),
            optional=True,
        )  # note, internal pull-up resistor, 30-50 kOhm by Table 35

        # TODO need to pass through to pin mapper
        # self.osc32 = self.Port(CrystalDriver(frequency_limits=32.768*kHertz(tol=0),  # TODO actual tolerances
        #                                      voltage=self.pwr.link().voltage),
        #                        optional=True)  # TODO other specs from Table 23
        self.osc = self.Port(
            CrystalDriver(frequency_limits=(4, 16) * MHertz, voltage=self.pwr.link().voltage), optional=True
        )  # Table 22

        self.swd = self.Port(SwdTargetPort.empty())
        self._io_ports.insert(0, self.swd)

    @override
    def _system_pinmap(self) -> Mapping[Union[Iterable[str], str], Union[Passive, HasPassivePort]]:
        return {
            "1": self.pwr,  # Vbat
            "9": self.pwr,  # VddA
            "8": self.gnd,  # VssA
            ("23", "35", "47"): self.gnd,  # Vss
            ("24", "36", "48"): self.pwr,  # Vdd
            "44": self.gnd,  # BOOT0
            "5": self.osc.xtal_in,  # TODO remappable to PD0
            "6": self.osc.xtal_out,  # TODO remappable to PD1
            "7": self.nrst,
        }

    @override
    def _io_pinmap(self) -> PinMapUtil:
        # Port models
        dio_ft_model = DigitalBidir.from_supply(
            self.gnd,
            self.pwr,
            voltage_limit_abs=(-0.3, 5.2) * Volt,  # Table 5.3.1, general operating conditions, TODO relaxed for Vdd>2v
            current_limits=(-20, 20) * mAmp,  # Section 5.3.13 Output driving current, TODO loose with relaxed VOL/VOH
            input_threshold_factor=(0.35, 0.65),  # TODO relaxed (but more complex) bounds available
            pullup_capable=True,
            pulldown_capable=True,
        )
        dio_std_model = DigitalBidir.from_supply(
            self.gnd,
            self.pwr,
            voltage_limit_tolerance=(-0.3, 0.3) * Volt,  # Table 5.3.1, general operating conditions
            current_limits=(-20, 20) * mAmp,  # Section 5.3.13 Output driving current, TODO loose with relaxed VOL/VOH
            input_threshold_factor=(0.35, 0.65),  # TODO relaxed (but more complex) bounds available
            pullup_capable=True,
            pulldown_capable=True,
        )
        dio_pc_13_14_15_model = DigitalBidir.from_supply(
            self.gnd,
            self.pwr,
            voltage_limit_tolerance=(-0.3, 0.3) * Volt,  # Table 5.3.1, general operating conditions
            current_limits=(-3, 3) * mAmp,  # Section 5.3.13 Output driving current
            input_threshold_factor=(0.35, 0.65),  # TODO relaxed (but more complex) bounds available
            pullup_capable=True,
            pulldown_capable=True,
        )

        adc_model = AnalogSink.from_supply(
            self.gnd,
            self.pwr,
            voltage_limit_tolerance=(-0.3, 0.3) * Volt,  # general operating conditions, IO input voltage
            signal_limit_tolerance=(0, 0),  # conversion voltage range, 0 to Vref+ (assumed VddA)
            impedance=(100, float("inf")) * kOhm,
        )

        uart_model = UartPort(DigitalBidir.empty())
        spi_model = SpiController(DigitalBidir.empty())
        # TODO SPI peripherals, which have fixed-pin CS lines
        i2c_model = I2cController(DigitalBidir.empty())
        i2c_target_model = I2cTarget(DigitalBidir.empty())

        return PinMapUtil(
            [  # Table 5, partial table for 48-pin only
                PinResource("PA0", {"PA0": dio_std_model, "ADC12_IN0": adc_model}),
                PinResource("PA1", {"PA1": dio_std_model, "ADC12_IN1": adc_model}),
                PinResource("PA2", {"PA2": dio_std_model, "ADC12_IN2": adc_model}),
                PinResource("PA3", {"PA3": dio_std_model, "ADC12_IN3": adc_model}),
                PinResource("PA4", {"PA4": dio_std_model, "ADC12_IN4": adc_model}),
                PinResource("PA5", {"PA5": dio_std_model, "ADC12_IN5": adc_model}),
                PinResource("PA6", {"PA6": dio_std_model, "ADC12_IN6": adc_model}),
                PinResource("PA7", {"PA7": dio_std_model, "ADC12_IN7": adc_model}),
                PinResource("PB0", {"PB0": dio_std_model, "ADC12_IN8": adc_model}),
                PinResource("PB1", {"PB1": dio_std_model, "ADC12_IN9": adc_model}),
                PinResource("PB2", {"PB2": dio_ft_model}),  # BOOT1
                PinResource("PB10", {"PB10": dio_ft_model}),
                PinResource("PB11", {"PB11": dio_ft_model}),
                PinResource("PB12", {"PB12": dio_ft_model}),
                PinResource("PB13", {"PB13": dio_ft_model}),
                PinResource("PB14", {"PB14": dio_ft_model}),
                PinResource("PB15", {"PB15": dio_ft_model}),
                PinResource("PA8", {"PA8": dio_ft_model}),
                PinResource("PA9", {"PA9": dio_ft_model}),
                PinResource("PA10", {"PA10": dio_ft_model}),
                PinResource("PA11", {"PA11": dio_ft_model, "USBDM": Passive()}),
                PinResource("PA12", {"PA12": dio_ft_model, "USBDP": Passive()}),
                # PinResource('PA13', {'PA13': dio_ft_model}),  # forced SWDIO default is JTMS/SWDIO
                # PinResource('PA14', {'PA14': dio_ft_model}),  # forced SWCLK, default is JTCK/SWCLK
                PinResource("PA15", {"PA15": dio_ft_model}),  # default is JTDI
                PinResource("PB3", {"PB3": dio_ft_model}),  # SWO, default is JTDO
                PinResource("PB4", {"PB4": dio_ft_model}),  # default is JNTRST
                PinResource("PB5", {"PB5": dio_std_model}),
                PinResource("PB6", {"PB6": dio_ft_model}),
                PinResource("PB7", {"PB7": dio_ft_model}),
                PinResource("PB8", {"PB8": dio_ft_model}),
                PinResource("PB9", {"PB9": dio_ft_model}),
                # PinResource('NRST', {'NRST': dio_std_model}),  # non-mappable to IO!
                # de-prioritize these for auto-assignment since they're low-current
                PinResource("PC13", {"PC13": dio_pc_13_14_15_model}),
                PinResource("PC14", {"PC14": dio_pc_13_14_15_model, "OSC32_IN": Passive()}),
                PinResource("PC15", {"PC15": dio_pc_13_14_15_model, "OSC32_OUT": Passive()}),
                PeripheralFixedResource("USART2", uart_model, {"tx": ["PA2", "PD5"], "rx": ["PA3", "PD6"]}),
                PeripheralFixedResource(
                    "SPI1", spi_model, {"sck": ["PA5", "PB3"], "miso": ["PA6", "PB4"], "mosi": ["PA7", "PB5"]}
                ),
                PeripheralFixedResource(
                    "USART3", uart_model, {"tx": ["PB10", "PD8", "PC10"], "rx": ["PB11", "PD9", "PC11"]}
                ),
                PeripheralFixedResource("I2C2", i2c_model, {"scl": ["PB10"], "sda": ["PB11"]}),
                PeripheralFixedResource(
                    "I2C2_T",
                    i2c_target_model,
                    {"scl": ["PB10"], "sda": ["PB11"]},  # TODO shared resource w/ I2C controller
                ),
                PeripheralFixedResource("SPI2", spi_model, {"sck": ["PB13"], "miso": ["PB14"], "mosi": ["PB15"]}),
                PeripheralFixedResource("USART1", uart_model, {"tx": ["PA9", "PB6"], "rx": ["PA10", "PB7"]}),
                PeripheralFixedResource(
                    "CAN",
                    CanControllerPort(DigitalBidir.empty()),
                    {"txd": ["PA12", "PD1", "PB9"], "rxd": ["PA11", "PD0", "PB8"]},
                ),
                PeripheralFixedResource(
                    "USB", UsbDevicePort(speed=UsbLink.UsbFullSpeedOnly), {"dm": ["PA11"], "dp": ["PA12"]}
                ),
                PeripheralFixedPin(
                    "SWD",
                    SwdTargetPort(dio_std_model),
                    {  # TODO most are FT pins
                        "swdio": "PA13",
                        "swclk": "PA14",  # note: SWO is PB3
                    },
                ),
                PeripheralFixedResource("I2C1", i2c_model, {"scl": ["PB6", "PB8"], "sda": ["PB7", "PB9"]}),
                PeripheralFixedResource(
                    "I2C1_T",
                    i2c_target_model,
                    {"scl": ["PB6", "PB8"], "sda": ["PB7", "PB9"]},  # TODO shared resource w/ I2C controller
                ),
            ]
        ).remap_pins(self._PIN_MAPPING)

    @override
    def generate(self) -> None:
        super().generate()

        self.footprint(
            "U",
            "Package_QFP:LQFP-48_7x7mm_P0.5mm",
            self._make_pinning(),
            mfr="STMicroelectronics",
            part="STM32F103xxT6",
            datasheet="https://www.st.com/resource/en/datasheet/stm32f103c8.pdf",
            pnp_rot=-90,
        )
        self.assign(self.lcsc_part, "C8304")  # max memory CBT6 variant
        self.assign(self.actual_basic_part, False)


class UsbDpPullUp(InternalSubcircuit, Block):
    def __init__(self, resistance: RangeLike):
        super().__init__()
        self.pwr = self.Port(VoltageSink(), [Power])
        self.usb = self.Port(UsbPassivePort(), [InOut])

        self.dp = self.Block(Resistor(resistance))
        self.connect(self.pwr.net, self.dp.a)
        self.connect(self.usb.dp, self.dp.b)


class Stm32f103(
    Resettable,
    IoControllerI2cTarget,
    IoControllerCan,
    IoControllerUsb,
    Microcontroller,
    IoControllerWithSwdTargetConnector,
    WithCrystalGenerator,
    IoControllerPowerRequired,
    GeneratorBlock,
):
    DEFAULT_CRYSTAL_FREQUENCY = 8 * MHertz(tol=0.005)  # as in common dev boards / eval boards

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.generator_param(
            self.reset.is_connected(),
            self.pin_assigns,
            self.gpio.requested(),
            self.can.requested(),
            self.usb.requested(),
        )

    @override
    def contents(self) -> None:
        super().contents()

        with self.implicit_connect(ImplicitConnect(self.pwr, [Power]), ImplicitConnect(self.gnd, [Common])) as imp:
            self.ic = imp.Block(Stm32f103_Device(pin_assigns=ArrayStringExpr()))
            self.connect(self.xtal_node, self.ic.osc)
            self.connect(self.swd_node, self.ic.swd)
            self.connect(self.reset_node, self.ic.nrst)

            self.pwr_cap = ElementDict[DecouplingCapacitor]()
            # one 0.1uF cap each for Vdd1-5 and one bulk 4.7uF cap
            self.pwr_cap[0] = imp.Block(DecouplingCapacitor(4.7 * uFarad(tol=0.2)))
            for i in range(1, 4):
                self.pwr_cap[i] = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))

            # one 10nF and 1uF cap for VddA TODO generate the same cap if a different Vref is used
            self.vdda_cap_0 = imp.Block(DecouplingCapacitor(10 * nFarad(tol=0.2)))
            self.vdda_cap_1 = imp.Block(DecouplingCapacitor(1 * uFarad(tol=0.2)))

    @override
    def generate(self) -> None:
        super().generate()

        def usb_export_transform(self_io: BasePort, assign: Optional[str]) -> Optional[BasePort]:
            self.usb_pull = self.Block(
                UsbDpPullUp(resistance=1.5 * kOhm(tol=0.01))
            )  # required by datasheet Table 44  # TODO proper tolerancing?
            self.connect(self.usb_pull.pwr, self.pwr)
            self.connect(self_io, self.usb_pull.usb)
            return self_io

        # add a passthrough for gpio (DigitalBidir) to allow the SWD pins to be attached, if using
        self._wrap_inner(self.ic, {UsbDevicePort: usb_export_transform, DigitalBidir: lambda port, assign: port})

        if self.get(self.reset.is_connected()):
            self.connect(self.reset, self.ic.nrst)

    @override
    def _crystal_required(self) -> bool:  # crystal needed for CAN or USB b/c tighter freq tolerance
        return (
            len(self.get(self.can.requested())) > 0
            or len(self.get(self.usb.requested())) > 0
            or super()._crystal_required()
        )


@deprecated("Use Stm32f103 instead of Stm32f103_48")
class Stm32f103_48(Stm32f103):
    pass
