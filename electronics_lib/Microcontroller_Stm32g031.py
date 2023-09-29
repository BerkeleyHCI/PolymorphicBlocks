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

        # # Additional ports (on top of BaseIoController)
        # self.pwr = self.Port(VoltageSink(
        #     voltage_limits=(3.0, 3.6)*Volt,  # TODO relaxed range down to 2.0 if ADC not used, or 2.4 if USB not used
        #     current_draw=(0, 50.3)*mAmp + self.io_current_draw.upper()  # Table 13
        # ), [Power])
        # self.gnd = self.Port(Ground(), [Common])
        #
        # self.nrst = self.Port(DigitalSink.from_supply(
        #     self.gnd, self.pwr,
        #     voltage_limit_tolerance=(-0.3, 0.3)*Volt,  # Table 5.3.1, general operating conditions  TODO: FT IO, BOOT0 IO
        #     current_draw=(0, 0)*Amp,
        #     input_threshold_abs=(0.8, 2)*Volt
        # ), optional=True)  # note, internal pull-up resistor, 30-50 kOhm by Table 35
        #
        # # TODO need to pass through to pin mapper
        # # self.osc32 = self.Port(CrystalDriver(frequency_limits=32.768*kHertz(tol=0),  # TODO actual tolerances
        # #                                      voltage_out=self.pwr.link().voltage),
        # #                        optional=True)  # TODO other specs from Table 23
        # self.osc = self.Port(CrystalDriver(frequency_limits=(4, 16)*MHertz,
        #                                    voltage_out=self.pwr.link().voltage),
        #                      optional=True)  # Table 22
        #
        # self.swd = self.Port(SwdTargetPort.empty())
        # self._io_ports.insert(0, self.swd)

    def _system_pinmap(self) -> Dict[str, CircuitPort]:
        return VariantPinRemapper({  # Pin/peripheral resource definitions (section 4)
            'Vdd': self.pwr,
            'Vss': self.gnd,
            # 'BOOT0': self.gnd,
            'PF2-NRST': self.nrst,
        }).remap(self.SYSTEM_PIN_REMAP)

    def _io_pinmap(self) -> PinMapUtil:
        # Port models
        # dio_ft_model = DigitalBidir.from_supply(
        #     self.gnd, self.pwr,
        #     voltage_limit_abs=(-0.3, 5.2) * Volt,  # Table 5.3.1, general operating conditions, TODO relaxed for Vdd>2v
        #     current_draw=(0, 0)*Amp, current_limits=(-20, 20)*mAmp,  # Section 5.3.13 Output driving current, TODO loose with relaxed VOL/VOH
        #     input_threshold_factor=(0.35, 0.65),  # TODO relaxed (but more complex) bounds available
        #     pullup_capable=True, pulldown_capable=True
        # )
        # dio_std_model = DigitalBidir.from_supply(
        #     self.gnd, self.pwr,
        #     voltage_limit_tolerance=(-0.3, 0.3)*Volt,  # Table 5.3.1, general operating conditions
        #     current_draw=(0, 0)*Amp, current_limits=(-20, 20)*mAmp,  # Section 5.3.13 Output driving current, TODO loose with relaxed VOL/VOH
        #     input_threshold_factor=(0.35, 0.65),  # TODO relaxed (but more complex) bounds available
        #     pullup_capable=True, pulldown_capable=True,
        # )
        # dio_pc_13_14_15_model = DigitalBidir.from_supply(
        #     self.gnd, self.pwr,
        #     voltage_limit_tolerance=(-0.3, 0.3)*Volt,  # Table 5.3.1, general operating conditions
        #     current_draw=(0, 0)*Amp, current_limits=(-3, 3)*mAmp,  # Section 5.3.13 Output driving current
        #     input_threshold_factor=(0.35, 0.65),  # TODO relaxed (but more complex) bounds available
        #     pullup_capable=True, pulldown_capable=True,
        # )
        #
        # adc_model = AnalogSink.from_supply(
        #     self.gnd, self.pwr,
        #     voltage_limit_tolerance=(-0.3, 0.3)*Volt,  # general operating conditions, IO input voltage
        #     signal_limit_tolerance=(0, 0),  # conversion voltage range, 0 to Vref+ (assumed VddA)
        #     impedance=(100, float('inf')) * kOhm
        # )

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
            PinResource('PA14', {'PA14-BOOT0': dio_fta_model, 'ADC_IN18': adc_model}),  # BOOT0, SWCLK, ADC_IN18
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
            PeripheralFixedPin('SWD', SwdTargetPort(DigitalBidir.empty()), {
                'swdio': 'PA13', 'swclk': 'PA14',  # note: SWO is PB3
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
    SYSTEM_PIN_REMAP = {
        # 'Vbat': '1',
        # 'VddA': '9',
        # 'VssA': '8',
        # 'Vss': ['23', '35', '47'],
        # 'Vdd': ['24', '36', '48'],
        # 'BOOT0': '44',
        # 'OSC_IN': '5',
        # 'OSC_OUT': '6',
        # 'NRST': '7',
    }
    RESOURCE_PIN_REMAP = {
        # 'PC13': '2',
        # 'PC14': '3',
        # 'PC15': '4',
        #
        # 'PA0': '10',
        # 'PA1': '11',
        # 'PA2': '12',
        # 'PA3': '13',
        # 'PA4': '14',
        # 'PA5': '15',
        # 'PA6': '16',
        # 'PA7': '17',
        # 'PB0': '18',
        # 'PB1': '19',
        #
        # 'PB2': '20',
        # 'PB10': '21',
        # 'PB11': '22',
        # 'PB12': '25',
        # 'PB13': '26',
        # 'PB14': '27',
        # 'PB15': '28',
        #
        # 'PA8': '29',
        # 'PA9': '30',
        # 'PA10': '31',
        # 'PA11': '32',
        # 'PA12': '33',
        # 'PA13': '34',
        #
        # 'PA14': '37',
        # 'PA15': '38',
        # 'PB3': '39',
        # 'PB4': '40',
        # 'PB5': '41',
        # 'PB6': '42',
        # 'PB7': '43',
        #
        # 'PB8': '45',
        # 'PB9': '46',
    }
    PACKAGE = 'Package_DFN_QFN:QFN-28_4x4mm_P0.5mm'
    PART = 'STM32G031Gxxx'
    LCSC_PART = 'C432211'  # G8U6 variantTrue
