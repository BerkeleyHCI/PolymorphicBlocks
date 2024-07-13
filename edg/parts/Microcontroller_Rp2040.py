from abc import abstractmethod
from typing import *

from ..abstract_parts import *
from .JlcPart import JlcPart


@non_library
class Rp2040_Interfaces(IoControllerI2cTarget, IoControllerUsb, BaseIoController):
  """Defines base interfaces for ESP32C3 microcontrollers"""


@non_library
class Rp2040_Ios(Rp2040_Interfaces, BaseIoControllerPinmapGenerator):
  """IOs definitions independent of infrastructural (e.g. power) pins."""
  RESOURCE_PIN_REMAP: Dict[str, str]  # resource name in base -> pin name

  @abstractmethod
  def _vddio(self) -> Port[VoltageLink]:
    """Returns VDDIO (can be VoltageSink or VoltageSource)."""
    ...

  def _iovdd_model(self):
    return VoltageSink(
      voltage_limits=(1.62, 3.63)*Volt,  # Table 628
      current_draw=(1.2, 4.3)*mAmp + self.io_current_draw.upper()  # Table 629
    )

  def _dio_model(self, pwr: Port[VoltageLink]) -> DigitalBidir:
    return DigitalBidir.from_supply(  # table 4.4
      self.gnd, pwr,
      voltage_limit_tolerance=(-0.3, 0.3) * Volt,
      current_limits=(-12, 12)*mAmp,  # by IOH / IOL modes
      input_threshold_abs=(0.8, 2.0)*Volt,  # for IOVdd=3.3, TODO other IOVdd ranges
      pullup_capable=True, pulldown_capable=True
    )

  def _io_pinmap(self) -> PinMapUtil:
    pwr = self._vddio()
    dio_usb_model = dio_ft_model = dio_std_model = self._dio_model(pwr)

    adc_model = AnalogSink.from_supply(  # Table 626
      self.gnd, pwr,
      voltage_limit_tolerance=(0, 0),  # ADC input voltage range
      signal_limit_tolerance=(0, 0),  # ADC input voltage range
      impedance=(100, float('inf')) * kOhm
    )

    uart_model = UartPort(DigitalBidir.empty())
    spi_model = SpiController(DigitalBidir.empty())
    i2c_model = I2cController(DigitalBidir.empty())
    i2c_target_model = I2cTarget(DigitalBidir.empty())

    return PinMapUtil([
      PinResource('GPIO0', {'GPIO0': dio_ft_model}),
      PinResource('GPIO1', {'GPIO1': dio_ft_model}),
      PinResource('GPIO2', {'GPIO2': dio_ft_model}),
      PinResource('GPIO3', {'GPIO3': dio_ft_model}),
      PinResource('GPIO4', {'GPIO4': dio_ft_model}),
      PinResource('GPIO5', {'GPIO5': dio_ft_model}),
      PinResource('GPIO6', {'GPIO6': dio_ft_model}),
      PinResource('GPIO7', {'GPIO7': dio_ft_model}),
      PinResource('GPIO8', {'GPIO8': dio_ft_model}),
      PinResource('GPIO9', {'GPIO9': dio_ft_model}),
      PinResource('GPIO10', {'GPIO10': dio_ft_model}),
      PinResource('GPIO11', {'GPIO11': dio_ft_model}),
      PinResource('GPIO12', {'GPIO12': dio_ft_model}),
      PinResource('GPIO13', {'GPIO13': dio_ft_model}),
      PinResource('GPIO14', {'GPIO14': dio_ft_model}),
      PinResource('GPIO15', {'GPIO15': dio_ft_model}),
      PinResource('GPIO16', {'GPIO16': dio_ft_model}),
      PinResource('GPIO17', {'GPIO17': dio_ft_model}),
      PinResource('GPIO18', {'GPIO18': dio_ft_model}),
      PinResource('GPIO19', {'GPIO19': dio_ft_model}),
      PinResource('GPIO20', {'GPIO20': dio_ft_model}),
      PinResource('GPIO21', {'GPIO21': dio_ft_model}),

      PinResource('GPIO22', {'GPIO22': dio_ft_model}),
      PinResource('GPIO23', {'GPIO23': dio_ft_model}),
      PinResource('GPIO24', {'GPIO24': dio_ft_model}),
      PinResource('GPIO25', {'GPIO25': dio_ft_model}),

      PinResource('GPIO26', {'GPIO26': dio_std_model, 'ADC0': adc_model}),
      PinResource('GPIO27', {'GPIO27': dio_std_model, 'ADC1': adc_model}),
      PinResource('GPIO28', {'GPIO28': dio_std_model, 'ADC2': adc_model}),
      PinResource('GPIO29', {'GPIO29': dio_std_model, 'ADC3': adc_model}),

      # fixed-pin peripherals
      PeripheralFixedPin('USB', UsbDevicePort(dio_usb_model), {
        'dm': 'USB_DM', 'dp': 'USB_DP'
      }),

      # reassignable peripherals
      PeripheralFixedResource('UART0', uart_model, {
        'tx': ['GPIO0', 'GPIO12', 'GPIO16', 'GPIO28'],
        'rx': ['GPIO1', 'GPIO13', 'GPIO17', 'GPIO29']
      }),
      PeripheralFixedResource('UART1', uart_model, {
        'tx': ['GPIO4', 'GPIO8', 'GPIO20', 'GPIO24'],
        'rx': ['GPIO5', 'GPIO9', 'GPIO21', 'GPIO25']
      }),

      PeripheralFixedResource('SPI0', spi_model, {
        'miso': ['GPIO0', 'GPIO4', 'GPIO16', 'GPIO20'],  # RX
        'sck': ['GPIO2', 'GPIO6', 'GPIO18', 'GPIO22'],
        'mosi': ['GPIO3', 'GPIO7', 'GPIO19', 'GPIO23']  # TX
      }),
      PeripheralFixedResource('SPI1', spi_model, {
        'miso': ['GPIO8', 'GPIO12', 'GPIO24', 'GPIO28'],  # RX
        'sck': ['GPIO10', 'GPIO14', 'GPIO26'],
        'mosi': ['GPIO11', 'GPIO15', 'GPIO27']  # TX
      }),
      # SPI peripheral omitted, since TX tri-state is not tied to CS and must be controlled in software
      PeripheralFixedResource('I2C0', i2c_model, {
        'sda': ['GPIO0', 'GPIO4', 'GPIO8', 'GPIO12', 'GPIO16', 'GPIO20', 'GPIO24', 'GPIO28'],
        'scl': ['GPIO1', 'GPIO5', 'GPIO9', 'GPIO13', 'GPIO17', 'GPIO21', 'GPIO25', 'GPIO20']
      }),
      PeripheralFixedResource('I2C1', i2c_model, {
        'sda': ['GPIO2', 'GPIO6', 'GPIO10', 'GPIO14', 'GPIO18', 'GPIO22', 'GPIO24', 'GPIO26'],
        'scl': ['GPIO3', 'GPIO7', 'GPIO11', 'GPIO15', 'GPIO19', 'GPIO23', 'GPIO25', 'GPIO27']
      }),
      PeripheralFixedResource('I2C0_T', i2c_target_model, {  # TODO shared resource w/ I2C controller
        'sda': ['GPIO0', 'GPIO4', 'GPIO8', 'GPIO12', 'GPIO16', 'GPIO20', 'GPIO24', 'GPIO28'],
        'scl': ['GPIO1', 'GPIO5', 'GPIO9', 'GPIO13', 'GPIO17', 'GPIO21', 'GPIO25', 'GPIO20']
      }),
      PeripheralFixedResource('I2C1_T', i2c_target_model, {  # TODO shared resource w/ I2C controller
        'sda': ['GPIO2', 'GPIO6', 'GPIO10', 'GPIO14', 'GPIO18', 'GPIO22', 'GPIO24', 'GPIO26'],
        'scl': ['GPIO3', 'GPIO7', 'GPIO11', 'GPIO15', 'GPIO19', 'GPIO23', 'GPIO25', 'GPIO27']
      }),

      PeripheralFixedPin('SWD', SwdTargetPort(dio_std_model), {
        'swdio': 'SWDIO', 'swclk': 'SWCLK',
      }),
    ]).remap_pins(self.RESOURCE_PIN_REMAP)


