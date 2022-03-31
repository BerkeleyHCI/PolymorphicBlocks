from typing import Optional
from electronics_model import *
from .Categories import *
from .AbstractPassives import Inductor, DecouplingCapacitor


@abstract_block
class DcDcConverter(PowerConditioner):
  """Base class for all DC-DC converters with shared ground (non-isoalted)."""
  @init_in_parent
  def __init__(self, output_voltage: RangeLike) -> None:
    super().__init__()

    self.output_voltage = self.ArgParameter(output_voltage)

    self.pwr_in = self.Port(VoltageSink.empty(), [Power, Input])
    self.pwr_out = self.Port(VoltageSource.empty(), [Output])
    self.gnd = self.Port(Ground.empty(), [Common])

    self.require(self.pwr_out.voltage_out.within(self.output_voltage),
                 "Output voltage must be within spec")


@abstract_block
class LinearRegulator(DcDcConverter):
  """Application circuit, inclulding supporting components like capacitors if needed,
  around a linear regulator step-down converter."""


@abstract_block
class LinearRegulatorDevice(DiscreteChip):
  """Abstract base class that provides a default model with common functionality for a linear regulator chip.
  Does not include supporting components like capacitors.
  """
  @init_in_parent
  def __init__(self) -> None:
    super().__init__()

    # these device model parameters must be provided by subtypes
    self.actual_dropout = self.Parameter(RangeExpr())
    self.actual_quiescent_current = self.Parameter(RangeExpr())
    self.actual_target_voltage = self.Parameter(RangeExpr())

    self.pwr_in = self.Port(VoltageSink(
      voltage_limits=RangeExpr(),
      current_draw=RangeExpr()
    ), [Power, Input])
    # dropout voltage is modeled to expand the tolerance range for actual output voltage
    self.pwr_out = self.Port(VoltageSource(
      voltage_out=(  # bounds are lowest of the target voltage or dropout voltage
        self.actual_target_voltage.lower().min(self.pwr_in.link().voltage.lower() - self.actual_dropout.upper()),
        self.actual_target_voltage.upper().min(self.pwr_in.link().voltage.upper() - self.actual_dropout.lower()),
      ),
      current_limits=RangeExpr()
    ), [Output])
    self.gnd = self.Port(Ground(), [Common])

    self.assign(self.pwr_in.current_draw,
                self.pwr_out.link().current_drawn + self.actual_quiescent_current)


@abstract_block
class DcDcSwitchingConverter(DcDcConverter):
  @staticmethod
  def _calculate_ripple(output_current: RangeLike, *, rated_current: Optional[FloatLike] = None,
                        ripple_ratio: RangeLike = Default((0.2, 0.5))) -> RangeExpr:
    """
    Calculates the target inductor ripple current (with parameters - concrete values not necessary)
    given the output current draw, and optionally a non-default ripple ratio and rated current.

    In general, ripple current largely trades off inductor maximum current and inductance.

    The default ripple ratio is an expansion of the heuristic 0.3-0.4 to account for tolerancing.
    the rated current is used to set a reasonable ceiling for ripple current, when the actual current
    is very low. Per the LMR33630 datasheet, the device's rated current should be used in these cases.
    """
    output_current_range = RangeExpr._to_expr_type(output_current)
    ripple_ratio_range = RangeExpr._to_expr_type(ripple_ratio)
    upper_ripple_limit = ripple_ratio_range.upper() * output_current_range.upper()
    if rated_current is not None:  # if rated current is specified, extend the upper limit for small current draws
      upper_ripple_limit = upper_ripple_limit.max(ripple_ratio_range.lower() * rated_current)
    return RangeExpr._to_expr_type((
      ripple_ratio_range.lower() * output_current_range.upper(),
      upper_ripple_limit))

  @init_in_parent
  def __init__(self, *args, ripple_current_factor: RangeLike,
               input_ripple_limit: FloatLike = Default(75 * mVolt),
               output_ripple_limit: FloatLike = Default(25 * mVolt),
               **kwargs) -> None:
    """https://www.ti.com/lit/an/slta055/slta055.pdf: recommends 75mV for maximum peak-peak ripple voltage
    """
    super().__init__(*args, **kwargs)

    self.ripple_current_factor = self.ArgParameter(ripple_current_factor)
    self.input_ripple_limit = self.ArgParameter(input_ripple_limit)
    self.output_ripple_limit = self.ArgParameter(output_ripple_limit)

    self.frequency = self.Parameter(RangeExpr())

