from typing import *

from electronics_abstract_parts import *
from .JlcPart import JlcPart
from .Microcontroller_Esp import HasEspProgramming


@non_library
class Esp32c3_Interfaces(IoControllerI2s, IoControllerWifi, IoControllerBle, BaseIoController):
  """Defines base interfaces for ESP32C3 microcontrollers"""


@abstract_block
class Esp32c3_Base(Esp32c3_Interfaces, InternalSubcircuit, IoControllerPowerRequired, BaseIoControllerPinmapGenerator):
  """Base class for ESP32-C3 series devices, with RISC-V core, 2.4GHz WiF,i, BLE5.
  PlatformIO: use board ID esp32-c3-devkitm-1

  Chip datasheet: https://espressif.com/sites/default/files/documentation/esp32-c3_datasheet_en.pdf
  """
  def __init__(self, **kwargs) -> None:
    super().__init__(**kwargs)

    self.pwr.init_from(VoltageSink(
      voltage_limits=(3.0, 3.6)*Volt,  # section 4.2
      current_draw=(0.001, 335)*mAmp + self.io_current_draw.upper()  # section 4.6, from power off to RF active
    ))
    self.gnd.init_from(Ground())

    self._dio_model = DigitalBidir.from_supply(  # table 4.4
      self.gnd, self.pwr,
      voltage_limit_tolerance=(-0.3, 0.3)*Volt,
      current_limits=(-28, 40)*mAmp,
      current_draw=(0, 0)*Amp,
      input_threshold_factor=(0.25, 0.75),
      pullup_capable=True, pulldown_capable=True,
    )

    # section 2.4: strapping IOs that need a fixed value to boot, and currently can't be allocated as GPIO
    self.en = self.Port(self._dio_model)  # needs external pullup
    self.io2 = self.Port(self._dio_model)  # needs external pullup
    self.io8 = self.Port(self._dio_model)  # needs external pullup, may control prints
    self.io9 = self.Port(self._dio_model, optional=True)  # internally pulled up for SPI boot, connect to GND for download

    # similarly, the programming UART is fixed and allocated separately
    self.uart0 = self.Port(UartPort(self._dio_model), optional=True)

  def _system_pinmap(self) -> Dict[str, CircuitPort]:
    return {
      'Vdd': self.pwr,
      'Vss': self.gnd,
      'EN': self.en,
      'GPIO2': self.io2,
      'GPIO8': self.io8,
      'GPIO9': self.io9,
      'TXD': self.uart0.tx,
      'RXD': self.uart0.rx,
    }

  def _io_pinmap(self) -> PinMapUtil:
    adc_model = AnalogSink(
      voltage_limits=(0, 2.5) * Volt,  # table 15, effective ADC range
      current_draw=(0, 0) * Amp,
      # TODO: impedance / leakage - not specified by datasheet
    )

    uart_model = UartPort(DigitalBidir.empty())
    spi_model = SpiMaster(DigitalBidir.empty(), (0, 60)*MHertz)  # section 3.4.2, max block in GP master mode
    i2c_model = I2cMaster(DigitalBidir.empty())  # section 3.4.4, supporting 100/400 and up to 800 kbit/s

    return PinMapUtil([  # section 2.2
      PinResource('GPIO0', {'GPIO0': self._dio_model, 'ADC1_CH0': adc_model}),  # also XTAL_32K_P
      PinResource('GPIO1', {'GPIO1': self._dio_model, 'ADC1_CH1': adc_model}),  # also XTAL_32K_N
      # PinResource('GPIO2', {'GPIO2': dio_model, 'ADC1_CH2': adc_model}),  # boot pin, non-allocatable
      PinResource('GPIO3', {'GPIO3': self._dio_model, 'ADC1_CH3': adc_model}),
      PinResource('MTMS', {'GPIO4': self._dio_model, 'ADC1_CH4': adc_model}),
      PinResource('MTDI', {'GPIO5': self._dio_model, 'ADC2_CH0': adc_model}),
      PinResource('MTCK', {'GPIO6': self._dio_model}),
      PinResource('MTDO', {'GPIO7': self._dio_model}),
      # PinResource('GPIO8', {'GPIO8': dio_model}),  # boot pin, non-allocatable
      # PinResource('GPIO9', {'GPIO9': dio_model}),  # boot pin, non-allocatable
      PinResource('GPIO10', {'GPIO10': self._dio_model}),
      PinResource('VDD_SPI', {'GPIO11': self._dio_model}),
      # SPI pins skipped - internal to the modules supported so far
      PinResource('GPIO18', {'GPIO18': self._dio_model}),
      PinResource('GPIO19', {'GPIO19': self._dio_model}),
      # PinResource('GPIO20', {'GPIO20': dio_model}),  # boot pin, non-allocatable
      # PinResource('GPIO21', {'GPIO21': dio_model}),  # boot pin, non-allocatable

      # peripherals in section 3.11
      # PeripheralFixedResource('U0', uart_model, {  # programming pin, non-allocatable
      #   'txd': ['GPIO21'], 'rxd': ['GPIO20']
      # }),
      PeripheralAnyResource('U1', uart_model),
      PeripheralAnyResource('I2C', i2c_model),
      PeripheralAnyResource('SPI2', spi_model),
      PeripheralAnyResource('I2S', I2sController.empty()),
    ])


