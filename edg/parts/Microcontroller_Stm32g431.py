from typing import *

from .JlcPart import JlcPart
from ..abstract_parts import *


@abstract_block
class Stm32g431Base_Device(IoControllerI2cTarget, IoControllerCan, IoControllerUsb, InternalSubcircuit, IoControllerUsbCc,
                           BaseIoControllerPinmapGenerator,
                           GeneratorBlock, JlcPart, FootprintBlock):
    PACKAGE: str  # package name for footprint(...)
    PART: str  # part name for footprint(...)
    LCSC_PART: str
    LCSC_BASIC_PART: bool

    SYSTEM_PIN_REMAP: Dict[str, Union[str, List[str]]]  # pin name in base -> pin name(s)
    RESOURCE_PIN_REMAP: Dict[str, str]  # resource name in base -> pin name

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # Power and ground
        self.pwr = self.Port(VoltageSink(
            voltage_limits=(1.71, 3.6) * Volt,
            current_draw=(14 * nAmp, 44.0 * mAmp)  # Table 32
        ), [Power])

        self.gnd = self.Port(Ground(), [Common])

        self.swd = self.Port(SwdTargetPort.empty())
        self._io_ports.insert(0, self.swd)
        self.nrst = self.Port(DigitalSink.empty(), optional=True)  # internally pulled up

    def _system_pinmap(self) -> Dict[str, CircuitPort]:
        return VariantPinRemapper({
            'Vdd': self.pwr,
            'Vss': self.gnd,
            # 'VddA': self.pwr,
            # 'VssA': self.gnd,
            'BOOT0': self.gnd,
            'PG10-NRST': self.nrst,
        }).remap(self.SYSTEM_PIN_REMAP)

    def _io_pinmap(self) -> PinMapUtil:
        input_range = self.gnd.link().voltage.hull(self.pwr.link().voltage)
        io_voltage_limit = (input_range + (-0.3, 3.6) * Volt).intersect(
            self.gnd.link().voltage + (-0.3, 5.5) * Volt)  # Section 5.3.1
        input_threshold_factor = (0.3, 0.7)  # Section 5.3.14
        current_limits = (-20, 20) * mAmp  # Table 15

        dio_ft_model = DigitalBidir.from_supply(
            self.gnd, self.pwr,
            voltage_limit_abs=io_voltage_limit,
            current_limits=current_limits,
            input_threshold_factor=input_threshold_factor,
            pullup_capable=True, pulldown_capable=True
        )
        dio_tt_model = DigitalBidir.from_supply(
            self.gnd, self.pwr,
            voltage_limit_tolerance=(-0.3, 0.3) * Volt,  # Table 19
            current_limits=current_limits,
            input_threshold_factor=input_threshold_factor,
            pullup_capable=True, pulldown_capable=True
        )

        # Pin definition, 4.10
        dio_fta_model = dio_ftca_model = dio_ftf_model = dio_ftfa_model = \
            dio_ftfu_model = dio_ftfd_model = dio_ftda_model = dio_ftu_model = dio_ft_model
        dio_tta_model = dio_tt_model

        dio_ftc_model = DigitalBidir.from_supply(
            self.gnd, self.pwr,
            voltage_limit_abs=(-0.3, 5.0) * Volt,
            current_limits=current_limits,
            input_threshold_factor=input_threshold_factor,
            pullup_capable=True, pulldown_capable=True
        )

        adc_model = AnalogSink.from_supply(
            self.gnd, self.pwr,
            voltage_limit_tolerance=(-0.3, 0.3) * Volt,
            signal_limit_tolerance=(0, 0),
            impedance=(50, float('inf')) * kOhm  # TODO: this is maximum external input impedance, maybe restrictive
        )
        dac_model = AnalogSource.from_supply(
            self.gnd, self.pwr,
            signal_out_bound=(0.2 * Volt, -0.2 * Volt),  # signal_out_bound only applies when output buffer on
            impedance=(9.6, 13.8) * kOhm  # assumes buffer off
        )
        self.nrst.init_from(DigitalSink.from_supply(  # specified differently than other pins
            self.gnd, self.pwr,
            voltage_limit_abs=io_voltage_limit,  # assumed
            input_threshold_factor=(0.3, 0.7),
            pullup_capable=True  # internal pullup
        ))

        uart_model = UartPort(DigitalBidir.empty())
        spi_model = SpiController(DigitalBidir.empty())
        i2c_model = I2cController(DigitalBidir.empty())
        i2c_target_model = I2cTarget(DigitalBidir.empty())

        return PinMapUtil([  # for 32 pins only for now
            PinResource('PF0', {'PF0': dio_ftfa_model, 'ADC1_IN10': adc_model}),  # TODO remappable to OSC_IN
            PinResource('PF1', {'PF1': dio_fta_model, 'ADC2_IN10': adc_model}),  # TODO remappable to OSC_OUT

            PinResource('PA0', {'PA0': dio_tta_model, 'ADC12_IN1': adc_model}),
            PinResource('PA1', {'PA1': dio_tta_model, 'ADC12_IN2': adc_model}),
            PinResource('PA2', {'PA2': dio_tta_model, 'ADC1_IN3': adc_model}),
            PinResource('PA3', {'PA3': dio_tta_model, 'ADC1_IN4': adc_model}),
            PinResource('PA4', {'PA4': dio_tta_model, 'ADC2_IN17': adc_model, 'DAC1_OUT1': dac_model}),
            PinResource('PA5', {'PA5': dio_tta_model, 'ADC2_IN13': adc_model, 'DAC1_OUT2': dac_model}),
            PinResource('PA6', {'PA6': dio_tta_model, 'ADC2_IN3': adc_model}),
            PinResource('PA7', {'PA7': dio_tta_model, 'ADC2_IN4': adc_model}),
            PinResource('PA8', {'PA8': dio_ftf_model}),
            PinResource('PA9', {'PA9': dio_ftfd_model}),
            PinResource('PA10', {'PA10': dio_ftda_model}),
            PinResource('PA11', {'PA11': dio_ftu_model}),  # USB_DM
            PinResource('PA12', {'PA12': dio_ftu_model}),  # USB_DP
            PinResource('PA13', {'PA13': dio_ftf_model}),
            PinResource('PA14', {'PA14': dio_ftf_model}),
            PinResource('PA15', {'PA15': dio_ftf_model}),

            PinResource('PB0', {'PB0': dio_tta_model, 'ADC1_IN15': adc_model}),
            PinResource('PB3', {'PB3': dio_ft_model}),
            PinResource('PB4', {'PB4': dio_ftc_model}),
            PinResource('PB5', {'PB5': dio_ftf_model}),
            PinResource('PB6', {'PB6': dio_ftc_model}),
            PinResource('PB7', {'PB7': dio_ftf_model}),
            PinResource('PB8', {'PB8': dio_ftf_model}),

            # From table 13
            PeripheralFixedResource('SPI1', spi_model, {
                'sck': ['PA5', 'PB3'], 'miso': ['PA6', 'PB4'], 'mosi': ['PA7', 'PB5']
            }),
            PeripheralFixedResource('SPI2', spi_model, {
                'sck': ['PF1'], 'miso': ['PA10'], 'mosi': ['PA11']
            }),
            PeripheralFixedResource('SPI3', spi_model, {
                'sck': ['PB3'], 'miso': ['PB4'], 'mosi': ['PB5']
            }),
            PeripheralFixedResource('I2S2', I2sController(DigitalBidir.empty()), {
                'sck': ['PB13', 'PF1'], 'ws': ['PB12', 'PF0'], 'sd': ['PA11', 'PB15']
            }),
            PeripheralFixedResource('I2S3', I2sController(DigitalBidir.empty()), {
                'sck': ['PB3'], 'ws': ['PA4', 'PA15'], 'sd': ['PB5']
            }),
            PeripheralFixedResource('USART1', uart_model, {
                'tx': ['PA9', 'PB6'], 'rx': ['PA10', 'PB7']
            }),
            PeripheralFixedResource('USART2', uart_model, {
                'tx': ['PA2', 'PA14', 'PB3'], 'rx': ['PA3', 'PA15', 'PB4']
            }),
            PeripheralFixedResource('USART3', uart_model, {
                'tx': ['PB9', 'PB10'], 'rx': ['PB8', 'PB11', ]
            }),
            PeripheralFixedResource('LPUART1', uart_model, {
                'tx': ['PA2', 'PB11'], 'rx': ['PA3', 'PB10']
            }),
            PeripheralFixedResource('I2C1', i2c_model, {
                'scl': ['PA13', 'PA15', 'PB8'], 'sda': ['PA14', 'PB7', 'PB9']
            }),
            PeripheralFixedResource('I2C1_T', i2c_target_model, {
                'scl': ['PA13', 'PA15', 'PB8'], 'sda': ['PA14', 'PB7', 'PB9']
            }),
            PeripheralFixedResource('I2C2', i2c_model, {
                'scl': ['PA9'], 'sda': ['PA8', 'PF0']
            }),
            PeripheralFixedResource('I2C2_T', i2c_target_model, {
                'scl': ['PA9'], 'sda': ['PA8', 'PF0']
            }),
            PeripheralFixedResource('I2C3', i2c_model, {
                'scl': ['PA8'], 'sda': ['PB5']
            }),
            PeripheralFixedResource('FDCAN', CanControllerPort(DigitalBidir.empty()), {
                'tx': ['PA12', 'PB9'], 'rx': ['PA11', 'PB8']
            }),
            PeripheralFixedResource('SWD', SwdTargetPort(DigitalBidir.empty()), {
                'swdio': ['PA13'], 'swclk': ['PA14'],
            }),
            PeripheralFixedResource('USB', UsbDevicePort(DigitalBidir.empty()), {
                'dm': ['PA11'], 'dp': ['PA12']
            }),
            PeripheralFixedResource('USBCC', UsbCcPort(pullup_capable=True), {
                'cc1': ['PB6'], 'cc2': ['PB4']
            }),
        ]).remap_pins(self.RESOURCE_PIN_REMAP)

    def generate(self) -> None:
        super().generate()
        self.footprint(
            'U', self.PACKAGE,
            self._make_pinning(),
            mfr='STMicroelectronics', part=self.PART,
            datasheet='https://www.st.com/resource/en/datasheet/stm32g431kb.pdf'
        )
        self.assign(self.lcsc_part, self.LCSC_PART)
        self.assign(self.actual_basic_part, False)


