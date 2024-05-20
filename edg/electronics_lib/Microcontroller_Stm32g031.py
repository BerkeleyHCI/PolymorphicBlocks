from typing import *

from electronics_abstract_parts import *
from .JlcPart import JlcPart


@abstract_block
class Stm32g031Base_Device(IoControllerI2cTarget, IoControllerCan, IoControllerUsb, InternalSubcircuit, BaseIoControllerPinmapGenerator,
                           GeneratorBlock, JlcPart, FootprintBlock):
    PACKAGE: str  # package name for footprint(...)
    PART: str  # part name for footprint(...)
    LCSC_PART: str
    LCSC_BASIC_PART: bool

    SYSTEM_PIN_REMAP: Dict[str, Union[str, List[str]]]  # pin name in base -> pin name(s)
    RESOURCE_PIN_REMAP: Dict[str, str]  # resource name in base -> pin name

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        # Additional ports (on top of BaseIoController)
        self.pwr = self.Port(VoltageSink(
            voltage_limits=(1.7, 3.6)*Volt,  # Table 5.3.1 "standard operating voltage", not including Vrefbuf
            current_draw=(0.001, 7.6)*mAmp + self.io_current_draw.upper()  # Table 25 (run), 30 (standby)
        ), [Power])
        self.gnd = self.Port(Ground(), [Common])

        self.swd = self.Port(SwdTargetPort.empty())
        self._io_ports.insert(0, self.swd)

        self.nrst = self.Port(DigitalBidir.empty(), optional=True)  # internally pulled up

    def _system_pinmap(self) -> Dict[str, CircuitPort]:
        return VariantPinRemapper({  # Pin/peripheral resource definitions (section 4)
            'Vdd': self.pwr,
            'Vss': self.gnd,
            'PF2-NRST': self.nrst,
        }).remap(self.SYSTEM_PIN_REMAP)

    def _io_pinmap(self) -> PinMapUtil:
        # Port models
        input_range = self.gnd.link().voltage.hull(self.pwr.link().voltage)
        io_voltage_limit = (input_range + (-0.3, 3.6)*Volt).intersect(self.gnd.link().voltage + (-0.3, 5.5)*Volt)
        dio_ft_model = DigitalBidir.from_supply(
            self.gnd, self.pwr,
            voltage_limit_abs=io_voltage_limit,
            current_limits=(-15, 15)*mAmp,  # Section 5.3.14, relaxed bounds for relaxed Vol/Voh
            input_threshold_factor=(0.3, 0.7),  # Section 5.3.14
            pullup_capable=True, pulldown_capable=True
        )
        dio_fta_model = dio_ftea_model = dio_ftf_model = dio_ftfa_model = dio_ft_model

        self.nrst.init_from(DigitalBidir.from_supply(  # specified differently than other pins
            self.gnd, self.pwr,
            voltage_limit_abs=io_voltage_limit,  # assumed
            current_limits=(-15, 15)*mAmp,  # Section 5.3.14, relaxed bounds for relaxed Vol/Voh
            input_threshold_factor=(0.3, 0.7),
            pullup_capable=True  # internal pullup
        ))

        adc_model = AnalogSink.from_supply(
            self.gnd, self.pwr,
            voltage_limit_abs=io_voltage_limit,
            signal_limit_tolerance=(0, 0),  # conversion voltage range, VssA to Vref+ (assumed VddA)
            impedance=(50, float('inf'))*kOhm  # max external impedance, at lowest listed sampling rate
        )

        uart_model = UartPort(DigitalBidir.empty())
        spi_model = SpiController(DigitalBidir.empty())
        # TODO SPI peripherals, which have fixed-pin CS lines
        i2c_model = I2cController(DigitalBidir.empty())
        i2c_target_model = I2cTarget(DigitalBidir.empty())

        return PinMapUtil([  # Table 12, partial table for up to 32-pin only
            PinResource('PC14', {'PC14': dio_ft_model}),  # OSC32_IN, OSC_IN (?)
            PinResource('PC15', {'PC15': dio_ft_model}),  # OSC32_OUT
            # PinResource('PF2', {'PF2': dio_ft_model}),  # NRST
            PinResource('PA0', {'PA0': dio_fta_model, 'ADC_IN0': adc_model}),
            PinResource('PA1', {'PA1': dio_ftea_model, 'ADC_IN1': adc_model}),
            PinResource('PA2', {'PA2': dio_fta_model, 'ADC_IN2': adc_model}),
            PinResource('PA3', {'PA3': dio_ftea_model, 'ADC_IN3': adc_model}),

            PinResource('PA4', {'PA4': dio_fta_model, 'ADC_IN4': adc_model}),
            PinResource('PA5', {'PA5': dio_ftea_model, 'ADC_IN5': adc_model}),
            PinResource('PA6', {'PA6': dio_ftea_model, 'ADC_IN6': adc_model}),
            PinResource('PA7', {'PA7': dio_fta_model, 'ADC_IN7': adc_model}),
            PinResource('PB0', {'PB0': dio_ftea_model, 'ADC_IN8': adc_model}),
            PinResource('PB1', {'PB1': dio_ftea_model, 'ADC_IN9': adc_model}),
            PinResource('PB2', {'PB2': dio_ftea_model, 'ADC_IN10': adc_model}),
            PinResource('PA8', {'PA8': dio_ft_model}),

            PinResource('PA9', {'PA9': dio_ftf_model}),
            PinResource('PC6', {'PC6': dio_ft_model}),
            PinResource('PA10', {'PA10': dio_ftf_model}),
            PinResource('PA11', {'PA11': dio_ftfa_model, 'ADC_IN15': adc_model}),
            PinResource('PA12', {'PA12': dio_ftfa_model, 'ADC_IN16': adc_model}),
            PinResource('PA13', {'PA13': dio_ftea_model, 'ADC_IN17': adc_model}),  # SWDIO
            # nBOOT_SEL flash bit can be programmed to ignore nBOOT0 bit
            PinResource('PA14', {'PA14': dio_fta_model, 'ADC_IN18': adc_model}),  # BOOT0, SWCLK, ADC_IN18
            PinResource('PA15', {'PA15': dio_ft_model}),

            PinResource('PB3', {'PB3': dio_ft_model}),
            PinResource('PB4', {'PB4': dio_ft_model}),
            PinResource('PB5', {'PB5': dio_ft_model}),
            PinResource('PB6', {'PB6': dio_ft_model}),
            PinResource('PB7', {'PB7': dio_ftea_model, 'ADC_IN11': adc_model}),
            PinResource('PB8', {'PB8': dio_ft_model}),
            PinResource('PB9', {'PB9': dio_ft_model}),

            PeripheralFixedResource('SPI2', spi_model, {
                'sck': ['PA0', 'PB8'], 'miso': ['PA3', 'PB2', 'PA9', 'PB6'], 'mosi': ['PA4', 'PA10', 'PB7']
            }),
            PeripheralFixedResource('SPI1', spi_model, {
                'sck': ['PA1', 'PA5', 'PB3'], 'miso': ['PA6', 'PA11', 'PB4'], 'mosi': ['PA2', 'PA7', 'PA12', 'PB5']
            }),
            PeripheralFixedResource('I2S1', I2sController(DigitalBidir.empty()), {
                'sck': ['PA1', 'PA5', 'PB3'], 'ws': ['PA4', 'PB0', 'PA15'], 'sd': ['PA2', 'PA7', 'PA12', 'PB5']
            }),
            PeripheralFixedResource('USART2', uart_model, {
                'tx': ['PA2', 'PA14'], 'rx': ['PA3', 'PA15']
            }),
            PeripheralFixedResource('LPUART1', uart_model, {
                'tx': ['PA2'], 'rx': ['PA3']
            }),
            PeripheralFixedResource('USART1', uart_model, {
                'tx': ['PA9', 'PB6'], 'rx': ['PA10', 'PB7']
            }),
            PeripheralFixedResource('I2C1', i2c_model, {
                'scl': ['PA9', 'PB6', 'PB8'], 'sda': ['PA10', 'PB7', 'PB9']
            }),
            PeripheralFixedResource('I2C1_T', i2c_target_model, {  # TODO shared resource w/ I2C controller
                'scl': ['PA9', 'PB6', 'PB8'], 'sda': ['PA10', 'PB7', 'PB9']
            }),
            PeripheralFixedResource('I2C2', i2c_model, {
                'scl': ['PA11'], 'sda': ['PA12']
            }),
            PeripheralFixedResource('I2C2_T', i2c_target_model, {  # TODO shared resource w/ I2C controller
                'scl': ['PA11'], 'sda': ['PA12']
            }),
            PeripheralFixedResource('SWD', SwdTargetPort(DigitalBidir.empty()), {
                'swdio': ['PA13'], 'swclk': ['PA14'],
            }),
        ]).remap_pins(self.RESOURCE_PIN_REMAP)

    def generate(self) -> None:
        super().generate()

        self.footprint(
            'U', self.PACKAGE,
            self._make_pinning(),
            mfr='STMicroelectronics', part=self.PART,
            datasheet='https://www.st.com/resource/en/datasheet/stm32g031c6.pdf'
        )
        self.assign(self.lcsc_part, self.LCSC_PART)
        self.assign(self.actual_basic_part, False)


