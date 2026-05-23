from typing import Mapping

from typing_extensions import override

from ..electronics_interfaces import *


class Comparator(KiCadInstantiableBlock, Analog):
    """Abstract comparator interface, output goes high when inp > inn."""

    @override
    def symbol_pinning(self, symbol_name: str) -> Mapping[str, BasePort]:
        assert symbol_name in ("Simulation_SPICE:OPAMP", "edg_importable:Opamp")
        return {"+": self.inp, "-": self.inn, "3": self.out, "V+": self.pwr, "V-": self.gnd}

    @classmethod
    @override
    def block_from_symbol(cls, symbol_name: str, properties: Mapping[str, str]) -> "Comparator":
        return Comparator()

    def __init__(self) -> None:
        super().__init__()

        self.pwr = self.Port(VoltageSink.empty(), [Power])
        self.gnd = self.Port(Ground.empty(), [Common])
        self.inn = self.Port(AnalogSink.empty())
        self.inp = self.Port(AnalogSink.empty())
        self.out = self.Port(DigitalSource.empty())
