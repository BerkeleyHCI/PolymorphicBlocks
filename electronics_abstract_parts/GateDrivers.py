from electronics_model import *
from .Categories import Interface


@abstract_block
class HalfBridgeDriver(Interface, Block):
  """Half-bridge driver with independent low / high control for driving two NMOS devices,
  with a high-side driver that allows a voltage offset from the main gnd.

  This device:
  - may or may not have shoot-through protection,
  - may or may not have an internal bootstrap diode or controller,
  - may or may not support non-half-bridge topologies (eg, high-side ground required to be the FET common node)
  """
  def __init__(self):
    super().__init__()
    self.pwr = self.Port(VoltageSink.empty(), [Power])  # logic side and low FET
    self.gnd = self.Port(Ground.empty(), [Common])

    self.low_in = self.Port(DigitalSink.empty())
    self.high_in = self.Port(DigitalSink.empty())

    self.low_out = self.Port(DigitalSource.empty())  # referenced to main gnd

    self.high_pwr = self.Port(VoltageSink.empty())
    self.high_gnd = self.Port(VoltageSink.empty())  # this encodes the voltage limit from gnd
    self.high_out = self.Port(DigitalSource.empty())  # referenced to high_pwr and high_gnd
