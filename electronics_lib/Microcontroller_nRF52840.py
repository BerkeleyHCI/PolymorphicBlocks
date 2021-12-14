from typing import *
from itertools import chain

from electronics_abstract_parts import *


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
      output_threshold_factor=(0, 1),
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
      '31': self.swd.swclk,
      '32': self.swd.swdio,
      '37': self.gnd,
    }

    digital_ports = [port for port in self._all_assignable_ios if not isinstance(port, AnalogSink)]
    assigned_pins = PinAssignmentUtil(
      AnyPinAssign([port for port in self._all_assignable_ios if isinstance(port, AnalogSink)],
                   range(6, 14)),
      AnyPinAssign(digital_ports + [self.swd.swo],
                   chain(range(2, 14), range(15, 21), range(26, 31), range(33, 37))),
    ).assign(
      [port for port in self._all_assignable_ios if self.get(port.is_connected())] + [self.swd.swo],
      self._get_suggested_pin_maps(pin_assigns_str))

    overassigned_pins = set(assigned_pins.assigned_pins.keys()).intersection(set(system_pins.keys()))
    assert not overassigned_pins, f"over-assigned pins {overassigned_pins}"

    all_pins = {
      **{str(pin): port for pin, port in assigned_pins.assigned_pins.items()},
      **{str(pin): port for pin, port in system_pins.items()}
    }

    self.footprint(
      'U', 'edg:Holyiot-18010-NRF52840',
      all_pins,
      mfr='Holyiot', part='18010',
      datasheet='https://learn.adafruit.com/adafruit-itsybitsy-nrf52840-express',
    )
