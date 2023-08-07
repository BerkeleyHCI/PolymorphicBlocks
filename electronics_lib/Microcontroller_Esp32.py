from abc import abstractmethod
from typing import *

from electronics_abstract_parts import *
from .JlcPart import JlcPart
from .Microcontroller_Esp import HasEspProgramming


@non_library
class Esp32_Interfaces(IoControllerDac, IoControllerCan, IoControllerDvp8, IoControllerI2s, IoControllerWifi,
                       IoControllerBle, IoControllerBluetooth, BaseIoController):
  """Defines base interfaces for ESP32 microcontrollers"""


@non_library
class Esp32_Ios(Esp32_Interfaces, BaseIoControllerPinmapGenerator):
  RESOURCE_PIN_REMAP: Dict[str, str]  # resource name in base -> pin name

  @abstractmethod
  def _gnd_vddio(self) -> Tuple[Port[VoltageLink], Port[VoltageLink]]:
    """Returns GND and VDDIO (either can be VoltageSink or VoltageSource)."""
    ...

  def _vdd_model(self) -> VoltageSink:
    return VoltageSink(
      voltage_limits=(3.0, 3.6)*Volt,  # section 5.2, table 14, most restrictive limits
      current_draw=(0.001, 370)*mAmp + self.io_current_draw.upper()  # from power off (table 8) to RF working (WRROM datasheet table 9)
    )

  def _dio_model(self, gnd: Port[VoltageLink], pwr: Port[VoltageLink]) -> DigitalBidir:
    return DigitalBidir.from_supply(  # section 5.2, table 15
      gnd, pwr,
      voltage_limit_tolerance=(-0.3, 0.3) * Volt,
      current_limits=(-28, 40)*mAmp,
      current_draw=(0, 0)*Amp,
      input_threshold_factor=(0.25, 0.75),
      pullup_capable=True, pulldown_capable=True,
    )

  def _io_pinmap(self) -> PinMapUtil:
    gnd, pwr = self._gnd_vddio()
    dio_model = self._dio_model(gnd, pwr)
    sdio_model = DigitalBidir.from_supply(  # section 5.2, table 15, for SDIO power domain pins
      gnd, pwr,
      voltage_limit_tolerance=(-0.3, 0.3) * Volt,
      current_limits=(-28, 20)*mAmp,  # reduced sourcing capability
      current_draw=(0, 0)*Amp,
      input_threshold_factor=(0.25, 0.75),
      pullup_capable=True, pulldown_capable=True,
    )

    adc_model = AnalogSink.from_supply(gnd, pwr)  # TODO: no specs in datasheet?!
    dac_model = AnalogSource.from_supply(gnd, pwr)  # TODO: no specs in datasheet?!

    uart_model = UartPort(DigitalBidir.empty())
    spi_model = SpiController(DigitalBidir.empty(), (0, 80) * MHertz)  # section 4.1.17
    i2c_model = I2cController(DigitalBidir.empty())  # section 4.1.11, 100/400kHz and up to 5MHz
    can_model = CanControllerPort(DigitalBidir.empty())  # aka TWAI
    i2s_model = I2sController(DigitalBidir.empty())
    dvp8_model = Dvp8Host(DigitalBidir.empty())

    return PinMapUtil([  # section 2.2, table 1
      # VDD3P3_RTC
      PinResource('SENSOR_VP', {'ADC1_CH0': adc_model}),  # also input-only 'GPIO36': dio_model, RTC_GPIO
      PinResource('SENSOR_CAPP', {'ADC1_CH1': adc_model}),  # also input-only 'GPIO37': dio_model, RTC_GPIO
      PinResource('SENSOR_CAPN', {'ADC1_CH2': adc_model}),  # also input-only 'GPIO38': dio_model,  RTC_GPIO
      PinResource('SENSOR_VN', {'ADC1_CH3': adc_model}),  # also input-only 'GPIO39': dio_model, RTC_GPIO

      PinResource('VDET_1', {'ADC1_CH6': adc_model}),  # also input-only 'GPIO34': dio_model, RTC_GPIO
      PinResource('VDET_2', {'ADC1_CH7': adc_model}),  # also input-only 'GPIO35': dio_model,  RTC_GPIO
      PinResource('32K_XP', {'GPIO32': dio_model, 'ADC1_CH4': adc_model}),  # also RTC_GPIO, 32K_XP
      PinResource('32K_XN', {'GPIO33': dio_model, 'ADC1_CH5': adc_model}),  # also RTC_GPIO, 32K_XN

      PinResource('GPIO25', {'GPIO25': dio_model, 'ADC2_CH8': adc_model, 'DAC_1': dac_model}),  # also RTC_GPIO
      PinResource('GPIO26', {'GPIO26': dio_model, 'ADC2_CH9': adc_model, 'DAC_2': dac_model}),  # also RTC_GPIO
      PinResource('GPIO27', {'GPIO27': dio_model, 'ADC2_CH7': adc_model}),  # also RTC_GPIO

      PinResource('MTMS', {'GPIO14': dio_model, 'ADC2_CH6': adc_model}),  # also RTC_GPIO
      PinResource('MTDI', {'GPIO12': dio_model, 'ADC2_CH5': adc_model}),  # also RTC_GPIO, noncritical strapping pin
      PinResource('MTCK', {'GPIO13': dio_model, 'ADC2_CH4': adc_model}),  # also RTC_GPIO
      PinResource('MTDO', {'GPIO15': dio_model, 'ADC2_CH3': adc_model}),  # also RTC_GPIO, noncritical strapping pin

      # PinResource('GPIO2', {'GPIO2': self._dio_model, 'ADC2_CH2': adc_model}),  # also RTC_GPIO, strapping pin
      # PinResource('GPIO0', {'GPIO0': self._dio_model, 'ADC2_CH1': adc_model}),  # also RTC_GPIO, strapping pin
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

      PeripheralAnyResource('I2S0', i2s_model),  # while CLK is restricted pinning, SCK = BCK here
      PeripheralAnyResource('I2S1', i2s_model),

      PeripheralAnyResource('DVP', dvp8_model),  # TODO this also eats an I2S port, also available as 16-bit
    ]).remap_pins(self.RESOURCE_PIN_REMAP)