class Esp32c3_Wroom02_Device(Esp32c3_Base, FootprintBlock, JlcPart):
  """ESP32C module

  Module datasheet: https://www.espressif.com/sites/default/files/documentation/esp32-c3-wroom-02_datasheet_en.pdf
  """
  def _system_pinmap(self) -> Dict[str, CircuitPort]:
    return VariantPinRemapper(super()._system_pinmap()).remap({
      'Vdd': '1',
      'Vss': ['9', '19'],  # 19 is EP
      'EN': '2',
      'GPIO2': '16',
      'GPIO8': '7',
      'GPIO9': '8',
      'RXD': '11',  # RXD, GPIO20
      'TXD': '12',  # TXD, GPIO21
    })

  def _io_pinmap(self) -> PinMapUtil:
    return super()._io_pinmap().remap_pins({
      'MTMS': '3',  # GPIO4
      'MTDI': '4',  # GPIO5
      'MTCK': '5',  # GPIO6
      'MTDO': '6',  # GPIO7
      'GPIO10': '10',
      'GPIO18': '13',
      'GPIO19': '14',
      'GPIO3': '15',
      'GPIO1': '17',
      'GPIO0': '18',
    })

  def generate(self) -> None:
    super().generate()

    self.footprint(
      'U', 'RF_Module:ESP-WROOM-02',
      self._make_pinning(),
      mfr='Espressif Systems', part='ESP32-C3-WROOM-02',
      datasheet='https://www.espressif.com/sites/default/files/documentation/esp32-c3-wroom-02_datasheet_en.pdf',
    )
    self.assign(self.lcsc_part, 'C2934560')
    self.assign(self.actual_basic_part, False)


class Esp32c3_Wroom02(Microcontroller, Radiofrequency, HasEspProgramming, Esp32c3_Interfaces, IoControllerPowerRequired,
                      BaseIoControllerExportable):
  """Wrapper around Esp32c3_Wroom02 with external capacitors and UART programming header."""
  def contents(self) -> None:
    super().contents()

    with self.implicit_connect(
        ImplicitConnect(self.pwr, [Power]),
        ImplicitConnect(self.gnd, [Common])
    ) as imp:
      self.ic = imp.Block(Esp32c3_Wroom02_Device(pin_assigns=ArrayStringExpr()))
      self.connect(self.program_uart_node, self.ic.uart0)
      self.connect(self.program_en_node, self.ic.en)
      self.connect(self.program_boot_node, self.ic.io9)

      self.vcc_cap0 = imp.Block(DecouplingCapacitor(10 * uFarad(tol=0.2)))  # C1
      self.vcc_cap1 = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))  # C2

      # Note strapping pins (section 3.3) IO2, 8, 9; IO9 is internally pulled up
      # IO9 (internally pulled up) is 1 for SPI boot and 0 for download boot
      # IO2 must be 1 for both SPI and download boot, while IO8 must be 1 for download boot
      self.io8_pull = imp.Block(PullupResistor(10 * kOhm(tol=0.05))).connected(io=self.ic.io8)
      self.io2_pull = imp.Block(PullupResistor(10 * kOhm(tol=0.05))).connected(io=self.ic.io2)
      self.en_pull = imp.Block(PullupDelayRc(10 * kOhm(tol=0.05), 10*mSecond(tol=0.2))).connected(io=self.ic.en)