@abstract_block
class BuckConverter(DcDcSwitchingConverter):
  """Step-down switching converter"""
  def __init__(self, *args, ripple_current_factor: RangeLike = (0.2, 0.5), **kwargs) -> None:
    # TODO default ripple is very heuristic, intended 0.3-0.4, loosely adjusted for inductor tolerance
    # TODO can this be integrated with some kind of AbstractDcDcConverter?
    super().__init__(*args, ripple_current_factor=ripple_current_factor, **kwargs)

    self.require(self.pwr_out.voltage_out.upper() <= self.pwr_in.voltage_limits.upper())


class BuckConverterPowerPath(GeneratorBlock):
  """A helper block to generate the power path (inductors, capacitors) for a switching buck converter.

  Main assumptions in component sizing:
  - Operating only in continuous mode, TODO: also consider boundary and discontinuous mode
  - TODO: account for capacitor ESR?

  Useful resources:
  https://www.ti.com/lit/an/slva477b/slva477b.pdf
    Component sizing in continuous mode
    Listed references go into more detail
  http://www.onmyphd.com/?p=voltage.regulators.buck.step.down.converter
    Very detailed analysis including component sizing, operating modes, calculating losses
  """
  @init_in_parent
  def __init__(self, input_voltage: RangeLike, output_voltage: RangeLike, frequency: RangeLike,
               output_current: RangeLike, current_limits: RangeLike, inductor_current_ripple: RangeLike, *,
               efficiency: RangeLike = Default((0.9, 1.0)),  # from TI reference
               input_voltage_ripple: FloatLike = Default(75*mVolt),
               output_voltage_ripple: FloatLike = Default(25*mVolt),
               dutycycle_limit: RangeLike = Default((0.1, 0.9))):  # arbitrary
    super().__init__()

    self.pwr_in = self.Port(VoltageSink(), [Power])  # models the input cap only
    self.pwr_out = self.Port(VoltageSource())  # models the output cap and inductor power source
    self.switch = self.Port(VoltageSink())  # current draw defined as average
    self.gnd = self.Port(Ground(), [Common])

    self.output_voltage = output_voltage
    self.current_limits = current_limits

    self.actual_dutycycle = self.Parameter(RangeExpr())
    self.peak_current = self.Parameter(FloatExpr())  # peak (non-averaged) current draw from switch pin

    self.generator(self.generate_passives, input_voltage, output_voltage, frequency, output_current,
                   inductor_current_ripple, efficiency,
                   input_voltage_ripple, output_voltage_ripple, dutycycle_limit)

  def generate_passives(self, input_voltage: Range, output_voltage: Range, frequency: Range,
                        output_current: Range, inductor_current_ripple: Range,
                        efficiency: Range,
                        input_voltage_ripple: float, output_voltage_ripple: float,
                        dutycycle_limit: Range) -> None:
    dutycycle = output_voltage / input_voltage / efficiency
    self.assign(self.actual_dutycycle, dutycycle)
    # if these are violated, these generally mean that the converter will start tracking the input
    # these can (maybe?) be waived if tracking (plus losses) is acceptable
    self.require(self.actual_dutycycle.within(dutycycle_limit), f"dutycycle {dutycycle} outside limit {dutycycle_limit}")
    # these are actual numbers to be used in calculations, accounting for tracking behavior
    effective_dutycycle = dutycycle.bound_to(dutycycle_limit)

    # calculate minimum inductance based on worst case values (operating range corners producing maximum inductance)
    # this range must be constructed manually to not double-count the tolerance stackup of the voltages
    inductance_min = (output_voltage.lower * (input_voltage.upper - output_voltage.lower) /
                      (inductor_current_ripple.upper * frequency.lower * input_voltage.upper))
    inductance_max = (output_voltage.lower * (input_voltage.upper - output_voltage.lower) /
                      (inductor_current_ripple.lower * frequency.lower * input_voltage.upper))
    self.assign(self.peak_current, output_current.upper + inductor_current_ripple.upper / 2)
    self.inductor = self.Block(Inductor(
      inductance=(inductance_min, inductance_max)*Henry,
      current=(0, self.peak_current),
      frequency=frequency*Hertz
    ))
    self.connect(self.switch, self.inductor.a.as_voltage_sink(
      voltage_limits=RangeExpr.ALL,
      current_draw=self.pwr_out.link().current_drawn*dutycycle))
    self.connect(self.pwr_out, self.inductor.b.as_voltage_source(
      voltage_out=self.output_voltage,
      current_limits=self.current_limits
    ))

    # TODO pick a single worst-case DC
    input_capacitance = Range.from_lower(output_current.upper * effective_dutycycle.upper * (1 - effective_dutycycle.lower) /
                                         (frequency.lower * input_voltage_ripple))
    self.in_cap = self.Block(DecouplingCapacitor(
      capacitance=input_capacitance*Farad,
    ))
    # TODO size based on transient response, add to voltage tolerance stackups
    output_capacitance = Range.from_lower(inductor_current_ripple.upper /
                                          (8 * frequency.lower * output_voltage_ripple))
    self.out_cap = self.Block(DecouplingCapacitor(
      capacitance=output_capacitance*Farad,
    ))
    self.connect(self.pwr_in, self.in_cap.pwr)
    self.connect(self.pwr_out, self.out_cap.pwr)
    self.connect(self.gnd, self.in_cap.gnd, self.out_cap.gnd)


