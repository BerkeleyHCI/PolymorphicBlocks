from typing import Type

from edg_core import *
from .VoltagePorts import VoltageLink, VoltageSink, VoltageSource


@non_library  # this can't be instantiated
class BaseConnectedGenerator(GeneratorBlock):
  INPUT_TYPE: Type[Port]
  OUTPUTS_TYPE: Type[Port]

  @init_in_parent
  def __init__(self, in_is_connected: BoolLike) -> None:
    """in_is_connected needs to be connected from above, since from the perspective
    of this block, the input is always (locally) connected"""
    super().__init__()
    self.out = self.Port(self.INPUT_TYPE.empty())
    self.in_connected = self.Port(self.OUTPUTS_TYPE.empty(), optional=True)
    self.in_unconnected = self.Port(self.OUTPUTS_TYPE.empty())
    self.generator(self.generate, in_is_connected)

  def generate(self, input_connected: bool):
    if input_connected:
      self.connect(self.out, self.in_connected)
      self.in_unconnected.init_from(self.OUTPUTS_TYPE())  # create ideal port
    else:
      self.connect(self.out, self.in_unconnected)


class VoltageSourceConnected(BaseConnectedGenerator):
  INPUT_TYPE = VoltageSource
  OUTPUTS_TYPE = VoltageSink
