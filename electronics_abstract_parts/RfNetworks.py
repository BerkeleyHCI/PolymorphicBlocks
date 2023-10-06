from math import pi, sqrt
from typing import Tuple

from electronics_model import *
from .AbstractCapacitor import Capacitor
from .AbstractInductor import Inductor
from .Categories import *


class PiLowPassFilter(AnalogFilter, GeneratorBlock):
    """Passive-typed pi impedance matching network.
    Based on equations from https://www.silabs.com/documents/public/application-notes/an1275-imp-match-for-network-arch.pdf
    and also referencing https://www.electronicdesign.com/technologies/communications/article/21801154/back-to-basics-impedance-matching-part-3
    and https://www.qsl.net/zl1an/CH1.pdf
    Frequency defines the entire bandwidth this filter should work across.

    WORK IN PROGRESS. NON-STABLE API.

    TODO: use ranges and tolerances throughout"""
    @classmethod
    def _reactance_to_capacitance(cls, freq: float, reactance: float) -> float:
        return -1 / (2*pi*freq*reactance)  # negative reactance is capacitive

    @classmethod
    def _reactance_to_inductance(cls, freq: float, reactance: float) -> float:
        return reactance / (2*pi*freq)

    @classmethod
    def _calculate_l_values(cls, freq: float, r1: float, z2: complex) -> Tuple[float, float]:
        """Calculate a L matching network for a real R1 and optionally-complex Z2
        and returns L, C2"""
        if z2.imag != 0:
            q2 = z2.imag / z2.real  # Q of the load
            # for z2 do a parallel transformation, to rp2 real resistance and xp2 capacitance
            rp2 = z2.real * (q2 * q2 + 1)
            xp2 = rp2 / q2
            cp2 = cls._reactance_to_capacitance(freq, xp2)  # parallel capacitance aka cstray
        else:
            rp2 = z2.real
            cp2 = 0  # for real impedance, no stray capacitance

        q = sqrt(rp2 / r1 - 1)
        net_xp = -rp2 / q  # TODO: where is the negative sign coming from
        net_xs = q * r1
        return cls._reactance_to_inductance(freq, net_xs), cls._reactance_to_capacitance(freq, net_xp) - cp2

    @classmethod
    def _calculate_values(cls, freq: float, q: float, z1: complex, z2: complex) -> Tuple[float, float, float, float]:
        """Given the center frequency, q factor, impedances z1 and z2, calculate the matching network
        and returns C1, C2, L, and virtual resistance Rv"""
        rh = max(z1.real, z2.real)
        rv = rh / (q*q + 1)

        return 0, 0, 0, rv

    @init_in_parent
    def __init__(self, frequency: RangeLike, src_resistance: FloatLike, src_reactance: FloatLike,
                 load_resistance: FloatLike,
                 voltage: RangeLike, current: RangeLike):
        super().__init__()
        self.input = self.Port(Passive.empty(), [Input])
        self.output = self.Port(Passive.empty(), [Output])
        self.gnd = self.Port(Ground.empty(), [Common])

        self.frequency = self.ArgParameter(frequency)
        self.src_resistance = self.ArgParameter(src_resistance)
        self.src_reactance = self.ArgParameter(src_reactance)
        self.load_resistance = self.ArgParameter(load_resistance)
        self.voltage = self.ArgParameter(voltage)
        self.current = self.ArgParameter(current)

        self.generator_param(self.frequency, self.src_resistance, self.src_reactance, self.load_resistance)

    def generate(self) -> None:
        super().generate()

        frequency = self.get(self.frequency)
        bandwidth = frequency.upper() - frequency.lower()
        q = frequency.center() / bandwidth

        rg = complex(self.get(self.src_resistance), self.get(self.src_reactance))
        rl = self.get(self.load_resistance)

        rh = max(rg.real, rl)  # TODO is this accurate for the complex case?
        rv = rh / (q*q + 1)

        self.c1 = self.Block(Capacitor(capacitance=(0, 0)*Farad, voltage=self.voltage))
        self.c2 = self.Block(Capacitor(capacitance=(0, 0)*Farad, voltage=self.voltage))
        self.l = self.Block(Inductor(inductance=(0, 0)*Henry, current=self.current))
        self.connect(self.input, self.c1.pos, self.l.a)
        self.connect(self.l.b, self.c2.pos, self.output)
        self.connect(self.c1.neg, self.c2.neg)
        self.connect(self.c1.neg.adapt_to(Ground()), self.gnd)
