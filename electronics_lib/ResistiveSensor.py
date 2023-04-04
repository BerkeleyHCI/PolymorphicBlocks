from electronics_abstract_parts import *
from .PassiveConnector import PassiveConnector


class ConnectorResistiveSensor(Analog, Block):
  """Senses the resistance of an external resistor (through an abstract connector
  that is part of this block) using a simple voltage divider circuit.
  The external resistor is on the bottom (which makes this of a classic Wheatstone Bridge
  as drawn on Wikipedia)."""
  @init_in_parent
  def __init__(self, resistance_range: RangeLike, fixed_resistance: RangeLike) -> None:
    super().__init__()
    self.resistance_range = self.ArgParameter(resistance_range)
    self.fixed_resistance = self.ArgParameter(fixed_resistance)

    self.input = self.Port(VoltageSink.empty(), [Input])
    self.output = self.Port(AnalogSource.empty(), [Output])
    self.gnd = self.Port(Ground.empty())

    # TODO deduplicate with ResistiveDivider class?
    self.actual_ratio = self.Parameter(RangeExpr())
    self.actual_impedance = self.Parameter(RangeExpr())
    self.actual_series_impedance = self.Parameter(RangeExpr())

  def contents(self):
    self.top = self.Block(Resistor(self.fixed_resistance, voltage=self.input.link().voltage))
    self.bot = self.Block(PassiveConnector(2))
    self.connect(self.input, self.top.a.adapt_to(VoltageSink(
      current_draw=self.output.link().current_drawn
    )))
    self.connect(self.output, self.top.b.adapt_to(AnalogSource(
      voltage_out=(self.input.link().voltage.lower() * self.actual_ratio.lower(),
                   self.input.link().voltage.upper() * self.actual_ratio.upper()),
      current_limits=RangeExpr.ALL,
      impedance=self.actual_impedance
    )), self.bot.pins.request('1').adapt_to(AnalogSink()))
    self.connect(self.gnd, self.bot.pins.request('2').adapt_to(Ground()))

    self.assign(self.actual_impedance,
                1 / (1 / self.top.actual_resistance + 1 / self.resistance_range))
    self.assign(self.actual_series_impedance,
                self.top.actual_resistance + self.resistance_range)
    self.assign(self.actual_ratio,
                1 / (self.top.actual_resistance / self.resistance_range + 1))
