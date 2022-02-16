from electronics_model import *
from .Categories import *


@abstract_block
class Resistor(PassiveComponent):
  # TODO no default resistance
  @init_in_parent
  def __init__(self, resistance: RangeLike, power: RangeLike = Default(RangeExpr.ZERO)) -> None:
    super().__init__()

    self.a = self.Port(Passive())
    self.b = self.Port(Passive())

    self.resistance = self.ArgParameter(resistance)
    self.power = self.ArgParameter(power)  # operating power range
    self.actual_resistance = self.Parameter(RangeExpr())


class PullupResistor(DiscreteApplication):
  """Pull-up resistor with an VoltageSink for automatic implicit connect to a Power line."""
  # TODO no default resistance
  @init_in_parent
  def __init__(self, resistance: RangeLike) -> None:
    super().__init__()

    self.res = self.Block(Resistor(resistance, 0*Watt(tol=0)))  # TODO automatically calculate power

    self.pwr = self.Export(self.res.a.as_voltage_sink(), [Power])
    self.io = self.Export(self.res.b.as_digital_pull_high_from_supply(self.pwr), [InOut])


class PulldownResistor(DiscreteApplication):
  """Pull-down resistor with an VoltageSink for automatic implicit connect to a Ground line."""
  # TODO no default resistance
  @init_in_parent
  def __init__(self, resistance: RangeLike) -> None:
    super().__init__()

    self.res = self.Block(Resistor(resistance, 0*Watt(tol=0)))  # TODO automatically calculate power

    self.gnd = self.Export(self.res.a.as_ground(), [Common])
    self.io = self.Export(self.res.b.as_digital_pull_low_from_supply(self.gnd), [InOut])


class SeriesPowerResistor(DiscreteApplication):
  """Series resistor for power applications"""
  @init_in_parent
  def __init__(self, resistance: RangeLike, current_limits: RangeLike) -> None:
    super().__init__()

    self.resistance = self.ArgParameter(resistance)
    self.current_limits = self.ArgParameter(current_limits)

    self.res = self.Block(Resistor(
      resistance=self.resistance,
      power=(self.current_limits.lower() * self.current_limits.lower() * self.resistance.lower(),
             self.current_limits.upper() * self.current_limits.upper() * self.resistance.upper())
    ))

    self.pwr_in = self.Export(self.res.a.as_voltage_sink(
      voltage_limits=(-float('inf'), float('inf')),
      current_draw=RangeExpr()
    ), [Power, Input])
    self.pwr_out = self.Export(self.res.b.as_voltage_source(
      voltage_out=self.pwr_in.link().voltage - self.current_limits * self.resistance,
      current_limits=self.current_limits
    ), [Output])
    self.assign(self.pwr_in.current_draw, self.pwr_out.link().current_drawn)


from electronics_model.VoltagePorts import VoltageSinkAdapterAnalogSource  # TODO dehack with better adapters
class CurrentSenseResistor(DiscreteApplication):
  """Current sense resistor with a power passthrough resistor and positive and negative sense temrinals."""
  @init_in_parent
  def __init__(self, resistance: RangeLike, current_limits: RangeLike) -> None:
    super().__init__()

    self.res = self.Block(SeriesPowerResistor(resistance, current_limits))
    self.pwr_in = self.Export(self.res.pwr_in, [Input])
    self.pwr_out = self.Export(self.res.pwr_out, [Output])

    self.sense_in = self.Port(AnalogSource())
    self.sense_out = self.Port(AnalogSource())

  def contents(self):
    super().contents()

    # TODO dehack with better adapters that also handle bridging
    self.pwr_adapter = self.Block(VoltageSinkAdapterAnalogSource())
    self.connect(self.pwr_in, self.pwr_adapter.src)
    self.connect(self.pwr_adapter.dst, self.sense_in)
    self.connect(self.res.pwr_out.as_analog_source(), self.sense_out)


@abstract_block
class UnpolarizedCapacitor(PassiveComponent):
  """Base type for a capacitor, that defines its parameters and without ports (since capacitors can be polarized)"""
  # TODO no default capacitance and voltage rating
  @init_in_parent
  def __init__(self, capacitance: RangeLike, voltage: RangeLike) -> None:
    super().__init__()

    self.capacitance = self.ArgParameter(capacitance)
    self.voltage = self.ArgParameter(voltage)  # defined as operating voltage range


@abstract_block
class Capacitor(UnpolarizedCapacitor):
  """Polarized capacitor, which we assume will be the default"""
  # TODO no default capacitance and voltage rating
  @init_in_parent
  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)

    self.pos = self.Port(Passive())
    self.neg = self.Port(Passive())


class DecouplingCapacitor(DiscreteApplication):
  """Optionally polarized capacitor used for DC decoupling, with VoltageSink connections with voltage inference.
  Implemented as a shim block."""
  # TODO no default capacitance
  @init_in_parent
  def __init__(self, capacitance: RangeLike) -> None:
    super().__init__()

    self.cap = self.Block(Capacitor(capacitance, voltage=RangeExpr()))
    self.pwr = self.Export(self.cap.pos.as_voltage_sink())
    self.gnd = self.Export(self.cap.neg.as_voltage_sink())

    self.assign(self.cap.voltage, self.pwr.link().voltage - self.gnd.link().voltage)


@abstract_block
class Inductor(PassiveComponent):
  # TODO no default inductance
  @init_in_parent
  def __init__(self, inductance: RangeLike,
               current: RangeLike = Default(RangeExpr.ZERO),
               frequency: RangeLike = Default(RangeExpr.EMPTY_ZERO)) -> None:
    super().__init__()

    self.a = self.Port(Passive())
    self.b = self.Port(Passive())

    self.inductance = inductance
    self.current = current  # defined as operating current range, non-directioned
    self.frequency = frequency  # defined as operating frequency range
    # TODO: in the future, when we consider efficiency - for now, use current ratings
    # self.resistance_dc = self.Parameter(RangeExpr())
