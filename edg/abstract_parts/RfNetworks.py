from math import pi, sqrt
from typing import Tuple, Any

from ..electronics_model import *
from .AbstractCapacitor import Capacitor
from .AbstractInductor import Inductor
from .Categories import *


class DiscreteRfWarning(BlockInterfaceMixin[Block]):
    """Mixin class providing a override-able (via refinements) warnings for blocks with a discrete RF layout.
    Discrete RF circuits can be tricky to get right from a layout standpoint and may require tuning to account for
    parasitics of real devices.
    The discrete RF library components / generators are also experimental and subject to change.
    They also do not adhere to the tolerance conventions of non-RF parts."""
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.discrete_rf_warning = self.Parameter(BoolExpr(False))

    def contents(self) -> None:
        super().contents()
        self.require(self.discrete_rf_warning == False, "warning: discrete RF circuit, design may be tricky")


class LLowPassFilter:
    # TODO: implement as circuit generator
    @classmethod
    def _calculate_impedance(cls, z1: complex, z2: complex) -> Tuple[float, float]:
        """Calculate the impedances for the elements of the L matching network,
        for complex Z1 (series-inductor side) and Z2 (parallel-capacitor side),
        returning reactances Xs (series element) and Xp (parallel element)"""
        rp1 = z1.real
        xp1 = z1.imag  # if z1 complex, the stray capacitance which gets resonated out with more l

        if z2.imag != 0:  # if z2 complex, split into real resistance and stray capacitance
            q2 = z2.imag / z2.real  # Q of the load
            rp2 = z2.real * (q2 * q2 + 1)  # parallel transformation into rp2 real part and xp2 capacitive part
            xp2 = rp2 / q2  # parallel capacitance aka cstray
        else:
            rp2 = z2.real
            xp2 = float('inf')  # for real impedance, no stray capacitance

        q = sqrt(rp2 / rp1 - 1)
        net_xp = -rp2 / q  # TODO: where is the negative sign coming from
        net_xs = q * rp1

        return net_xs - xp1, 1/(1/net_xp - 1/xp2)

    @classmethod
    def _calculate_values(cls, freq: float, z1: complex, z2: complex) -> Tuple[float, float]:
        """Calculate a L matching network for complex Z1 (series-inductor side) and Z2 (parallel-capacitor side)
        and returns L, C"""
        xs, xp = cls._calculate_impedance(z1, z2)
        return PiLowPassFilter._reactance_to_inductance(freq, xs),\
            PiLowPassFilter._reactance_to_capacitance(freq, xp)