class Stm32g431_G_Device(Stm32g431Base_Device):
    SYSTEM_PIN_REMAP = {
        'Vdd': ['1', '15', '17'],  # 15 VDDA
        'Vss': ['14', '16', '32'],  # 14 VSSA
        'BOOT0': '31',
        'PG10-NRST': '4',
    }
    RESOURCE_PIN_REMAP = {
        'PF0': '2',
        'PF1': '3',
        'PA0': '5',
        'PA1': '6',
        'PA2': '7',
        'PA3': '8',
        'PA4': '9',
        'PA5': '10',
        'PA6': '11',
        'PA7': '12',
        'PA8': '18',
        'PA9': '19',
        'PA10': '20',
        'PA11': '21',
        'PA12': '22',
        'PA13': '23',
        'PA14': '24',
        'PA15': '25',
        'PB0': '13',
        'PB3': '26',
        'PB4': '27',
        'PB5': '28',
        'PB6': '29',
        'PB7': '30',
    }
    PACKAGE = 'Package_DFN_QFN:UFQFPN-32-1EP_5x5mm_P0.5mm_EP3.5x3.5mm'
    PART = 'STM32G431KB'
    LCSC_PART = 'C1341901'  # STM32G431KBU3


@abstract_block
class Stm32g431Base(Resettable, IoControllerI2cTarget, Microcontroller, IoControllerWithSwdTargetConnector,
                    IoControllerPowerRequired, BaseIoControllerExportable, GeneratorBlock):
    DEVICE: Type[Stm32g431Base_Device] = Stm32g431Base_Device

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.ic: Stm32g431Base_Device
        self.generator_param(self.reset.is_connected())

    def contents(self) -> None:
        super().contents()
        with self.implicit_connect(
                ImplicitConnect(self.pwr, [Power]),
                ImplicitConnect(self.gnd, [Common])
        ) as imp:
            self.ic = imp.Block(self.DEVICE(pin_assigns=ArrayStringExpr()))
            self.connect(self.swd_node, self.ic.swd)
            self.connect(self.reset_node, self.ic.nrst)

            # from https://www.st.com/resource/en/application_note/an5093-getting-started-with-stm32g4-series--hardware-development-boards-stmicroelectronics.pdf
            self.pwr_cap0 = imp.Block(DecouplingCapacitor(10 * uFarad(tol=0.2)))
            # from the above pdf, we need 100nF per number of VDD
            self.pwr_cap1 = imp.Block(DecouplingCapacitor(100 * nFarad(tol=0.2)))
            self.pwr_cap2 = imp.Block(DecouplingCapacitor(100 * nFarad(tol=0.2)))
            self.pwr_cap3 = imp.Block(DecouplingCapacitor(100 * nFarad(tol=0.2)))
            self.pwr_cap4 = imp.Block(DecouplingCapacitor(1 * uFarad(tol=0.2)))

    def generate(self) -> None:
        super().generate()
        if self.get(self.reset.is_connected()):
            self.connect(self.reset, self.ic.nrst)  # otherwise NRST has internal pull-up


class Stm32g431kb(Stm32g431Base):
    DEVICE = Stm32g431_G_Device
