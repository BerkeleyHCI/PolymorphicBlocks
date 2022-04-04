from itertools import chain
from typing import *

from electronics_abstract_parts import *


class Stm32f303Base_Device():
  @staticmethod
  def mappable_ios(gnd: Union[VoltageSource, VoltageSink], vdd: Union[VoltageSource, VoltageSink],
                   vdda: Union[VoltageSource, VoltageSink]) -> PinMapUtil:
    """Returns the mappable for a STM32F303 device with the input power and ground references.
    This allows a shared definition between discrete chips and microcontroller boards"""
    # these are common to all IO blocks
    input_threshold_factor = (0.3, 0.7)  # TODO relaxed (but more complex) bounds available for different IO blocks
    current_limits = (-20, 20)*mAmp  # Section 6.3.14, TODO loose with relaxed VOL/VOH
    dio_tc_model = DigitalBidir.from_supply(
      gnd, vdd,
      voltage_limit_abs=(-0.3, 0.3) * Volt,  # Table 19
      current_draw=(0, 0)*Amp, current_limits=current_limits,
      input_threshold_factor=input_threshold_factor,
      pullup_capable=True, pulldown_capable=True
    )
    dio_tt_model = DigitalBidir.from_supply(
      gnd, vdd,
      voltage_limit_abs=(-0.3, 3.6) * Volt,  # Table 19
      current_draw=(0, 0)*Amp, current_limits=current_limits,
      input_threshold_factor=input_threshold_factor,
      pullup_capable=True, pulldown_capable=True
    )
    dio_tta_model = DigitalBidir.from_supply(
      gnd, vdd,
      voltage_limit_abs=(-0.3, vdda.link().voltage.lower() + 0.3) * Volt,  # Table 19
      current_draw=(0, 0)*Amp, current_limits=current_limits,
      input_threshold_factor=input_threshold_factor,
      pullup_capable=True, pulldown_capable=True
    )
    dio_ft_model = DigitalBidir.from_supply(
      gnd, vdd,
      voltage_limit_abs=(-0.3, 5.5) * Volt,  # Table 19
      current_draw=(0, 0)*Amp, current_limits=current_limits,
      input_threshold_factor=input_threshold_factor,
      pullup_capable=True, pulldown_capable=True
    )
    dio_ftf_model = dio_ft_model
    dio_boot0_model = DigitalBidir.from_supply(
      gnd, vdd,
      voltage_limit_abs=(-0.3, 5.5) * Volt,  # Table 19
      current_draw=(0, 0)*Amp, current_limits=current_limits,
      input_threshold_factor=input_threshold_factor,
      pullup_capable=True, pulldown_capable=True
    )

    adc_model = AnalogSink(
      voltage_limits=(-0.3, 3.6) * Volt,
      current_draw=(0, 0) * Amp,
      impedance=100*kOhm(tol=0)  # TODO: actually spec'd as maximum external impedance; internal impedance not given
    )
    dac_model = AnalogSource(
      voltage_out=(0.2, 3.1) * Volt,  # TODO should derive from common rail
      current_limits=(0, 0) * Amp,  # TODO not given by spec
      impedance=15*kOhm(tol=0)  # assumes buffer off
    )

    uart_model = UartPort(DigitalBidir.empty())
    spi_model = SpiMaster(DigitalBidir.empty())
    i2c_model = I2cMaster(DigitalBidir.empty())

    return PinMapUtil([  # Table 5, partial table for 48-pin only
      PinResource('PC13', {'PC13': dio_tc_model}),
      PinResource('PC14', {'PC14': dio_tc_model}),  # TODO remappable to OSC32_IN
      PinResource('PC15', {'PC15': dio_tc_model}),  # TODO remappable to OSC32_OUT
      PinResource('PF0', {'PF0': dio_ft_model}),  # TODO remappable to OSC_OUT
      PinResource('PF1', {'PF1': dio_ft_model}),  # TODO remappable to OSC_OUT

      PinResource('PA0', {'PA0': dio_tta_model, 'ADC1_IN1': adc_model}),
      PinResource('PA1', {'PA1': dio_tta_model, 'ADC1_IN2': adc_model}),
      PinResource('PA2', {'PA2': dio_tta_model, 'ADC1_IN3': adc_model}),
      PinResource('PA3', {'PA3': dio_tta_model, 'ADC1_IN4': adc_model}),
      PinResource('PA4', {'PA4': dio_tta_model, 'ADC2_IN1': adc_model, 'DAC1_OUT1': dac_model}),
      PinResource('PA5', {'PA5': dio_tta_model, 'ADC2_IN2': adc_model, 'DAC1_OUT2': dac_model}),







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
      # PinResource('PA13', {'PA13': dio_ft_model}),  # forced SWDIO default is JTMS/SWDIO

      # PinResource('PA14', {'PA14': dio_ft_model}),  # forced SWCLK, default is JTCK/SWCLK
      PinResource('PA15', {'PA15': dio_ft_model}),  # default is JTDI
      # PinResource('PB3', {'PB3': dio_ft_model}),  # forced SWO, default is JTDO
      PinResource('PB4', {'PB4': dio_ft_model}),  # default is JNTRST
      PinResource('PB5', {'PB5': dio_std_model}),
      PinResource('PB6', {'PB6': dio_ft_model}),
      PinResource('PB7', {'PB7': dio_ft_model}),
      PinResource('PB8', {'PB8': dio_ft_model}),
      PinResource('PB9', {'PB9': dio_ft_model}),

      # PinResource('NRST', {'NRST': dio_std_model}),  # non-mappable to IO!

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
      PeripheralFixedResource('USB', UsbDevicePort(DigitalBidir.empty()), {
        'dm': ['PA11'], 'dp': ['PA12']
      }),
      PeripheralFixedPin('SWD', SwdTargetPort(dio_std_model), {  # TODO most are FT pins
        'swdio': ['PA13'], 'swclk': ['PA14'], 'reset': ['NRST'], 'swo': ['PB3'],
      }),
      PeripheralFixedResource('I2C1', i2c_model, {
        'scl': ['PB6', 'PB8'], 'sda': ['PB7', 'PB9']
      }),
    ])


class Nucleo_F303k8(Microcontroller, FootprintBlock, AssignablePinBlock):  # TODO refactor with _Device
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


class Nucleo_F303k8_new(PinMappable, IoController, GeneratorBlock, FootprintBlock):
  """Nucleo32 F303K8 configured as power source from USB."""
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.usb.defined()  # no usb support

  def generate(self, assignments: str,
               gpio_allocates: List[str], adc_allocates: List[str], dac_allocates: List[str],
               spi_allocates: List[str], i2c_allocates: List[str], uart_allocates: List[str],
               can_allocates: List[str]) -> None:
    self.footprint(
      'U', 'edg:Nucleo32',
      all_pins,
      mfr='STMicroelectronics', part='NUCLEO-F303K8',
      datasheet='https://www.st.com/resource/en/user_manual/dm00231744.pdf',
    )
