import re
from typing import Optional, cast, Mapping, Dict, Any

from ..electronics_model import *
from .ESeriesUtil import ESeriesUtil
from .PartsTable import PartsTableColumn, PartsTableRow
from .PartsTablePart import PartsTableSelector
from .Categories import *
from .StandardFootprint import StandardFootprint, HasStandardFootprint


class ResistorStandardFootprint(StandardFootprint['Resistor']):
  REFDES_PREFIX = 'R'

  FOOTPRINT_PINNING_MAP = {
    (
      'Resistor_SMD:R_0201_0603Metric',
      'Resistor_SMD:R_0402_1005Metric',
      'Resistor_SMD:R_0603_1608Metric',
      'Resistor_SMD:R_0805_2012Metric',
      'Resistor_SMD:R_1206_3216Metric',
      'Resistor_SMD:R_1210_3225Metric',
      'Resistor_SMD:R_2010_5025Metric',
      'Resistor_SMD:R_2512_6332Metric',

      'Resistor_THT:R_Axial_DIN0204_L3.6mm_D1.6mm_P5.08mm_Horizontal',
      'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal',
      'Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P12.70mm_Horizontal',
      'Resistor_THT:R_Axial_DIN0411_L9.9mm_D3.6mm_P12.70mm_Horizontal',
      'Resistor_THT:R_Axial_DIN0414_L11.9mm_D4.5mm_P15.24mm_Horizontal',

      'Resistor_THT:R_Axial_DIN0204_L3.6mm_D1.6mm_P1.90mm_Vertical',
      'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical',
      'Resistor_THT:R_Axial_DIN0309_L9.0mm_D3.2mm_P2.54mm_Vertical',
      'Resistor_THT:R_Axial_DIN0411_L9.9mm_D3.6mm_P5.08mm_Vertical',
      'Resistor_THT:R_Axial_DIN0414_L11.9mm_D4.5mm_P5.08mm_Vertical',
    ): lambda block: {
      '1': block.a,
      '2': block.b,
    },
  }


@abstract_block
class Resistor(PassiveComponent, KiCadInstantiableBlock, HasStandardFootprint):
  _STANDARD_FOOTPRINT = ResistorStandardFootprint

  RESISTOR_REGEX = re.compile("^" + f"([\d.{PartParserUtil.SI_PREFIXES}]+(?:\s*[{PartParserUtil.SI_PREFIXES}])?)\s*[RΩ]?" +
                              "\s*" + "((?:\+-|\+/-|±)?\s*[\d.]+\s*%?)?" + "$")
  RESISTOR_DEFAULT_TOL = 0.05  # TODO this should be unified elsewhere

  def symbol_pinning(self, symbol_name: str) -> Mapping[str, BasePort]:
    assert symbol_name in ('Device:R', 'Device:R_Small')
    return {'1': self.a, '2': self.b}

  @classmethod
  def parse_resistor(cls, value: str) -> Range:
    match = cls.RESISTOR_REGEX.match(value)
    assert match is not None, f"could not parse resistor from value '{value}'"
    center = PartParserUtil.parse_value(match.group(1), '')
    if match.group(2) is not None:
      tol_str = match.group(2)
      if not tol_str.startswith('±'):  # format conversion to more strict parser
        tol_str = '±' + tol_str
      return PartParserUtil.parse_abs_tolerance(tol_str, center, 'Ω')
    else:
      return Range.from_tolerance(center, (-cls.RESISTOR_DEFAULT_TOL, cls.RESISTOR_DEFAULT_TOL))

  @classmethod
  def block_from_symbol(cls, symbol_name: str, properties: Mapping[str, str]) -> 'Resistor':
    return Resistor(resistance=cls.parse_resistor(properties['Value']))

  def __init__(self, resistance: RangeLike, power: RangeLike = RangeExpr.ZERO,
               voltage: RangeLike = RangeExpr.ZERO) -> None:
    super().__init__()

    self.a = self.Port(Passive.empty())
    self.b = self.Port(Passive.empty())

    self.resistance = self.ArgParameter(resistance)
    self.power = self.ArgParameter(power)  # operating power range
    self.voltage = self.ArgParameter(voltage)  # operating voltage range
    self.actual_resistance = self.Parameter(RangeExpr())
    self.actual_power_rating = self.Parameter(RangeExpr())
    self.actual_voltage_rating = self.Parameter(RangeExpr())

  def contents(self) -> None:
    super().contents()

    self.description = DescriptionString(
      "<b>resistance:</b> ", DescriptionString.FormatUnits(self.actual_resistance, "Ω"),
      " <b>of spec</b> ", DescriptionString.FormatUnits(self.resistance, "Ω"), "\n",
      "<b>power rating:</b> ", DescriptionString.FormatUnits(self.actual_power_rating, "W"),
      " <b>of operating:</b> ", DescriptionString.FormatUnits(self.power, "W"), "\n",
      "<b>voltage rating:</b> ", DescriptionString.FormatUnits(self.actual_voltage_rating, "V"),
      " <b>of operating:</b> ", DescriptionString.FormatUnits(self.voltage, "V")
    )


