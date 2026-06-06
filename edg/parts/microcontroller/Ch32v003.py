from typing import *

from typing_extensions import override

from ...circuits import *
from ...vendor_parts.jlc.JlcPart import JlcPart
from ..connector.Headers import PinHeader254
from ..connector.TagConnect import TagConnect


@abstract_block_default(lambda: Ch32vSdiHeader254)
class Ch32vSdiHeader(ProgrammingConnector):
    """Abstract programming header for the CH32V using the one-pin SDI interface with SWIO pin."""

    def __init__(self) -> None:
        super().__init__()

        self.pwr = self.Port(VoltageSink.empty(), [Power])
        self.gnd = self.Port(Ground.empty(), [Common])
        self.swio = self.Port(DigitalBidir.empty())
        self.reset = self.Port(DigitalBidir.empty(), optional=True)  # may not be connected internally


class Ch32vSdiHeader254(Ch32vSdiHeader):
    """3-pin minimal programming header for CH32V."""

    @override
    def contents(self) -> None:
        super().contents()

        self.gnd.init_from(Ground())
        self.pwr.init_from(VoltageSink())
        self.swio.init_from(DigitalBidir())
        self.reset.init_from(DigitalBidir())  # not connected

        self.conn = self.Block(PinHeader254()).connected({"1": self.pwr, "2": self.gnd, "3": self.swio})


class Ch32vSdiTc2030(Ch32vSdiHeader):
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
        )  # note, switched internal pull-up resistor, 35-55 kOhm

        self.osc = self.Port(
            CrystalDriver(frequency_limits=(4, 25) * MHertz, voltage_out=self.vdd.link().voltage), optional=True
        )  # Table 3-10 crystal / resonator specs, typ 24 MHz

        self._dio_ft_model = DigitalBidir.from_supply(
            self.vss,
            self.vdd,
            voltage_limit_abs=(-0.3, 5.5) * Volt,  # table 3.1
            current_limits=(-20, 20) * mAmp,  # table 3.1
            input_threshold_abs=(  # table 3-16
                0.19 * (self.vdd.link().voltage.lower() - 2.7) + 0.65 + self.vss.link().voltage.lower(),
                0.22 * (self.vdd.link().voltage.upper() - 2.7) + 1.55 + self.vss.link().voltage.upper(),
            ),
            pullup_capable=True,  # 35-55 kOhm
            pulldown_capable=True,  # 35-55 kOhm
        )
        self._dio_std_model = DigitalBidir.from_supply(
            self.vss,
            self.vdd,
            voltage_limit_tolerance=(-0.3, 0.3) * Volt,  # table 3.1
            current_limits=(-20, 20) * mAmp,  # table 3.1
            input_threshold_abs=(  # table 3-16
                0.19 * (self.vdd.link().voltage.lower() - 2.7) + 0.65 + self.vss.link().voltage.lower(),
                0.22 * (self.vdd.link().voltage.upper() - 2.7) + 1.55 + self.vss.link().voltage.upper(),
            ),
            pullup_capable=True,  # 35-55 kOhm
            pulldown_capable=True,  # 35-55 kOhm
        )

        self.swio = self.Port(self._dio_std_model)

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
        adc_model = AnalogSink.from_supply(
            self.vss,
            self.vdd,
            voltage_limit_tolerance=(-0.3, 0.3) * Volt,  # table 3.1
            impedance=(100, float("inf")) * kOhm,
        )

        uart_model = UartPort(DigitalBidir.empty())
        spi_model = SpiController(DigitalBidir.empty())
        # TODO SPI peripherals, which have fixed-pin CS lines
        i2c_model = I2cController(DigitalBidir.empty())
        i2c_target_model = I2cTarget(DigitalBidir.empty())

        return PinMapUtil(
            [  # table 2-1
                PinResource("PD4", {"PD4": self._dio_std_model, "A7": adc_model}),
                PinResource("PD5", {"PD5": self._dio_std_model, "A5": adc_model}),
                PinResource("PD6", {"PD6": self._dio_std_model, "A6": adc_model}),
                PinResource("PD7", {"PD7": self._dio_std_model}),  # NRST
                PinResource("PA1", {"PA1": self._dio_std_model, "A1": adc_model}),
                PinResource("PA2", {"PA2": self._dio_std_model, "A0": adc_model}),
                PinResource("PD0", {"PD0": self._dio_std_model}),
                PinResource("PC0", {"PC0": self._dio_std_model}),
                PinResource("PC1", {"PC1": self._dio_ft_model}),
                PinResource("PC2", {"PC2": self._dio_ft_model}),
                PinResource("PC3", {"PC3": self._dio_std_model}),
                PinResource("PC4", {"PC4": self._dio_ft_model, "A2": adc_model}),
                PinResource("PC5", {"PC5": self._dio_ft_model}),
                PinResource("PC6", {"PC6": self._dio_ft_model}),
                PinResource("PC7", {"PC7": self._dio_std_model}),
                PinResource("PD1", {"PD1": self._dio_std_model}),  # SWIO
                PinResource("PD2", {"PD2": self._dio_std_model, "A3": adc_model}),
                PinResource("PD3", {"PD3": self._dio_std_model, "A4": adc_model}),
                PeripheralFixedResource(
                    "U", uart_model, {"tx": ["PD5", "PD0", "PD6", "PC0"], "rx": ["PD6", "PD1", "PD5", "PC1"]}
                ),
                PeripheralFixedResource("SPI", spi_model, {"sck": ["PC5"], "miso": ["PC7"], "mosi": ["PC6"]}),
                PeripheralFixedResource("I2C", i2c_model, {"scl": ["PC2", "PD1", "PC5"], "sda": ["PC1", "PD0", "PC6"]}),
                PeripheralFixedResource(
                    "I2C_T", i2c_target_model, {"scl": ["PC2", "PD1", "PC5"], "sda": ["PC1", "PD0", "PC6"]}
                ),
            ]
        ).remap_pins(self._PIN_MAPPING)

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