@abstract_block
class DiscreteBuckConverter(BuckConverter):
  """Really more a category for discrete buck converter subcircuits (as opposed to integrated components)"""


@abstract_block
class BoostConverter(DcDcSwitchingConverter):
  """Step-up switching converter"""
  def __init__(self, *args, ripple_current_factor: RangeLike = Default((0.2, 0.5)), **kwargs) -> None:
    # TODO default ripple is very heuristic, intended 0.3-0.4, loosely adjusted for inductor tolerance
    # TODO can this be integrated with some kind of AbstractDcDcConverter?
    super().__init__(*args, ripple_current_factor=ripple_current_factor, **kwargs)
    self.require(self.pwr_out.voltage_out.lower() >= self.pwr_in.voltage_limits.lower())


class BoostConverterPowerPath(GeneratorBlock):
  """A helper block to generate the power path (inductors, capacitors) for a synchronous boost converter.

  Main assumptions in component sizing
  - Operating only in continuous mode, TODO: also consider boundary and discontinuous mode
  - TODO: account for capacitor ESR?

  Useful resources:
  https://www.ti.com/lit/an/slva372c/slva372c.pdf
    Component sizing in continuous mode
    Listed references go into more detail
  http://www.simonbramble.co.uk/dc_dc_converter_design/boost_converter/boost_converter_design.htm
    Detailed analysis of converter with discrete FET and diode
  """
  @init_in_parent
  def __init__(self, input_voltage: RangeLike, output_voltage: RangeLike, frequency: RangeLike,
               output_current: RangeLike, current_limits: RangeLike, inductor_current_ripple: RangeLike, *,
               efficiency: RangeLike = Default((0.8, 1.0)),  # from TI reference
               input_voltage_ripple: FloatLike = Default(75*mVolt),
               output_voltage_ripple: FloatLike = Default(25*mVolt),
               dutycycle_limit: RangeLike = Default((0.2, 0.85))):  # arbitrary
    super().__init__()

    self.pwr_in = self.Port(VoltageSink(), [Power])  # models input cap and inductor power draw
    self.pwr_out = self.Port(VoltageSink())  # only used for the output cap
    # TODO switch is a sink as far as dataflow directionality, but it's a voltage and current source
    self.switch = self.Port(VoltageSink())  # current draw defined as average
    self.gnd = self.Port(Ground(), [Common])

    self.output_voltage = output_voltage
    self.current_limits = current_limits

    self.actual_dutycycle = self.Parameter(RangeExpr())
    self.peak_current = self.Parameter(FloatExpr())  # peak (non-averaged) current draw from switch pin

    self.generator(self.generate_passives, input_voltage, output_voltage, frequency, output_current,
                   inductor_current_ripple, efficiency,
                   input_voltage_ripple, output_voltage_ripple, dutycycle_limit)

  def generate_passives(self, input_voltage: Range, output_voltage: Range, frequency: Range,
                        output_current: Range, inductor_current_ripple: Range,
                        efficiency: Range,
                        input_voltage_ripple: float, output_voltage_ripple: float,
                        dutycycle_limit: Range) -> None:
    dutycycle = 1 - input_voltage / output_voltage * efficiency
    self.assign(self.actual_dutycycle, dutycycle)
    # if these are violated, these generally mean that the converter will start tracking the input
    # these can (maybe?) be waived if tracking (plus losses) is acceptable
    self.require(self.actual_dutycycle.within(dutycycle_limit), f"dutycycle {dutycycle} outside limit {dutycycle_limit}")
    # these are actual numbers to be used in calculations
    effective_dutycycle = dutycycle.bound_to(dutycycle_limit)

    # Calculate minimum inductance based on worst case values (operating range corners producing maximum inductance)
    # This range must be constructed manually to not double-count the tolerance stackup of the voltages
    inductance_min = (input_voltage.lower * (output_voltage.upper - input_voltage.lower) /
                      (inductor_current_ripple.upper * frequency.lower * output_voltage.lower))
    inductance_max = (input_voltage.lower * (output_voltage.upper - input_voltage.lower) /
                      (inductor_current_ripple.lower * frequency.lower * output_voltage.lower))
    self.assign(self.peak_current,
                inductor_current_ripple.upper / 2 + output_current.upper / (1 - effective_dutycycle.upper))
    self.inductor = self.Block(Inductor(
      inductance=(inductance_min, inductance_max)*Henry,
      current=(0, self.peak_current),
      frequency=frequency*Hertz
    ))
    self.connect(self.pwr_in, self.inductor.a.as_voltage_sink(
      voltage_limits=RangeExpr.ALL,
      current_draw=self.pwr_out.link().current_drawn / (1 - effective_dutycycle)))
    self.connect(self.switch, self.inductor.b.as_voltage_sink(
      voltage_limits=RangeExpr.ALL,
      current_draw=self.pwr_out.link().current_drawn / (1 - effective_dutycycle)))

    input_capacitance = Range.from_lower((output_current.upper / effective_dutycycle.lower) * (1 - effective_dutycycle.lower) /
                                         (frequency.lower * input_voltage_ripple))
    self.in_cap = self.Block(DecouplingCapacitor(
      capacitance=input_capacitance*Farad,
    ))
    output_capacitance = Range.from_lower(output_current.upper * effective_dutycycle.upper /
                                          (frequency.lower * output_voltage_ripple))
    self.out_cap = self.Block(DecouplingCapacitor(
      capacitance=output_capacitance*Farad,
    ))
    self.connect(self.pwr_in, self.in_cap.pwr)
    self.connect(self.pwr_out, self.out_cap.pwr)
    self.connect(self.gnd, self.in_cap.gnd, self.out_cap.gnd)


@abstract_block
class DiscreteBoostConverter(BoostConverter):
  """Really more a category for discrete buck converter subcircuits (as opposed to integrated components)"""
