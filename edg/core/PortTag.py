from __future__ import annotations

from typing import *
from .Ports import BasePort, Port


class PortTag:
    def __init__(self, tpe: Type[BasePort]) -> None:
        self.port_tpe = tpe


Input = PortTag(
    Port
)  # basic untyped tag for implicit dataflow inputs (including voltage sources); for only voltages, this would be the one with the largest magnitude
Output = PortTag(Port)  # basic untyped tag for implicit dataflow outputs
InOut = PortTag(Port)  # basic untyped tag for implicit dataflow inout, including pullup/pulldowns
