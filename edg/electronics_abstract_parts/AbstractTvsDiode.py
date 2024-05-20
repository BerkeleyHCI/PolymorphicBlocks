from ...electronics_model import *
from .Categories import *
from .AbstractDiodes import BaseDiode


@abstract_block
class TvsDiode(BaseDiode):
    """Base class for TVS diodes with TVS specific parameters
    Cathode should be connected to the signal, and anode to ground.

    Working and breakdown voltages are the total working voltage - typically from zero to +V for
    unidirectional diodes, or -V to +V for bidirectional diodes.
    Working voltage is user-specified and may not account for tolerances,
    while breakdown voltage should be checked against the actual operating voltages.
    TODO: does this model make sense?

    TODO: model capacitance frequency? model breakdown and clamping voltage?
    TODO: how does this differ from Zener diodes?
    """
    @init_in_parent
    def __init__(self, working_voltage: RangeLike, *,
                 capacitance: RangeLike = Range.all()) -> None:
        super().__init__()

        self.working_voltage = self.ArgParameter(working_voltage)
        self.capacitance = self.ArgParameter(capacitance)

        self.actual_working_voltage = self.Parameter(RangeExpr())
        self.actual_breakdown_voltage = self.Parameter(RangeExpr())
        self.actual_capacitance = self.Parameter(RangeExpr())


class ProtectionTvsDiode(Protection):
    """TVS diode across a power rail"""
    @init_in_parent
    def __init__(self, working_voltage: RangeLike):
        super().__init__()

        self.pwr = self.Port(VoltageSink.empty(), [Power, InOut])
        self.gnd = self.Port(Ground.empty(), [Common])

        self.working_voltage = self.ArgParameter(working_voltage)

    def contents(self):
        super().contents()
        self.diode = self.Block(TvsDiode(working_voltage=self.working_voltage))
        self.connect(self.diode.cathode.adapt_to(VoltageSink(
            voltage_limits=self.diode.actual_breakdown_voltage,
        )), self.pwr)
        self.connect(self.diode.anode.adapt_to(Ground()), self.gnd)


class DigitalTvsDiode(Protection):
    """TVS diode protecting a signal line"""
    @init_in_parent
    def __init__(self, working_voltage: RangeLike, *, capacitance: RangeLike = Range.all()):
        super().__init__()

        self.io = self.Port(DigitalSink.empty(), [InOut])
        self.gnd = self.Port(Ground.empty(), [Common])

        self.working_voltage = self.ArgParameter(working_voltage)
        self.capacitance = self.ArgParameter(capacitance)

    def contents(self):
        super().contents()
        self.diode = self.Block(TvsDiode(working_voltage=self.working_voltage, capacitance=self.capacitance))
        self.connect(self.diode.cathode.adapt_to(DigitalSink(
            voltage_limits=self.diode.actual_breakdown_voltage,
        )), self.io)
        self.connect(self.diode.anode.adapt_to(Ground()), self.gnd)
