from math import pi

from electronics_model import *
from .AbstractCapacitor import Capacitor
from .AbstractInductor import Inductor
from .Categories import *


class PiLowPassFilter(AnalogFilter, GeneratorBlock):
    """Passive-typed pi impedance matching network.
    Based on equations from https://www.electronicdesign.com/technologies/communications/article/21801154/back-to-basics-impedance-matching-part-3
    Frequency defines the entire bandwidth this filter should work across.

    WORK IN PROGRESS. NON-STABLE API.

    TODO: use ranges and tolerances throughout"""
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

        self.c1 = self.Block(Capacitor(capacitance=(0, 0)*Farad, voltage=self.voltage))
        self.c2 = self.Block(Capacitor(capacitance=(0, 0)*Farad, voltage=self.voltage))
        self.l = self.Block(Inductor(inductance=(0, 0)*Henry, current=self.current))
        self.connect(self.input, self.c1.pos, self.l.a)
        self.connect(self.l.b, self.c2.pos, self.output)
        self.connect(self.c1.neg, self.c2.neg)
        self.connect(self.c1.neg.adapt_to(Ground()), self.gnd)