class LLowPassFilterWith2HNotch(GeneratorBlock, RfFilter):
    """L filter for impedance matching for RF with an overlaid second-harmonic LC notch filter.
    The target reactance is given by the L filter.
    Then, the L and C values are from the simultaneous solution of:
    the parallel reactance equation, at bandpass frequency w:
      x_L = w*L
      x_C = -1/(w*C)
      x_parallel = 1/(1/x_L+1/x_C),
    the LC tank equation, at DIFFERENT bandstop frequency at the second harmonic w_bp = 2*w:
      w_bp = 1/(sqrt(l*c))
    solving both gives a new L of 3/4 the baseline L
    """
    @classmethod
    def _calculate_values(cls, freq: float, z1: complex, z2: complex) -> Tuple[float, float, float]:
        """Returns L, Cp, Clc"""
        l, c = LLowPassFilter._calculate_values(freq, z1, z2)
        lc_l = l * 3 / 4
        lc_c = 1/(lc_l * (2*pi*2*freq)**2)
        return lc_l, c, lc_c

    def __init__(self, frequency: FloatLike, src_resistance: FloatLike, src_reactance: FloatLike,
                 load_resistance: FloatLike, tolerance: FloatLike,
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
        self.tolerance = self.ArgParameter(tolerance)

        self.generator_param(self.frequency, self.src_resistance, self.src_reactance, self.load_resistance,
                             self.tolerance)

    def generate(self) -> None:
        super().generate()

        zs = complex(self.get(self.src_resistance), self.get(self.src_reactance))
        rl = self.get(self.load_resistance)

        l, c, c_lc = self._calculate_values(self.get(self.frequency), zs, rl)
        tolerance = self.get(self.tolerance)

        self.l = self.Block(Inductor(inductance=l*Henry(tol=tolerance), current=self.current))
        self.c = self.Block(Capacitor(capacitance=c*Farad(tol=tolerance), voltage=self.voltage))
        self.c_lc = self.Block(Capacitor(capacitance=c_lc*Farad(tol=tolerance), voltage=self.voltage))

        self.connect(self.input, self.l.a, self.c_lc.neg)
        self.connect(self.l.b, self.c_lc.pos, self.c.pos, self.output)
        self.connect(self.gnd, self.c.neg.adapt_to(Ground()))


class LHighPassFilter:
    # TODO: implement as circuit generator

    @classmethod
    def _calculate_values(cls, freq: float, z1: complex, z2: complex) -> Tuple[float, float]:
        """Calculate a L matching network for complex Z1 (parallel-inductor side) and Z2 (series-capacitor side)
        and returns L, C"""
        if z1.imag != 0:  # if z1 complex, split into real resistance and stray capacitance
            q1 = z1.imag / z1.real  # Q of the load
            rp1 = z1.real * (q1 * q1 + 1)  # parallel transformation into rp2 real part and xp2 capacitive part
            xp1 = rp1 / q1
        else:
            rp1 = z1.real
            xp1 = 0  # technically infinite

        rs2 = z2.real
        xs2 = z2.imag  # if z1 complex, the stray capacitance which gets resonated out with more l

        q = sqrt(rp1 / rs2 - 1)
        net_xp = rp1 / q
        net_xs = - q * rs2  # TODO: where is the negative sign coming from

        if xp1 != 0:
            net_xp = 1/(1/net_xp - 1/xp1)  # add reactance to cancel out z1 in parallel

        return PiLowPassFilter._reactance_to_inductance(freq, net_xp), \
            PiLowPassFilter._reactance_to_capacitance(freq, net_xs - xs2)


class PiLowPassFilter(GeneratorBlock, RfFilter):
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
    def _calculate_values(cls, freq: float, q: float, z1: complex, z2: complex) -> Tuple[float, float, float, float]:
        """Given the center frequency, q factor, impedances z1 and z2, calculate the matching network
        and returns C1, C2, L, and virtual resistance Rv"""
        rh = max(z1.real, z2.real)
        rv = rh / (q*q + 1)

        l1, c1 = LLowPassFilter._calculate_values(freq, complex(rv, 0), z1)
        l2, c2 = LLowPassFilter._calculate_values(freq, complex(rv, 0), z2)

        return c1, c2, l1 + l2, rv

    def __init__(self, frequency: RangeLike, src_resistance: FloatLike, src_reactance: FloatLike,
                 load_resistance: FloatLike, tolerance: FloatLike,
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
        self.tolerance = self.ArgParameter(tolerance)

        self.generator_param(self.frequency, self.src_resistance, self.src_reactance, self.load_resistance,
                             self.tolerance)

    def generate(self) -> None:
        super().generate()

        frequency = self.get(self.frequency)
        bandwidth = frequency.upper - frequency.lower
        q = frequency.center() / bandwidth

        rg = complex(self.get(self.src_resistance), self.get(self.src_reactance))
        rl = self.get(self.load_resistance)

        c1, c2, l, rv = self._calculate_values(frequency.center(), q, rg, rl)

        tolerance = self.get(self.tolerance)

        self.c1 = self.Block(Capacitor(capacitance=c1*Farad(tol=tolerance), voltage=self.voltage))
        self.c2 = self.Block(Capacitor(capacitance=c2*Farad(tol=tolerance), voltage=self.voltage))
        self.l = self.Block(Inductor(inductance=l*Henry(tol=tolerance), current=self.current))
        self.connect(self.input, self.c1.pos, self.l.a)
        self.connect(self.l.b, self.c2.pos, self.output)
        self.connect(self.gnd, self.c1.neg.adapt_to(Ground()), self.c2.neg.adapt_to(Ground()))
