from abc import abstractmethod
from itertools import chain
from typing import *

from electronics_abstract_parts import *


@abstract_block
class Lpc1549BaseNew_Device(IoController, DiscreteChip, GeneratorBlock, FootprintBlock, PinMappable):
  @init_in_parent
  def __init__(self) -> None:
    super().__init__()

    # Ports with shared references
    self.vdd = self.Port(VoltageSink(
      voltage_limits=(2.4, 3.6) * Volt,
      current_draw=(0, 19)*mAmp,  # rough guesstimate from Figure 11.1 for supply Idd (active mode)
    ), [Power])
    self.vss = self.Port(Ground(), [Common])

    # Port models
    dio_5v_model = DigitalBidir.from_supply(
      self.vss, self.vdd,
      voltage_limit_abs=(0, 5) * Volt,
      current_draw=(0, 0) * Amp,
      current_limits=(-50, 45) * mAmp,
      input_threshold_factor=(0.3, 0.7),
      pullup_capable=True, pulldown_capable=True
    )
    dio_non5v_model = DigitalBidir.from_supply(  # only used when overlapped w/ DAC PIO0_12
      self.vss, self.vdd,  # up to VddA
      voltage_limit_tolerance=(0, 0) * Volt,
      current_draw=(0, 0) * Amp,
      current_limits=(-50, 45) * mAmp,
      input_threshold_factor=(0.3, 0.7),
      pullup_capable=True, pulldown_capable=True
    )
    dio_highcurrrent_model = DigitalBidir.from_supply(  # only used for PIO0_24
      self.vss, self.vdd,
      voltage_limit_abs=(0, 5) * Volt,
      current_draw=(0, 0) * Amp,
      current_limits=(-50, 20) * mAmp,  # TODO: 12mA when Vdd < 2.7V
      input_threshold_factor=(0.3, 0.7),
      pullup_capable=True, pulldown_capable=True
    )

    adc_model = AnalogSink(
      voltage_limits=(0, self.vdd.link().voltage.upper()),
      current_draw=(0, 0) * Amp,
      impedance=(100, float('inf')) * kOhm
    )
    dac_model = AnalogSource(
      voltage_out=(0, self.vdd.link().voltage.upper() - 0.3),
      current_limits=Default(RangeExpr.ALL),  # not given by spec
      impedance=(300, 300) * Ohm  # Table 25, "typical" rating
    )

    uart_model = UartPort(DigitalBidir.empty())
    spi_model = SpiMaster(DigitalBidir.empty())

    # Fixed-function ports
    # Crystals from table 15, 32, 33
    # TODO Table 32, model crystal load capacitance and series resistance ratings
    self.xtal = self.Port(CrystalDriver(frequency_limits=(1, 25)*MHertz, voltage_out=self.vdd.link().voltage),
                          optional=True)
    # Assumed from "32kHz crystal" in 14.5
    self.xtal_rtc = self.Port(CrystalDriver(frequency_limits=(32, 33)*kHertz, voltage_out=self.vdd.link().voltage),
                              optional=True)

    # Pin/peripheral resource definitions (table 3)
    self.abstract_pinmaps = PinMapUtil([
      PinResource('PIO0_0', {'PIO0_0': dio_5v_model, 'ADC0_10': adc_model}),
      PinResource('PIO0_1', {'PIO0_1': dio_5v_model, 'ADC0_7': adc_model}),
      PinResource('PIO0_2', {'PIO0_2': dio_5v_model, 'ADC0_6': adc_model}),
      PinResource('PIO0_3', {'PIO0_3': dio_5v_model, 'ADC0_5': adc_model}),
      PinResource('PIO0_4', {'PIO0_4': dio_5v_model, 'ADC0_4': adc_model}),
      PinResource('PIO0_5', {'PIO0_5': dio_5v_model, 'ADC0_3': adc_model}),
      PinResource('PIO0_6', {'PIO0_6': dio_5v_model, 'ADC0_2': adc_model}),
      PinResource('PIO0_7', {'PIO0_7': dio_5v_model, 'ADC0_1': adc_model}),

      PinResource('PIO0_8', {'PIO0_8': dio_5v_model, 'ADC0_0': adc_model}),
      PinResource('PIO0_9', {'PIO0_9': dio_5v_model, 'ADC1_1': adc_model}),
      PinResource('PIO0_10', {'PIO0_10': dio_5v_model, 'ADC1_2': adc_model}),
      PinResource('PIO0_11', {'PIO0_11': dio_5v_model, 'ADC1_3': adc_model}),
      PinResource('PIO0_12', {'PIO0_12': dio_non5v_model, 'DAC_OUT': dac_model}),
      PinResource('PIO0_13', {'PIO0_13': dio_5v_model, 'ADC1_6': adc_model}),
      PinResource('PIO0_14', {'PIO0_14': dio_5v_model, 'ADC1_7': adc_model}),
      PinResource('PIO0_15', {'PIO0_15': dio_5v_model, 'ADC1_8': adc_model}),
      PinResource('PIO0_16', {'PIO0_16': dio_5v_model, 'ADC1_9': adc_model}),
      PinResource('PIO0_17', {'PIO0_17': dio_5v_model}),

      PinResource('PIO0_18', {'PIO0_18': dio_5v_model}),
      PinResource('PIO0_19', {'PIO0_19': dio_5v_model}),
      PinResource('PIO0_20', {'PIO0_20': dio_5v_model}),
      PinResource('PIO0_21', {'PIO0_21': dio_5v_model}),
      PinResource('PIO0_22', {'PIO0_22': dio_5v_model}),
      PinResource('PIO0_23', {'PIO0_23': dio_5v_model}),
      PinResource('PIO0_24', {'PIO0_24': dio_highcurrrent_model}),
      PinResource('PIO0_25', {'PIO0_25': dio_5v_model}),
      PinResource('PIO0_26', {'PIO0_26': dio_5v_model}),

      PinResource('PIO0_27', {'PIO0_27': dio_5v_model}),
      PinResource('PIO0_28', {'PIO0_28': dio_5v_model}),
      PinResource('PIO0_29', {'PIO0_29': dio_5v_model}),
      PinResource('PIO0_30', {'PIO0_30': dio_5v_model, 'ADC0_11': adc_model}),
      PinResource('PIO0_31', {'PIO0_31': dio_5v_model, 'ADC0_9': adc_model}),
      PinResource('PIO1_0', {'PIO1_0': dio_5v_model, 'ADC0_8': adc_model}),
      PinResource('PIO1_1', {'PIO1_1': dio_5v_model, 'ADC1_0': adc_model}),
      PinResource('PIO1_2', {'PIO1_2': dio_5v_model, 'ADC1_4': adc_model}),
      PinResource('PIO1_3', {'PIO1_3': dio_5v_model, 'ADC1_5': adc_model}),
      PinResource('PIO1_4', {'PIO1_4': dio_5v_model, 'ADC1_10': adc_model}),
      PinResource('PIO1_5', {'PIO1_5': dio_5v_model, 'ADC1_11': adc_model}),


      PinResource('PIO1_6', {'PIO1_6': dio_5v_model}),
      PinResource('PIO1_7', {'PIO1_7': dio_5v_model}),
      PinResource('PIO1_8', {'PIO1_8': dio_5v_model}),
      PinResource('PIO1_9', {'PIO1_9': dio_5v_model}),
      PinResource('PIO1_10', {'PIO1_10': dio_5v_model}),
      PinResource('PIO1_11', {'PIO1_11': dio_5v_model}),

      # 100-pin version ignored, since that isn't used

      PeripheralAnyPinResource('UART0', uart_model),
      PeripheralAnyPinResource('UART1', uart_model),
      PeripheralAnyPinResource('UART2', uart_model),
      PeripheralAnyPinResource('SPI0', spi_model),
      PeripheralAnyPinResource('SPI1', spi_model),
      PeripheralAnyPinResource('CAN0', CanControllerPort(DigitalBidir.empty())),

      PeripheralFixedResource('I2C0', I2cMaster(DigitalBidir.empty()), {
        'scl': ['PIO0_22'], 'sda': ['PIO0_23']
      }),
      PeripheralFixedPin('USB', UsbDevicePort(), {
        'dp': ['USB_DP'], 'dm': ['USB_DM']
      }),

      # Figure 49: requires a pull-up on SWDIO and pull-down on SWCLK, but none on RESET.
      # Reset has an internal pull-up (or can be configured as unused), except when deep power down is needed
      # TODO: SWO is arbitrary and can also be NC, current mapped to TDO
      PeripheralFixedResource('SWD', SwdTargetPort(DigitalBidir.empty()), {
        'swclk': ['PIO0_19'], 'swdio': ['PIO0_20'], 'reset': ['PIO0_21'], 'swo': ['PIO0_8'],
      }),
    ])

    self.generator(self.generate, self.pin_mapping,
                   self.gpio.allocated(), self.adc.allocated(), self.dac.allocated(),
                   self.spi.allocated(), self.i2c.allocated(), self.uart.allocated(),
                   self.usb.allocated(), self.can.allocated())

  @abstractmethod
  def generate(self, assignments: str,
               gpio_allocates: List[str], adc_allocates: List[str], dac_allocates: List[str],
               spi_allocates: List[str], i2c_allocates: List[str], uart_allocates: List[str],
               usb_allocates: List[str], can_allocates: List[str]) -> None: ...