class Rp2040_Device(Rp2040_Ios, BaseIoControllerPinmapGenerator, InternalSubcircuit,
                    GeneratorBlock, JlcPart, FootprintBlock):
  RESOURCE_PIN_REMAP = {
    'GPIO0': '2',
    'GPIO1': '3',
    'GPIO2': '4',
    'GPIO3': '5',
    'GPIO4': '6',
    'GPIO5': '7',
    'GPIO6': '8',
    'GPIO7': '9',
    'GPIO8': '11',
    'GPIO9': '12',
    'GPIO10': '13',
    'GPIO11': '14',
    'GPIO12': '15',
    'GPIO13': '16',
    'GPIO14': '17',
    'GPIO15': '18',
    'GPIO16': '27',
    'GPIO17': '28',
    'GPIO18': '29',
    'GPIO19': '30',
    'GPIO20': '31',
    'GPIO21': '32',

    'GPIO22': '34',
    'GPIO23': '35',
    'GPIO24': '36',
    'GPIO25': '37',

    'GPIO26': '38',
    'GPIO27': '39',
    'GPIO28': '40',
    'GPIO29': '41',

    'USB_DM': '46',
    'USB_DP': '47',

    'SWDIO': '25',
    'SWCLK': '24',
  }

  def _vddio(self) -> Port[VoltageLink]:
    return self.iovdd

  def __init__(self, **kwargs) -> None:
    super().__init__(**kwargs)

    self.gnd = self.Port(Ground(), [Common])
    self.iovdd = self.Port(self._iovdd_model(), [Power])

    self.dvdd = self.Port(VoltageSink(  # Digital Core
      voltage_limits=(0.99, 1.21)*Volt,  # Table 628
      current_draw=(0.18, 40)*mAmp,  # Table 629 typ Dormant to Figure 171 approx max DVdd
    ))
    self.vreg_vout = self.Port(VoltageSource(  # actually adjustable, section 2.10.3
      voltage_out=1.1*Volt(tol=0.03),  # default is 1.1v nominal with 3% variation (Table 192)
      current_limits=(0, 100)*mAmp  # Table 1, max current
    ))
    self.vreg_vin = self.Port(VoltageSink(
      voltage_limits=(1.62, 3.63)*Volt,  # Table 628
      current_draw=self.vreg_vout.is_connected().then_else(self.vreg_vout.link().current_drawn, 0*Amp(tol=0)),
    ))
    self.usb_vdd = self.Port(VoltageSink(
      voltage_limits=RangeExpr(),  # depends on if USB is needed
      current_draw=(0.2, 2.0)*mAmp,  # Table 629 typ BOOTSEL Idle to max BOOTSEL Active
    ))
    self.adc_avdd = self.Port(VoltageSink(
      voltage_limits=(2.97, 3.63)*Volt,  # Table 628, performance compromised at <2.97V, lowest 1.62V
      # current draw not specified in datasheet
    ))

    # Additional ports (on top of IoController)
    self.qspi = self.Port(SpiController.empty())  # TODO actually QSPI
    self.qspi_cs = self.Port(DigitalBidir.empty())
    self.qspi_sd2 = self.Port(DigitalBidir.empty())
    self.qspi_sd3 = self.Port(DigitalBidir.empty())

    self.xosc = self.Port(CrystalDriver(frequency_limits=(1, 15)*MHertz,  # datasheet 2.15.2.2
                                        voltage_out=self.iovdd.link().voltage),
                          optional=True)

    self.swd = self.Port(SwdTargetPort.empty())
    self.run = self.Port(DigitalSink.empty(), optional=True)  # internally pulled up
    self._io_ports.insert(0, self.swd)

  def contents(self) -> None:
    super().contents()

    # Port models
    dio_ft_model = dio_std_model = self._dio_model(self.iovdd)
    self.qspi.init_from(SpiController(dio_std_model))
    self.qspi_cs.init_from(dio_std_model)
    self.qspi_sd2.init_from(dio_std_model)
    self.qspi_sd3.init_from(dio_std_model)
    self.run.init_from(DigitalSink.from_bidir(dio_ft_model))

  # Pin/peripheral resource definitions (table 3)
  def _system_pinmap(self) -> Dict[str, CircuitPort]:
    return {
      '51': self.qspi_sd3,
      '52': self.qspi.sck,
      '53': self.qspi.mosi,  # IO0
      '54': self.qspi_sd2,
      '55': self.qspi.miso,  # IO1
      '56': self.qspi_cs,  # IO1

      '20': self.xosc.xtal_in,
      '21': self.xosc.xtal_out,

      '24': self.swd.swclk,
      '25': self.swd.swdio,
      '26': self.run,

      '19': self.gnd,  # TESTEN, connect to gnd

      '1': self.iovdd,
      '10': self.iovdd,
      '22': self.iovdd,
      '33': self.iovdd,
      '42': self.iovdd,
      '49': self.iovdd,

      '23': self.dvdd,
      '50': self.dvdd,

      '44': self.vreg_vin,
      '45': self.vreg_vout,
      '48': self.usb_vdd,
      '43': self.adc_avdd,
      '57': self.gnd,  # pad
    }

  def generate(self) -> None:
    super().generate()

    if not self.get(self.usb.requested()):  # Table 628, VDD_USB can be lower if USB not used (section 2.9.4)
      self.assign(self.usb_vdd.voltage_limits, (1.62, 3.63)*Volt)
    else:
      self.assign(self.usb_vdd.voltage_limits, (3.135, 3.63)*Volt)

    self.footprint(
      'U', 'Package_DFN_QFN:QFN-56-1EP_7x7mm_P0.4mm_EP3.2x3.2mm',
      self._make_pinning(),
      mfr='Raspberry Pi', part='RP2040',
      datasheet='https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf'
    )
    self.assign(self.lcsc_part, 'C2040')
    self.assign(self.actual_basic_part, False)


