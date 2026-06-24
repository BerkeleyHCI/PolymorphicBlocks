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
        self.dp = self.Block(Resistor(self.resistance))
        self.connect(self.dp.a, self.interior.dp)
        self.connect(self.dp.b, self.exterior.dp)
        self.dm = self.Block(Resistor(self.resistance))
        self.connect(self.dm.a, self.interior.dm)
        self.connect(self.dm.b, self.exterior.dm)
