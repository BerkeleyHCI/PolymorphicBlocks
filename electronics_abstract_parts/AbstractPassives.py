from electronics_model import *
from itertools import chain
from .Categories import *


@abstract_block
class Resistor(PassiveComponent):

  # TODO no default resistance
  @init_in_parent
  def __init__(self, resistance: RangeLike = RangeExpr(), power: RangeLike = (0, 0) * Watt) -> None:
    super().__init__()

    self.a = self.Port(Passive())
    self.b = self.Port(Passive())

    self.spec_resistance = self.Parameter(RangeExpr(resistance))
    self.resistance = self.Parameter(RangeExpr())
    self.power = self.Parameter(RangeExpr(power))  # operating power range


class PullupResistor(DiscreteApplication):
  """Pull-up resistor with an VoltageSink for automatic implicit connect to a Power line."""
  # TODO no default resistance
  @init_in_parent
  def __init__(self, resistance: RangeLike = RangeExpr()) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink(), [Power])
    self.io = self.Port(DigitalSingleSource(), [InOut])

    self.resistance = self.Parameter(RangeExpr(resistance))

  def contents(self):
    super().contents()
    self.res = self.Block(Resistor(self.resistance, 0*Watt(tol=0)))  # TODO automatically calculate power

    self.connect(self.pwr, self.res.a.as_voltage_sink())
    self.connect(self.io, self.res.b.as_digital_pull_high_from_supply(self.pwr))


class PulldownResistor(DiscreteApplication):
  """Pull-down resistor with an VoltageSink for automatic implicit connect to a Ground line."""
  # TODO no default resistance
  @init_in_parent
  def __init__(self, resistance: RangeLike = RangeExpr()) -> None:
    super().__init__()

    self.resistance = self.Parameter(RangeExpr(resistance))

    self.gnd = self.Port(Ground(), [Common])
    self.io = self.Port(DigitalSingleSource(), [InOut])

  def contents(self):
    super().contents()
    self.res = self.Block(Resistor(self.resistance, 0*Watt(tol=0)))  # TODO automatically calculate power

    self.connect(self.gnd, self.res.a.as_ground())
    self.connect(self.io, self.res.b.as_digital_pull_low_from_supply(self.gnd))


class SeriesPowerResistor(DiscreteApplication):
  """Series resistor for power applications"""
  @init_in_parent
  def __init__(self, resistance: RangeLike = RangeExpr(), current_limits: RangeLike = RangeExpr()) -> None:
    super().__init__()

    self.pwr_in = self.Port(VoltageSink(), [Power, Input])
    self.pwr_out = self.Port(VoltageSource(), [Output])

    self.resistance = self.Parameter(RangeExpr(resistance))
    self.current_limits = self.Parameter(RangeExpr(current_limits))

  def contents(self):
    super().contents()

    self.res = self.Block(Resistor(
      resistance=self.resistance,
      power=(self.current_limits.lower() * self.current_limits.lower() * self.resistance.lower(),
             self.current_limits.upper() * self.current_limits.upper() * self.resistance.upper())
    ))
    self.connect(self.res.a.as_voltage_sink(
      voltage_limits=(-float('inf'), float('inf')),
      current_draw=RangeExpr()
    ), self.pwr_in)
    self.connect(self.res.b.as_voltage_source(
      voltage_out=self.pwr_in.link().voltage - self.current_limits * self.resistance,
      current_limits=self.current_limits
    ), self.pwr_out)

    # Note, this is a worst-case current draw that uses passed in current limits, instead of actual current draw
    # This is done to avoid a cyclic dependency
    # TODO: better current limits using actual current drawn
    self.assign(self.pwr_in.current_draw, self.pwr_out.link().current_drawn)


from electronics_model.VoltagePorts import VoltageSinkAdapterAnalogSource  # TODO dehack with better adapters
class CurrentSenseResistor(DiscreteApplication):
  """Current sense resistor with a power passthrough resistor and positive and negative sense temrinals."""
  @init_in_parent
  def __init__(self, resistance: RangeLike = RangeExpr(), current_limits: RangeLike = RangeExpr()) -> None:
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
  def __init__(self, capacitance: RangeLike = RangeExpr(), voltage: RangeLike = RangeExpr(),
               part_spec: StringLike = "") -> None:
    super().__init__()

    self.capacitance = self.Parameter(RangeExpr(capacitance))
    self.voltage = self.Parameter(RangeExpr(voltage))  # defined as operating voltage range


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
  def __init__(self, capacitance: RangeLike = RangeExpr()) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink(), [Power, Input])
    self.gnd = self.Port(VoltageSink(), [Common, Output])

    self.capacitance = self.Parameter(RangeExpr(capacitance))

  def contents(self):
    super().contents()
    self.cap = self.Block(Capacitor(self.capacitance, voltage=(self.pwr.link().voltage - self.gnd.link().voltage)))

    self.connect(self.pwr, self.cap.pos.as_voltage_sink())
    self.connect(self.gnd, self.cap.neg.as_voltage_sink())


@abstract_block
class Inductor(PassiveComponent):
  # TODO no default inductance
  @init_in_parent
  def __init__(self, inductance: RangeLike = RangeExpr(),
               current: RangeLike = Default(RangeExpr.ZERO),
               frequency: RangeLike = Default(RangeExpr.EMPTY_ZERO)) -> None:
    super().__init__()

    self.a = self.Port(Passive())
    self.b = self.Port(Passive())

    self.inductance = self.Parameter(RangeExpr(inductance))
    self.current = self.Parameter(RangeExpr(current))  # defined as operating current range, non-directioned
    self.frequency = self.Parameter(RangeExpr(frequency))  # defined as operating frequency range
    # TODO: in the future, when we consider efficiency - for now, use current ratings
    # self.resistance_dc = self.Parameter(RangeExpr())
