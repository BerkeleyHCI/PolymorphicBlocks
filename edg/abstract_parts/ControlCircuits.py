import math
from typing import Dict

from typing_extensions import override

from ..electronics_model import *
from .AbstractResistor import Resistor
from .AbstractCapacitor import Capacitor
from .AbstractOpamp import Opamp
from .Categories import OpampApplication


class CompensatorType2(OpampApplication, KiCadSchematicBlock, KiCadImportableBlock):
    """A Type II Compensator circuit used in feedback control loops.

    In simple terms, this can be thought of as a inverting integrator (Type I Compensator)
    with better high frequency stability. This adds a zero-pole pair centered around the
    (parameter) crossover frequency fc, which provides phase boost near fc to improve phase margin.
    In some cases, this target may be set lower than the actual crossover frequency to achieve better gain margin,
    at the cost of phase margin.

    K is defined as the ratio of the fc to the zero frequency fz, so fz=fc/K and fp=fc*K.
    Higher K (wider plateau in gain vs. frequency) provides more phase boost, but reduces the high-frequency
    gain roll-off which reduces noise.
    These Ks translate into these phase boosts:
    K=1.7 => 30 degrees  (lower K: faster response)
    K=2.4 => 45 degrees
    K=3.7 => 60 degrees  (higher K: more damped response, more stable, more phase margin)
    K is not toleranced, instead it inherits tolerancing of the crossover frequency.

    The crossover_gain is the target gain (as a ratio, NOT dB) of this circuit in isolation at fc.
    This is usually the reciprocal of the plant gain at that frequency so loop gain is 1 at fc.
    This parameter may be determined or tuned through simulation.

    The rin parameter sets the value of the input resistor (R1 in references). This is a degree of freedom
    and balances between power consumption (higher R1) and noise (lower R1). Typical values are in mid-kOhm range.

    Real opamps have limited gain-bandwidth, ensure that the crossover frequency is well below (roughly at least 10x)
    the gain-bandwidth of the selected opamp.

    This current implementation omits the bias resistor (R4 in the TI formulation) and assumes the input is DC-based
    at the reference voltage.

    References:
    "THE K FACTOR: A NEW MATHEMATICAL TOOL FOR STABILITY ANALYSIS AND SYNTHESIS", Venable Instruments
    https://4867466.fs1.hubspotusercontent-na2.net/hubfs/4867466/White%20Papers/Documents%20/The%20K%20Factor.pdf
    (the implementation of this classes uses this formulation)

    "Demystifying Type II and Type III Compensators Using Op-Amp and OTA for DC/DC Converters"
    https://www.ti.com/lit/an/slva662/slva662.pdf

    "Design Type II Compensation In A Systematic Way", Liyu Cao
    https://www.researchgate.net/profile/Liyu-Cao/publication/256455457_Design_Type_II_Compensation_In_A_Systematic_Way/links/0c960522ba2296f7b2000000/Design-Type-II-Compensation-In-A-Systematic-Way.pdf
    this formulation uses an alpha factor to shift the crossover frequency leftwards, for more gain margin
    """

    @override
    def symbol_pinning(self, symbol_name: str) -> Dict[str, BasePort]:
        mapping: Dict[str, Dict[str, BasePort]] = {
            "Simulation_SPICE:OPAMP": {
                "+": self.input,
                "-": self.reference,
                "3": self.output,
                "V+": self.pwr,
                "V-": self.gnd,
            },
            "edg_importable:IntegratorInverting": {
                "-": self.input,
                "R": self.reference,
                "3": self.output,
                "V+": self.pwr,
                "V-": self.gnd,
            },
        }
        return mapping[symbol_name]

    def __init__(self, rin: RangeLike, crossover_freq: RangeLike, k: FloatLike, crossover_gain: FloatLike):
        super().__init__()

        self.amp = self.Block(Opamp())
        self.pwr = self.Port(VoltageSink.empty(), [Power])
        self.gnd = self.Port(Ground.empty(), [Common])

        self.input = self.Port(AnalogSink.empty())
        self.output = self.Port(AnalogSource.empty())
        self.reference = self.Port(AnalogSink.empty())  # negative reference for the input and output signals

        self.rin = self.ArgParameter(rin)
        self.crossover_freq = self.ArgParameter(crossover_freq)
        self.k = self.ArgParameter(k)
        self.crossover_gain = self.ArgParameter(crossover_gain)  # in ratio, not dB!

    @override
    def contents(self) -> None:
        super().contents()

        self.r1 = self.Block(Resistor(self.rin))
        self.c2 = self.Block(Capacitor(capacitance=1 / (2 * math.pi * self.crossover_freq * self.crossover_gain * self.k * self.r1.actual_resistance),
                                       voltage=self.output.link().voltage))
        self.c1 = self.Block(Capacitor(capacitance=self.c2.capacitance * (self.k * self.k - 1),
                                       voltage=self.output.link().voltage))
        self.r2 = self.Block(Resistor(self.k / (2 * math.pi * self.crossover_freq * self.c1.actual_capacitance)))

        self.import_kicad(
            self.file_path("resources", f"{self.__class__.__name__}.kicad_sch"),
            conversions={
                "r1.1": AnalogSink(impedance=self.r1.actual_resistance),  # TODO very simplified and probably very wrong
                # these model the opamp in- node
                "r1.2": AnalogSource(voltage_out=self.amp.out.voltage_out, impedance=self.r1.actual_resistance),
                "r2.1": AnalogSink(),
                "c2.2": AnalogSink(),
                # these model the opamp out node
                "c2.1": AnalogSink(),
                "c1.1": AnalogSink(),
            },
        )