class Stm32g031_G_Device(Stm32g031Base_Device):
    """"STM32G031 GxU in UFQFPN28 package."""
    SYSTEM_PIN_REMAP = {
        'Vdd': '3',
        'Vss': '4',
        'PF2-NRST': '5',
    }
    RESOURCE_PIN_REMAP = {
        'PC14': '1',
        'PC15': '2',
        'PA0': '6',
        'PA1': '7',

        'PA2': '8',
        'PA3': '9',
        'PA4': '10',
        'PA5': '11',
        'PA6': '12',
        'PA7': '13',
        'PB0': '14',

        'PB1': '15',
        'PA8': '16',
        'PC6': '17',
        'PA11': '18',
        'PA12': '19',
        'PA13': '20',
        'PA14': '21',

        'PA15': '22',
        'PB3': '23',
        'PB4': '24',
        'PB5': '25',
        'PB6': '26',
        'PB7': '27',
        'PB8': '28',
    }
    PACKAGE = 'Package_DFN_QFN:QFN-28_4x4mm_P0.5mm'
    PART = 'STM32G031Gxxx'
    LCSC_PART = 'C432211'  # G8U6 variant


@abstract_block
class Stm32g031Base(Resettable, IoControllerI2cTarget, Microcontroller, IoControllerWithSwdTargetConnector,
                    IoControllerPowerRequired, BaseIoControllerExportable, GeneratorBlock):
    DEVICE: Type[Stm32g031Base_Device] = Stm32g031Base_Device  # type: ignore

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ic: Stm32g031Base_Device
        self.generator_param(self.reset.is_connected())

    def contents(self):
        super().contents()

        with self.implicit_connect(
                ImplicitConnect(self.pwr, [Power]),
                ImplicitConnect(self.gnd, [Common])
        ) as imp:
            self.ic = imp.Block(self.DEVICE(pin_assigns=ArrayStringExpr()))
            self.connect(self.swd_node, self.ic.swd)
            self.connect(self.reset_node, self.ic.nrst)

            # from https://www.st.com/resource/en/application_note/an5096-getting-started-with-stm32g0-series-hardware-development-stmicroelectronics.pdf
            self.pwr_cap0 = imp.Block(DecouplingCapacitor(4.7 * uFarad(tol=0.2)))
            self.pwr_cap1 = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))

    def generate(self):
        super().generate()

        if self.get(self.reset.is_connected()):
            self.connect(self.reset, self.ic.nrst)  # otherwise NRST has internal pull-up


class Stm32g031_G(Stm32g031Base):
    DEVICE = Stm32g031_G_Device
