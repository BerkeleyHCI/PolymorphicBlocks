from abc import abstractmethod
from typing import *

from electronics_abstract_parts import *
from .JlcPart import JlcPart


@non_library
class Nrf52840_Interfaces(IoControllerUsb, IoControllerI2s, IoControllerBle, BaseIoController):
  """Defines base interfaces for nRF52840 microcontrollers"""


@abstract_block
class Nrf52840_Ios(Nrf52840_Interfaces, BaseIoControllerPinmapGenerator, InternalSubcircuit, GeneratorBlock, FootprintBlock):
  """nRF52840 IO mappings
  https://infocenter.nordicsemi.com/pdf/nRF52840_PS_v1.7.pdf"""
  RESOURCE_PIN_REMAP: Dict[str, str]  # resource name in base -> pin name

  @abstractmethod
  def _gnd_vddio(self) -> Tuple[Port[VoltageLink], Port[VoltageLink]]:
    ...

  def _vdd_model(self) -> VoltageSink:
    return VoltageSink(
      voltage_limits=(1.75, 3.6)*Volt,  # 1.75 minimum for power-on reset
      current_draw=(0, 212 / 64 + 4.8)*mAmp + self.io_current_draw.upper()  # CPU @ max 212 Coremarks + 4.8mA in RF transmit
    )

  def _dio_model(self, gnd: Port[VoltageLink], pwr: Port[VoltageLink]) -> DigitalBidir:
    return DigitalBidir.from_supply(
      gnd, pwr,
      voltage_limit_tolerance=(-0.3, 0.3) * Volt,
      current_limits=(-6, 6)*mAmp,  # minimum current, high drive, Vdd>2.7
      current_draw=(0, 0)*Amp,
      input_threshold_factor=(0.3, 0.7),
      pullup_capable=True, pulldown_capable=True,
    )

  def _io_pinmap(self) -> PinMapUtil:
    """Returns the mappable for given the input power and ground references.
    This separates the system pins definition from the IO pins definition."""
    gnd, pwr = self._gnd_vddio()
    dio_model = self._dio_model(gnd, pwr)
    dio_lf_model = dio_model  # "standard drive, low frequency IO only" (differences not modeled)

    adc_model = AnalogSink(
      voltage_limits=(gnd.link().voltage.upper(), pwr.link().voltage.lower()) +
                     (-0.3, 0.3) * Volt,
      current_draw=(0, 0) * Amp,
      impedance=Range.from_lower(1)*MOhm
    )

    uart_model = UartPort(DigitalBidir.empty())
    spi_model = SpiController(DigitalBidir.empty(), (125, 32000) * kHertz)
    spi_peripheral_model = SpiPeripheral(DigitalBidir.empty(), (125, 32000) * kHertz)  # tristated by CS pin
    i2c_model = I2cController(DigitalBidir.empty())
    i2c_target_model = I2cTarget(DigitalBidir.empty())
    i2s_model = I2sController(DigitalBidir.empty())

    hf_io_pins = [
      'P0.00', 'P0.01', 'P0.26', 'P0.27', 'P0.04',
      'P0.05', 'P0.06', 'P0.07', 'P0.08', 'P1.08', 'P1.09', 'P0.11', 'P0.12',
      'P0.14', 'P0.16', 'P0.19', 'P0.21', 'P0.23', 'P0.25',  # 'P0.18'
      'P0.13', 'P0.15', 'P0.17', 'P0.20', 'P0.22', 'P0.24',  'P1.00',
    ]

    return PinMapUtil([  # Section 7.1.2 with QIAA aQFN73 & QFAA QFN48 pins only
      PinResource('P0.31', {'P0.31': dio_lf_model, 'AIN7': adc_model}),
      PinResource('P0.29', {'P0.29': dio_lf_model, 'AIN5': adc_model}),
      PinResource('P0.02', {'P0.02': dio_lf_model, 'AIN0': adc_model}),
      PinResource('P1.15', {'P1.15': dio_lf_model}),
      PinResource('P1.13', {'P1.13': dio_lf_model}),
      PinResource('P1.10', {'P1.10': dio_lf_model}),
      PinResource('P0.30', {'P0.30': dio_lf_model, 'AIN6': adc_model}),
      PinResource('P0.28', {'P0.28': dio_lf_model, 'AIN4': adc_model}),
      PinResource('P0.03', {'P0.03': dio_lf_model, 'AIN1': adc_model}),
      PinResource('P1.14', {'P1.14': dio_lf_model}),
      PinResource('P1.12', {'P1.12': dio_lf_model}),
      PinResource('P1.11', {'P1.11': dio_lf_model}),
      PinResource('P0.00', {'P0.00': dio_model}),  # TODO also 32.768 kHz crystal in
      PinResource('P0.01', {'P0.01': dio_model}),  # TODO also 32.768 kHz crystal in
      PinResource('P0.26', {'P0.26': dio_model}),
      PinResource('P0.27', {'P0.27': dio_model}),
      PinResource('P0.04', {'P0.04': dio_model, 'AIN2': adc_model}),
      PinResource('P0.10', {'P0.10': dio_lf_model}),  # TODO also NFC2

      PinResource('P0.05', {'P0.05': dio_model, 'AIN3': adc_model}),
      PinResource('P0.06', {'P0.06': dio_model}),
      PinResource('P0.09', {'P0.09': dio_lf_model}),  # TODO also NFC1
      PinResource('P0.07', {'P0.07': dio_model}),
      PinResource('P0.08', {'P0.08': dio_model}),
      PinResource('P1.08', {'P1.08': dio_model}),
      PinResource('P1.07', {'P1.07': dio_lf_model}),
      PinResource('P1.09', {'P1.09': dio_model}),
      PinResource('P1.06', {'P1.06': dio_lf_model}),
      PinResource('P0.11', {'P0.11': dio_model}),
      PinResource('P1.05', {'P1.05': dio_lf_model}),
      PinResource('P0.12', {'P0.12': dio_model}),
      PinResource('P1.04', {'P1.04': dio_lf_model}),
      PinResource('P1.03', {'P1.03': dio_lf_model}),
      PinResource('P1.02', {'P1.02': dio_lf_model}),
      PinResource('P1.01', {'P1.01': dio_lf_model}),
      PinResource('P0.14', {'P0.14': dio_model}),
      PinResource('P0.16', {'P0.16': dio_model}),
      # PinResource('P0.18', {'P0.18': dio_model}),  # configurable as RESET, mappable
      PinResource('P0.19', {'P0.19': dio_model}),
      PinResource('P0.21', {'P0.21': dio_model}),
      PinResource('P0.23', {'P0.23': dio_model}),
      PinResource('P0.25', {'P0.25': dio_model}),

      PinResource('P0.13', {'P0.13': dio_model}),
      PinResource('P0.15', {'P0.15': dio_model}),
      PinResource('P0.17', {'P0.17': dio_model}),
      PinResource('P0.20', {'P0.20': dio_model}),
      PinResource('P0.22', {'P0.22': dio_model}),
      PinResource('P0.24', {'P0.24': dio_model}),
      PinResource('P1.00', {'P1.00': dio_model}),  # TRACEDATA[0] and SWO, if used as IO must clear TRACECONFIG reg

      PeripheralFixedPin('SWD', SwdTargetPort(dio_model), {
        'swclk': 'SWCLK', 'swdio': 'SWDIO',
      }),
      PeripheralFixedPin('USBD', UsbDevicePort(), {
        'dp': 'D+', 'dm': 'D-'
      }),

      PeripheralFixedResource('SPIM0', spi_model, {
        'sck': hf_io_pins, 'miso': hf_io_pins, 'mosi': hf_io_pins,
      }),
      PeripheralFixedResource('SPIM1', spi_model, {
        'sck': hf_io_pins, 'miso': hf_io_pins, 'mosi': hf_io_pins,
      }),
      PeripheralFixedResource('SPIM2', spi_model, {
        'sck': hf_io_pins, 'miso': hf_io_pins, 'mosi': hf_io_pins,
      }),
      PeripheralFixedResource('SPIM3', spi_model, {
        'sck': hf_io_pins, 'miso': hf_io_pins, 'mosi': hf_io_pins,
      }),
      PeripheralFixedResource('SPIS0', spi_peripheral_model, {  # TODO shared resource w/ SPI controller
        'sck': hf_io_pins, 'miso': hf_io_pins, 'mosi': hf_io_pins,
      }),
      PeripheralFixedResource('SPIS1', spi_peripheral_model, {  # TODO shared resource w/ SPI controller
        'sck': hf_io_pins, 'miso': hf_io_pins, 'mosi': hf_io_pins,
      }),
      PeripheralFixedResource('SPIS2', spi_peripheral_model, {  # TODO shared resource w/ SPI controller
        'sck': hf_io_pins, 'miso': hf_io_pins, 'mosi': hf_io_pins,
      }),
      PeripheralFixedResource('TWIM0', i2c_model, {
        'scl': hf_io_pins, 'sda': hf_io_pins,
      }),
      PeripheralFixedResource('TWIM1', i2c_model, {
        'scl': hf_io_pins, 'sda': hf_io_pins,
      }),
      PeripheralFixedResource('TWIS0', i2c_target_model, {  # TODO shared resource w/ I2C controller
        'scl': hf_io_pins, 'sda': hf_io_pins,
      }),
      PeripheralFixedResource('TWIS1', i2c_target_model, {  # TODO shared resource w/ I2C controller
        'scl': hf_io_pins, 'sda': hf_io_pins,
      }),
      PeripheralFixedResource('UARTE0', uart_model, {
        'tx': hf_io_pins, 'rx': hf_io_pins,
      }),
      PeripheralFixedResource('UARTE1', uart_model, {
        'tx': hf_io_pins, 'rx': hf_io_pins,
      }),
      PeripheralFixedResource('I2S', i2s_model, {
        'sck': hf_io_pins, 'ws': hf_io_pins, 'sd': hf_io_pins,
      }),
    ]).remap_pins(self.RESOURCE_PIN_REMAP)