@abstract_block
class Lpc1549_48New_Device(Lpc1549BaseNew_Device):
  def generate(self, assignments: str,
               gpio_allocates: List[str], adc_allocates: List[str], dac_allocates: List[str],
               spi_allocates: List[str], i2c_allocates: List[str], uart_allocates: List[str],
               usb_allocates: List[str], can_allocates: List[str]):
    system_pins: Dict[str, CircuitPort] = {
      '16': self.vdd,  # VddA
      '17': self.vss,  # VssA
      '10': self.vdd,  # VrefP_ADC
      '14': self.vdd,  # VrefP_DAC
      '11': self.vss,  # VrefN
      '30': self.vdd,  # TODO support optional Vbat
      '20': self.vss,
      '27': self.vdd,
      '39': self.vdd,
      '40': self.vss,
      '41': self.vss,
      '42': self.vdd,

      '26': self.xtal.xtal_in,  # TODO Table 3, note 11, float/gnd (gnd preferred) if not used
      '25': self.xtal.xtal_out,  # TODO Table 3, note 11, float if not used
      '31': self.xtal_rtc.xtal_in,  # 14.5 can be grounded if RTC not used
      '32': self.xtal_rtc.xtal_out,
    }

    ios = self._instantiate_ios([(self.gpio, gpio_allocates), (self.adc, adc_allocates), (self.dac, dac_allocates),
                                 (self.spi, spi_allocates), (self.i2c, i2c_allocates), (self.uart, uart_allocates),
                                 (self.usb, usb_allocates), (self.can, can_allocates)])
    (io_pins, port_models) = self.abstract_pinmaps.remap_pins({
      'PIO0_0': '1',
      'PIO0_1': '2',
      'PIO0_2': '3',
      'PIO0_3': '4',
      'PIO0_4': '5',
      'PIO0_5': '6',
      'PIO0_6': '7',
      'PIO0_7': '8',

      'PIO0_8': '9',
      'PIO0_9': '12',
      'PIO0_10': '15',
      'PIO0_11': '18',
      'PIO0_12': '19',
      'PIO0_13': '21',
      'PIO0_14': '22',
      'PIO0_15': '23',
      'PIO0_16': '24',
      'PIO0_17': '28',

      'PIO0_18': '13',
      'PIO0_19': '29',
      'PIO0_20': '33',
      'PIO0_21': '34',
      'PIO0_22': '37',
      'PIO0_23': '38',
      'PIO0_24': '43',
      'PIO0_25': '44',
      'PIO0_26': '45',

      'PIO0_27': '46',
      'PIO0_28': '47',
      'PIO0_29': '48',

      'USB_DP': '35',
      'USB_DM': '36',
    }).assign(ios, assignments)

    self.footprint(
      'U', 'Package_QFP:LQFP-48_7x7mm_P0.5mm',
      dict(chain(system_pins.items(), io_pins.items())),
      mfr='NXP', part='LPC1549JBD48',
      datasheet='https://www.nxp.com/docs/en/data-sheet/LPC15XX.pdf'
    )