@non_library
class TableResistor(PartsTableSelector, Resistor):
  RESISTANCE = PartsTableColumn(Range)
  POWER_RATING = PartsTableColumn(Range)
  VOLTAGE_RATING = PartsTableColumn(Range)

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.generator_param(self.resistance, self.power, self.voltage)

  def _row_filter(self, row: PartsTableRow) -> bool:
    return super()._row_filter(row) and \
      row[self.RESISTANCE].fuzzy_in(self.get(self.resistance)) and \
      self.get(self.power).fuzzy_in(row[self.POWER_RATING]) and \
      self.get(self.voltage).fuzzy_in(row[self.VOLTAGE_RATING])

  def _row_generate(self, row: PartsTableRow) -> None:
    super()._row_generate(row)
    self.assign(self.actual_resistance, row[self.RESISTANCE])
    self.assign(self.actual_power_rating, row[self.POWER_RATING])
    self.assign(self.actual_voltage_rating, row[self.VOLTAGE_RATING])

  @classmethod
  def _row_sort_by(cls, row: PartsTableRow) -> Any:
    return (ESeriesUtil.series_of(row[cls.RESISTANCE].center(), default=ESeriesUtil.SERIES_MAX + 1),
            super()._row_sort_by(row))


class SeriesResistor(Resistor, GeneratorBlock):
  """Splits a resistor into equal resistors in series. Improves power and voltage ratings
  by distributing the load across multiple devices.

  Generally used as a refinement to break up a single (logical) resistor that is dissipating too much power
  or has an excessive voltage across it. Accounts for tolerance stackup for power and voltage distribution
  using specified (not actual) resistor tolerance - is a pessimistic calculation."""
  def __init__(self, *args, count: IntLike = 2, **kwargs):
    super().__init__(*args, **kwargs)
    self.count = self.ArgParameter(count)
    self.generator_param(self.count, self.resistance)

  def generate(self) -> None:
    super().generate()
    count = self.get(self.count)
    last_port = self.a
    cumu_resistance: RangeLike = Range.exact(0)
    cumu_power_rating: RangeLike = Range.exact(0)
    cumu_voltage_rating: RangeLike = Range.exact(0)
    self.res = ElementDict[Resistor]()

    # calculate tolerance stackup effects on R for worst-case power and voltage
    resistance_range = self.get(self.resistance)
    resistance_tol = (resistance_range.upper - resistance_range.lower) / 2 / resistance_range.center()
    resistance_tol = min(0.05, resistance_tol)  # in practice there should be no >5% resistors
    resistance_ratio_range = Range((1 - resistance_tol) / (count + resistance_tol * (count - 2)),
                                   (1 + resistance_tol) / (count - resistance_tol * (count - 2)))

    elt_resistance = resistance_range / count
    elt_power = self.power * resistance_ratio_range
    elt_voltage = self.voltage * resistance_ratio_range

    for i in range(count):
      self.res[i] = res = self.Block(Resistor(resistance=elt_resistance,
                                              power=elt_power,
                                              voltage=elt_voltage))
      self.connect(last_port, res.a)
      cumu_resistance = cumu_resistance + res.actual_resistance
      cumu_power_rating = cumu_power_rating + res.actual_power_rating
      cumu_voltage_rating = cumu_voltage_rating + res.actual_voltage_rating
      last_port = res.b
    self.connect(last_port, self.b)
    self.assign(self.actual_resistance, cumu_resistance)
    self.assign(self.actual_power_rating, cumu_power_rating)
    self.assign(self.actual_voltage_rating, cumu_voltage_rating)