@abstract_block
class Nrf52840_Base(Nrf52840_Ios, IoControllerPowerRequired, InternalSubcircuit, GeneratorBlock):
  SYSTEM_PIN_REMAP: Dict[str, Union[str, List[str]]]  # pin name in base -> pin name(s)

  def _gnd_vddio(self) -> Tuple[Port[VoltageLink], Port[VoltageLink]]:
    return self.gnd, self.pwr

  def _system_pinmap(self) -> Dict[str, CircuitPort]:
    return VariantPinRemapper({
      'Vdd': self.pwr,
      'Vss': self.gnd,
      'Vbus': self.pwr_usb,
      'nRESET': self.nreset,
    }).remap(self.SYSTEM_PIN_REMAP)

  def __init__(self, **kwargs) -> None:
    super().__init__(**kwargs)

    self.pwr.init_from(self._vdd_model())
    self.gnd.init_from(Ground())

    self.pwr_usb = self.Port(VoltageSink(
      voltage_limits=(4.35, 5.5)*Volt,
      current_draw=(0.262, 7.73) * mAmp  # CPU/USB sleeping to everything active
    ), optional=True)
    self.require((self.usb.length() > 0).implies(self.pwr_usb.is_connected()), "USB require Vbus connected")

    # Additional ports (on top of IoController)
    # Crystals from table 15, 32, 33
    # TODO Table 32, model crystal load capacitance and series resistance ratings
    self.xtal = self.Port(CrystalDriver(frequency_limits=(1, 25)*MHertz, voltage_out=self.pwr.link().voltage),
                          optional=True)
    # Assumed from "32kHz crystal" in 14.5
    self.xtal_rtc = self.Port(CrystalDriver(frequency_limits=(32, 33)*kHertz, voltage_out=self.pwr.link().voltage),
                              optional=True)

    self.swd = self.Port(SwdTargetPort.empty())
    self.nreset = self.Port(DigitalSink.from_bidir(self._dio_model(self.gnd, self.pwr)))
    self._io_ports.insert(0, self.swd)


