from itertools import chain
from typing import *

from electronics_abstract_parts import *
from .PassiveConnector import PassiveConnector
from .JlcPart import JlcPart


@abstract_block
class Esp32_Device(PinMappable, IoController, DiscreteChip, GeneratorBlock, FootprintBlock):
  """Base class for ESP32 series microcontrollrs with WiFi and Bluetooth (classic and LE)

  Chip datasheet: https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf
  """
  def __init__(self, **kwargs) -> None:
    super().__init__(**kwargs)

    self.pwr.init_from(VoltageSink(
      voltage_limits=(3.0, 3.6)*Volt,  # section 5.2, table 14, most restrictive limits
      current_draw=(0.001, 370) * mAmp  # from power off (table 8) to RF working (WRROM datasheet table 9)
      # # TODO propagate current consumption from IO ports
    ))
    self.gnd.init_from(Ground())

    self.dio_model = dio_model = DigitalBidir.from_supply(  # section 5.2, table 15
      self.gnd, self.pwr,
      voltage_limit_tolerance=(-0.3, 0.3) * Volt,
      current_limits=(-28, 40)*mAmp,
      current_draw=(0, 0)*Amp,
      input_threshold_factor=(0.25, 0.75),
      pullup_capable=True, pulldown_capable=True,
    )
    sdio_model = DigitalBidir.from_supply(  # section 5.2, table 15, for SDIO power domain pins
      self.gnd, self.pwr,
      voltage_limit_tolerance=(-0.3, 0.3) * Volt,
      current_limits=(-28, 20)*mAmp,  # reduced sourcing capability
      current_draw=(0, 0)*Amp,
      input_threshold_factor=(0.25, 0.75),
      pullup_capable=True, pulldown_capable=True,
    )

    self.chip_pu = self.Port(dio_model)  # power control, must NOT be left floating, table 1

    # section 2.4, table 5: strapping IOs that need a fixed value to boot, TODO currently not allocatable post-boot
    self.io0 = self.Port(dio_model)  # default pullup (SPI boot), set low to download boot
    self.io2 = self.Port(dio_model)  # default pulldown (enable download boot), ignored during SPI boot

    # similarly, the programming UART is fixed and allocated separately
    self.uart0 = self.Port(UartPort(dio_model), optional=True)

    self.system_pinmaps = VariantPinRemapper({
      'Vdd': self.pwr,
      'Vss': self.gnd,
      'CHIP_PU': self.chip_pu,
      'GPIO0': self.io0,
      'GPIO2': self.io2,
      # 'MTDO': ...,  # disconnected, internally pulled up for strapping - U0TXD active
      # 'MTDI': ...,  # disconnected, internally pulled down for strapping - 3.3v LDO
      'U0RXD': self.uart0.rxd,
      'U0TXD': self.uart0.txd,
    })

    self.abstract_pinmaps = self.mappable_ios(dio_model, sdio_model, self.gnd, self.pwr)

    # TODO add JTAG support

    self.generator(self.generate, self.pin_assigns,
                   self.gpio.allocated(), self.adc.allocated(), self.dac.allocated(),
                   self.spi.allocated(), self.i2c.allocated(), self.uart.allocated(),
                   self.usb.allocated())

  @staticmethod
  def mappable_ios(dio_model: DigitalBidir, sdio_model: DigitalBidir,
                   gnd: VoltageSource, pwr: VoltageSource) -> PinMapUtil:
    adc_model = AnalogSink.from_supply(gnd, pwr)  # TODO: no specs in datasheet?!
    dac_model = AnalogSource.from_supply(gnd, pwr)  # TODO: no specs in datasheet?!

    uart_model = UartPort(DigitalBidir.empty())
    spi_model = SpiMaster(DigitalBidir.empty(), (0, 80)*MHertz)  # section 4.1.17
    i2c_model = I2cMaster(DigitalBidir.empty())  # section 4.1.11, 100/400kHz and up to 5MHz
    can_model = CanControllerPort(DigitalBidir.empty())  # aka TWAI

    return PinMapUtil([  # section 2.2, table 1
      # VDD3P3_RTC
      PinResource('SENSOR_VP', {'GPIO36': dio_model, 'ADC1_CH0': adc_model}),  # also RTC_GPIO
      PinResource('SENSOR_CAPP', {'GPIO37': dio_model, 'ADC1_CH1': adc_model}),  # also RTC_GPIO
      PinResource('SENSOR_CAPN', {'GPIO38': dio_model, 'ADC1_CH2': adc_model}),  # also RTC_GPIO
      PinResource('SENSOR_VN', {'GPIO39': dio_model, 'ADC1_CH3': adc_model}),  # also RTC_GPIO

      PinResource('VDET_1', {'GPIO34': dio_model, 'ADC1_CH6': adc_model}),  # also RTC_GPIO
      PinResource('VDET_2', {'GPIO35': dio_model, 'ADC1_CH7': adc_model}),  # also RTC_GPIO
      PinResource('32K_XP', {'GPIO32': dio_model, 'ADC1_CH4': adc_model}),  # also RTC_GPIO, 32K_XP
      PinResource('32K_XP', {'GPIO33': dio_model, 'ADC1_CH5': adc_model}),  # also RTC_GPIO, 32K_XN

      PinResource('GPIO25', {'GPIO25': dio_model, 'ADC2_CH8': adc_model, 'DAC_1': dac_model}),  # also RTC_GPIO
      PinResource('GPIO26', {'GPIO26': dio_model, 'ADC2_CH9': adc_model, 'DAC_2': dac_model}),  # also RTC_GPIO
      PinResource('GPIO27', {'GPIO27': dio_model, 'ADC2_CH7': adc_model}),  # also RTC_GPIO

      PinResource('MTMS', {'GPIO14': dio_model, 'ADC2_CH6': adc_model}),  # also RTC_GPIO
      # PinResource('MTDI', {'GPIO12': dio_model, 'ADC2_CH5': adc_model}),  # also RTC_GPIO, strapping pin
      PinResource('MTCK', {'GPIO13': dio_model, 'ADC2_CH4': adc_model}),  # also RTC_GPIO
      # PinResource('MTDO', {'GPIO15': dio_model, 'ADC2_CH3': adc_model}),  # also RTC_GPIO, strapping pin

      # PinResource('GPIO2', {'GPIO2': dio_model, 'ADC2_CH2': adc_model}),  # also RTC_GPIO, strapping pin
      # PinResource('GPIO0', {'GPIO0': dio_model, 'ADC2_CH1': adc_model}),  # also RTC_GPIO, strapping pin
      PinResource('GPIO4', {'GPIO4': dio_model, 'ADC2_CH0': adc_model}),  # also RTC_GPIO

      # VDD_SDIO
      PinResource('GPIO16', {'GPIO16': sdio_model}),
      PinResource('GPIO17', {'GPIO17': sdio_model}),
      PinResource('SD_DATA_2', {'GPIO9': sdio_model}),
      PinResource('SD_DATA_3', {'GPIO10': sdio_model}),
      PinResource('SD_CMD', {'GPIO11': sdio_model}),
      PinResource('SD_CLK', {'GPIO6': sdio_model}),
      PinResource('SD_DATA_0', {'GPIO7': sdio_model}),
      PinResource('SD_DATA_1', {'GPIO8': sdio_model}),

      # VDD_3P3_CPU
      PinResource('GPIO5', {'GPIO5': dio_model}),
      PinResource('GPIO18', {'GPIO18': dio_model}),
      PinResource('GPIO23', {'GPIO23': dio_model}),
      PinResource('GPIO19', {'GPIO19': dio_model}),
      PinResource('GPIO22', {'GPIO22': dio_model}),
      # PinResource('U0RXD', {'GPIO3': dio_model}),  # for programming, technically reallocatable
      # PinResource('U0TXD', {'GPIO1': dio_model}),  # for programming, technically reallocatable
      PinResource('GPIO21', {'GPIO21': dio_model}),

      # section 4.2, table 12: peripheral pin assignments
      # note LED and motor PWMs can be assigned to any pin
      # PeripheralAnyResource('U0', uart_model),  # for programming, technically reallocatable
      PeripheralAnyResource('U1', uart_model),
      PeripheralAnyResource('U2', uart_model),

      PeripheralAnyResource('I2CEXT0', i2c_model),
      PeripheralAnyResource('I2CEXT1', i2c_model),

      # PeripheralAnyResource('SPI', spi_model),  # for flash, non-allocatable
      PeripheralAnyResource('HSPI', spi_model),
      PeripheralAnyResource('VSPI', spi_model),

      PeripheralAnyResource('TWAI', can_model),
    ])

  SYSTEM_PIN_REMAP: Dict[str, Union[str, List[str]]]  # pin name in base -> pin name(s)
  RESOURCE_PIN_REMAP: Dict[str, str]  # resource name in base -> pin name

  def generate(self, assignments: List[str],
               gpio_allocates: List[str], adc_allocates: List[str], dac_allocates: List[str],
               spi_allocates: List[str], i2c_allocates: List[str], uart_allocates: List[str],
               usb_allocates: List[str]) -> None: ...


