from deprecated import deprecated

from ..electronics_interfaces import *


class Neopixel(Light, Block):
    """Abstract base class for individually-addressable, serially-connected Neopixel-type
    (typically RGB) LEDs and defines the pwr/gnd/din/dout interface."""

    def __init__(self) -> None:
        super().__init__()
        self.pwr = self.Port(VoltageSink.empty(), [Power])
        self.gnd = self.Port(Ground.empty(), [Common])
        self.din = self.Port(DigitalSink.empty(), [Input])
        self.dout = self.Port(DigitalSource.empty(), optional=True)

    @property
    @deprecated(f"use pwr")
    def vdd(self) -> VoltageSink:
        return self.pwr
