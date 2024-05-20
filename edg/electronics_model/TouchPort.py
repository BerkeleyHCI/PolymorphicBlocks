from ..core import *
from .CircuitBlock import CircuitLink
from .VoltagePorts import CircuitPort


class TouchLink(CircuitLink):
  """Touch sensor link, consisting of one sensor (typically a PCB copper pattern) and one driver.
  These contain no modeling."""
  def __init__(self) -> None:
    super().__init__()
    self.driver = self.Port(TouchDriver())
    self.pad = self.Port(TouchPadPort())


class TouchDriver(CircuitPort[TouchLink]):
  """Touch sensor driver-side port, typically attached to a microcontroller pin.
  Internal to this port should be any circuitry needed to make the sensor work.
  Separately from the port, the microcontroller should generate additionally needed circuits,
  like the sensing caps for STM32 devices."""
  link_type = TouchLink


class TouchPadPort(CircuitPort[TouchLink]):
  """Touch sensor-side port, typically attached to a copper pad."""
  link_type = TouchLink
