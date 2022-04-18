from typing import *
from itertools import chain

from electronics_abstract_parts import *
from electronics_lib import SwdCortexTargetWithTdiConnector


@abstract_block
class Nrf52840Base_Device(PinMappable, IoController, DiscreteChip, GeneratorBlock):
  """nRF52840 base device and IO mappings
  https://infocenter.nordicsemi.com/pdf/nRF52840_PS_v1.7.pdf"""

  def __init__(self, **kwargs) -> None:
    super().__init__(**kwargs)

    self.pwr_usb = self.Port(VoltageSink(
      voltage_limits=(4.35, 5.5)*Volt,
      current_draw=(0.262, 7.73) * mAmp  # CPU/USB sleeping to everything active
    ), optional=True)

    # Additional ports (on top of IoController)
    # Crystals from table 15, 32, 33
    # TODO Table 32, model crystal load capacitance and series resistance ratings
    self.xtal = self.Port(CrystalDriver(frequency_limits=(1, 25)*MHertz, voltage_out=self.pwr.link().voltage),
                          optional=True)
    # Assumed from "32kHz crystal" in 14.5
    self.xtal_rtc = self.Port(CrystalDriver(frequency_limits=(32, 33)*kHertz, voltage_out=self.pwr.link().voltage),
                              optional=True)

    self.swd = self.Port(SwdTargetPort().empty())

    self.generator(self.generate, self.pin_assigns,
                   self.gpio.allocated(), self.adc.allocated(), self.dac.allocated(),
                   self.spi.allocated(), self.i2c.allocated(), self.uart.allocated(),
                   self.usb.allocated(), self.swd.is_connected())

  def contents(self) -> None:
    super().contents()

    # Ports with shared references
    self.pwr.init_from(VoltageSink(
      voltage_limits=(1.75, 3.6)*Volt,  # 1.75 minimum for power-on reset
      current_draw=(0, 212 / 64 + 4.8) * mAmp  # CPU @ max 212 Coremarks + 4.8mA in RF transmit
      # TODO propagate current consumption from IO ports
    ))
    self.gnd.init_from(Ground())

    self.system_pinmaps = VariantPinRemapper({
      'Vdd': self.pwr,
      'Vss': self.gnd,
      'Vbus': self.pwr_usb,
    })

    self.abstract_pinmaps = self.mappable_ios(self.gnd, self.pwr)

    self.require((self.usb.length() > 0).implies(self.pwr_usb.is_connected()), "USB require Vbus connected")

  @staticmethod
  def mappable_ios(gnd: Union[VoltageSource, VoltageSink], vdd: Union[VoltageSource, VoltageSink]) -> PinMapUtil:
    """Returns the mappable for given the input power and ground references.
    This separates the system pins definition from the IO pins definition."""
    dio_model = DigitalBidir.from_supply(
      gnd, vdd,
      voltage_limit_tolerance=(-0.3, 0.3) * Volt,
      current_limits=(-6, 6)*mAmp,  # minimum current, high drive, Vdd>2.7
      current_draw=(0, 0)*Amp,
      input_threshold_factor=(0.3, 0.7),
      pullup_capable=True, pulldown_capable=True,
    )
    dio_lf_model = dio_model  # "standard drive, low frequency IO only" (differences not modeled)

    adc_model = AnalogSink(
      voltage_limits=(gnd.link().voltage.upper(), vdd.link().voltage.lower()) +
                     (-0.3, 0.3) * Volt,
      current_draw=(0, 0) * Amp,
      impedance=Range.from_lower(1)*MOhm
    )

    uart_model = UartPort(DigitalBidir.empty())
    spi_model = SpiMaster(DigitalBidir.empty())
    i2c_model = I2cMaster(DigitalBidir.empty())

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
      # PinResource('P1.00', {'P1.00': dio_model}),  # TRACEDATA[0] and SWO, if used as IO must clear TRACECONFIG reg

      PeripheralFixedPin('SWD', SwdTargetPort(dio_model), {
        'swclk': ['SWCLK'], 'swdio': ['SWDIO'], 'reset': ['P0.18'], 'swo': ['P1.00'],
      }),
      PeripheralFixedPin('USB', UsbDevicePort(), {
        'dp': ['D+'], 'dm': ['D-']
      }),

      PeripheralAnyResource('SPI0', spi_model),
      PeripheralAnyResource('SPI1', spi_model),
      PeripheralAnyResource('SPI2', spi_model),
      PeripheralAnyResource('SPI3', spi_model),
      PeripheralAnyResource('I2C0', i2c_model),
      PeripheralAnyResource('I2C1', i2c_model),
      PeripheralAnyResource('UART0', uart_model),
      PeripheralAnyResource('UART1', uart_model),
    ])

  SYSTEM_PIN_REMAP: Dict[str, Union[str, List[str]]]  # pin name in base -> pin name(s)
  RESOURCE_PIN_REMAP: Dict[str, str]  # resource name in base -> pin name

  def generate(self, assignments: str,
               gpio_allocates: List[str], adc_allocates: List[str], dac_allocates: List[str],
               spi_allocates: List[str], i2c_allocates: List[str], uart_allocates: List[str],
               usb_allocates: List[str], swd_connected: bool) -> None: ...


