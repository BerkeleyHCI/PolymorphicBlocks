from typing import *

from electronics_abstract_parts import *
from .JlcPart import JlcPart
from .Microcontroller_Esp import HasEspProgramming


@non_library
class Esp32c3_Interfaces(IoControllerSpiPeripheral, IoControllerI2cTarget, IoControllerI2s, IoControllerWifi,
                         IoControllerBle, BaseIoController):
  """Defines base interfaces for ESP32C3 microcontrollers"""


@abstract_block
class Esp32c3_Base(Esp32c3_Interfaces, InternalSubcircuit, BaseIoControllerPinmapGenerator):
  """Base class for ESP32-C3 series devices, with RISC-V core, 2.4GHz WiF,i, BLE5.
  PlatformIO: use board ID esp32-c3-devkitm-1

  Chip datasheet: https://espressif.com/sites/default/files/documentation/esp32-c3_datasheet_en.pdf
  """
  def __init__(self, **kwargs) -> None:
    super().__init__(**kwargs)

    self.pwr = self.Port(VoltageSink(
      voltage_limits=(3.0, 3.6)*Volt,  # section 4.2
      current_draw=(0.001, 335)*mAmp + self.io_current_draw.upper()  # section 4.6, from power off to RF active
    ), [Power])
    self.gnd = self.Port(Ground(), [Common])

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
    self.io8 = self.Port(self._dio_model)  # needs external pullup, required for download boot
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
    adc_model = AnalogSink.from_supply(
      self.gnd, self.pwr,
      signal_limit_abs=(0, 2.5)*Volt,  # table 15, effective ADC range
      # TODO: impedance / leakage - not specified by datasheet
    )

    uart_model = UartPort(DigitalBidir.empty())
    spi_model = SpiController(DigitalBidir.empty(), (0, 60) * MHertz)  # section 3.4.2, max block in GP controller mode
    spi_peripheral_model = SpiPeripheral(DigitalBidir.empty(), (0, 60) * MHertz)
    i2c_model = I2cController(DigitalBidir.empty())  # section 3.4.4, supporting 100/400 and up to 800 kbit/s
    i2c_target_model = I2cTarget(DigitalBidir.empty())

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
      PeripheralAnyResource('I2C_T', i2c_target_model),  # TODO shared resource w/ I2C controller
      PeripheralAnyResource('SPI2', spi_model),
      PeripheralAnyResource('SPI2_P', spi_peripheral_model),  # TODO shared resource w/ SPI controller
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


class Esp32c3_Wroom02(Microcontroller, Radiofrequency, HasEspProgramming, Resettable, Esp32c3_Interfaces,
                      IoControllerPowerRequired, BaseIoControllerExportable, GeneratorBlock):
  """Wrapper around Esp32c3_Wroom02 with external capacitors and UART programming header."""
  def __init__(self):
    super().__init__()
    self.ic: Esp32c3_Wroom02_Device
    self.generator_param(self.reset.is_connected())

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
      vdd_pull = self.pwr.as_digital_source()
      self.connect(self.ic.io8, vdd_pull)
      self.connect(self.ic.io2, vdd_pull)


  def generate(self) -> None:
    super().generate()

    if self.get(self.reset.is_connected()):
      self.connect(self.reset, self.ic.en)
    else:
      self.en_pull = self.Block(PullupDelayRc(10 * kOhm(tol=0.05), 10*mSecond(tol=0.2))).connected(
        gnd=self.gnd, pwr=self.pwr, io=self.ic.en)