class PullupResistor(DiscreteApplication):
  """Pull-up resistor with an VoltageSink for automatic implicit connect to a Power line."""
  def __init__(self, resistance: RangeLike) -> None:
    super().__init__()

    self.res = self.Block(Resistor(resistance, 0*Watt(tol=0)))  # TODO automatically calculate power

    self.pwr = self.Export(self.res.a.adapt_to(VoltageSink()), [Power])
    self.io = self.Export(self.res.b.adapt_to(
      DigitalSource.pullup_from_supply(self.pwr)
    ), [InOut])

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
  def __init__(self, resistance: RangeLike) -> None:
    super().__init__()

    self.res = self.Block(Resistor(resistance, 0*Watt(tol=0)))  # TODO automatically calculate power

    self.gnd = self.Export(self.res.a.adapt_to(Ground()), [Common])
    self.io = self.Export(self.res.b.adapt_to(
      DigitalSource.pulldown_from_supply(self.gnd)
    ), [InOut])

  def connected(self, gnd: Optional[Port[GroundLink]] = None, io: Optional[Port[DigitalLink]] = None) -> \
      'PulldownResistor':
    """Convenience function to connect both ports, returning this object so it can still be given a name."""
    if gnd is not None:
      cast(Block, builder.get_enclosing_block()).connect(gnd, self.gnd)
    if io is not None:
      cast(Block, builder.get_enclosing_block()).connect(io, self.io)
    return self


class PullupResistorArray(TypedTestPoint, GeneratorBlock):
  """Array of PullupResistors, sized from the port array's connections."""
  def __init__(self, resistance: RangeLike):
    super().__init__()
    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.io = self.Port(Vector(DigitalSource.empty()), [InOut])
    self.generator_param(self.io.requested())
    self.resistance = self.ArgParameter(resistance)

  def generate(self) -> None:
    super().generate()
    self.res = ElementDict[PullupResistor]()
    for requested in self.get(self.io.requested()):
      res = self.res[requested] = self.Block(PullupResistor(self.resistance))
      self.connect(self.pwr, res.pwr)
      self.connect(self.io.append_elt(DigitalSource.empty(), requested), res.io)


class PulldownResistorArray(TypedTestPoint, GeneratorBlock):
  """Array of PulldownResistors, sized from the port array's connections."""
  def __init__(self, resistance: RangeLike):
    super().__init__()
    self.gnd = self.Port(Ground.empty(), [Common])
    self.io = self.Port(Vector(DigitalSource.empty()), [InOut])
    self.generator_param(self.io.requested())
    self.resistance = self.ArgParameter(resistance)

  def generate(self) -> None:
    super().generate()
    self.res = ElementDict[PulldownResistor]()
    for requested in self.get(self.io.requested()):
      res = self.res[requested] = self.Block(PulldownResistor(self.resistance))
      self.connect(self.gnd, res.gnd)
      self.connect(self.io.append_elt(DigitalSource.empty(), requested), res.io)