class Esp32_Wroom_32_Device(Esp32_Device, FootprintBlock, JlcPart):
  """ESP32-WROOM-32 module

  Module datasheet: https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32e_esp32-wroom-32ue_datasheet_en.pdf
  """
  SYSTEM_PIN_REMAP: Dict[str, Union[str, List[str]]] = {
    'Vdd': '2',
    'Vss': ['1', '15', '38', '39'],  # 39 is EP
    'CHIP_PU': '3',  # aka EN

    'GPIO0': '25',
    'GPIO2': '24',
    'MTDO': '23',  # aka GPIO15
    'MTDI': '14',  # aka GPIO12
    'U0RXD': '34',
    'U0TXD': '35',
  }

  RESOURCE_PIN_REMAP = {
    # 'MTMS': '3',  # GPIO4
    # 'MTDI': '4',  # GPIO5
    # 'MTCK': '5',  # GPIO6
    # 'MTDO': '6',  # GPIO7
    # 'GPIO10': '10',
    # 'GPIO18': '13',
    # 'GPIO19': '14',
    # 'GPIO3': '15',
    # 'GPIO1': '17',
    # 'GPIO0': '18',
  }

  def generate(self, assignments: List[str],
               gpio_allocates: List[str], adc_allocates: List[str], dac_allocates: List[str],
               spi_allocates: List[str], i2c_allocates: List[str], uart_allocates: List[str],
               usb_allocates: List[str]) -> None:
    system_pins: Dict[str, CircuitPort] = self.system_pinmaps.remap(self.SYSTEM_PIN_REMAP)

    allocated = self.abstract_pinmaps.remap_pins(self.RESOURCE_PIN_REMAP).allocate([
      (UsbDevicePort, usb_allocates), (SpiMaster, spi_allocates), (I2cMaster, i2c_allocates),
      (UartPort, uart_allocates),
      (AnalogSink, adc_allocates), (AnalogSource, dac_allocates), (DigitalBidir, gpio_allocates),
    ], assignments)
    self.generator_set_allocation(allocated)

    io_pins = self._instantiate_from(self._get_io_ports(), allocated)

    self.assign(self.lcsc_part, 'C701342')
    self.assign(self.actual_basic_part, False)
    self.footprint(
      'U', 'ESP32-WROOM-32E',
      dict(chain(system_pins.items(), io_pins.items())),
      mfr='Espressif Systems', part='ESP32-WROOM-32',
      datasheet='https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32e_esp32-wroom-32ue_datasheet_en.pdf',
    )