class Holyiot_18010_Device(Nrf52840_Base):
  SYSTEM_PIN_REMAP: Dict[str, Union[str, List[str]]] = {
    'Vdd': '14',
    'Vss': ['1', '25', '37'],
    'Vbus': '22',
    'nRESET': '21',
  }
  RESOURCE_PIN_REMAP = {  # boundary pins only, inner pins ignored
    'P1.11': '2',
    'P1.10': '3',
    'P1.13': '4',
    'P1.15': '5',
    'P0.03': '6',
    'P0.02': '7',
    'P0.28': '8',
    'P0.29': '9',
    'P0.30': '10',
    'P0.31': '11',
    'P0.04': '12',
    'P0.05': '13',

    'P0.07': '15',
    'P1.09': '16',
    'P0.12': '17',
    'P0.23': '18',
    'P0.21': '19',
    'P0.19': '20',
    'D-': '23',
    'D+': '24',

    'P0.22': '26',
    'P1.00': '27',
    'P1.03': '28',
    'P1.01': '29',
    'P1.02': '30',
    'SWCLK': '31',
    'SWDIO': '32',
    'P1.04': '33',
    'P1.06': '34',
    'P0.09': '35',
    'P0.10': '36',
  }

  def generate(self) -> None:
    super().generate()

    self.footprint(
      'U', 'edg:Holyiot-18010-NRF52840',
      self._make_pinning(),
      mfr='Holyiot', part='18010',
      datasheet='http://www.holyiot.com/tp/2019042516322180424.pdf'
    )