@abstract_block
class Esp32_Base(Esp32_Ios, IoController, InternalSubcircuit, GeneratorBlock):
  """Base class for ESP32 series microcontrollers with WiFi and Bluetooth (classic and LE)

  Chip datasheet: https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf
  """
  SYSTEM_PIN_REMAP: Dict[str, Union[str, List[str]]]  # pin name in base -> pin name(s)

  def __init__(self, **kwargs) -> None:
    super().__init__(**kwargs)

    self.pwr.init_from(self._vdd_model())
    self.gnd.init_from(Ground())

    dio_model = self._dio_model(self.pwr, self.gnd)
    self.chip_pu = self.Port(dio_model)  # power control, must NOT be left floating, table 1
    # section 2.4, table 5: strapping IOs that need a fixed value to boot, TODO currently not allocatable post-boot
    self.io0 = self.Port(dio_model, optional=True)  # default pullup (SPI boot), set low to download boot
    self.io2 = self.Port(dio_model, optional=True)  # default pulldown (enable download boot), ignored during SPI boot

    # similarly, the programming UART is fixed and allocated separately
    self.uart0 = self.Port(UartPort(dio_model), optional=True)

  def _gnd_vddio(self) -> Tuple[Port[VoltageLink], Port[VoltageLink]]:
    return self.gnd, self.pwr

  def _system_pinmap(self) -> Dict[str, CircuitPort]:
    return VariantPinRemapper({
      'Vdd': self.pwr,
      'Vss': self.gnd,
      'CHIP_PU': self.chip_pu,
      'GPIO0': self.io0,
      'GPIO2': self.io2,
      # 'MTDO': ...,  # disconnected, internally pulled up for strapping - U0TXD active
      # 'MTDI': ...,  # disconnected, internally pulled down for strapping - 3.3v LDO
      'U0RXD': self.uart0.rx,
      'U0TXD': self.uart0.tx,
    }).remap(self.SYSTEM_PIN_REMAP)


