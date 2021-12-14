from electronics_model import *
from .DummyDevices import MergedAnalogSource
from .AbstractPassives import Resistor


@abstract_block
class AnalogSwitch(Block):
  """Base class for a SPDT analog switch.
  """
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink())
    self.gnd = self.Port(Ground())

    self.control = self.Port(DigitalSink())

    self.com = self.Port(Passive())
    self.no = self.Port(Passive())
    self.nc = self.Port(Passive())

    # TODO: this is a different way of modeling parts - parameters in the part itself
    # instead of on the ports (because this doesn't have typed ports)
    self.led_forward_voltage = self.Parameter(RangeExpr())
    self.led_current_limit = self.Parameter(RangeExpr())
    self.led_current_recommendation = self.Parameter(RangeExpr())
    self.load_voltage_limit = self.Parameter(RangeExpr())
    self.load_current_limit = self.Parameter(RangeExpr())
    self.load_resistance = self.Parameter(RangeExpr())
