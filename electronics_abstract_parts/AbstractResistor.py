from typing import Optional, cast

from electronics_model import *
from .PartsTable import PartsTableColumn
from .PartsTablePart import PartsTableFootprint
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
    self.actual_power_rating = self.Parameter(RangeExpr())


@abstract_block
class TableResistor(Resistor, PartsTableFootprint, GeneratorBlock):
  RESISTANCE = PartsTableColumn(Range)
  POWER_RATING = PartsTableColumn(Range)

  @init_in_parent
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.generator(self.select_part, self.resistance, self.power, self.part, self.footprint_spec)

  def select_part(self, resistance: Range, power_dissipation: Range, part_spec: str, footprint_spec: str) -> None:
    parts = self._get_table().filter(lambda row: (
        (not part_spec or part_spec == row[self.PART_NUMBER]) and
        (not footprint_spec or footprint_spec == row[self.KICAD_FOOTPRINT]) and
        row[self.RESISTANCE].fuzzy_in(resistance) and
        power_dissipation.fuzzy_in(row[self.POWER_RATING])
    ))
    part = parts.first(f"no resistors in {resistance} Ohm, {power_dissipation} W")

    self.assign(self.actual_part, part[self.PART_NUMBER])
    self.assign(self.matching_parts, len(parts))
    self.assign(self.actual_resistance, part[self.RESISTANCE])
    self.assign(self.actual_power_rating, part[self.POWER_RATING])

    self._make_footprint(part)


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
