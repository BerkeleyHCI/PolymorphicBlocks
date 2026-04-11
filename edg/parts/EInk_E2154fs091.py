from deprecated import deprecated

from .EInk_WaveshareDriver import Waveshare_Epd
from ..abstract_parts import *


@deprecated("replaced with Waveshare EPD which has better compatibility")
class E2154fs091(EInk):
    def __init__(self) -> None:
        super().__init__()

        self.ic = self.Block(Waveshare_Epd())
        self.gnd = self.Export(self.ic.gnd, [Common])
        self.pwr = self.Export(self.ic.pwr, [Power])
        self.busy = self.Export(self.ic.busy)
        self.reset = self.Export(self.ic.reset)
        self.dc = self.Export(self.ic.dc)
        self.cs = self.Export(self.ic.cs)
        self.spi = self.Export(self.ic.spi)
