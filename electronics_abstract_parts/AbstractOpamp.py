from electronics_model import *
from .Categories import *

@abstract_block
class Opamp(Block):
  """Base class for opamps. Parameters need to be more restricted in subclasses.
  """

  @init_in_parent
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(ElectricalSink(), [Power])
    self.gnd = self.Port(Ground(), [Common])

    self.inp = self.Port(AnalogSink())
    self.inn = self.Port(AnalogSink())
    self.out = self.Port(AnalogSource())


class OpampFollower(AnalogFilter):
  def __init__(self):
    super().__init__()

    self.amp = self.Block(Opamp())

    self.pwr = self.Export(self.amp.pwr)
    self.gnd = self.Export(self.amp.gnd)

    self.input = self.Export(self.amp.inp, [Input])
    self.output = self.Export(self.amp.out, [Output])
    self.connect(self.amp.out, self.amp.inn)
