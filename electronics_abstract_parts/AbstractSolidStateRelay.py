from electronics_model import *


@abstract_block
class SolidStateRelay_Device(Block):
  """Base class for solid state relays.
  LED pins are passive (like the abstract LED) and the enclosing class should provide
  the circuitry to make it a DigitalSink port.
  """
  def __init__(self) -> None:
    super().__init__()

    self.leda = self.Port(Passive())
    self.ledk = self.Port(Passive())

    self.feta = self.Port(Passive())
    self.fetb = self.Port(Passive())

    # TODO: this is a different way of modeling parts - parameters in the part itself
    # instead of on the ports (because this doesn't have typed ports)
    self.led_forward_voltage = self.Parameter(RangeExpr())
    self.led_current_limit = self.Parameter(RangeExpr())
    self.led_current_recommendation = self.Parameter(RangeExpr())
    self.load_current_limit = self.Parameter(RangeExpr())
    self.load_resistance = self.Parameter(RangeExpr())


class DigitalAnalogIsolatedSwitch(Block):
  """Digitally controlled solid state relay that switches an analog signal.
  Includes a ballasting resistor.
  """
  def __init__(self) -> None:
    super().__init__()

    # TODO implement me