@abstract_block
class Lpc1549_64New_Device(Lpc1549BaseNew_Device):
  def generate(self, assignments: str,
               gpio_allocates: List[str], adc_allocates: List[str], dac_allocates: List[str],
               spi_allocates: List[str], i2c_allocates: List[str], uart_allocates: List[str],
               usb_allocates: List[str], can_allocates: List[str]):
    system_pins: Dict[str, CircuitPort] = {
      '20': self.vdd,  # VddA
      '21': self.vss,  # VssA
      '13': self.vdd,  # VrefP_ADC
      '18': self.vdd,  # VrefP_DAC
      '14': self.vss,  # VrefN
      '41': self.vdd,  # TODO support optional Vbat
      '22': self.vdd,
      '26': self.vss,
      '27': self.vss,
      '37': self.vdd,
      '52': self.vdd,
      '55': self.vss,
      '56': self.vss,
      '57': self.vdd,

      '36': self.xtal.xtal_in,  # TODO Table 3, note 11, float/gnd (gnd preferred) if not used
      '35': self.xtal.xtal_out,  # TODO Table 3, note 11, float if not used
      '42': self.xtal_rtc.xtal_in,  # 14.5 can be grounded if RTC not used
      '43': self.xtal_rtc.xtal_out,
    }

    ios = self._instantiate_ios([(self.gpio, gpio_allocates), (self.adc, adc_allocates), (self.dac, dac_allocates),
                                 (self.spi, spi_allocates), (self.i2c, i2c_allocates), (self.uart, uart_allocates),
                                 (self.usb, usb_allocates), (self.can, can_allocates)])
    (io_pins, port_models) = self.abstract_pinmaps.remap_pins({
      'PIO0_0': '2',
      'PIO0_1': '5',
      'PIO0_2': '6',
      'PIO0_3': '7',
      'PIO0_4': '8',
      'PIO0_5': '9',
      'PIO0_6': '10',
      'PIO0_7': '11',

      'PIO0_8': '12',
      'PIO0_9': '16',
      'PIO0_10': '19',
      'PIO0_11': '23',
      'PIO0_12': '24',
      'PIO0_13': '29',
      'PIO0_14': '30',
      'PIO0_15': '31',
      'PIO0_16': '32',
      'PIO0_17': '39',

      'PIO0_18': '17',
      'PIO0_19': '40',
      'PIO0_20': '44',
      'PIO0_21': '45',
      'PIO0_22': '49',
      'PIO0_23': '50',
      'PIO0_24': '58',
      'PIO0_25': '60',
      'PIO0_26': '61',

      'PIO0_27': '62',
      'PIO0_28': '63',
      'PIO0_29': '64',

      'USB_DP': '47',
      'USB_DM': '48',
    }).assign(ios, assignments)

    self.footprint(
      'U', 'Package_QFP:LQFP-64_10x10mm_P0.5mm',
      dict(chain(system_pins.items(), io_pins.items())),
      mfr='NXP', part='LPC1549JBD64',
      datasheet='https://www.nxp.com/docs/en/data-sheet/LPC15XX.pdf'
    )
