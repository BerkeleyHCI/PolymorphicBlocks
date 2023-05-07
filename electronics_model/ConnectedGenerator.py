from typing import Type, TypeVar, Generic

from edg_core import *
from .VoltagePorts import VoltageLink, VoltageSink, VoltageSource
from .DigitalPorts import DigitalLink, DigitalSink, DigitalSource


@abstract_block  # really this is just a category
class DefaultConnectionBlock(InternalBlock):
  """A utility block that takes in an input port that may be connected
  and an output port that is required, and if the input is not present, connects the
  output to a default port.
  If the input is present, the default port presents an 'ideal' port. - TODO can this be a true disconnect?
  If the input is not present, the default port is connected to the output.
  """
  pass


OutputType = TypeVar('OutputType', bound=Port)
InputsType = TypeVar('InputsType', bound=Port)
LinkType = TypeVar('LinkType', bound=Link)
SelfType = TypeVar('SelfType', bound='BaseConnectedGenerator')
@non_library  # this can't be instantiated
class BaseConnectedGenerator(DefaultConnectionBlock, GeneratorBlock, Generic[OutputType, InputsType, LinkType]):
  """The template actually lives here"""
  INPUTS_TYPE: Type[Port]
  OUTPUT_TYPE: Type[Port]

  @init_in_parent
  def __init__(self, in_is_connected: BoolLike = BoolExpr()) -> None:
    """in_is_connected needs to be connected from above, since from the perspective
    of this block, the input is always (locally) connected"""
    super().__init__()
    self.out = self.Port(self.OUTPUT_TYPE.empty())
    self.in_connected = self.Port(self.INPUTS_TYPE.empty(), optional=True)
    self.in_default = self.Port(self.INPUTS_TYPE.empty())
    self.in_is_connected = self.ArgParameter(in_is_connected)
    self.generator_param(self.in_is_connected)

  def generate(self):
    super().generate()
    if self.get(self.in_is_connected):
      self.connect(self.out, self.in_connected)
      self.in_default.init_from(self.INPUTS_TYPE())  # create ideal port
    else:
      self.connect(self.out, self.in_default)
      # no ideal port needed, this should be invalid anyways

  def out_with_default(self: SelfType, out: Port[LinkType], in_connected: Port[LinkType],
                       in_default: Port[LinkType]) -> SelfType:
    # note this runs in parent scope, so in_is_connected is valid
    parent = builder.get_enclosing_block()
    assert parent is not None
    parent.connect(self.out, out)
    parent.connect(self.in_connected, in_connected)
    parent.connect(self.in_default, in_default)
    parent.assign(self.in_is_connected, in_connected.is_connected())
    return self


class VoltageSourceConnected(BaseConnectedGenerator[VoltageSource, VoltageSink, VoltageLink]):
  OUTPUT_TYPE = VoltageSource
  INPUTS_TYPE = VoltageSink


class DigitalSourceConnected(BaseConnectedGenerator[DigitalSource, DigitalSink, DigitalLink]):
  OUTPUT_TYPE = DigitalSource
  INPUTS_TYPE = DigitalSink
