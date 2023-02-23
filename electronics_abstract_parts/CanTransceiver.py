from electronics_model import *
from .Categories import *


@abstract_block
class CanTransceiver(Interface, Block):
  """Abstract CAN transceiver"""
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink.empty(), [Power])  # for isolated converters, this is the logic side supply
    self.gnd = self.Port(Ground.empty(), [Common])

    self.controller = self.Port(CanTransceiverPort.empty(), [Input])
    self.can = self.Port(CanDiffPort.empty(), [Output])


@abstract_block
class IsolatedCanTransceiver(CanTransceiver):
  def __init__(self) -> None:
    super().__init__()

    self.can_pwr = self.Port(VoltageSink.empty())  # no implicit connect tags for isolated side
    self.can_gnd = self.Port(Ground.empty())
