from typing import *

from electronics_abstract_parts import *


@abstract_block
class Stm32f303Base_Device(BaseIoControllerPinmapGenerator):
  """Base class for STM32F303 devices.
  Unlike other microcontrollers, this one also supports dev boards (Nucleo-32) which can be
  a power source, so there's a bit more complexity here."""
  SYSTEM_PIN_REMAP: Dict[str, Union[str, List[str]]]
  RESOURCE_PIN_REMAP: Dict[str, str]

  def __init__(self):
    super().__init__()

    # this provides a layer of indirection to allow power to be either a sink or source,
    # based on whether this is a chip or dev board
    self._gnd: CircuitPort[VoltageLink]
    self._vdd: CircuitPort[VoltageLink]
    self._vdda: CircuitPort[VoltageLink]

  def _system_pinmap(self) -> Dict[str, CircuitPort]:
    return VariantPinRemapper({
      # TODO remapping currently doesn't work for these which are chip-only (not on dev board) pins
      # 'Vbat': self._vdd,
      # 'VddA': self._vdda,
      # 'VssA': self._gnd,
      'Vss': self._gnd,
      'Vdd': self._vdd,
      # 'BOOT0': self._gnd,
    }).remap(self.SYSTEM_PIN_REMAP)

  def _io_pinmap(self) -> PinMapUtil:
    """Returns the mappable for a STM32F303 device with the input power and ground references.
    This allows a shared definition between discrete chips and microcontroller boards"""
    # these are common to all IO blocks
    input_threshold_factor = (0.3, 0.7)  # TODO relaxed (but more complex) bounds available for different IO blocks
    current_limits = (-20, 20)*mAmp  # Section 6.3.14, TODO loose with relaxed VOL/VOH
    dio_tc_model = DigitalBidir.from_supply(
      self._gnd, self._vdd,
      voltage_limit_abs=(-0.3, 0.3) * Volt,  # Table 19
      current_draw=(0, 0)*Amp, current_limits=current_limits,
      input_threshold_factor=input_threshold_factor,
      pullup_capable=True, pulldown_capable=True
    )
    dio_tc_switch_model = DigitalBidir.from_supply(
      self._gnd, self._vdd,
      voltage_limit_abs=(-0.3, 0.3) * Volt,  # Table 19
      current_draw=(0, 0)*Amp, current_limits=(-3, 0),  # Table 13, note 1, can sink 3 mA and should not source current
      input_threshold_factor=input_threshold_factor,
      pullup_capable=True, pulldown_capable=True
    )
    dio_tt_model = DigitalBidir.from_supply(
      self._gnd, self._vdd,
      voltage_limit_abs=(-0.3, 3.6) * Volt,  # Table 19
      current_draw=(0, 0)*Amp, current_limits=current_limits,
      input_threshold_factor=input_threshold_factor,
      pullup_capable=True, pulldown_capable=True
    )
    dio_tta_model = DigitalBidir.from_supply(
      self._gnd, self._vdd,
      voltage_limit_abs=(-0.3 * Volt, self._vdda.link().voltage.lower() + 0.3 * Volt),  # Table 19
      current_draw=(0, 0)*Amp, current_limits=current_limits,
      input_threshold_factor=input_threshold_factor,
      pullup_capable=True, pulldown_capable=True
    )
    dio_ft_model = DigitalBidir.from_supply(
      self._gnd, self._vdd,
      voltage_limit_abs=(-0.3, 5.5) * Volt,  # Table 19
      current_draw=(0, 0)*Amp, current_limits=current_limits,
      input_threshold_factor=input_threshold_factor,
      pullup_capable=True, pulldown_capable=True
    )
    dio_ftf_model = dio_ft_model
    dio_boot0_model = DigitalBidir.from_supply(
      self._gnd, self._vdd,
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

    return PinMapUtil([  # Table 13, partial table for 48-pin only
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

      PinResource('PA6', {'PA6': dio_tta_model, 'ADC2_IN3': adc_model, 'DAC2_OUT1': dac_model}),
      PinResource('PA7', {'PA7': dio_tta_model, 'ADC2_IN4': adc_model}),
      PinResource('PB0', {'PB0': dio_tta_model, 'ADC1_IN11': adc_model}),
      PinResource('PB1', {'PB1': dio_tta_model, 'ADC1_IN12': adc_model}),
      PinResource('PB2', {'PB2': dio_tta_model, 'ADC2_IN12': adc_model}),
      PinResource('PB10', {'PB10': dio_tt_model}),
      PinResource('PB11', {'PB11': dio_tta_model}),
      PinResource('PB12', {'PB12': dio_tta_model, 'ADC2_IN13': adc_model}),
      PinResource('PB13', {'PB13': dio_tta_model, 'ADC1_IN13': adc_model}),
      PinResource('PB14', {'PB14': dio_tta_model, 'ADC2_IN14': adc_model}),

      PinResource('PB15', {'PB15': dio_tta_model, 'ADC2_IN15': adc_model}),
      PinResource('PA8', {'PA8': dio_ft_model}),
      PinResource('PA9', {'PA9': dio_ft_model}),
      PinResource('PA10', {'PA10': dio_ft_model}),
      PinResource('PA11', {'PA11': dio_ft_model}),
      PinResource('PA12', {'PA12': dio_ft_model}),
      PinResource('PA13', {'PA13': dio_ft_model}),  # also JTMS/SWDAT

      PinResource('PA14', {'PA14': dio_ftf_model}),  # also JTCK/SWCLK
      PinResource('PA15', {'PA15': dio_ftf_model}),  # also JTDI
      PinResource('PB3', {'PB3': dio_ft_model}),  # also JTDO/TRACESWO
      PinResource('PB4', {'PB4': dio_ft_model}),
      PinResource('PB5', {'PB5': dio_ft_model}),
      PinResource('PB6', {'PB6': dio_ftf_model}),
      PinResource('PB7', {'PB7': dio_ftf_model}),

      PinResource('PB8', {'PB8': dio_ftf_model}),
      PinResource('PB9', {'PB9': dio_ftf_model}),

      PeripheralFixedResource('USART2', uart_model, {
        'tx': ['PA2', 'PA14', 'PB3'], 'rx': ['PA3', 'PA15', 'PB4']
      }),
      PeripheralFixedResource('SPI1', spi_model, {
        'sck': ['PA5', 'PB3'], 'miso': ['PA6', 'PB4'], 'mosi': ['PA7', 'PB5']
      }),
      PeripheralFixedResource('USART3', uart_model, {  # 1/3 check
        'tx': ['PB10', 'PC10', 'PB9'], 'rx': ['PB11', 'PC11', 'PB8']
      }),
      PeripheralFixedResource('USART1', uart_model, {
        'tx': ['PA9', 'PB6'], 'rx': ['PA10', 'PB7']
      }),
      PeripheralFixedResource('CAN', CanControllerPort(DigitalBidir.empty()), {
        'tx': ['PA12', 'PB9'], 'rx': ['PA11', 'PB8']
      }),
      PeripheralFixedResource('I2C1', i2c_model, {
        'scl': ['PA15', 'PB6', 'PB8'], 'sda': ['PA14', 'PB7', 'PB9']
      }),

      PeripheralFixedPin('SWD', SwdTargetPort(dio_ft_model), {  # TODO some are FTf pins
        'swdio': 'PA13', 'swclk': 'PA14', 'reset': 'NRST'  # note: SWO is PB3
      }),
    ]).remap_pins(self.RESOURCE_PIN_REMAP)


class Nucleo_F303k8(Stm32f303Base_Device, GeneratorBlock, FootprintBlock):
  """Nucleo32 F303K8 configured as power source from USB."""
  SYSTEM_PIN_REMAP = {
    'Vss': ['4', '17'],
    'Vdd': '29',
  }
  RESOURCE_PIN_REMAP = {
    'PA9': '1',  # CN3.1, D1
    'PA10': '2',  # CN3.2, D0
    # 'NRST': '3'  # CN3.3, RESET
    'PA12': '5',  # CN3.5, D2
    'PB0': '6',  # CN3.6, D3
    'PB7': '7',  # CN3.7, D4
    'PB6': '8',  # CN3.8, D5
    'PB1': '9',  # CN3.9, D6
    'PF0': '10',  # CN3.10, D7
    'PF1': '11',  # CN3.11, D8
    'PA8': '12',  # CN3.12, D9
    'PA11': '13',  # CN3.13, D10
    'PB5': '14',  # CN3.14, D11
    'PB4': '15',  # CN3.15, D12

    # 'NRST': '18'  # CN4.3, RESET
    'PA2': '20',  # CN4.5, A7
    'PA7': '21',  # CN4.6, A6
    'PA6': '22',  # CN4.7, A5
    'PA5': '23',  # CN4.8, A4
    'PA4': '24',  # CN4.9, A3
    'PA3': '25',  # CN4.10, A2
    'PA1': '26',  # CN4.11, A1
    'PA0': '27',  # CN4.12, A0
    'PB3': '30',  # CN4.15, D13
  }

  def __init__(self):
    super().__init__()

    self.pwr_5v = self.Port(VoltageSource(
      voltage_out=(4.75 - 0.58, 5.1) * Volt,  # 4.75V USB - 0.58v BAT60JFILM drop to 5.1 from LD1117S50TR, ignoring ST890CDR
      current_limits=(0, 0.5) * Amp  # max USB draw  # TODO higher from external power
    ), optional=True)
    self.pwr_in = self.Port(VoltageSink(
      voltage_limits=(5.1 + 1.2 + 0.58, 15) * Volt,  # lower from 5v out + LD1117S50TR dropout + BAT60JFILM diode
      # TODO can be lower if don't need 5.0v out
      current_draw=(0, 0) * Amp  # TODO current draw specs, the part doesn't really have a datasheet
    ), optional=True)
    self.pwr_3v3 = self.Port(VoltageSource(
      voltage_out=3.3 * Volt(tol=0.03),  # LD39050PU33R worst-case Vout accuracy
      current_limits=(0, 0.5) * Amp  # max USB current draw, LDO also guarantees 500mA output current
    ), optional=True)
    self.gnd = self.Port(GroundSource(), optional=True)

    self._vdd = self.pwr_3v3
    self._vdda = self.pwr_3v3
    self._gnd = self.gnd

  def generate(self) -> None:
    super().generate()

    footprint_pinning = self._make_pinning()
    footprint_pinning.update({  # the 5v+ input and Vbus out are Nucleo-32 specific
      '16': self.pwr_in,
      '19': self.pwr_5v,
    })
    self.footprint(
      'U', 'edg:Nucleo32',
      footprint_pinning,
      mfr='STMicroelectronics', part='NUCLEO-F303K8',
      datasheet='https://www.st.com/resource/en/user_manual/dm00231744.pdf',
    )
