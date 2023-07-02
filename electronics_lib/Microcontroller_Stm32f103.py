from typing import *

from electronics_abstract_parts import *
from .JlcPart import JlcPart


@abstract_block
class Stm32f103Base_Device(InternalSubcircuit, BaseIoControllerPinmapGenerator, GeneratorBlock, JlcPart, FootprintBlock):
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
      voltage_limits=(3.0, 3.6)*Volt,  # TODO relaxed range down to 2.0 if ADC not used, or 2.4 if USB not used
      current_draw=(0, 50.3)*mAmp + self.io_current_draw.upper()  # Table 13
    ), [Power])
    self.gnd = self.Port(Ground(), [Common])

    self.nrst = self.Port(DigitalSink.from_supply(
      self.gnd, self.pwr,
      voltage_limit_tolerance=(-0.3, 0.3)*Volt,  # Table 5.3.1, general operating conditions  TODO: FT IO, BOOT0 IO
      current_draw=(0, 0)*Amp,
      input_threshold_abs=(0.8, 2)*Volt
    ), optional=True)  # note, internal pull-up resistor, 30-50 kOhm by Table 35

    # TODO need to pass through to pin mapper
    # self.osc32 = self.Port(CrystalDriver(frequency_limits=32.768*kHertz(tol=0),  # TODO actual tolerances
    #                                      voltage_out=self.pwr.link().voltage),
    #                        optional=True)  # TODO other specs from Table 23
    self.osc = self.Port(CrystalDriver(frequency_limits=(4, 16)*MHertz,
                                       voltage_out=self.pwr.link().voltage),
                         optional=True)  # Table 22

    self.swd = self.Port(SwdTargetPort().empty())
    self._io_ports.insert(0, self.swd)

  def _system_pinmap(self) -> Dict[str, CircuitPort]:
    return VariantPinRemapper({  # Pin/peripheral resource definitions (table 3)
      'Vbat': self.pwr,
      'VddA': self.pwr,
      'VssA': self.gnd,
      'Vss': self.gnd,
      'Vdd': self.pwr,
      'BOOT0': self.gnd,
      'OSC_IN': self.osc.xtal_in,  # TODO remappable to PD0
      'OSC_OUT': self.osc.xtal_out,  # TODO remappable to PD1
    }).remap(self.SYSTEM_PIN_REMAP)

  def _io_pinmap(self) -> PinMapUtil:
    # Port models
    dio_ft_model = DigitalBidir.from_supply(
      self.gnd, self.pwr,
      voltage_limit_abs=(-0.3, 5.2) * Volt,  # Table 5.3.1, general operating conditions, TODO relaxed for Vdd>2v
      current_draw=(0, 0)*Amp, current_limits=(-20, 20)*mAmp,  # Section 5.3.13 Output driving current, TODO loose with relaxed VOL/VOH
      input_threshold_factor=(0.35, 0.65),  # TODO relaxed (but more complex) bounds available
      pullup_capable=True, pulldown_capable=True
    )
    dio_std_model = DigitalBidir.from_supply(
      self.gnd, self.pwr,
      voltage_limit_tolerance=(-0.3, 0.3)*Volt,  # Table 5.3.1, general operating conditions
      current_draw=(0, 0)*Amp, current_limits=(-20, 20)*mAmp,  # Section 5.3.13 Output driving current, TODO loose with relaxed VOL/VOH
      input_threshold_factor=(0.35, 0.65),  # TODO relaxed (but more complex) bounds available
      pullup_capable=True, pulldown_capable=True,
    )
    dio_pc_13_14_15_model = DigitalBidir.from_supply(
      self.gnd, self.pwr,
      voltage_limit_tolerance=(-0.3, 0.3)*Volt,  # Table 5.3.1, general operating conditions
      current_draw=(0, 0)*Amp, current_limits=(-3, 3)*mAmp,  # Section 5.3.13 Output driving current
      input_threshold_factor=(0.35, 0.65),  # TODO relaxed (but more complex) bounds available
      pullup_capable=True, pulldown_capable=True,
    )

    adc_model = AnalogSink(
      voltage_limits=(self.gnd.link().voltage.lower(), self.pwr.link().voltage.upper()),
      current_draw=(0, 0) * Amp,
      impedance=(100, float('inf')) * kOhm
    )

    uart_model = UartPort(DigitalBidir.empty())
    spi_model = SpiMaster(DigitalBidir.empty())
    i2c_model = I2cMaster(DigitalBidir.empty())

    return PinMapUtil([  # Table 5, partial table for 48-pin only
      PinResource('PA0', {'PA0': dio_std_model, 'ADC12_IN0': adc_model}),
      PinResource('PA1', {'PA1': dio_std_model, 'ADC12_IN1': adc_model}),
      PinResource('PA2', {'PA2': dio_std_model, 'ADC12_IN2': adc_model}),
      PinResource('PA3', {'PA3': dio_std_model, 'ADC12_IN3': adc_model}),
      PinResource('PA4', {'PA4': dio_std_model, 'ADC12_IN4': adc_model}),
      PinResource('PA5', {'PA5': dio_std_model, 'ADC12_IN5': adc_model}),
      PinResource('PA6', {'PA6': dio_std_model, 'ADC12_IN6': adc_model}),
      PinResource('PA7', {'PA7': dio_std_model, 'ADC12_IN7': adc_model}),
      PinResource('PB0', {'PB0': dio_std_model, 'ADC12_IN8': adc_model}),
      PinResource('PB1', {'PB1': dio_std_model, 'ADC12_IN9': adc_model}),

      PinResource('PB2', {'PB2': dio_ft_model}),  # BOOT1
      PinResource('PB10', {'PB10': dio_ft_model}),
      PinResource('PB11', {'PB11': dio_ft_model}),
      PinResource('PB12', {'PB12': dio_ft_model}),
      PinResource('PB13', {'PB13': dio_ft_model}),
      PinResource('PB14', {'PB14': dio_ft_model}),
      PinResource('PB15', {'PB15': dio_ft_model}),

      PinResource('PA8', {'PA8': dio_ft_model}),
      PinResource('PA9', {'PA9': dio_ft_model}),
      PinResource('PA10', {'PA10': dio_ft_model}),
      PinResource('PA11', {'PA11': dio_ft_model}),
      PinResource('PA12', {'PA12': dio_ft_model}),
      # PinResource('PA13', {'PA13': dio_ft_model}),  # forced SWDIO default is JTMS/SWDIO

      # PinResource('PA14', {'PA14': dio_ft_model}),  # forced SWCLK, default is JTCK/SWCLK
      PinResource('PA15', {'PA15': dio_ft_model}),  # default is JTDI
      PinResource('PB3', {'PB3': dio_ft_model}),  # SWO, default is JTDO
      PinResource('PB4', {'PB4': dio_ft_model}),  # default is JNTRST
      PinResource('PB5', {'PB5': dio_std_model}),
      PinResource('PB6', {'PB6': dio_ft_model}),
      PinResource('PB7', {'PB7': dio_ft_model}),
      PinResource('PB8', {'PB8': dio_ft_model}),
      PinResource('PB9', {'PB9': dio_ft_model}),

      # PinResource('NRST', {'NRST': dio_std_model}),  # non-mappable to IO!

      # de-prioritize these for auto-assignment since they're low-current
      PinResource('PC13', {'PC13': dio_pc_13_14_15_model}),
      PinResource('PC14', {'PC14': dio_pc_13_14_15_model, 'OSC32_IN': Passive()}),
      PinResource('PC15', {'PC15': dio_pc_13_14_15_model, 'OSC32_OUT': Passive()}),

      PeripheralFixedResource('USART2', uart_model, {
        'tx': ['PA2', 'PD5'], 'rx': ['PA3', 'PD6']
      }),
      PeripheralFixedResource('SPI1', spi_model, {
        'sck': ['PA5', 'PB3'], 'miso': ['PA6', 'PB4'], 'mosi': ['PA7', 'PB5']
      }),
      PeripheralFixedResource('USART3', uart_model, {
        'tx': ['PB10', 'PD8', 'PC10'], 'rx': ['PB11', 'PD9', 'PC11']
      }),
      PeripheralFixedResource('I2C2', i2c_model, {
        'scl': ['PB10'], 'sda': ['PB11']
      }),
      PeripheralFixedResource('SPI2', spi_model, {
        'sck': ['PB13'], 'miso': ['PB14'], 'mosi': ['PB15']
      }),
      PeripheralFixedResource('USART1', uart_model, {
        'tx': ['PA9', 'PB6'], 'rx': ['PA10', 'PB7']
      }),
      PeripheralFixedResource('CAN', CanControllerPort(DigitalBidir.empty()), {
        'txd': ['PA12', 'PD1', 'PB9'], 'rxd': ['PA11', 'PD0', 'PB8']
      }),
      PeripheralFixedResource('USB', UsbDevicePort(DigitalBidir.empty()), {
        'dm': ['PA11'], 'dp': ['PA12']
      }),
      PeripheralFixedPin('SWD', SwdTargetPort(dio_std_model), {  # TODO most are FT pins
        'swdio': 'PA13', 'swclk': 'PA14', 'reset': 'NRST'  # note: SWO is PB3
      }),
      PeripheralFixedResource('I2C1', i2c_model, {
        'scl': ['PB6', 'PB8'], 'sda': ['PB7', 'PB9']
      }),
    ]).remap_pins(self.RESOURCE_PIN_REMAP)

  def generate(self) -> None:
    super().generate()

    self.footprint(
      'U', self.PACKAGE,
      self._make_pinning(),
      mfr='STMicroelectronics', part=self.PART,
      datasheet='https://www.st.com/resource/en/datasheet/stm32f103c8.pdf'
    )
    self.assign(self.lcsc_part, self.LCSC_PART)
    self.assign(self.actual_basic_part, self.LCSC_BASIC_PART)


