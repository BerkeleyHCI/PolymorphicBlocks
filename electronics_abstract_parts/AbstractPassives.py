from typing import Optional, cast

from electronics_model import *
from .Categories import *


@abstract_block
class Resistor(PassiveComponent):
  @init_in_parent
  def __init__(self, resistance: RangeLike, power: RangeLike = Default(RangeExpr.ZERO)) -> None:
    super().__init__()

    self.a = self.Port(Passive.empty())
    self.b = self.Port(Passive.empty())

    self.resistance = self.ArgParameter(resistance)
    self.power = self.ArgParameter(power)  # operating power range
    self.actual_resistance = self.Parameter(RangeExpr())


class PullupResistor(DiscreteApplication):
  """Pull-up resistor with an VoltageSink for automatic implicit connect to a Power line."""
  @init_in_parent
  def __init__(self, resistance: RangeLike) -> None:
    super().__init__()

    self.res = self.Block(Resistor(resistance, 0*Watt(tol=0)))  # TODO automatically calculate power

    self.pwr = self.Export(self.res.a.as_voltage_sink(), [Power])
    self.io = self.Export(self.res.b.as_digital_pull_high_from_supply(self.pwr), [InOut])

  def connected(self, pwr: Optional[Port[VoltageLink]] = None, io: Optional[Port[DigitalLink]] = None) -> \
      'PullupResistor':
    """Convenience function to connect both ports, returning this object so it can still be given a name."""
    if pwr is not None:
      cast(Block, builder.get_enclosing_block()).connect(pwr, self.pwr)
    if io is not None:
      cast(Block, builder.get_enclosing_block()).connect(io, self.io)
    return self


class PulldownResistor(DiscreteApplication):
  """Pull-down resistor with an VoltageSink for automatic implicit connect to a Ground line."""
  @init_in_parent
  def __init__(self, resistance: RangeLike) -> None:
    super().__init__()

    self.res = self.Block(Resistor(resistance, 0*Watt(tol=0)))  # TODO automatically calculate power

    self.gnd = self.Export(self.res.a.as_ground(), [Common])
    self.io = self.Export(self.res.b.as_digital_pull_low_from_supply(self.gnd), [InOut])

  def connected(self, gnd: Optional[Port[VoltageLink]] = None, io: Optional[Port[DigitalLink]] = None) -> \
      'PulldownResistor':
    """Convenience function to connect both ports, returning this object so it can still be given a name."""
    if gnd is not None:
      cast(Block, builder.get_enclosing_block()).connect(gnd, self.gnd)
    if io is not None:
      cast(Block, builder.get_enclosing_block()).connect(io, self.io)
    return self


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

  def connected(self, pwr_in: Optional[Port[VoltageLink]] = None, pwr_out: Optional[Port[VoltageLink]] = None) -> \
      'SeriesPowerResistor':
    """Convenience function to connect both ports, returning this object so it can still be given a name."""
    if pwr_in is not None:
      cast(Block, builder.get_enclosing_block()).connect(pwr_in, self.pwr_in)
    if pwr_out is not None:
      cast(Block, builder.get_enclosing_block()).connect(pwr_out, self.pwr_out)
    return self


from electronics_model.VoltagePorts import VoltageSinkAdapterAnalogSource  # TODO dehack with better adapters
class CurrentSenseResistor(DiscreteApplication):
  """Current sense resistor with a power passthrough resistor and positive and negative sense temrinals."""
  @init_in_parent
  def __init__(self, resistance: RangeLike, current_limits: RangeLike) -> None:
    super().__init__()

    self.res = self.Block(SeriesPowerResistor(resistance, current_limits))
    self.pwr_in = self.Export(self.res.pwr_in, [Input])
    self.pwr_out = self.Export(self.res.pwr_out, [Output])

    self.sense_in = self.Port(AnalogSource.empty())
    self.sense_out = self.Port(AnalogSource.empty())

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
  @init_in_parent
  def __init__(self, capacitance: RangeLike, voltage: RangeLike) -> None:
    super().__init__()

    self.capacitance = self.ArgParameter(capacitance)
    self.voltage = self.ArgParameter(voltage)  # defined as operating voltage range


@abstract_block
class Capacitor(UnpolarizedCapacitor):
  """Polarized capacitor, which we assume will be the default"""
  @init_in_parent
  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)

    self.pos = self.Port(Passive.empty())
    self.neg = self.Port(Passive.empty())


class DecouplingCapacitor(DiscreteApplication):
  """Optionally polarized capacitor used for DC decoupling, with VoltageSink connections with voltage inference.
  Implemented as a shim block."""
  @init_in_parent
  def __init__(self, capacitance: RangeLike) -> None:
    super().__init__()

    self.cap = self.Block(Capacitor(capacitance, voltage=RangeExpr()))
    self.gnd = self.Export(self.cap.neg.as_voltage_sink(), [Common])
    self.pwr = self.Export(self.cap.pos.as_voltage_sink(), [Power])

    self.assign(self.cap.voltage, self.pwr.link().voltage - self.gnd.link().voltage)

  def connected(self, gnd: Optional[Port[VoltageLink]] = None, pwr: Optional[Port[VoltageLink]] = None) -> \
      'DecouplingCapacitor':
    """Convenience function to connect both ports, returning this object so it can still be given a name."""
    if gnd is not None:
      cast(Block, builder.get_enclosing_block()).connect(gnd, self.gnd)
    if pwr is not None:
      cast(Block, builder.get_enclosing_block()).connect(pwr, self.pwr)
    return self


@abstract_block
class Inductor(PassiveComponent):
  @init_in_parent
  def __init__(self, inductance: RangeLike,
               current: RangeLike = Default(RangeExpr.ZERO),
               frequency: RangeLike = Default(RangeExpr.EMPTY_ZERO)) -> None:
    super().__init__()

    self.a = self.Port(Passive.empty())
    self.b = self.Port(Passive.empty())

    self.inductance = self.ArgParameter(inductance)
    self.current = self.ArgParameter(current)  # defined as operating current range, non-directioned
    self.frequency = self.ArgParameter(frequency)  # defined as operating frequency range
    # TODO: in the future, when we consider efficiency - for now, use current ratings
    # self.resistance_dc = self.Parameter(RangeExpr())