class Esp32_Wroom_32_Device(IoControllerPowerRequired, Esp32_Base, FootprintBlock, JlcPart):
  """ESP32-WROOM-32 module

  Module datasheet: https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32e_esp32-wroom-32ue_datasheet_en.pdf
  """
  SYSTEM_PIN_REMAP: Dict[str, Union[str, List[str]]] = {
    'Vdd': '2',
    'Vss': ['1', '15', '38', '39'],  # 39 is EP
    'CHIP_PU': '3',  # aka EN

    'GPIO0': '25',
    'GPIO2': '24',

    'U0RXD': '34',
    'U0TXD': '35',
  }

  RESOURCE_PIN_REMAP = {
    'SENSOR_VP': '4',
    'SENSOR_VN': '5',
    'VDET_1': '6',
    'VDET_2': '7',
    '32K_XP': '8',
    '32K_XN': '9',
    'GPIO25': '10',
    'GPIO26': '11',
    'GPIO27': '12',
    'MTMS': '13',
    'MTDI': '14',  # aka GPIO12

    'MTCK': '16',
    # pins 17-22 NC

    'MTDO': '23',  # aka GPIO15
    'GPIO4': '26',
    'GPIO16': '27',  # for QSPI PSRAM variants this cannot be used
    'GPIO17': '28',
    'GPIO5': '29',
    'GPIO18': '30',
    'GPIO19': '31',
    # pin 32 NC
    'GPIO21': '33',
    'GPIO22': '36',
    'GPIO23': '37',
  }

  def generate(self) -> None:
    super().generate()

    self.assign(self.lcsc_part, 'C701342')
    self.assign(self.actual_basic_part, False)
    self.footprint(
      'U', 'RF_Module:ESP32-WROOM-32',
      self._make_pinning(),
      mfr='Espressif Systems', part='ESP32-WROOM-32',
      datasheet='https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32e_esp32-wroom-32ue_datasheet_en.pdf',
    )


class Esp32_Wroom_32(Microcontroller, Radiofrequency, HasEspProgramming, Esp32_Interfaces, IoControllerPowerRequired,
                     BaseIoControllerExportable):
  """Wrapper around Esp32c3_Wroom02 with external capacitors and UART programming header.
  NOT COMPATIBLE WITH QSPI PSRAM VARIANTS - for those, GPIO16 needs to be pulled up.
  """
  def contents(self) -> None:
    super().contents()

    with self.implicit_connect(
        ImplicitConnect(self.pwr, [Power]),
        ImplicitConnect(self.gnd, [Common])
    ) as imp:
      self.ic = imp.Block(Esp32_Wroom_32_Device(pin_assigns=ArrayStringExpr()))
      self.connect(self.program_uart_node, self.ic.uart0)
      self.connect(self.program_en_node, self.ic.chip_pu)
      self.connect(self.program_boot_node, self.ic.io0)

      self.vcc_cap0 = imp.Block(DecouplingCapacitor(22 * uFarad(tol=0.2)))  # C1
      self.vcc_cap1 = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))  # C2

      # strapping pins are by default pulled to SPI boot, and can be reconfigured to download boot
      self.en_pull = imp.Block(PullupDelayRc(10 * kOhm(tol=0.05), 10*mSecond(tol=0.2))).connected(io=self.ic.chip_pu)