class Rp2040Usb(InternalSubcircuit, Block):
  """Supporting passives for USB for RP2040"""
  def __init__(self) -> None:
    super().__init__()
    self.usb_rp = self.Port(UsbHostPort.empty(), [Input])
    self.usb = self.Port(UsbDevicePort.empty(), [Output])

  def contents(self) -> None:
    super().contents()

    self.dp_res = self.Block(Resistor(27*Ohm(tol=0.05)))
    self.dm_res = self.Block(Resistor(27*Ohm(tol=0.05)))

    self.connect(self.usb_rp.dm, self.dm_res.a.adapt_to(DigitalBidir()))  # internal ports are ideal
    self.connect(self.usb.dm, self.dm_res.b.adapt_to(
      UsbBitBang.digital_external_from_link(self.usb_rp.dm)))

    self.connect(self.usb_rp.dp, self.dp_res.a.adapt_to(DigitalBidir()))
    self.connect(self.usb.dp, self.dp_res.b.adapt_to(
      UsbBitBang.digital_external_from_link(self.usb_rp.dp)))


class Rp2040(Resettable, Rp2040_Interfaces, Microcontroller, IoControllerWithSwdTargetConnector,
             WithCrystalGenerator, IoControllerPowerRequired, BaseIoControllerExportable, GeneratorBlock):
  DEFAULT_CRYSTAL_FREQUENCY = 12*MHertz(tol=0.005)

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.ic: Rp2040_Device
    self.generator_param(self.reset.is_connected())

  def contents(self) -> None:
    super().contents()

    with self.implicit_connect(
        ImplicitConnect(self.pwr, [Power]),
        ImplicitConnect(self.gnd, [Common])
    ) as imp:
      # https://datasheets.raspberrypi.com/rp2040/hardware-design-with-rp2040.pdf
      self.ic = imp.Block(Rp2040_Device(pin_assigns=ArrayStringExpr()))
      self.connect(self.xtal_node, self.ic.xosc)
      self.connect(self.swd_node, self.ic.swd)
      self.connect(self.reset_node, self.ic.run)

      self.iovdd_cap = ElementDict[DecouplingCapacitor]()
      for i in range(6):  # one per IOVdd, combining USBVdd and IOVdd pin 49 per the example
        self.iovdd_cap[i] = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))
      self.avdd_cap = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))

      self.vreg_in_cap = imp.Block(DecouplingCapacitor(1 * uFarad(tol=0.2)))

      self.mem = imp.Block(SpiMemory(Range.all()))
      self.connect(self.ic.qspi, self.mem.spi)
      self.connect(self.ic.qspi_cs, self.mem.cs)
      mem_qspi = self.mem.with_mixin(SpiMemoryQspi())
      self.connect(self.ic.qspi_sd2, mem_qspi.io2)
      self.connect(self.ic.qspi_sd3, mem_qspi.io3)

    self.connect(self.pwr, self.ic.vreg_vin, self.ic.adc_avdd, self.ic.usb_vdd)
    self.connect(self.ic.vreg_vout, self.ic.dvdd)

    self.dvdd_cap = ElementDict[DecouplingCapacitor]()
    for i in range(2):
      self.dvdd_cap[i] = self.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2))).connected(self.gnd, self.ic.dvdd)

    self.vreg_out_cap = self.Block(DecouplingCapacitor(1 * uFarad(tol=0.2))).connected(self.gnd, self.ic.dvdd)

  def generate(self):
    super().generate()

    if self.get(self.reset.is_connected()):
      self.connect(self.reset, self.ic.run)

  ExportType = TypeVar('ExportType', bound=Port)
  def _make_export_vector(self, self_io: ExportType, inner_vector: Vector[ExportType], name: str,
                          assign: Optional[str]) -> Optional[str]:
    if isinstance(self_io, UsbDevicePort):  # assumed at most one USB port generates
      inner_io = inner_vector.request(name)
      (self.usb_res, ), self.usb_chain = self.chain(inner_io, self.Block(Rp2040Usb()), self_io)
      return assign
    return super()._make_export_vector(self_io, inner_vector, name, assign)

  def _crystal_required(self) -> bool:  # crystal needed for USB b/c tighter freq tolerance
    return len(self.get(self.usb.requested())) > 0 or super()._crystal_required()


