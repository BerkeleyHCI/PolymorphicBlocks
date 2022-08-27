from .Categories import *


@abstract_block
class Opamp(Block):
  """Base class for opamps. Parameters need to be more restricted in subclasses.
  """
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.gnd = self.Port(Ground.empty(), [Common])

    self.inp = self.Port(AnalogSink.empty())
    self.inn = self.Port(AnalogSink.empty())
    self.out = self.Port(AnalogSource.empty())