class Holyiot_18010(Microcontroller, Radiofrequency, Resettable, Nrf52840_Interfaces, IoControllerWithSwdTargetConnector,
                    IoControllerPowerRequired, BaseIoControllerExportable, GeneratorBlock):
  """Wrapper around the Holyiot 18010 that includes supporting components (programming port)"""
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.ic: Holyiot_18010_Device
    self.ic = self.Block(Holyiot_18010_Device(pin_assigns=ArrayStringExpr()))
    self.pwr_usb = self.Export(self.ic.pwr_usb, optional=True)
    self.generator_param(self.reset.is_connected())

  def contents(self):
    super().contents()
    self.connect(self.pwr, self.ic.pwr)
    self.connect(self.gnd, self.ic.gnd)

    self.connect(self.swd_node, self.ic.swd)
    self.connect(self.reset_node, self.ic.nreset)

  def generate(self):
    if self.get(self.reset.is_connected()):
      self.connect(self.reset, self.ic.nreset)

class Mdbt50q_1mv2_Device(Nrf52840_Base, JlcPart):
  SYSTEM_PIN_REMAP: Dict[str, Union[str, List[str]]] = {
    'Vdd': ['28', '30'],  # 28=Vdd, 30=VddH; 31=DccH is disconnected - from section 8.3 for input voltage <3.6v
    'Vss': ['1', '2', '15', '33', '55'],
    'Vbus': '32',
    'nRESET': '40',
  }
  RESOURCE_PIN_REMAP = {  # boundary pins only, inner pins ignored
    'P1.10': '3',
    'P1.11': '4',
    'P1.12': '5',
    'P1.13': '6',
    'P1.14': '7',
    'P1.15': '8',
    'P0.03': '9',
    'P0.29': '10',
    'P0.02': '11',
    'P0.31': '12',
    'P0.28': '13',
    'P0.30': '14',

    'P0.27': '16',
    'P0.00': '17',
    'P0.01': '18',
    'P0.26': '19',
    'P0.04': '20',
    'P0.05': '21',
    'P0.06': '22',
    'P0.07': '23',
    'P0.08': '24',
    'P1.08': '25',
    'P1.09': '26',
    'P0.11': '27',
    'P0.12': '29',
    'D-': '34',
    'D+': '35',

    'P0.14': '36',
    'P0.13': '37',
    'P0.16': '38',
    'P0.15': '39',
    'P0.17': '41',
    'P0.19': '42',
    'P0.21': '43',
    'P0.20': '44',
    'P0.23': '45',
    'P0.22': '46',
    'P1.00': '47',
    'P0.24': '48',
    'P0.25': '49',
    'P1.02': '50',
    'SWDIO': '51',
    'P0.09': '52',
    'SWCLK': '53',
    'P0.10': '54',

    'P1.04': '56',
    'P1.06': '57',
    'P1.07': '58',
    'P1.05': '59',
    'P1.03': '60',
    'P1.01': '61',
  }

  def generate(self) -> None:
    super().generate()

    self.assign(self.lcsc_part, 'C5118826')
    self.assign(self.actual_basic_part, False)
    self.footprint(
      'U', 'RF_Module:Raytac_MDBT50Q',
      self._make_pinning(),
      mfr='Raytac', part='MDBT50Q-1MV2',
      datasheet='https://www.raytac.com/download/index.php?index_id=43'
    )