class Esp32_Wroom_32(PinMappable, Microcontroller, IoController, Block):
  """Wrapper around Esp32c3_Wroom02 with external capacitors and UART programming header."""
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.ic = self.Block(Esp32_Wroom_32_Device(pin_assigns=self.pin_assigns))

  def contents(self) -> None:
    super().contents()
    self.connect(self.pwr, self.ic.pwr)
    self.connect(self.gnd, self.ic.gnd)
    self._export_ios_from(self.ic)
    self.assign(self.actual_pin_assigns, self.ic.actual_pin_assigns)

    with self.implicit_connect(
        ImplicitConnect(self.pwr, [Power]),
        ImplicitConnect(self.gnd, [Common])
    ) as imp:
      # Note strapping pins (section 2.4 of chip datasheet - TODO)

      # self.vcc_cap0 = imp.Block(DecouplingCapacitor(10 * uFarad(tol=0.2)))  # C1
      # self.vcc_cap1 = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))  # C2
      #
      # # Note strapping pins (section 3.3) IO2, 8, 9; IO9 is internally pulled up
      # # IO9 (internally pulled up) is 1 for SPI boot and 0 for download boot
      # # IO2 must be 1 for both SPI and download boot, while IO8 must be 1 for download boot
      # self.io8_pull = imp.Block(PullupResistor(10 * kOhm(tol=0.05))).connected(io=self.ic.io8)
      # self.io2_pull = imp.Block(PullupResistor(10 * kOhm(tol=0.05))).connected(io=self.ic.io2)
      # self.en_pull = imp.Block(PullupDelayRc(10 * kOhm(tol=0.05), 10*mSecond(tol=0.2))).connected(io=self.ic.en)
      # # by default instantiate a programming switch, TODO option to disable as a config
      # (self.prog, ), _ = self.chain(imp.Block(DigitalSwitch()), self.ic.io9)
      #
      # self.uart0 = imp.Block(EspProgrammingHeader())
      # self.connect(self.uart0.uart, self.ic.uart0)
