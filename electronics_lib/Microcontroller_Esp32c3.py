from itertools import chain
from typing import *

from electronics_abstract_parts import *
from .PassiveConnector import PassiveConnector


@abstract_block
class Esp32c3_Device(PinMappable, IoController, DiscreteChip, GeneratorBlock, FootprintBlock):
  """Base class for ESP32-C3 series devices, with RISC-V core, 2.4GHz WiF,i, BLE5, and USB.
  PlatformIO: use board ID esp32-c3-devkitm-1

  Chip datasheet: https://espressif.com/sites/default/files/documentation/esp32-c3_datasheet_en.pdf
  """
  def __init__(self, **kwargs) -> None:
    super().__init__(**kwargs)

    self.pwr.init_from(VoltageSink(
      voltage_limits=(3.0, 3.6)*Volt,  # section 4.2
      current_draw=(0.001, 335) * mAmp  # section 4.6, from power off to RF active
      # TODO propagate current consumption from IO ports
    ))
    self.gnd.init_from(Ground())

    self.dio_model = dio_model = DigitalBidir.from_supply(  # table 4.4
      self.gnd, self.pwr,
      voltage_limit_tolerance=(-0.3, 0.3) * Volt,
      current_limits=(-28, 40)*mAmp,
      current_draw=(0, 0)*Amp,
      input_threshold_factor=(0.25, 0.75),
      pullup_capable=True, pulldown_capable=True,
    )

    # section 2.4: strapping IOs that need a fixed value to boot, and currently can't be allocated as GPIO
    self.en = self.Port(dio_model)  # needs external pullup
    self.io2 = self.Port(dio_model)  # needs external pullup
    self.io8 = self.Port(dio_model)  # needs external pullup, may control prints
    self.io9 = self.Port(dio_model)  # internally pulled up for SPI boot, connect to GND for download

    # similarly, the programming UART is fixed and allocated separately
    self.uart0 = self.Port(UartPort(dio_model))

    self.system_pinmaps = VariantPinRemapper({
      'Vdd': self.pwr,
      'Vss': self.gnd,
      'EN': self.en,
      'GPIO2': self.io2,
      'GPIO8': self.io8,
      'GPIO9': self.io9,
      'TXD': self.uart0.tx,
      'RXD': self.uart0.rx,
    })

    self.abstract_pinmaps = self.mappable_ios(dio_model)

    # TODO add JTAG support

    self.generator(self.generate, self.pin_assigns,
                   self.gpio.allocated(), self.adc.allocated(), self.dac.allocated(),
                   self.spi.allocated(), self.i2c.allocated(), self.uart.allocated(),
                   self.usb.allocated())

  @staticmethod
  def mappable_ios(dio_model: DigitalBidir) -> PinMapUtil:
    adc_model = AnalogSink(
      voltage_limits=(0, 2.5) * Volt,  # table 15, effective ADC range
      current_draw=(0, 0) * Amp,
      # TODO: impedance / leakage - not specified by datasheet
    )

    uart_model = UartPort(DigitalBidir.empty())
    spi_model = SpiMaster(DigitalBidir.empty(), (0, 60)*MHertz)  # section 3.4.2, max block in GP master mode
    i2c_model = I2cMaster(DigitalBidir.empty())  # section 3.4.4, supporting 100/400 and up to 800 kbit/s

    return PinMapUtil([  # section 2.2
      PinResource('GPIO0', {'GPIO0': dio_model, 'ADC1_CH0': adc_model}),  # also XTAL_32K_P
      PinResource('GPIO1', {'GPIO1': dio_model, 'ADC1_CH1': adc_model}),  # also XTAL_32K_N
      # PinResource('GPIO2', {'GPIO2': dio_model, 'ADC1_CH2': adc_model}),  # boot pin, non-allocatable
      PinResource('GPIO3', {'GPIO3': dio_model, 'ADC1_CH3': adc_model}),
      PinResource('MTMS', {'GPIO4': dio_model, 'ADC1_CH4': adc_model}),
      PinResource('MTDI', {'GPIO5': dio_model, 'ADC2_CH0': adc_model}),
      PinResource('MTCK', {'GPIO6': dio_model}),
      PinResource('MTDO', {'GPIO7': dio_model}),
      # PinResource('GPIO8', {'GPIO8': dio_model}),  # boot pin, non-allocatable
      # PinResource('GPIO9', {'GPIO9': dio_model}),  # boot pin, non-allocatable
      PinResource('GPIO10', {'GPIO10': dio_model}),
      PinResource('VDD_SPI', {'GPIO11': dio_model}),
      # SPI pins skipped - internal to the modules supported so far
      PinResource('GPIO18', {'GPIO18': dio_model}),
      PinResource('GPIO19', {'GPIO19': dio_model}),
      # PinResource('GPIO20', {'GPIO20': dio_model}),  # boot pin, non-allocatable
      # PinResource('GPIO21', {'GPIO21': dio_model}),  # boot pin, non-allocatable

      # peripherals in section 3.11
      # PeripheralFixedResource('U0', uart_model, {  # programming pin, non-allocatable
      #   'txd': ['GPIO21'], 'rxd': ['GPIO20']
      # }),
      PeripheralAnyResource('U1', uart_model),
      PeripheralAnyResource('I2C', i2c_model),
      PeripheralAnyResource('SPI2', spi_model),
      PeripheralFixedResource('USB', UsbDevicePort(), {
        'dp': ['GPIO19'], 'dm': ['DPIO18']
      }),
    ])

  SYSTEM_PIN_REMAP: Dict[str, Union[str, List[str]]]  # pin name in base -> pin name(s)
  RESOURCE_PIN_REMAP: Dict[str, str]  # resource name in base -> pin name

  def generate(self, assignments: List[str],
               gpio_allocates: List[str], adc_allocates: List[str], dac_allocates: List[str],
               spi_allocates: List[str], i2c_allocates: List[str], uart_allocates: List[str],
               usb_allocates: List[str]) -> None: ...


