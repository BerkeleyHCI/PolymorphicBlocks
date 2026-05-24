from typing_extensions import override

from ..abstract_parts import *


class UsbSeriesResistor(InternalSubcircuit, Block):
    """Inline resistor on DM and DP lines, sometimes needed by microcontrollers."""

    def __init__(self, resistance: RangeLike) -> None:
        super().__init__()
        self.resistance = self.ArgParameter(resistance)
        self.interior = self.Port(UsbHostPort.empty(), [Input])
        self.exterior = self.Port(UsbDevicePort.empty(), [Output])

    @override
    def contents(self) -> None:
        super().contents()
        self.dp = self.Block(DigitalBidirSeriesResistor(self.resistance)).connected(self.interior.dp, self.exterior.dp)
        self.dm = self.Block(DigitalBidirSeriesResistor(self.resistance)).connected(self.interior.dm, self.exterior.dm)
