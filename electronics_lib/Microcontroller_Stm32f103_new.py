from abc import abstractmethod
from itertools import chain
from typing import *

from electronics_abstract_parts import *
from electronics_lib import OscillatorCrystal, SwdCortexTargetHeader


@abstract_block
class Stm32f103Base_Device(PinMappable, IoController, DiscreteChip, GeneratorBlock, FootprintBlock):
  def __init__(self, **kwargs) -> None:
    super().__init__(**kwargs)

    # Additional ports (on top of IoController)
    self.nrst = self.Port(DigitalSink.from_supply(
      self.vss, self.vdd,
      voltage_limit_tolerance=(-0.3, 0.3)*Volt,  # Table 5.3.1, general operating conditions  TODO: FT IO, BOOT0 IO
      current_draw=(0, 0)*Amp,
      input_threshold_abs=(0.8, 2)*Volt
    ), optional=True)  # note, internal pull-up resistor, 30-50 kOhm by Table 35

    self.osc32 = self.Port(CrystalDriver(frequency_limits=32.768*kHertz(tol=0),  # TODO actual tolerances
                                         voltage_out=self.vdd.link().voltage),
                           optional=True)  # TODO other specs from Table 23
    self.osc = self.Port(CrystalDriver(frequency_limits=(4, 16)*MHertz,
                                       voltage_out=self.vdd.link().voltage),
                         optional=True)  # Table 22

    self.swd = self.Port(SwdTargetPort().empty())

    self.generator(self.generate, self.pin_assigns,
                   self.gpio.allocated(), self.adc.allocated(), self.dac.allocated(),
                   self.spi.allocated(), self.i2c.allocated(), self.uart.allocated(),
                   self.usb.allocated(), self.can.allocated(), self.swd.is_connected())

  def contents(self) -> None:
    super().contents()

    # Ports with shared references
    self.pwr.init_from(VoltageSink(
      voltage_limits=(3.0, 3.6)*Volt,  # TODO relaxed range down to 2.0 if ADC not used, or 2.4 if USB not used
      current_draw=(0, 50.3)*mAmp  # Table 13, TODO propagate current consumption from IO ports
    ))
    self.gnd.init_from(Ground())

    # Port models
    dio_ft_model = DigitalBidir.from_supply(
      self.gnd, self.pwr,
      voltage_limit_abs=(-0.3, 5.2) * Volt,  # Table 5.3.1, general operating conditions, TODO relaxed for Vdd>2v
      current_draw=(0, 0)*Amp, current_limits=(-8, 8)*mAmp,  # Section 5.1.13 Output driving current, TODO relaxed specs with relaxed VOL/VOH
      input_threshold_factor=(0.35, 0.65),  # TODO relaxed (but more complex) bounds available
      pullup_capable=True, pulldown_capable=True
    )
    dio_std_model = DigitalBidir.from_supply(
      self.gnd, self.pwr,
      voltage_limit_tolerance=(-0.3, 0.3)*Volt,  # Table 5.3.1, general operating conditions
      current_draw=(0, 0)*Amp, current_limits=(-8, 8)*mAmp,  # Section 5.1.13 Output driving current, TODO relaxed specs with relaxed VOL/VOH
      input_threshold_factor=(0.35, 0.65),  # TODO relaxed (but more complex) bounds available
      pullup_capable=True, pulldown_capable=True,
    )
    dio_pc_13_14_15_model = DigitalBidir.from_supply(
      self.gnd, self.pwr,
      voltage_limit_tolerance=(-0.3, 0.3)*Volt,  # Table 5.3.1, general operating conditions
      current_draw=(0, 0)*Amp, current_limits=(-3, 3)*mAmp,  # Section 5.1.13 Output driving current
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

    # Pin/peripheral resource definitions (table 3)
    self.system_pinmaps = VariantPinRemapper({
      'Vbat': self.pwr,
      'VddA': self.pwr,
      'VssA': self.gnd,
      'Vss': self.gnd,
      'Vdd': self.pwr,
      'BOOT0': self.gnd,
      'OSC_IN': self.osc.xtal_in,  # TODO remappable to PD0
      'OSC_OUT': self.osc.xtal_out,  # TODO remappable to PD1
      # 'NRST':  # TODO how to handle dedicated reset pin for SWD
    })

    self.abstract_pinmaps = PinMapUtil([  # Table 5, partial table fo 48-pin only
      PinResource('PC13', {'PC13': dio_pc_13_14_15_model}),
      PinResource('PC14', {'PC14': dio_pc_13_14_15_model, 'OSC32_IN': Passive()}),
      PinResource('PC15', {'PC15': dio_pc_13_14_15_model, 'OSC32_OUT': Passive()}),

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
      PinResource('PA13', {'PA13': dio_ft_model}),  # default is JTMS/SWO

      PinResource('PA14', {'PA13': dio_ft_model}),  # default is JTCK/SWCLK
      PinResource('PA15', {'PA15': dio_ft_model}),  # default is JTDI
      PinResource('PB3', {'PB3': dio_ft_model}),  # default is JTDO
      PinResource('PB4', {'PB4': dio_ft_model}),  # default is JNTRST
      PinResource('PB5', {'PB5': dio_std_model}),
      PinResource('PB6', {'PB6': dio_ft_model}),
      PinResource('PB7', {'PB7': dio_ft_model}),
      PinResource('PB8', {'PB8': dio_ft_model}),
      PinResource('PB9', {'PB9': dio_ft_model}),

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
        'tx': ['PA12', 'PD1', 'PB9'], 'rx': ['PA11', 'PD0', 'PB8']
      }),
      PeripheralFixedPin('USB', UsbDevicePort(), {
        'dm': ['PA11'], 'dp': ['PA12']
      }),
      PeripheralFixedResource('SWD', SwdTargetPort(DigitalBidir.empty()), {
        'swdio': ['PA13'], 'swclk': ['PA14'], 'reset': ['NRST'], 'swo': ['PB3'],
      }),
      PeripheralFixedResource('I2C1', i2c_model, {
        'scl': ['PB6', 'PB8'], 'sda': ['PB7', 'PB9']
      }),
    ])

  SYSTEM_PIN_REMAP: Dict[str, Union[str, List[str]]]  # pin name in base -> pin name(s)
  RESOURCE_PIN_REMAP: Dict[str, str]  # resource name in base -> pin name
  PACKAGE: str  # package name for footprint(...)
  PART: str  # part name for footprint(...)

  @abstractmethod
  def generate(self, assignments: str,
               gpio_allocates: List[str], adc_allocates: List[str], dac_allocates: List[str],
               spi_allocates: List[str], i2c_allocates: List[str], uart_allocates: List[str],
               usb_allocates: List[str], can_allocates: List[str], swd_connected: bool) -> None:
    system_pins: Dict[str, CircuitPort] = self.system_pinmaps.remap(self.SYSTEM_PIN_REMAP)

    allocated = self.abstract_pinmaps.remap_pins(self.RESOURCE_PIN_REMAP).allocate([
      (UsbDevicePort, usb_allocates), (SpiMaster, spi_allocates), (I2cMaster, i2c_allocates),
      (UartPort, uart_allocates), (CanControllerPort, can_allocates),
      (SwdTargetPort, ['swd'] if swd_connected else []),
      (AnalogSink, adc_allocates), (AnalogSource, dac_allocates), (DigitalBidir, gpio_allocates),
    ], assignments)

    io_pins = self._instantiate_from([self.gpio, self.adc, self.dac, self.spi, self.i2c, self.uart,
                                      self.usb, self.can, self.swd],
                                     allocated)

    self.footprint(
      'U', self.PACKAGE,
      dict(chain(system_pins.items(), io_pins.items())),
      mfr='NXP', part=self.PART,
      datasheet='https://www.nxp.com/docs/en/data-sheet/LPC15XX.pdf'
    )