class Esp32c3_Device(Esp32c3_Base, FootprintBlock, JlcPart):
  """ESP32C3 with 4MB integrated flash
  TODO: support other part numbers, including without integrated flash
  """
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.lna_in = self.Port(Passive())

    # chip power draw is modeled in self.pwr
    self.vdd3p3 = self.Port(VoltageSink(  # needs to be downstream of a filter
      voltage_limits=(3.0, 3.6)*Volt,  # section 4.2
    ))
    self.vdd3p3_rtc = self.Port(VoltageSink(
      voltage_limits=(3.0, 3.6)*Volt,  # section 4.2
    ))
    self.vdd3p3_cpu = self.Port(VoltageSink(
      voltage_limits=(3.0, 3.6)*Volt,  # section 4.2
    ))
    self.vdd_spi = self.Port(VoltageSink(
      voltage_limits=(3.0, 3.6)*Volt,  # section 4.2
    ))

    # 10ppm requirement from ESP32-C3-WROOM schematic, and in ESP32 hardware design guidelines
    self.xtal = self.Port(CrystalDriver(frequency_limits=40*MHertz(tol=10e-6),
                                        voltage_out=self.pwr.link().voltage))

  def _system_pinmap(self) -> Dict[str, CircuitPort]:
    return VariantPinRemapper(super()._system_pinmap()).remap({
      'Vdd': ['31', '32'],  # VDDA
      'Vss': ['33'],  # 33 is EP
      'GPIO2': '6',
      'EN': '7',
      'GPIO8': '14',
      'GPIO9': '15',
      'RXD': '27',  # U0RXD, GPIO20
      'TXD': '28',  # U0TXD, GPIO21
    })

  def _io_pinmap(self) -> PinMapUtil:
    return super()._io_pinmap().remap_pins({
      'GPIO0': '4',
      'GPIO1': '5',
      'GPIO3': '8',
      'MTMS': '9',  # GPIO4
      'MTDI': '10',  # GPIO5
      'MTCK': '12',  # GPIO6
      'MTDO': '13',  # GPIO7
      'GPIO10': '16',
      'GPIO18': '25',
      'GPIO19': '26',
    })

  def generate(self) -> None:
    super().generate()

    pinning = self._make_pinning()
    pinning.update({
      '1': self.lna_in,
      '11': self.vdd3p3_rtc,
      '17': self.vdd3p3_cpu,
      '18': self.vdd_spi,
      '2': self.vdd3p3,
      '3': self.vdd3p3,
      '30': self.xtal.xtal_in,
      '29': self.xtal.xtal_out,
    })

    self.footprint(
      'U', 'Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.65x3.65mm',
      pinning,
      mfr='Espressif Systems', part='ESP32-C3FH4',
      datasheet='https://www.espressif.com/sites/default/files/documentation/esp32-c3-wroom-02_datasheet_en.pdf',
    )
    self.assign(self.lcsc_part, 'C2858491')  # "discontinued"
    self.assign(self.actual_basic_part, False)


