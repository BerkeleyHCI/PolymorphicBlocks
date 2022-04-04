from typing import *
from itertools import chain

from electronics_abstract_parts import *


class Nrf52840Base_Device(PinMappable, IoController, DiscreteChip, GeneratorBlock, FootprintBlock):
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
                   self.usb.allocated(), self.can.allocated(), self.swd.is_connected())

  def contents(self) -> None:
    super().contents()

    # Ports with shared references
    self.pwr.init_from(VoltageSink(
      voltage_limits=(1.75, 3.6)*Volt,  # 1.75 minimum for power-on reset
      current_draw=(0, 212 / 64 + 4.8) * mAmp  # CPU @ max 212 Coremarks + 4.8mA in RF transmit
      # TODO propagate current consumption from IO ports
    ))
    self.gnd.init_from(Ground())

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
      # PinResource('P1.00', {'P1.00': dio_model}),  # TRACEDATA[0] and SWO

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

class Holyiot_18010(Nrf52840Base_Device):
  SYSTEM_PIN_REMAP = {
    'Vss': ['1', '25', '37'],
    'Vdd': '14',
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












class Holyiot_18010_Nrf52840(Microcontroller, FootprintBlock, AssignablePinBlock):
  """
  Holyiot 18010, nRF52840-based BLE module with castellated edge pads
  """

  @init_in_parent
  def __init__(self) -> None:
    super().__init__()

    self.pwr_3v = self.Port(VoltageSink(
      voltage_limits=(1.75, 3.6)*Volt,  # 1.75 minimum for power-on reset
      current_draw=(0, 212 / 64 + 4.8) * mAmp  # CPU @ max 212 Coremarks + 4.8mA in RF transmit
    ), [Power])  # TODO propagate IO pin currents
    self.pwr_usb = self.Port(VoltageSink(
      voltage_limits=(4.35, 5.5)*Volt,
      current_draw=(0.262, 7.73) * mAmp  # CPU/USB sleeping to everything active
    ), optional=True)
    self.gnd = self.Port(Ground(), [Common])

    io_model = DigitalBidir.from_supply(
      self.gnd, self.pwr_3v,
      voltage_limit_tolerance=(-0.3, 0.3) * Volt,
      current_limits=(-6, 6)*mAmp,  # minimum current, high drive, Vdd>2.7
      current_draw=(0, 0)*Amp,
      input_threshold_factor=(0.3, 0.7),
      pullup_capable=True, pulldown_capable=True,
    )

    adc_model = AnalogSink(
      voltage_limits=(self.gnd.link().voltage.upper(), self.pwr_3v.link().voltage.lower()) +
                     (-0.3, 0.3) * Volt,
      current_draw=(0, 0) * Amp,
      impedance=Range.from_lower(1)*MOhm
    )








    self.digital = ElementDict[DigitalBidir]()
    for i in range(28):
      self.digital[i] = self.Port(io_model, optional=True)
      self._add_assignable_io(self.digital[i])

    self.adc = ElementDict[AnalogSink]()
    for i in range(8):
      self.adc[i] = self.Port(adc_model, optional=True)
      self._add_assignable_io(self.adc[i])

    self.uart_0 = self.Port(UartPort(io_model), optional=True)
    self._add_assignable_io(self.uart_0)

    self.spi_0 = self.Port(SpiMaster(io_model), optional=True)
    self._add_assignable_io(self.spi_0)

    self.usb_0 = self.Port(UsbDevicePort(), optional=True)

    self.swd = self.Port(SwdTargetPort(io_model), optional=True)
    self._add_assignable_io(self.swd)

    self.generator(self.pin_assign, self.pin_assigns,
                   req_ports=list(chain(self.digital.values(), self.adc.values(),
                                        [self.uart_0, self.spi_0, self.swd])))

  def pin_assign(self, pin_assigns_str: str) -> None:
    system_pins: Dict[str, CircuitPort] = {
      '1': self.gnd,
      '14': self.pwr_3v,
      '21': self.swd.reset,
      '22': self.pwr_usb,
      '23': self.usb_0.dm,
      '24': self.usb_0.dp,
      '25': self.gnd,
      '31': self.swd.swclk,
      '32': self.swd.swdio,
      '37': self.gnd,
    }

    digital_ports = [port for port in self._all_assignable_ios if not isinstance(port, AnalogSink)]
    assigned_pins = PinAssignmentUtil(
      AnyPinAssign([port for port in self._all_assignable_ios if isinstance(port, AnalogSink)],
                   range(6, 14)),
      AnyPinAssign(digital_ports,
                   chain(range(2, 14), range(15, 21), range(26, 31), range(33, 37))),
    ).assign(
      [port for port in self._all_assignable_ios if self.get(port.is_connected())],
      self._get_suggested_pin_maps(pin_assigns_str))

    overassigned_pins = set(assigned_pins.assigned_pins.keys()).intersection(set(system_pins.keys()))
    assert not overassigned_pins, f"over-assigned pins {overassigned_pins}"

    # TODO REMOVE THIS NASTY HACK - needed to partially assign the SWD pins since SWCLK, SWDIO, reset are fixed
    # but "SWO" is not a dedicated pin
    all_pins = {
      **{str(pin): port for pin, port in assigned_pins.assigned_pins.items()
         if port is not self.swd.reset and port is not self.swd.swclk and port is not self.swd.swdio},
      **{str(pin): port for pin, port in system_pins.items()}
    }

    self.footprint(
      'U', 'edg:Holyiot-18010-NRF52840',
      all_pins,
      mfr='Holyiot', part='18010',
      datasheet='https://learn.adafruit.com/adafruit-itsybitsy-nrf52840-express',
    )
