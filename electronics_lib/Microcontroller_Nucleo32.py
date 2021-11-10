from typing import *

from itertools import chain
from electronics_abstract_parts import *


class Nucleo_F303k8(Microcontroller, FootprintBlock, AssignablePinBlock):  # TODO refactor with _Device
  """
  Nucleo32 F303K8 configured as power source from USB.
  TODO base classes?
  TODO: union types to configure as sinks

  Documentation: UM1956, https://www.st.com/resource/en/user_manual/dm00231744.pdf
  """

  @init_in_parent
  def __init__(self) -> None:
    super().__init__()

    self.pwr_in = self.Port(VoltageSink(
      voltage_limits=(5.1 + 1.2 + 0.58, 15) * Volt,  # lower from 5v out + LD1117S50TR dropout + BAT60JFILM diode
      # TODO can be lower if don't need 5.0v out
      current_draw=(0, 0) * Amp # TODO current draw specs, the part doesn't really have a datasheet
    ), optional=True)
    self.pwr_5v = self.Port(VoltageSource(
      voltage_out=(4.75 - 0.58, 5.1) * Volt,  # 4.75V USB - 0.58v BAT60JFILM drop to 5.1 from LD1117S50TR, ignoring ST890CDR
      current_limits=(0, 0.5) * Amp  # max USB draw  # TODO higher from external power
    ), optional=True)
    self.pwr_3v3 = self.Port(VoltageSource(
      voltage_out=3.3 * Volt(tol=0.03),  # LD39050PU33R worst-case Vout accuracy
      current_limits=(0, 0.5) * Amp  # max USB current draw, LDO also guarantees 500mA output current
    ), optional=True)
    self.gnd = self.Port(GroundSource(), optional=True)

    io_model = DigitalBidir(  # account for multiple IO types, this uses the strictest one
      voltage_limits=(-0.3, 3.6) * Volt,
      current_draw=(0, 0) * Amp,
      voltage_out=(0 * Volt, 3.3 * Volt),
      current_limits=(-25, 25) * mAmp,
      input_thresholds=(0.3 * 3.3*0.97,
                        0.7 * 3.3*1.03),
      output_thresholds=(0 * Volt, 3.3 * 0.97 * Volt),
      pullup_capable=True, pulldown_capable=True
    )

    adc_model = AnalogSink(
      voltage_limits=(-0.3, 3.6) * Volt,
      current_draw=(0, 0) * Amp,
      impedance=100*kOhm  # TODO: actually spec'd as maximum external impedance; internal impedance not given
    )

    dac_model = AnalogSource(
      voltage_out=(0.2, 3.1) * Volt,  # TODO should derive from common rail
      current_limits=(0, 0) * Amp,  # TODO not given by spec
      impedance=15*kOhm  # assumes buffer off
    )

    self.digital = ElementDict[DigitalBidir]()
    for i in range(21):  # note, NRST, LED1 not assigned
      self.digital[i] = self.Port(io_model, optional=True)
      self._add_assignable_io(self.digital[i])

    self.adc = ElementDict[AnalogSink]()
    for i in range(9):
      self.adc[i] = self.Port(adc_model, optional=True)
      self._add_assignable_io(self.adc[i])

    self.dac = ElementDict[AnalogSource]()
    for i in range(2):
      self.dac[i] = self.Port(dac_model, optional=True)
      self._add_assignable_io(self.dac[i])

    self.uart_0 = self.Port(UartPort(io_model), optional=True)
    self._add_assignable_io(self.uart_0)

    self.spi_0 = self.Port(SpiMaster(io_model), optional=True)
    self._add_assignable_io(self.spi_0)

    self.can_0 = self.Port(CanControllerPort(io_model), optional=True)
    self._add_assignable_io(self.can_0)

    # TODO model IO draw - need internal source block?

    self.generator(self.pin_assign, self.pin_assigns,
                   req_ports=list(chain(self.digital.values(), self.adc.values(), self.dac.values(),
                                        [self.uart_0, self.spi_0, self.can_0])))

  def pin_assign(self, pin_assigns_str: str) -> None:
    # Note: application circuit at LPC15XX 14.6, Figure 49
    system_pins = {
      16: self.pwr_in,
      19: self.pwr_5v,
      29: self.pwr_3v3,
      4: self.gnd,
      17: self.gnd,
    }

    assigned_pins = PinAssignmentUtil(
      # TODO assign fixed-pin digital peripherals here
      AnyPinAssign([port for port in self._all_assignable_ios if isinstance(port, AnalogSource)],
                   [22, 23, 24]),  # TODO account for only two DACs
      AnyPinAssign([port for port in self._all_assignable_ios if isinstance(port, AnalogSink)],
                   [6, 9, 21, 22, 23, 24, 25, 26, 27]),
      AnyPinAssign([port for port in self._all_assignable_ios if isinstance(port, DigitalBidir)],
                   [1, 2, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
                    19, 20, 21, 22, 23, 24, 25, 26, 27]),
    ).assign(
      [port for port in self._all_assignable_ios if self.get(port.is_connected())],
      self._get_suggested_pin_maps(pin_assigns_str))

    overassigned_pins = set(assigned_pins.assigned_pins.keys()).intersection(set(system_pins.keys()))
    assert not overassigned_pins, f"over-assigned pins {overassigned_pins}"

    all_pins = {
      **{str(pin): port for pin, port in assigned_pins.assigned_pins.items()},
      **{str(pin): port for pin, port in system_pins.items()}
    }

    for self_port in assigned_pins.not_connected:
      assert isinstance(self_port, NotConnectablePort), f"non-NotConnectablePort {self_port.name()} marked NC"
      self_port.not_connected()

    self.footprint(
      'U', 'edg:Nucleo32',
      all_pins,
      mfr='STMicroelectronics', part='NUCLEO-F303K8',
      datasheet='https://www.st.com/resource/en/user_manual/dm00231744.pdf',
    )