class SeriesPowerResistor(DiscreteApplication, KiCadImportableBlock):
  """Series resistor for power applications"""
  def symbol_pinning(self, symbol_name: str) -> Mapping[str, BasePort]:
    assert symbol_name in ('Device:R', 'Device:R_Small')
    return {'1': self.pwr_in, '2': self.pwr_out}

  def __init__(self, resistance: RangeLike) -> None:
    super().__init__()

    self.resistance = self.ArgParameter(resistance)

    self.pwr_out = self.Port(VoltageSource.empty(), [Output])  # forward declaration
    self.pwr_in = self.Port(VoltageSink.empty(), [Power, Input])  # forward declaration
    current_draw = self.pwr_out.link().current_drawn.abs()

    self.res = self.Block(Resistor(
      resistance=self.resistance,
      power=current_draw * current_draw * self.resistance
    ))

    self.connect(self.pwr_in, self.res.a.adapt_to(VoltageSink(
      current_draw=self.pwr_out.link().current_drawn
    )))
    self.connect(self.pwr_out, self.res.b.adapt_to(VoltageSource(
      voltage_out=self.pwr_in.link().voltage,  # ignore voltage drop
    )))

    self.actual_power = self.Parameter(RangeExpr(current_draw * current_draw * self.res.actual_resistance))
    self.require(self.actual_power.within(self.res.actual_power_rating))
    self.actual_resistance = self.Parameter(RangeExpr(self.res.actual_resistance))

  def connected(self, pwr_in: Optional[Port[VoltageLink]] = None, pwr_out: Optional[Port[VoltageLink]] = None) -> \
      'SeriesPowerResistor':
    """Convenience function to connect both ports, returning this object so it can still be given a name."""
    if pwr_in is not None:
      cast(Block, builder.get_enclosing_block()).connect(pwr_in, self.pwr_in)
    if pwr_out is not None:
      cast(Block, builder.get_enclosing_block()).connect(pwr_out, self.pwr_out)
    return self


class CurrentSenseResistor(DiscreteApplication, KiCadImportableBlock, GeneratorBlock):
  """Current sense resistor with a power passthrough resistor and positive and negative sense temrinals."""
  def __init__(self, resistance: RangeLike, sense_in_reqd: BoolLike = True) -> None:
    super().__init__()

    self.res = self.Block(SeriesPowerResistor(resistance))
    self.pwr_in = self.Export(self.res.pwr_in, [Input])
    self.pwr_out = self.Export(self.res.pwr_out, [Output])

    self.sense_in = self.Port(AnalogSource.empty(), optional=True)
    self.sense_out = self.Port(AnalogSource.empty())

    # in some cases, the input rail may be the sense reference and this connection is optional
    # but this must be an explicit opt-in
    sense_in_reqd_param = self.ArgParameter(sense_in_reqd)
    self.require(sense_in_reqd_param.implies(self.sense_in.is_connected()))

    self.generator_param(self.sense_in.is_connected())

    self.actual_resistance = self.Parameter(RangeExpr(self.res.actual_resistance))

  def generate(self) -> None:
    super().generate()

    if self.get(self.sense_in.is_connected()):
      self.connect(self.pwr_in.as_analog_source(), self.sense_in)
    self.connect(self.res.pwr_out.as_analog_source(), self.sense_out)

  def connected(self, pwr_in: Optional[Port[VoltageLink]] = None, pwr_out: Optional[Port[VoltageLink]] = None) -> \
      'CurrentSenseResistor':
    """Convenience function to connect both ports, returning this object so it can still be given a name."""
    if pwr_in is not None:
      cast(Block, builder.get_enclosing_block()).connect(pwr_in, self.pwr_in)
    if pwr_out is not None:
      cast(Block, builder.get_enclosing_block()).connect(pwr_out, self.pwr_out)
    return self

  def symbol_pinning(self, symbol_name: str) -> Dict[str, Port]:
    assert symbol_name == 'edg_importable:CurrentSenseResistor'
    return {'1': self.pwr_in, '2': self.pwr_out, 'sense_in': self.sense_in, 'sense_out': self.sense_out}