class Stm32f103_48_Device(Stm32f103Base_Device):
  SYSTEM_PIN_REMAP = {
    'Vbat': '1',
    'VddA': '9',
    'VssA': '8',
    'Vss': ['23', '35', '47'],
    'Vdd': ['24', '36', '48'],
    'BOOT0': '44',
    'OSC_IN': '5',
    'OSC_OUT': '6',
  }
  RESOURCE_PIN_REMAP = {
    'PC13': '2',
    'PC14': '3',
    'PC15': '4',
    'NRST': '7',

    'PA0': '10',
    'PA1': '11',
    'PA2': '12',
    'PA3': '13',
    'PA4': '14',
    'PA5': '15',
    'PA6': '16',
    'PA7': '17',
    'PB0': '18',
    'PB1': '19',

    'PB2': '20',
    'PB10': '21',
    'PB11': '22',
    'PB12': '25',
    'PB13': '26',
    'PB14': '27',
    'PB15': '28',

    'PA8': '29',
    'PA9': '30',
    'PA10': '31',
    'PA11': '32',
    'PA12': '33',
    'PA13': '34',

    'PA14': '37',
    'PA15': '38',
    'PB3': '39',
    'PB4': '40',
    'PB5': '41',
    'PB6': '42',
    'PB7': '43',

    'PB8': '45',
    'PB9': '46',
  }
  PACKAGE = 'Package_QFP:LQFP-48_7x7mm_P0.5mm'
  PART = 'STM32F103xxT6'
  LCSC_PART = 'C8734'  # C8T6 variant - basic part
  # C77994 for GD32F103C8T6, probably mostly drop-in compatible, NOT basic part
  LCSC_BASIC_PART = True


