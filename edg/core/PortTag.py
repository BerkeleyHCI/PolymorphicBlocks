from __future__ import annotations

from typing import *
from .Ports import BasePort, Port


PortType = TypeVar('PortType', bound=BasePort, covariant=True)  # TODO this should just be Port, but current needed to work w/ BaseBlock.Port type hierarchy
class PortTag(Generic[PortType]):
  def __init__(self, tpe: Type[PortType]):
    self.port_tpe = tpe


Input = PortTag(Port)  # basic untyped tag for implicit dataflow inputs (including voltage sources); for only voltages, this would be the one with the largest magnitude
Output = PortTag(Port)  # basic untyped tag for implicit dataflow outputs
InOut = PortTag(Port)  # basic untyped tag for implicit dataflow inout, including pullup/pulldowns
