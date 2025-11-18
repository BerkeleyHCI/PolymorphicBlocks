from typing import Mapping

from .ResistiveDivider import FeedbackVoltageDivider, VoltageDivider
from ..abstract_parts import Analog
from ..electronics_model import *


class Comparator(KiCadInstantiableBlock, Analog):
    """Abstract comparator interface, output goes high when inp > inn."""
    def symbol_pinning(self, symbol_name: str) -> Mapping[str, BasePort]:
        assert symbol_name in ('Simulation_SPICE:OPAMP', 'edg_importable:Opamp')
        return {'+': self.inp, '-': self.inn, '3': self.out, 'V+': self.pwr, 'V-': self.gnd}

    @classmethod
    def block_from_symbol(cls, symbol_name: str, properties: Mapping[str, str]) -> 'Comparator':
        return Comparator()

    def __init__(self) -> None:
        super().__init__()

        self.pwr = self.Port(VoltageSink.empty(), [Power])
        self.gnd = self.Port(Ground.empty(), [Common])
        self.inn = self.Port(AnalogSink.empty())
        self.inp = self.Port(AnalogSink.empty())
        self.out = self.Port(DigitalSource.empty())


class VoltageComparator(GeneratorBlock):
    """A comparator subcircuit that compares an input voltage rail against some reference, either
    internally generated from the power lines or an external analog signals.
    Accounts for tolerance stackup on the reference input - so make sure the trip
    tolerance is specified wide enough.
    The output is logic high when the input exceeds the trip voltage by default,
    this can be inverted with the invert parameter.
    Optionally this can take a reference voltage input, otherwise this generates a divider.

    TODO: maybe a version that takes an input analog signal?
    """
    @init_in_parent
    def __init__(self, trip_voltage: RangeLike, *, invert: BoolLike = False,
                 input_impedance: RangeLike=(4.7, 47)*kOhm,
                 trip_ref: RangeLike=1.65*Volt(tol=0.10)):
        super().__init__()
        self.comp = self.Block(Comparator())
        self.gnd = self.Export(self.comp.gnd, [Common])
        self.pwr = self.Export(self.comp.pwr, [Power])
        self.input = self.Port(AnalogSink.empty(), [Input])
        self.output = self.Export(self.comp.out, [Output])
        self.ref = self.Port(AnalogSink.empty(), optional=True)

        self.trip_voltage = self.ArgParameter(trip_voltage)
        self.invert = self.ArgParameter(invert)
        self.trip_ref = self.ArgParameter(trip_ref)  # only used if self.ref disconnected
        self.input_impedance = self.ArgParameter(input_impedance)
        self.generator_param(self.ref.is_connected(), self.invert)

        self.actual_trip_voltage = self.Parameter(RangeExpr())

    def generate(self):
        super().generate()

        if self.get(self.ref.is_connected()):
            ref_pin: Port[AnalogLink] = self.ref
            ref_voltage = self.ref.link().signal
        else:
            self.ref_div = self.Block(VoltageDivider(
                output_voltage=self.trip_ref,
                impedance=self.input_impedance,
            ))
            self.connect(self.ref_div.input, self.pwr)
            self.connect(self.ref_div.gnd, self.gnd)
            ref_pin = self.ref_div.output
            ref_voltage = self.ref_div.output.link().signal

        self.comp_div = self.Block(FeedbackVoltageDivider(
            impedance=self.input_impedance,
            output_voltage=ref_voltage,
            assumed_input_voltage=self.trip_voltage
        ))
        self.assign(self.actual_trip_voltage, self.comp_div.actual_input_voltage)
        self.connect(self.comp_div.input, self.input.as_voltage_source())
        self.connect(self.comp_div.gnd, self.gnd)
        if not self.get(self.invert):  # positive connection
            self.connect(self.comp.inp, self.comp_div.output)
            self.connect(self.comp.inn, ref_pin)
        else:  # negative connection
            self.connect(self.comp.inn, self.comp_div.output)
            self.connect(self.comp.inp, ref_pin)