class Esp32c3(Microcontroller, Radiofrequency, HasEspProgramming, Resettable, Esp32c3_Interfaces,
              WithCrystalGenerator, IoControllerPowerRequired, BaseIoControllerExportable, GeneratorBlock):
  """ESP32-C3 application circuit, bare chip + RF circuits.
  NOT RECOMMENDED - you will need to do your own RF layout, instead consider using the WROOM module."""

  DEFAULT_CRYSTAL_FREQUENCY = 40*MHertz(tol=10e-6)

  def __init__(self):
    super().__init__()
    self.ic: Esp32c3_Device
    self.generator_param(self.reset.is_connected())

    self.not_recommended = self.Parameter(BoolExpr(False))

    self.io2_ext_connected: bool = False
    self.io8_ext_connected: bool = False

  def contents(self) -> None:
    super().contents()
    self.require(self.not_recommended, "not recommended: requires RF design, consider using the module version instead")

    with self.implicit_connect(
        ImplicitConnect(self.pwr, [Power]),
        ImplicitConnect(self.gnd, [Common])
    ) as imp:
      self.ic = imp.Block(Esp32c3_Device(pin_assigns=ArrayStringExpr()))
      self.connect(self.pwr, self.ic.vdd3p3_rtc, self.ic.vdd3p3_cpu, self.ic.vdd_spi)

      self.connect(self.xtal_node, self.ic.xtal)
      self.connect(self.program_uart_node, self.ic.uart0)
      self.connect(self.program_en_node, self.ic.en)
      self.connect(self.program_boot_node, self.ic.io9)

      self.vdd_bulk_cap = imp.Block(DecouplingCapacitor(10*uFarad(tol=0.2)))  # C5
      self.vdda_cap0 = imp.Block(DecouplingCapacitor(1*uFarad(tol=0.2)))  # C3
      self.vdda_cap1 = imp.Block(DecouplingCapacitor(10*nFarad(tol=0.2)))  # C3
      self.vddrtc_cap = imp.Block(DecouplingCapacitor(0.1*uFarad(tol=0.2)))  # C3
      self.vddcpu_cap = imp.Block(DecouplingCapacitor(0.1*uFarad(tol=0.2)))  # C10
      self.vddspi_cap = imp.Block(DecouplingCapacitor(1*uFarad(tol=0.2)))  # C11

      self.ant = self.Block(Antenna(frequency=(2402, 2484)*MHertz, impedance=50*Ohm(tol=0.1), power=(0, 0.126)*Watt))
      # expand the bandwidth to allow a lower Q and higher bandwidth
      # TODO: more principled calculation of Q / bandwidth, voltage, current and tolerance
      # 10% tolerance is roughly to support 5% off-nominal tolerance plus 5% component tolerance
      (self.pi, ), _ = self.chain(self.ic.lna_in,
                                  imp.Block(PiLowPassFilter((2402-200, 2484+200)*MHertz, 35*Ohm, 10*Ohm, 50*Ohm,
                                                            0.10, self.pwr.link().voltage, (0, 0.1)*Amp)),
                                  self.ant.a)

    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common])
    ) as imp:
      self.vdd3p3_l_cap = imp.Block(DecouplingCapacitor(0.1*uFarad(tol=0.2)))\
        .connected(pwr=self.pwr)  # C6
      self.vdd3p3_cap = imp.Block(DecouplingCapacitor(0.1*uFarad(tol=0.2)))\
        .connected(pwr=self.ic.vdd3p3)  # C7 - DNP on ESP32-C3-WROOM schematic but 0.1uF on hardware design guide
      self.vdd3p3_l = self.Block(SeriesPowerInductor(
        inductance=2*nHenry(tol=0.2),
      )).connected(self.pwr, self.ic.vdd3p3)

  def generate(self) -> None:
    super().generate()

    if self.get(self.reset.is_connected()):
      self.connect(self.reset, self.ic.en)
    else:
      self.en_pull = self.Block(PullupDelayRc(10 * kOhm(tol=0.05), 10*mSecond(tol=0.2))).connected(
        gnd=self.gnd, pwr=self.pwr, io=self.ic.en)

    # Note strapping pins (section 3.3) IO2, 8, 9; IO9 is internally pulled up
    # IO9 (internally pulled up) is 1 for SPI boot and 0 for download boot
    # IO2 must be 1 for both SPI and download boot, while IO8 must be 1 for download boot
    vdd_pull = self.pwr.as_digital_source()
    if not self.io8_ext_connected:
      self.connect(self.ic.io8, vdd_pull)
      self.io8_ext_connected = True  # set to ensure this runs after external connections
    if not self.io2_ext_connected:
      self.connect(self.ic.io2, vdd_pull)
      self.io2_ext_connected = True  # set to ensure this runs after external connections

  ExportType = TypeVar('ExportType', bound=Port)
  def _make_export_vector(self, self_io: ExportType, inner_vector: Vector[ExportType], name: str,
                          assign: Optional[str]) -> Optional[str]:
    """Add support for _GPIO2/8/9_STRAP and remap them to io2/8/9."""
    if isinstance(self_io, DigitalBidir):
      if assign == f'{name}=_GPIO2_STRAP':
        self.connect(self_io, self.ic.io2)
        assert not self.io2_ext_connected  # assert not yet hard tied
        self.io2_ext_connected = True
        return None
      elif assign == f'{name}=_GPIO8_STRAP':
        self.connect(self_io, self.ic.io8)
        assert not self.io8_ext_connected  # assert not yet hard tied
        self.io8_ext_connected = True
        return None
      elif assign == f'{name}=_GPIO9_STRAP':
        self.connect(self_io, self.ic.io9)
        return None
    return super()._make_export_vector(self_io, inner_vector, name, assign)

  def _crystal_required(self) -> bool:
    return True  # crystal oscillator always required