class Esp32c3_Wroom02_Device(Esp32c3_Device, FootprintBlock):
  """ESP32C module

  Module datasheet: https://www.espressif.com/sites/default/files/documentation/esp32-c3-wroom-02_datasheet_en.pdf
  """
  SYSTEM_PIN_REMAP: Dict[str, Union[str, List[str]]] = {
    'Vdd': '1',
    'Vss': ['9', '19'],  # 19 is EP
    'EN': '2',
    'GPIO2': '16',
    'GPIO8': '7',
    'GPIO9': '8',
    'RXD': '11',  # RXD, GPIO20
    'TXD': '12',  # TXD, GPIO21
  }

  RESOURCE_PIN_REMAP = {
    'GPIO4': '3',
    'GPIO5': '4',
    'GPIO6': '5',
    'GPIO7': '6',
    'GPIO10': '10',
    'GPIO18': '13',
    'GPIO19': '14',
    'GPIO3': '15',
    'GPIO1': '17',
    'GPIO0': '18',
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

    self.footprint(
      'U', 'RF_Module:ESP-WROOM-02',
      dict(chain(system_pins.items(), io_pins.items())),
      mfr='Espressif Systems', part='ESP-WROOM-02',
      datasheet='https://www.espressif.com/sites/default/files/documentation/esp32-c3-wroom-02_datasheet_en.pdf',
    )


class EspProgrammingHeader(ProgrammingConnector):
  def __init__(self) -> None:
    super().__init__()

    # TODO: should these also act as sources?
    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.gnd = self.Port(Ground.empty(), [Common])  # TODO pin at 0v
    self.uart = self.Port(UartPort.empty(), [Output])

    self.conn = self.Block(PassiveConnector())
    self.connect(self.pwr, self.conn.pins.allocate('1').as_voltage_sink())
    self.connect(self.uart.tx, self.conn.pins.allocate('2').as_digital_source())
    self.connect(self.uart.rx, self.conn.pins.allocate('3').as_digital_sink())
    self.connect(self.gnd, self.conn.pins.allocate('4').as_voltage_sink())


class PulldownJumper(Block):
  def __init__(self) -> None:
    super().__init__()

    self.gnd = self.Port(Ground.empty(), [Common])
    self.io = self.Port(DigitalSource.empty(), [Output])

    self.conn = self.Block(PassiveConnector())
    self.connect(self.io, self.conn.pins.allocate('1').as_digital_source())
    self.connect(self.gnd, self.conn.pins.allocate('2').as_voltage_sink())


class Esp32c3_Wroom02(PinMappable, Microcontroller, IoController, Block):
  """Wrapper around Esp32c3_Wroom02 with external capacitors and UART programming header."""
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.ic = self.Block(Esp32c3_Wroom02_Device(pin_assigns=self.pin_assigns))

  def contents(self) -> None:
    super().contents()
    self.connect(self.pwr, self.ic.pwr)
    self.connect(self.gnd, self.ic.gnd)
    self._export_ios_from(self.ic)

    with self.implicit_connect(
        ImplicitConnect(self.pwr, [Power]),
        ImplicitConnect(self.gnd, [Common])
    ) as imp:
      self.vcc_cap0 = imp.Block(DecouplingCapacitor(10 * uFarad(tol=0.2)))  # C1
      self.vcc_cap1 = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))  # C2

      # Note strapping pins (section 3.3) IO2, 8, 9; IO9 is internally pulled up
      # IO9 (internally pulled up) is 1 for SPI boot and 0 for download boot
      # IO2 must be 1 for both SPI and download boot, while IO8 must be 1 for download boot
      self.io8_pull = imp.Block(PulldownResistor(10 * kOhm(tol=0.05))).connected(io=self.ic.io8)
      self.io2_pull = imp.Block(PullupResistor(10 * kOhm(tol=0.05))).connected(io=self.ic.io2)
      self.en_pull = imp.Block(PullupDelayRc(10 * kOhm(tol=0.05), 10*mSecond(tol=0.2))).connected(io=self.ic.en)

      self.uart0 = imp.Block(EspProgrammingHeader())
      self.connect(self.uart0.uart, self.ic.uart0)

      self.io9 = imp.Block(PulldownJumper())
      self.connect(self.io9.io, self.ic.io9)