class Freenove_Esp32_Wrover(IoControllerUsbOut, IoControllerPowerOut, Esp32_Ios, IoController, GeneratorBlock,
                            FootprintBlock):
  """ESP32-WROVER-DEV breakout with camera.

  Module datasheet: https://www.espressif.com/sites/default/files/documentation/esp32-wrover-e_esp32-wrover-ie_datasheet_en.pdf
  Board used: https://amazon.com/ESP32-WROVER-Contained-Compatible-Bluetooth-Tutorials/dp/B09BC1N9LL
  Board internal schematic: https://github.com/Freenove/Freenove_ESP32_WROVER_Board/blob/f710fd6976e76ab76c29c2ee3042cd7bac22c3d6/Datasheet/ESP32_Schematic.pdf

  Top left is pin 1, going down the left side then up the right side.
  Up is defined from the text orientation (antenna is on top).
  """
  SYSTEM_PIN_REMAP: Dict[str, Union[str, List[str]]] = {
    'Vdd': '1',  # 3v3, output of internal AMS1117-3.3V LDO
    'Vusb': ['19', '20'],  # Vcc 5vUSB, input to internal LDO
    'Vss': ['14', '21', '29', '30', '34', '40'],

    'GPIO2': '26',  # fixed strapping pin, drives LED on PCB
  }
  RESOURCE_PIN_REMAP = {
    # 'SENSOR_VP': '3',  # camera CSI_Y6
    # 'SENSOR_VN': '4',  # camera CSI_Y7
    # 'VDET_1': '5',  # input only GPIO34, CSI_Y8
    # 'VDET_2': '6',  # input only GPIO35, CSI_Y9
    '32K_XP': '7',  # GPIO32
    '32K_XN': '8',  # GPIO33
    # 'GPIO25': '9',  # camera CSI_VYSNC
    # 'GPIO26': '10',  # camera I2C_SDA
    # 'GPIO27': '11',  # camera I2C_SCL
    'MTMS': '12',  # GPIO14
    'MTDI': '13',  # GPIO12

    'MTCK': '15',  # GPIO13
    # 'SD_DATA_2': '16',  # FLASH_D2, SD2
    # 'SD_DATA_3': '17',  # DLASH_D3, SD3
    # 'SD_CMD': '18',  # FLASH_CMD, CMD

    # 'SD_CLK': '22',  # FLASH_CLK, SD0
    # 'SD_DATA_0': '23',  # FLASH_D0, SD1
    # 'SD_DATA_1': '24',  # FLASH_D1, SD1
    'MTDO': '25',  # GPIO15

    # 'GPIO4': '28',  # camera CSI_Y2

    # 'GPIO5': '31',  # camera CSI_Y3
    # 'GPIO18': '32',  # camera CSI_Y4
    # 'GPIO19': '33',  # camera CSI_Y5

    # 'GPIO21': '35',  # camera XCLK

    # 'GPIO22': '38',  # camera CSI_PCLK
    # 'GPIO23': '39',  # camera CSI_HREF
  }

  def _gnd_vddio(self) -> Tuple[Port[VoltageLink], Port[VoltageLink]]:
    if self.get(self.gnd.is_connected()):  # board sinks power
      return self.gnd, self.pwr
    else:
      return self.gnd_out, self.pwr_out

  def _system_pinmap(self) -> Dict[str, CircuitPort]:
    if self.get(self.gnd.is_connected()):  # board sinks power
      self.require(~self.vusb_out.is_connected(), "can't source USB power if source gnd not connected")
      self.require(~self.pwr_out.is_connected(), "can't source 3v3 power if source gnd not connected")
      self.require(~self.gnd_out.is_connected(), "can't source gnd if source gnd not connected")
      return VariantPinRemapper({
        'Vdd': self.pwr,
        'Vss': self.gnd,
        'GPIO2': self.io2,
      }).remap(self.SYSTEM_PIN_REMAP)
    else:  # board sources power (default)
      self.require(~self.pwr.is_connected(), "can't sink power if source gnd connected")
      self.require(~self.gnd.is_connected(), "can't sink gnd if source gnd connected")
      return VariantPinRemapper({
        'Vdd': self.pwr_out,
        'Vss': self.gnd_out,
        'Vusb': self.vusb_out,
        'GPIO2': self.io2,
      }).remap(self.SYSTEM_PIN_REMAP)

  def __init__(self, **kawrgs) -> None:
    super().__init__(**kawrgs)

    self.gnd.init_from(Ground())
    self.pwr.init_from(self._vdd_model())

    self.gnd_out.init_from(GroundSource())
    self.vusb_out.init_from(VoltageSource(
      voltage_out=UsbConnector.USB2_VOLTAGE_RANGE,
      current_limits=UsbConnector.USB2_CURRENT_LIMITS
    ))
    self.pwr_out.init_from(VoltageSource(
      voltage_out=3.3*Volt(tol=0.05),  # tolerance is a guess
      current_limits=UsbConnector.USB2_CURRENT_LIMITS
    ))

    self.io2 = self.Port(DigitalBidir.empty(), optional=True)  # default pulldown (enable download boot), ignored during SPI boot

    self.generator_param(self.gnd.is_connected())

  def generate(self) -> None:
    super().generate()

    gnd, pwr = self._gnd_vddio()
    self.io2.init_from(self._dio_model(gnd, pwr))  # TODO remove this hack

    self.footprint(
      'U', 'edg:Freenove_ESP32-WROVER',
      self._make_pinning(),
      mfr='', part='Freenove ESP32-WROVER',
    )