class Mdbt50q_UsbSeriesResistor(InternalSubcircuit, Block):
  def __init__(self):
    super().__init__()
    self.usb_inner = self.Port(UsbHostPort().empty(), [Input])
    self.usb_outer = self.Port(UsbDevicePort().empty(), [Output])
    self.res_dp = self.Block(Resistor(27*Ohm(tol=0.01)))
    self.res_dm = self.Block(Resistor(27*Ohm(tol=0.01)))
    self.connect(self.usb_inner.dp, self.res_dp.a.adapt_to(DigitalBidir()))  # TODO propagate params - needs bridge mechanism
    self.connect(self.usb_outer.dp, self.res_dp.b.adapt_to(DigitalBidir()))
    self.connect(self.usb_inner.dm, self.res_dm.a.adapt_to(DigitalBidir()))
    self.connect(self.usb_outer.dm, self.res_dm.b.adapt_to(DigitalBidir()))


class Mdbt50q_1mv2(Microcontroller, Radiofrequency, Resettable, Nrf52840_Interfaces, IoControllerWithSwdTargetConnector,
                   IoControllerPowerRequired, BaseIoControllerExportable, GeneratorBlock):
  """Wrapper around the Mdbt50q_1mv2 that includes the reference schematic"""
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.ic: Mdbt50q_1mv2_Device
    self.ic = self.Block(Mdbt50q_1mv2_Device(pin_assigns=ArrayStringExpr()))  # defined in generator to mix in SWO/TDI
    self.pwr_usb = self.Export(self.ic.pwr_usb, optional=True)
    self.generator_param(self.reset.is_connected())

  def contents(self) -> None:
    super().contents()
    self.connect(self.pwr, self.ic.pwr)
    self.connect(self.gnd, self.ic.gnd)

    self.connect(self.swd_node, self.ic.swd)
    self.connect(self.reset_node, self.ic.nreset)

    with self.implicit_connect(
        ImplicitConnect(self.pwr, [Power]),
        ImplicitConnect(self.gnd, [Common])
    ) as imp:
      self.vcc_cap = imp.Block(DecouplingCapacitor(10 * uFarad(tol=0.2)))

  def generate(self):
    super().generate()

    if self.get(self.reset.is_connected()):
      self.connect(self.reset, self.ic.nreset)

  def _make_export_io(self, self_io: Port, inner_io: Port):
    if isinstance(self_io, UsbDevicePort):  # assumed at most one USB port generates
      (self.usb_res, ), self.usb_chain = self.chain(inner_io, self.Block(Mdbt50q_UsbSeriesResistor()), self_io)
      self.vbus_cap = self.Block(DecouplingCapacitor(10 * uFarad(tol=0.2))).connected(self.gnd, self.pwr_usb)
    else:
      super()._make_export_io(self_io, inner_io)


