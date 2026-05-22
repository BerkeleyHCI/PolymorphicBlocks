from typing_extensions import override

from ..abstract_parts import *


class ConnectorResistiveSensor(Analog, Block):
    """Senses the resistance of an external resistor (through an abstract connector
    that is part of this block) using a simple voltage divider circuit.
    The external resistor is on the bottom (which makes this of a classic Wheatstone Bridge
    as drawn on Wikipedia)."""

    def __init__(self, resistance_range: RangeLike, fixed_resistance: RangeLike) -> None:
        super().__init__()
        self.resistance_range = self.ArgParameter(resistance_range)
        self.fixed_resistance = self.ArgParameter(fixed_resistance)

        self.input = self.Port(VoltageSink(current_draw=RangeExpr()), [Power])
        self.output = self.Port(
            AnalogSource(voltage_out=RangeExpr(), signal_out=RangeExpr(), impedance=RangeExpr()), [Output]
        )
        self.gnd = self.Port(Ground(), [Common])

        # TODO deduplicate with ResistiveDivider class
        self.actual_ratio = self.Parameter(RangeExpr())
        self.actual_impedance = self.Parameter(RangeExpr())
        self.actual_series_impedance = self.Parameter(RangeExpr())

    @override
    def contents(self) -> None:
        self.top = self.Block(Resistor(self.fixed_resistance, voltage=self.input.link().voltage))
        self.bot = self.Block(PassiveConnector(2))
        self.connect(self.input.net, self.top.a)
        self.assign(self.input.current_draw, self.output.link().current_drawn)
        output_voltage = ResistiveDivider.divider_output(
            self.input.link().voltage, self.gnd.link().voltage, self.actual_ratio
        )
        self.assign(self.output.voltage_out, output_voltage)
        self.assign(self.output.signal_out, output_voltage)
        self.assign(self.output.impedance, self.actual_impedance)
        self.connect(self.output.net, self.top.b, self.bot.pins.request("1"))
        self.connect(self.gnd.net, self.bot.pins.request("2"))

        self.assign(self.actual_impedance, 1 / (1 / self.top.actual_resistance + 1 / self.resistance_range))
        self.assign(self.actual_series_impedance, self.top.actual_resistance + self.resistance_range)
        self.assign(self.actual_ratio, 1 / (self.top.actual_resistance / self.resistance_range + 1))