class Xiao_Rp2040(IoControllerUsbOut, IoControllerPowerOut, Rp2040_Ios, IoController, GeneratorBlock, FootprintBlock):
  """RP2040 development board, a tiny development (21x17.5mm) daughterboard.
  Has an onboard USB connector, so this can also source power.

  Limited pins (only 11 for IOs, of which 6 are usable as the other 5 have boot requirements).

  Requires Seeed Studio's KiCad library for the footprint: https://github.com/Seeed-Studio/OPL_Kicad_Library
  The 'Seeed Studio XIAO Series Library' must have been added as a footprint library of the same name.

  Pinning data: https://www.seeedstudio.com/blog/wp-content/uploads/2022/08/Seeed-Studio-XIAO-Series-Package-and-PCB-Design.pdf
  """
  SYSTEM_PIN_REMAP: Dict[str, Union[str, List[str]]] = {
    'VDD': '12',
    'GND': '13',
    'VUSB': '14',
  }
  RESOURCE_PIN_REMAP = {
    'GPIO26': '1',
    'GPIO27': '2',
    'GPIO28': '3',
    'GPIO29': '4',
    'GPIO6': '5',
    'GPIO7': '6',
    'GPIO0': '7',

    'GPIO1': '8',
    'GPIO2': '9',
    'GPIO4': '10',
    'GPIO3': '11',
  }

  def _vddio(self) -> Port[VoltageLink]:
    if self.get(self.pwr.is_connected()):  # board sinks power
      return self.pwr
    else:
      return self.pwr_out

  def _system_pinmap(self) -> Dict[str, CircuitPort]:
    if self.get(self.pwr.is_connected()):  # board sinks power
      self.require(~self.vusb_out.is_connected(), "can't source USB power if power input connected")
      self.require(~self.pwr_out.is_connected(), "can't source 3v3 power if power input connected")
      return VariantPinRemapper({
        'VDD': self.pwr,
        'GND': self.gnd,
      }).remap(self.SYSTEM_PIN_REMAP)
    else:  # board sources power (default)
      return VariantPinRemapper({
        'VDD': self.pwr_out,
        'GND': self.gnd,
        'VUSB': self.vusb_out,
      }).remap(self.SYSTEM_PIN_REMAP)

  def contents(self) -> None:
    super().contents()

    self.gnd.init_from(Ground())
    self.pwr.init_from(self._iovdd_model())

    self.vusb_out.init_from(VoltageSource(
      voltage_out=UsbConnector.USB2_VOLTAGE_RANGE,
      current_limits=UsbConnector.USB2_CURRENT_LIMITS
    ))
    self.pwr_out.init_from(VoltageSource(
      voltage_out=3.3*Volt(tol=0.05),  # tolerance is a guess
      current_limits=UsbConnector.USB2_CURRENT_LIMITS
    ))

    self.generator_param(self.pwr.is_connected())

  def generate(self) -> None:
    super().generate()

    self.footprint(
      'U', 'Seeed Studio XIAO Series Library:XIAO-Generic-Hybrid-14P-2.54-21X17.8MM',
      self._make_pinning(),
      mfr='', part='XIAO RP2040',
      datasheet='https://www.seeedstudio.com/XIAO-RP2040-v1-0-p-5026.html'
    )