class AnalogClampResistor(Protection, KiCadImportableBlock):
  """Inline resistor that limits the current (to a parameterized amount) which works in concert
  with ESD diodes in the downstream device to clamp the signal voltage to allowable levels.

  The protection voltage can be extended beyond the modeled range from the input signal,
  and can also be specified to allow zero output voltage (for when the downstream device
  is powered down)

  TODO: clamp_target should be inferred from the target voltage_limits,
  but voltage_limits doesn't always get propagated"""
  def __init__(self, clamp_target: RangeLike = (0, 3)*Volt, clamp_current: RangeLike = (0.25, 2.5)*mAmp,
               protection_voltage: RangeLike = (0, 0)*Volt, zero_out: BoolLike = False):
    super().__init__()

    self.signal_in = self.Port(AnalogSink.empty(), [Input])
    self.signal_out = self.Port(AnalogSource.empty(), [Output])

    self.clamp_target = self.ArgParameter(clamp_target)
    self.clamp_current = self.ArgParameter(clamp_current)
    self.protection_voltage = self.ArgParameter(protection_voltage)
    self.zero_out = self.ArgParameter(zero_out)

  def contents(self) -> None:
    super().contents()

    # TODO bidirectional clamping calcs?
    self.res = self.Block(Resistor(resistance=1/self.clamp_current * self.zero_out.then_else(
      self.signal_in.link().voltage.hull(self.protection_voltage).upper(),
      self.signal_in.link().voltage.hull(self.protection_voltage).upper() - self.clamp_target.upper(),
    )))
    self.connect(self.res.a.adapt_to(AnalogSink()), self.signal_in)
    self.connect(self.res.b.adapt_to(AnalogSource(
      voltage_out=self.signal_in.link().voltage.intersect(self.clamp_target),
      signal_out=self.signal_in.link().signal,
      impedance=self.signal_in.link().source_impedance + self.res.actual_resistance
    )), self.signal_out)

  def symbol_pinning(self, symbol_name: str) -> Dict[str, Port]:
    assert symbol_name == 'Device:R'
    return {'1': self.signal_in, '2': self.signal_out}


class DigitalClampResistor(Protection, KiCadImportableBlock):
  """Inline resistor that limits the current (to a parameterized amount) which works in concert
  with ESD diodes in the downstream device to clamp the signal voltage to allowable levels.

  The protection voltage can be extended beyond the modeled range from the input signal,
  and can also be specified to allow zero output voltage (for when the downstream device
  is powered down)

  TODO: clamp_target should be inferred from the target voltage_limits,
  but voltage_limits doesn't always get propagated."""
  def __init__(self, clamp_target: RangeLike = (0, 3)*Volt, clamp_current: RangeLike = (1.0, 10)*mAmp,
               protection_voltage: RangeLike = (0, 0)*Volt, zero_out: BoolLike = False):
    super().__init__()

    self.signal_in = self.Port(DigitalSink.empty(), [Input])
    self.signal_out = self.Port(DigitalSource.empty(), [Output])

    self.clamp_target = self.ArgParameter(clamp_target)
    self.clamp_current = self.ArgParameter(clamp_current)
    self.protection_voltage = self.ArgParameter(protection_voltage)
    self.zero_out = self.ArgParameter(zero_out)

  def contents(self) -> None:
    super().contents()

    # TODO bidirectional clamping calcs?
    self.res = self.Block(Resistor(resistance=1/self.clamp_current * self.zero_out.then_else(
      self.signal_in.link().voltage.hull(self.protection_voltage).upper(),
      self.signal_in.link().voltage.hull(self.protection_voltage).upper() - self.clamp_target.upper(),
      )))
    self.connect(self.res.a.adapt_to(DigitalSink(current_draw=self.signal_out.link().current_drawn)), self.signal_in)
    self.connect(self.res.b.adapt_to(DigitalSource(
      voltage_out=self.signal_in.link().voltage.intersect(self.clamp_target),
      output_thresholds=self.signal_in.link().output_thresholds
    )), self.signal_out)

  def symbol_pinning(self, symbol_name: str) -> Dict[str, Port]:
    assert symbol_name == 'Device:R'
    return {'1': self.signal_in, '2': self.signal_out}