class Holyiot_18010_Device(Nrf52840Base_Device, FootprintBlock):
  SYSTEM_PIN_REMAP: Dict[str, Union[str, List[str]]] = {
    'Vdd': '14',
    'Vss': ['1', '25', '37'],
    'Vbus': '22',
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
    'P0.18': '21',
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

  def generate(self, assignments: str,
               gpio_allocates: List[str], adc_allocates: List[str], dac_allocates: List[str],
               spi_allocates: List[str], i2c_allocates: List[str], uart_allocates: List[str],
               usb_allocates: List[str], swd_connected: bool) -> None:
    system_pins: Dict[str, CircuitPort] = self.system_pinmaps.remap(self.SYSTEM_PIN_REMAP)

    allocated = self.abstract_pinmaps.remap_pins(self.RESOURCE_PIN_REMAP).allocate([
      (SwdTargetPort, ['swd'] if swd_connected else []),
      (UsbDevicePort, usb_allocates), (SpiMaster, spi_allocates), (I2cMaster, i2c_allocates),
      (UartPort, uart_allocates),
      (AnalogSink, adc_allocates), (AnalogSource, dac_allocates), (DigitalBidir, gpio_allocates),
    ], assignments)

    io_pins = self._instantiate_from(self._get_io_ports() + [self.swd], allocated)

    self.footprint(
      'U', 'edg:Holyiot-18010-NRF52840',
      dict(chain(system_pins.items(), io_pins.items())),
      mfr='Holyiot', part='18010',
      datasheet='http://www.holyiot.com/tp/2019042516322180424.pdf',
    )


class Holyiot_18010(PinMappable, Microcontroller, IoController):
  """Wrapper around the Holyiot 18010 that includes supporting components (programming port)"""
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.ic = self.Block(Holyiot_18010_Device(pin_assigns=self.pin_assigns))
    self.pwr_usb = self.Export(self.ic.pwr_usb, optional=True)

  def contents(self):
    super().contents()
    self.connect(self.pwr, self.ic.pwr)
    self.connect(self.gnd, self.ic.gnd)
    self._export_ios_from(self.ic)

    with self.implicit_connect(
        ImplicitConnect(self.pwr, [Power]),
        ImplicitConnect(self.gnd, [Common])
    ) as imp:
      (self.swd, ), _ = self.chain(imp.Block(SwdCortexTargetWithTdiConnector()),
                                   self.ic.swd)


class Mdbt50q_1mv2_Device(Nrf52840Base_Device, FootprintBlock):
  SYSTEM_PIN_REMAP: Dict[str, Union[str, List[str]]] = {
    'Vdd': ['28', '30'],  # 28=Vdd, 30=VddH; 31=DccH is disconnected - from section 8.3 for input voltage <3.6v
    'Vss': ['1', '2', '15', '33', '55'],
    'Vbus': '32',
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
    'P0.18': '40',
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

  def generate(self, assignments: str,
               gpio_allocates: List[str], adc_allocates: List[str], dac_allocates: List[str],
               spi_allocates: List[str], i2c_allocates: List[str], uart_allocates: List[str],
               usb_allocates: List[str], swd_connected: bool) -> None:
    system_pins: Dict[str, CircuitPort] = self.system_pinmaps.remap(self.SYSTEM_PIN_REMAP)

    allocated = self.abstract_pinmaps.remap_pins(self.RESOURCE_PIN_REMAP).allocate([
      (SwdTargetPort, ['swd'] if swd_connected else []),
      (UsbDevicePort, usb_allocates), (SpiMaster, spi_allocates), (I2cMaster, i2c_allocates),
      (UartPort, uart_allocates),
      (AnalogSink, adc_allocates), (AnalogSource, dac_allocates), (DigitalBidir, gpio_allocates),
    ], assignments)

    io_pins = self._instantiate_from(self._get_io_ports() + [self.swd], allocated)

    self.footprint(
      'U', 'RF_Module:Raytac_MDBT50Q',
      dict(chain(system_pins.items(), io_pins.items())),
      mfr='Raytac', part='MDBT50Q-1MV2',
      datasheet='https://www.raytac.com/download/index.php?index_id=43',
    )


class Mdbt50q_UsbSeriesResistor(Block):
  def __init__(self):
    super().__init__()
    self.usb_inner = self.Port(UsbHostPort().empty())
    self.usb_outer = self.Port(UsbDevicePort().empty())
    self.res_dp = self.Block(Resistor(27*Ohm(tol=0.01)))
    self.res_dm = self.Block(Resistor(27*Ohm(tol=0.01)))
    self.connect(self.usb_inner.dp, self.res_dp.a.as_digital_bidir())  # TODO propagate params - needs bridge mechanism
    self.connect(self.usb_outer.dp, self.res_dp.b.as_digital_bidir())
    self.connect(self.usb_inner.dm, self.res_dm.a.as_digital_bidir())
    self.connect(self.usb_outer.dm, self.res_dm.b.as_digital_bidir())


class Mdbt50q_1mv2(PinMappable, Microcontroller, IoController, GeneratorBlock):
  """Wrapper around the Mdbt50q_1mv2 that includes the reference schematic"""
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.ic = self.Block(Mdbt50q_1mv2_Device(pin_assigns=self.pin_assigns))
    self.pwr_usb = self.Export(self.ic.pwr_usb, optional=True)

    self.generator(self.generate, self.usb.allocated())

  def generate(self, usb_allocated: List[str]) -> None:
    super().contents()
    self.connect(self.pwr, self.ic.pwr)
    self.connect(self.gnd, self.ic.gnd)
    self._export_ios_from(self.ic, excludes=[self.usb])

    self.vbus_cap = self.Block(DecouplingCapacitor(10 * uFarad(tol=0.2))).connected(self.gnd, self.pwr_usb)

    with self.implicit_connect(
        ImplicitConnect(self.pwr, [Power]),
        ImplicitConnect(self.gnd, [Common])
    ) as imp:
      (self.swd, ), _ = self.chain(imp.Block(SwdCortexTargetWithTdiConnector()),
                                   self.ic.swd)
      self.vcc_cap = imp.Block(DecouplingCapacitor(10 * uFarad(tol=0.2)))

    if usb_allocated:
      assert len(usb_allocated) == 1
      usb_allocated_name = usb_allocated[0]
      usb_port = self.usb.append_elt(UsbDevicePort.empty(), usb_allocated_name)
      self.usb_res = self.Block(Mdbt50q_UsbSeriesResistor())
      self.connect(self.ic.usb.allocate(usb_allocated_name), self.usb_res.usb_inner)
      self.connect(self.usb_res.usb_outer, usb_port)
