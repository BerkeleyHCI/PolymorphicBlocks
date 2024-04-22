from electronics_model import *
from .Categories import PowerSwitch


@abstract_block
class HalfBridgeDriver(PowerSwitch, Block):
  """Half-bridge driver with independent low / high control for driving two NMOS devices,
  with a high-side driver that allows a voltage offset from the main gnd.

  A parameter controls whether a boot diode is required (chip-internal or generated component) or disallowed.
  Devices with an internal boot diode must require has_boot_diode=False.
  Devices without an internal boot diode may generate an external one.

  This device:
  - may or may not have shoot-through protection
  - may or may not have an internal bootstrap diode or controller
  - may or may not support non-half-bridge topologies (eg, high-side ground required to be the FET common node)

  TODO: auto-generate parameters based on switching frequencies and FET parameters?
  """
  @init_in_parent
  def __init__(self, has_boot_diode: BoolLike):
    super().__init__()
    self.has_boot_diode = self.ArgParameter(has_boot_diode)

    self.pwr = self.Port(VoltageSink.empty(), [Power])  # logic side and low FET
    self.gnd = self.Port(Ground.empty(), [Common])

    self.low_out = self.Port(DigitalSource.empty())  # referenced to main gnd

    self.high_pwr = self.Port(VoltageSink.empty(), optional=True)  # not used with internal boot diode
    self.high_gnd = self.Port(VoltageSink.empty())  # this encodes the voltage limit from gnd
    self.high_out = self.Port(DigitalSource.empty())  # referenced to high_pwr and high_gnd


class HalfBridgeDriverIndependent(BlockInterfaceMixin[HalfBridgeDriver]):
  """Mixin that specifies a half-bridge driver with independent inputs"""
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.low_in = self.Port(DigitalSink.empty())
    self.high_in = self.Port(DigitalSink.empty())


class HalfBridgeDriverPwm(BlockInterfaceMixin[HalfBridgeDriver]):
  """Mixin that specifies a half-bridge driver with PWM input.
  If an enable pin is provided, it should use the optional Resettable mixin"""
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.pwm_in = self.Port(DigitalSink.empty())