class Feather_Nrf52840(IoControllerUsbOut, IoControllerPowerOut, Nrf52840_Ios, IoController, GeneratorBlock,
                       FootprintBlock):
  """Feather nRF52840 socketed dev board as either power source or sink"""

  SYSTEM_PIN_REMAP: Dict[str, Union[str, List[str]]] = {
    'Vdd': '2',  # 3v3
    'Vss': '4',

    # 'reset': '1',
    'Vbus': '26',
    # 'EN': '27',  # controls the onboard 3.3 LDO, internally pulled up
    # 'Vbat': '28',
  }
  RESOURCE_PIN_REMAP = {  # boundary pins only, inner pins ignored
    'P0.31': '3',  # AREF
    'P0.04': '5',  # A0
    'P0.05': '6',  # A1
    'P0.30': '7',  # A2
    'P0.28': '8',  # A3
    'P0.02': '9',  # A4
    'P0.03': '10',  # A5
    'P0.14': '11',  # SCK
    'P0.13': '12',  # MOSI
    'P0.15': '13',  # MISO
    'P0.24': '14',  # RXD
    'P0.25': '15',  # TXD
    'P0.10': '16',  # D2

    'P0.12': '17',  # SDA
    'P0.11': '18',  # SCL
    'P1.08': '19',  # D5
    'P0.07': '20',  # D6
    'P0.26': '21',  # D9
    'P0.27': '22',  # D10
    'P0.06': '23',  # D11
    'P0.08': '24',  # D12
    'P1.09': '25',  # D13

    # note onboard LED1 at P1.15, LED2 at P1.10
    # note onboard switch at P1.02, reset switch at P0.18
    # note onboard neopixel at P0.16 (data out not broken out)
    # note onboard VBAT sense divider at P0.29
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
      }).remap(self.SYSTEM_PIN_REMAP)
    else:  # board sources power (default)
      self.require(~self.pwr.is_connected(), "can't sink power if source gnd connected")
      self.require(~self.gnd.is_connected(), "can't sink gnd if source gnd connected")
      return VariantPinRemapper({
        'Vdd': self.pwr_out,
        'Vss': self.gnd_out,
        'Vbus': self.vusb_out,
      }).remap(self.SYSTEM_PIN_REMAP)

  def contents(self):
    super().contents()

    self.gnd.init_from(Ground())
    self.pwr.init_from(self._vdd_model())

    mbr120_drop = (0, 0.340)*Volt
    ap2112_3v3_out = 3.3*Volt(tol=0.015)  # note dropout voltage up to 400mV, current up to 600mA
    self.gnd_out.init_from(GroundSource())
    self.vusb_out.init_from(VoltageSource(
      voltage_out=UsbConnector.USB2_VOLTAGE_RANGE - mbr120_drop,
      current_limits=UsbConnector.USB2_CURRENT_LIMITS
    ))
    self.pwr_out.init_from(VoltageSource(
      voltage_out=ap2112_3v3_out,
      current_limits=UsbConnector.USB2_CURRENT_LIMITS
    ))

    self.generator_param(self.gnd.is_connected())

  def generate(self) -> None:
    super().generate()

    self.footprint(
      'U', 'bldc:FEATHERWING_NODIM',
      self._make_pinning(),
      mfr='Adafruit', part='Feather nRF52840 Express',
      datasheet='https://learn.adafruit.com/assets/68545'
    )