class UsbDpPullUp(InternalSubcircuit, Block):
  @init_in_parent
  def __init__(self, resistance: RangeLike):
    super().__init__()
    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.usb = self.Port(UsbPassivePort.empty(), [InOut])

    self.dp = self.Block(Resistor(resistance))
    self.connect(self.dp.a.adapt_to(VoltageSink()), self.pwr)
    self.connect(self.usb.dp, self.dp.b.adapt_to(DigitalBidir()))  # ideal
    self.usb.dm.init_from(DigitalBidir())  # ideal


@abstract_block
class Stm32f103Base(Microcontroller, IoControllerWithSwdTargetConnector, WithCrystalGenerator,
                    IoControllerPowerRequired, BaseIoControllerExportable):
  DEVICE: Type[Stm32f103Base_Device] = Stm32f103Base_Device  # type: ignore
  DEFAULT_CRYSTAL_FREQUENCY = 12*MHertz(tol=0.005)

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.ic: Stm32f103Base_Device

  def contents(self):
    super().contents()

    with self.implicit_connect(
        ImplicitConnect(self.pwr, [Power]),
        ImplicitConnect(self.gnd, [Common])
    ) as imp:
      self.ic = imp.Block(self.DEVICE(pin_assigns=ArrayStringExpr()))
      self.connect(self.xtal_node, self.ic.osc)
      self.connect(self.swd_node, self.ic.swd)

      self.pwr_cap = ElementDict[DecouplingCapacitor]()
      # one 0.1uF cap each for Vdd1-5 and one bulk 4.7uF cap
      self.pwr_cap[0] = imp.Block(DecouplingCapacitor(4.7 * uFarad(tol=0.2)))
      for i in range(1, 4):
        self.pwr_cap[i] = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))

      # one 10nF and 1uF cap for VddA TODO generate the same cap if a different Vref is used
      self.vdda_cap_0 = imp.Block(DecouplingCapacitor(10 * nFarad(tol=0.2)))
      self.vdda_cap_1 = imp.Block(DecouplingCapacitor(1 * uFarad(tol=0.2)))

  def _make_export_io(self, self_io: Port, inner_io: Port):
    if isinstance(self_io, UsbDevicePort):  # assumed at most one USB port generates
      self.usb_pull = self.Block(UsbDpPullUp(resistance=1.5*kOhm(tol=0.01)))  # required by datasheet Table 44  # TODO proper tolerancing?
      self.connect(self.usb_pull.pwr, self.pwr)
      self.connect(inner_io, self_io, self.usb_pull.usb)
    else:
      super()._make_export_io(self_io, inner_io)

  def _crystal_required(self) -> bool:  # crystal needed for CAN or USB b/c tighter freq tolerance
    return len(self.get(self.can.requested())) > 0 or len(self.get(self.usb.requested())) > 0 \
        or super()._crystal_required()


class Stm32f103_48(Stm32f103Base):
  DEVICE = Stm32f103_48_Device
