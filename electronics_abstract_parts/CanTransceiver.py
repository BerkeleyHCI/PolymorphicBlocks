from electronics_model import *
from .Categories import *


@abstract_block
class CanTransceiver(IntegratedCircuit, Block):
  """Abstract CAN transceiver"""
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink(), [Power])  # for isolated converters, this is the logic side supply
    self.gnd = self.Port(Ground(), [Common])

    self.controller = self.Port(CanTransceiverPort(), [Input])
    self.can = self.Port(CanDiffPort(), [Output])


@abstract_block
class IsolatedCanTransceiver(CanTransceiver):
  def __init__(self) -> None:
    super().__init__()

    self.can_pwr = self.Port(VoltageSink())  # no implicit connect tags for isolated side
    self.can_gnd = self.Port(Ground())
