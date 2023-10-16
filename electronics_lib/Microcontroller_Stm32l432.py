from typing import *

from electronics_abstract_parts import *
from .JlcPart import JlcPart


@abstract_block
class Stm32l432Base_Device(IoControllerI2cTarget, IoControllerDac, IoControllerCan, IoControllerUsb, InternalSubcircuit,
                           BaseIoControllerPinmapGenerator, GeneratorBlock, JlcPart, FootprintBlock):
    PACKAGE: str  # package name for footprint(...)
    PART: str  # part name for footprint(...)
    LCSC_PART: str
    LCSC_BASIC_PART: bool

    SYSTEM_PIN_REMAP: Dict[str, Union[str, List[str]]]  # pin name in base -> pin name(s)
    RESOURCE_PIN_REMAP: Dict[str, str]  # resource name in base -> pin name

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        # Additional ports (on top of BaseIoController)
        self.gnd = self.Port(Ground(), [Common])
        self.pwr = self.Port(VoltageSink(
            voltage_limits=(self.usb.length() > 0).then_else((3.0, 3.6)*Volt,
                                                             (self.dac.length() > 0).then_else((1.8, 3.6)*Volt,
                                                                                               (1.71, 3.6)*Volt)),
            current_draw=(0.00000782, 10.3)*mAmp + self.io_current_draw.upper()  # Table 25 (run), 37 (shutdown)
        ), [Power])
        self.swd = self.Port(SwdTargetPort.empty())
        self._io_ports.insert(0, self.swd)

        self.nrst = self.Port(DigitalBidir.empty())

    def _system_pinmap(self) -> Dict[str, CircuitPort]:
        return VariantPinRemapper({  # Pin/peripheral resource definitions (section 4)
            'Vdd': self.pwr,
            'VddA': self.pwr,
            'Vss': self.gnd,
            'NRST': self.nrst,
        }).remap(self.SYSTEM_PIN_REMAP)

    def _io_pinmap(self) -> PinMapUtil:
        # Port models
        input_range = self.gnd.link().voltage.hull(self.pwr.link().voltage)
        # tt is 3.6v tolerant IO, ft (and all except tt_xx) is 5v tolerant IO
        tt_voltage_limit = input_range + (-0.3, 0.3)*Volt
        io_voltage_limit = (input_range + (-0.3, 3.6)*Volt).intersect(self.gnd.link().voltage + (-0.3, 5.5)*Volt)
        dio_tta_model = DigitalBidir.from_supply(
            self.gnd, self.pwr,
            voltage_limit_abs=tt_voltage_limit,
            current_limits=(-20, 20)*mAmp,  # Table 19
            input_threshold_factor=(0.3, 0.7),  # section 6.3.14, simplest for 1.62<Vdd<3.6
            pullup_capable=True, pulldown_capable=True
        )
        dio_ft_model = dio_fta_model = dio_ftf_model = dio_ftfa_model = dio_ftu_model = DigitalBidir.from_supply(
            self.gnd, self.pwr,
            voltage_limit_abs=io_voltage_limit,
            current_limits=(-20, 20)*mAmp,  # Table 19
            input_threshold_factor=(0.3, 0.7),  # section 6.3.14, simplest for 1.62<Vdd<3.6
            pullup_capable=True, pulldown_capable=True
        )
        self.nrst.init_from(dio_ft_model)

        adc_tt_model = AnalogSink.from_supply(
            self.gnd, self.pwr,
            voltage_limit_abs=tt_voltage_limit,
            signal_limit_tolerance=(0, 0),  # conversion voltage range, VssA to Vref+ (assumed VddA)
            impedance=(50, float('inf'))*kOhm  # max external impedance
        )
        adc_ft_model = AnalogSink.from_supply(
            self.gnd, self.pwr,
            voltage_limit_abs=io_voltage_limit,
            signal_limit_tolerance=(0, 0),  # conversion voltage range, VssA to Vref+ (assumed VddA)
            impedance=(50, float('inf'))*kOhm  # max external impedance
        )
        dac_model = AnalogSource.from_supply(
            self.gnd, self.pwr,
            signal_out_bound=(0, 0),  # 0-Vref w/ DAC output buffer off
            impedance=(9.6, 13.8)*kOhm  # DAC buffer off
        )

        uart_model = UartPort(DigitalBidir.empty())
        spi_model = SpiController(DigitalBidir.empty())
        # TODO SPI peripherals, which have fixed-pin CS lines
        i2c_model = I2cController(DigitalBidir.empty())
        i2c_target_model = I2cTarget(DigitalBidir.empty())

        return PinMapUtil([  # Table 12, partial table for up to 32-pin only
            PinResource('PC14', {'PC14': dio_ft_model}),  # OSC32_IN
            PinResource('PC15', {'PC15': dio_ft_model}),  # OSC32_OUT
            PinResource('PA0', {'PA0': dio_fta_model, 'ADC1_IN5': adc_ft_model}),
            PinResource('PA1', {'PA1': dio_fta_model, 'ADC_1IN6': adc_ft_model}),
            PinResource('PA2', {'PA2': dio_fta_model, 'ADC_1IN7': adc_ft_model}),
            PinResource('PA3', {'PA3': dio_tta_model, 'ADC_1IN8': adc_ft_model}),
            PinResource('PA4', {'PA4': dio_tta_model, 'ADC_1IN9': adc_tt_model, 'DAC1_OUT1': dac_model}),
            PinResource('PA5', {'PA5': dio_tta_model, 'ADC_1IN10': adc_tt_model, 'DAC1_OUT2': dac_model}),
            PinResource('PA6', {'PA6': dio_fta_model, 'ADC_1IN10': adc_ft_model}),

            PinResource('PA7', {'PA7': dio_fta_model, 'ADC_1IN12': adc_ft_model}),
            PinResource('PB0', {'PB0': dio_fta_model, 'ADC_1IN15': adc_ft_model}),
            PinResource('PB1', {'PB1': dio_fta_model, 'ADC_1IN16': adc_ft_model}),
            PinResource('PA8', {'PA8': dio_ft_model}),
            PinResource('PA9', {'PA8': dio_ftf_model}),
            PinResource('PA10', {'PA10': dio_ftf_model}),
            PinResource('PA11', {'PA11': dio_ftu_model}),
            PinResource('PA12', {'PA12': dio_ftu_model}),
            PinResource('PA13', {'PA13': dio_ft_model}),

            PinResource('PA14', {'PA14': dio_ft_model}),
            PinResource('PA15', {'PA15': dio_ft_model}),
            PinResource('PB3', {'PB3': dio_fta_model}),
            PinResource('PB4', {'PB4': dio_ftfa_model}),
            PinResource('PB5', {'PB5': dio_ft_model}),
            PinResource('PB6', {'PB6': dio_ftfa_model}),
            PinResource('PB7', {'PB7': dio_ftfa_model}),
            PinResource('PH3', {'PH3': dio_ft_model}),  # BOOT0

            PeripheralFixedResource('SPI1', spi_model, {
                'sck': ['PA1', 'PA5', 'PB3'], 'miso': ['PA6', 'PA11', 'PB4'], 'mosi': ['PA7', 'PA12', 'PB5']
            }),
            PeripheralFixedResource('USART2', uart_model, {
                'tx': ['PA2'], 'rx': ['PA3', 'PA15']
            }),
            PeripheralFixedResource('LPUART1', uart_model, {
                'tx': ['PA2'], 'rx': ['PA3']
            }),
            PeripheralFixedResource('I2C3', i2c_model, {
                'scl': ['PA7'], 'sda': ['PB4']
            }),
            PeripheralFixedResource('I2C3_T', i2c_target_model, {  # TODO shared resource w/ I2C controller
                'scl': ['PA7'], 'sda': ['PB4']
            }),
            PeripheralFixedResource('I2C1', i2c_model, {
                'scl': ['PA9', 'PB6'], 'sda': ['PA10', 'PB7']
            }),
            PeripheralFixedResource('I2C1_T', i2c_target_model, {  # TODO shared resource w/ I2C controller
                'scl': ['PA9', 'PB6'], 'sda': ['PA10', 'PB7']
            }),
            PeripheralFixedResource('USART2', uart_model, {
                'tx': ['PA9'], 'rx': ['PA10']
            }),
            PeripheralFixedResource('CAN', CanControllerPort(DigitalBidir.empty()), {
                'tx': ['PA12'], 'rx': ['PA11']
            }),
            PeripheralFixedResource('USB', UsbDevicePort.empty(), {
                'dp': ['PA12'], 'dm': ['PA11']
            }),
            PeripheralFixedResource('SPI3', spi_model, {
                'sck': ['PB3'], 'miso': ['PB4'], 'mosi': ['PB5']
            }),
            PeripheralFixedResource('USART1', uart_model, {
                'tx': ['PB6'], 'rx': ['PB7']
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
            datasheet='https://www.st.com/resource/en/datasheet/stm32l432kc.pdf'
        )
        self.assign(self.lcsc_part, self.LCSC_PART)
        self.assign(self.actual_basic_part, False)


class Stm32l432k_Device(Stm32l432Base_Device):
    """"STM32L432Kx in UFQFPN32 package."""
    SYSTEM_PIN_REMAP = {
        'Vdd': ['17', '1'],
        'Vss': ['16', '32', '33'],  # recommended to connect EP to PCB ground
        'VddA': '5',
        'NRST': '4',
    }
    RESOURCE_PIN_REMAP = {
        'PC14': '2',
        'PC15': '3',
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
        'PA8': '18',
        'PA9': '19',
        'PA10': '20',
        'PA11': '21',
        'PA12': '22',
        'PA13': '23',

        'PA14': '24',
        'PA15': '25',
        'PB3': '26',
        'PB4': '27',
        'PB5': '28',
        'PB6': '29',
        'PB7': '30',
        'PH3': '31',
    }
    PACKAGE = 'Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm'
    PART = 'STM32L432Kxxx'
    LCSC_PART = 'C94784'  # KBU6 variant


@abstract_block
class Stm32l432Base(Resettable, IoControllerDac, IoControllerCan, IoControllerUsb, IoControllerI2cTarget,
                    Microcontroller, IoControllerWithSwdTargetConnector, WithCrystalGenerator,
                    IoControllerPowerRequired, BaseIoControllerExportable, GeneratorBlock):
    DEVICE: Type[Stm32l432Base_Device] = Stm32l432Base_Device  # type: ignore

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ic: Stm32l432Base_Device
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

            # from datasheet power supply scheme
            self.vdd_cap_bulk = imp.Block(DecouplingCapacitor(4.7*uFarad(tol=0.2)))
            self.vdd_cap = ElementDict[DecouplingCapacitor]()
            for i in range(2):  # one for each Vdd/Vss pair
                self.vdd_cap[i] = imp.Block(DecouplingCapacitor(0.1*uFarad(tol=0.2)))
            self.vdda_cap0 = imp.Block(DecouplingCapacitor(10*nFarad(tol=0.2)))
            self.vdda_cap1 = imp.Block(DecouplingCapacitor(1*uFarad(tol=0.2)))

    def generate(self):
        super().generate()

        if self.get(self.reset.is_connected()):
            self.connect(self.reset, self.ic.nrst)  # otherwise NRST has internal pull-up

    def _crystal_required(self) -> bool:  # crystal needed for CAN b/c tighter freq tolerance
        # note: no crystal needed for USB, has clock recovery system (CRS) trimming for USB only
        return len(self.get(self.can.requested())) > 0 or super()._crystal_required()


class Stm32l432k(Stm32l432Base):
    DEVICE = Stm32l432k_Device
