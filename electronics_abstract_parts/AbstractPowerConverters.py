from typing import Optional
from electronics_model import *
from .Categories import *
from .AbstractCapacitor import DecouplingCapacitor
from .AbstractInductor import Inductor


@abstract_block_default(lambda: IdealVoltageRegulator)
class VoltageRegulator(PowerConditioner):
  """Base class for all DC-DC voltage regulators with shared ground (non-isolated).
  Can produce an output voltage lower than, equal to, or greater than its input voltage."""
  @init_in_parent
  def __init__(self, output_voltage: RangeLike) -> None:
    super().__init__()

    self.output_voltage = self.ArgParameter(output_voltage)

    self.pwr_in = self.Port(VoltageSink.empty(), [Power, Input])
    self.pwr_out = self.Port(VoltageSource.empty(), [Output])
    self.gnd = self.Port(Ground.empty(), [Common])

  def contents(self):
    super().contents()

    self.description = DescriptionString(
      "<b>output voltage:</b> ", DescriptionString.FormatUnits(self.pwr_out.voltage_out, "V"),
      " <b>of spec:</b> ", DescriptionString.FormatUnits(self.output_voltage, "V"), "\n",
      "<b>input voltage:</b> ", DescriptionString.FormatUnits(self.pwr_in.link().voltage, "V")
    )

    self.require(self.pwr_out.voltage_out.within(self.output_voltage),
                 "Output voltage must be within spec")


@abstract_block_default(lambda: IdealLinearRegulator)
class LinearRegulator(VoltageRegulator):
  """Linear regulator, including supporting components in application circuit like capacitors if needed"""


class IdealLinearRegulator(LinearRegulator, IdealModel):
  """Ideal linear regulator, draws the output current and produces spec output voltage limited by input voltage"""
  def contents(self):
    super().contents()
    effective_output_voltage = self.output_voltage.intersect((0, self.pwr_in.link().voltage.upper()))
    self.pwr_in.init_from(VoltageSink(
      current_draw=self.pwr_out.link().current_drawn))
    self.pwr_out.init_from(VoltageSource(
      voltage_out=effective_output_voltage))
    self.gnd.init_from(Ground())


@non_library
class LinearRegulatorDevice(Block):
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
class SwitchingVoltageRegulator(VoltageRegulator):
  @staticmethod
  def _calculate_ripple(output_current: RangeLike, ripple_ratio: RangeLike, *,
                        rated_current: Optional[FloatLike] = None) -> RangeExpr:
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
      # this fallback limit is an arbitrary and low 0.2, not tied to specified ripple ratio since
      # it leads to unintuitive behavior where as the low bound increases (range shrinks) the inductance
      # spec actually becomes larger
      upper_ripple_limit = upper_ripple_limit.max(0.2 * rated_current)
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


@abstract_block_default(lambda: IdealBuckConverter)
class BuckConverter(SwitchingVoltageRegulator):
  """Step-down switching converter"""
  def __init__(self, *args, ripple_current_factor: RangeLike = (0.2, 0.5), **kwargs) -> None:
    # TODO default ripple is very heuristic, intended 0.3-0.4, loosely adjusted for inductor tolerance
    super().__init__(*args, ripple_current_factor=ripple_current_factor, **kwargs)
    self.require(self.pwr_out.voltage_out.upper() <= self.pwr_in.voltage_limits.upper())


@abstract_block_default(lambda: IdealBuckConverter)
class DiscreteBuckConverter(BuckConverter):
  """Category for discrete buck converter subcircuits (as opposed to integrated components)"""


class IdealBuckConverter(DiscreteBuckConverter, IdealModel):
  """Ideal buck converter producing the spec output voltage (buck-boost) limited by input voltage
  and drawing input current from conversation of power"""
  def contents(self):
    super().contents()
    effective_output_voltage = self.output_voltage.intersect((0, self.pwr_in.link().voltage.upper()))
    self.pwr_in.init_from(VoltageSink(
      current_draw=effective_output_voltage / self.pwr_in.link().voltage * self.pwr_out.link().current_drawn))
    self.pwr_out.init_from(VoltageSource(
      voltage_out=effective_output_voltage))
    self.gnd.init_from(Ground())


class BuckConverterPowerPath(InternalSubcircuit, GeneratorBlock):
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
               dutycycle_limit: RangeLike = Default((0.1, 0.9)),
               inductor_scale: IntLike = Default(1)):  # arbitrary
    super().__init__()

    self.pwr_in = self.Port(VoltageSink.empty(), [Power])  # models the input cap only
    self.pwr_out = self.Port(VoltageSource.empty())  # models the output cap and inductor power source
    self.switch = self.Port(VoltageSink.empty())  # current draw defined as average
    self.gnd = self.Port(Ground.empty(), [Common])

    self.output_voltage = self.ArgParameter(output_voltage)
    self.current_limits = self.ArgParameter(current_limits)
    self.dutycycle_limit = self.ArgParameter(dutycycle_limit)
    self.output_current = self.ArgParameter(output_current)
    self.inductor_current_ripple = self.ArgParameter(inductor_current_ripple)

    self.actual_dutycycle = self.Parameter(RangeExpr())
    self.actual_inductor_current_ripple = self.Parameter(RangeExpr())
    self.peak_current = self.Parameter(FloatExpr())  # peak (non-averaged) current draw from switch pin

    self.generator(self.generate_passives, input_voltage, output_voltage, frequency, output_current,
                   inductor_current_ripple, efficiency,
                   input_voltage_ripple, output_voltage_ripple, dutycycle_limit,
                   inductor_scale)

  def contents(self):
    super().contents()

    self.description = DescriptionString(
      "<b>duty cycle:</b> ", DescriptionString.FormatUnits(self.actual_dutycycle, ""),
      " <b>of limits:</b> ", DescriptionString.FormatUnits(self.dutycycle_limit, ""), "\n",
      "<b>peak switching current:</b> ", DescriptionString.FormatUnits(self.peak_current, "A"),
      " (<b>output operating avg:</b> ", DescriptionString.FormatUnits(self.output_current, "A"),
      ", <b>ripple spec:</b> ", DescriptionString.FormatUnits(self.inductor_current_ripple, "A"), ")"
    )

  @staticmethod
  def max_d_inverse_d(d_range: Range) -> float:
    """Some power calculations require the maximum of D*(1-D), which has a maximum at D=0.5"""
    if 0.5 in d_range:
      return 0.5 * (1 - 0.5)
    elif d_range.lower > 0.5:
      return d_range.lower * (1 - d_range.lower)
    elif d_range.upper < 0.5:
      return d_range.upper * (1 - d_range.upper)
    else:
      raise Exception(f"unexpected D range {d_range}")

  def generate_passives(self, input_voltage: Range, output_voltage: Range, frequency: Range,
                        output_current: Range, inductor_current_ripple: Range,
                        efficiency: Range,
                        input_voltage_ripple: float, output_voltage_ripple: float,
                        dutycycle_limit: Range, inductor_scale: int) -> None:
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
      inductance=(inductance_min/inductor_scale, inductance_max/inductor_scale)*Henry,
      current=(0, self.peak_current),
      frequency=frequency*Hertz
    ))

    actual_ripple_min = (output_voltage.lower * (input_voltage.upper - output_voltage.lower) /
                         (self.inductor.actual_inductance.upper() * frequency.lower * input_voltage.upper))
    actual_ripple_max = (output_voltage.lower * (input_voltage.upper - output_voltage.lower) /
                         (self.inductor.actual_inductance.lower() * frequency.lower * input_voltage.upper))
    self.assign(self.actual_inductor_current_ripple, (actual_ripple_min, actual_ripple_max))

    self.connect(self.switch, self.inductor.a.adapt_to(VoltageSink(
      voltage_limits=RangeExpr.ALL,
      current_draw=self.pwr_out.link().current_drawn*dutycycle
    )))
    self.connect(self.pwr_out, self.inductor.b.adapt_to(VoltageSource(
      voltage_out=self.output_voltage,
      current_limits=(0, self.current_limits.intersect(self.inductor.actual_current_rating).upper() -
                      (self.actual_inductor_current_ripple.upper() / 2))
    )))

    input_capacitance = Range.from_lower(output_current.upper * self.max_d_inverse_d(effective_dutycycle) /
                                         (frequency.lower * input_voltage_ripple))
    self.in_cap = self.Block(DecouplingCapacitor(
      capacitance=input_capacitance*Farad,
    )).connected(self.gnd, self.pwr_in)
    # TODO size based on transient response, add to voltage tolerance stackups
    output_capacitance = Range.from_lower(inductor_current_ripple.upper /
                                          (8 * frequency.lower * output_voltage_ripple))
    self.out_cap = self.Block(DecouplingCapacitor(
      capacitance=output_capacitance*Farad,
    )).connected(self.gnd, self.pwr_out)


@abstract_block_default(lambda: IdealBoostConverter)
class BoostConverter(SwitchingVoltageRegulator):
  """Step-up switching converter"""
  def __init__(self, *args, ripple_current_factor: RangeLike = Default((0.2, 0.5)), **kwargs) -> None:
    # TODO default ripple is very heuristic, intended 0.3-0.4, loosely adjusted for inductor tolerance
    super().__init__(*args, ripple_current_factor=ripple_current_factor, **kwargs)
    self.require(self.pwr_out.voltage_out.lower() >= self.pwr_in.voltage_limits.lower())


@abstract_block_default(lambda: IdealBoostConverter)
class DiscreteBoostConverter(BoostConverter):
  """Category for discrete boost converter subcircuits (as opposed to integrated components)"""


class IdealBoostConverter(DiscreteBoostConverter, IdealModel):
  """Ideal boost converter producing the spec output voltage (buck-boost) limited by input voltage
  and drawing input current from conversation of power"""
  def contents(self):
    super().contents()
    effective_output_voltage = self.output_voltage.intersect((self.pwr_in.link().voltage.lower(), float('inf')))
    self.pwr_in.init_from(VoltageSink(
      current_draw=effective_output_voltage / self.pwr_in.link().voltage * self.pwr_out.link().current_drawn))
    self.pwr_out.init_from(VoltageSource(
      voltage_out=effective_output_voltage))
    self.gnd.init_from(Ground())


class BoostConverterPowerPath(InternalSubcircuit, GeneratorBlock):
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

    self.pwr_in = self.Port(VoltageSink.empty(), [Power])  # models input cap and inductor power draw
    self.pwr_out = self.Port(VoltageSink.empty())  # only used for the output cap
    self.switch = self.Port(VoltageSource.empty())  # current draw defined as average
    self.gnd = self.Port(Ground.empty(), [Common])

    self.output_voltage = self.ArgParameter(output_voltage)
    self.current_limits = self.ArgParameter(current_limits)
    self.dutycycle_limit = self.ArgParameter(dutycycle_limit)
    self.output_current = self.ArgParameter(output_current)
    self.inductor_current_ripple = self.ArgParameter(inductor_current_ripple)

    self.actual_dutycycle = self.Parameter(RangeExpr())
    self.actual_inductor_current_ripple = self.Parameter(RangeExpr())
    self.peak_current = self.Parameter(FloatExpr())  # peak (non-averaged) current draw from switch pin

    self.generator(self.generate_passives, input_voltage, output_voltage, frequency, output_current,
                   inductor_current_ripple, efficiency,
                   input_voltage_ripple, output_voltage_ripple, dutycycle_limit)

  def contents(self):
    super().contents()

    self.description = DescriptionString(
      "<b>duty cycle:</b> ", DescriptionString.FormatUnits(self.actual_dutycycle, ""),
      " <b>of limits:</b> ", DescriptionString.FormatUnits(self.dutycycle_limit, ""), "\n",
      "<b>peak switching current:</b> ", DescriptionString.FormatUnits(self.peak_current, "A"),
      " (<b>output operating avg:</b> ", DescriptionString.FormatUnits(self.output_current, "A"),
      ", <b>ripple spec:</b> ", DescriptionString.FormatUnits(self.inductor_current_ripple, "A"), ")"
    )

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

    actual_ripple_min = (input_voltage.lower * (output_voltage.upper - input_voltage.lower) /
                         (self.inductor.actual_inductance.upper() * frequency.lower * output_voltage.lower))
    actual_ripple_max = (input_voltage.lower * (output_voltage.upper - input_voltage.lower) /
                         (self.inductor.actual_inductance.lower() * frequency.lower * output_voltage.lower))
    self.assign(self.actual_inductor_current_ripple, (actual_ripple_min, actual_ripple_max))

    self.connect(self.pwr_in, self.inductor.a.adapt_to(VoltageSink(
      voltage_limits=RangeExpr.ALL,
      current_draw=self.pwr_out.link().current_drawn / (1 - effective_dutycycle)
    )))
    self.connect(self.switch, self.inductor.b.adapt_to(VoltageSource(
      voltage_out=self.output_voltage,
      current_limits=(0, self.current_limits.intersect(self.inductor.actual_current_rating).upper() -
                      (self.actual_inductor_current_ripple.upper() / 2))
    )))

    # Capacitor equation Q = CV => i = C dv/dt => for constant current, i * t = C dV => dV = i * t / C
    # C = i * t / dV => C = i / (f * dV)
    # Boost converter draws current from input throughout the entire cycle, and by conversation of power
    # the average input current is Iin = Vout/Vin * Iout = 1/(1-D) * Iout
    # Boost converter current should be much less spikey than buck converter current and probably
    # less filtering than this is acceptable
    input_capacitance = Range.from_lower((output_current.upper / (1 - effective_dutycycle.upper)) /
                                         (frequency.lower * input_voltage_ripple))
    self.in_cap = self.Block(DecouplingCapacitor(
      capacitance=input_capacitance*Farad,
    )).connected(self.gnd, self.pwr_in)
    output_capacitance = Range.from_lower(output_current.upper * effective_dutycycle.upper /
                                          (frequency.lower * output_voltage_ripple))
    self.out_cap = self.Block(DecouplingCapacitor(
      capacitance=output_capacitance*Farad,
    )).connected(self.gnd, self.pwr_out)


@abstract_block_default(lambda: IdealVoltageRegulator)
class BuckBoostConverter(SwitchingVoltageRegulator):
  """Step-up or switch-down switching converter"""
  def __init__(self, *args, ripple_current_factor: RangeLike = Default((0.2, 0.5)), **kwargs) -> None:
    # TODO default ripple is very heuristic, intended 0.3-0.4, loosely adjusted for inductor tolerance
    super().__init__(*args, ripple_current_factor=ripple_current_factor, **kwargs)


@abstract_block_default(lambda: IdealVoltageRegulator)
class DiscreteBuckBoostConverter(BuckBoostConverter):
  """Category for discrete buck-boost converter subcircuits (as opposed to integrated components)"""


class IdealVoltageRegulator(DiscreteBuckBoostConverter, IdealModel):
  """Ideal buck-boost / general DC-DC converter producing the spec output voltage
  and drawing input current from conversation of power"""
  def contents(self):
    super().contents()
    self.pwr_in.init_from(VoltageSink(
      current_draw=self.output_voltage / self.pwr_in.link().voltage * self.pwr_out.link().current_drawn))
    self.pwr_out.init_from(VoltageSource(
      voltage_out=self.output_voltage))
    self.gnd.init_from(Ground())


class BuckBoostConverterPowerPath(InternalSubcircuit, GeneratorBlock):
  """A helper block to generate the power path (inductors, capacitors) for a 4-switch buck-boost converter.

  Main assumptions in component sizing
  - Operating only in continuous mode, TODO: also consider boundary and discontinuous mode
  - TODO: account for capacitor ESR?

  Useful resources:
  https://www.ti.com/lit/an/slva535b/slva535b.pdf
    Largely based on this document, the tl;dr of which is combine the buck and boost equations
  """
  @init_in_parent
  def __init__(self, input_voltage: RangeLike, output_voltage: RangeLike, frequency: RangeLike,
               output_current: RangeLike, inductor_current_ripple: RangeLike, *,
               efficiency: RangeLike = Default((0.8, 1.0)),  # from TI reference
               input_voltage_ripple: FloatLike = Default(75*mVolt),
               output_voltage_ripple: FloatLike = Default(25*mVolt)):  # arbitrary
    super().__init__()

    self.pwr_in = self.Port(VoltageSink.empty(), [Power])  # connected to the input cap, models input current
    self.switch_in = self.Port(VoltageSink.empty())  # models input high and low switch current draws
    self.switch_out = self.Port(VoltageSink.empty())  # models output high and low switch current draws
    self.pwr_out = self.Port(VoltageSink.empty())  # only used for the output cap
    self.gnd = self.Port(Ground.empty(), [Common])

    self.output_voltage = self.ArgParameter(output_voltage)
    self.output_current = self.ArgParameter(output_current)
    self.inductor_current_ripple = self.ArgParameter(inductor_current_ripple)
    # duty cycle limits not supported, since the crossover point has a dutycycle of 0 (boost) and 1 (buck)

    self.buck_dutycycle = self.Parameter(RangeExpr())  # possible actual duty cycle in buck mode
    self.boost_dutycycle = self.Parameter(RangeExpr())  # possible actual duty cycle in boost mode
    self.peak_current = self.Parameter(FloatExpr())  # peak (non-averaged) current draw through any switch

    self.generator(self.generate_passives, input_voltage, output_voltage, frequency, output_current,
                   inductor_current_ripple, efficiency,
                   input_voltage_ripple, output_voltage_ripple)

  def contents(self):
    super().contents()

    self.description = DescriptionString(
      "<b>duty cycle:</b> ", DescriptionString.FormatUnits(self.buck_dutycycle, ""), " (buck)",
      ", ", DescriptionString.FormatUnits(self.boost_dutycycle, ""), " (boost)\n",
      "<b>peak switching current:</b> ", DescriptionString.FormatUnits(self.peak_current, "A"),
      " (<b>output operating avg:</b> ", DescriptionString.FormatUnits(self.output_current, "A"),
      ", <b>ripple spec:</b> ", DescriptionString.FormatUnits(self.inductor_current_ripple, "A"), ")"
    )

  def generate_passives(self, input_voltage: Range, output_voltage: Range, frequency: Range,
                        output_current: Range, inductor_current_ripple: Range,
                        efficiency: Range,
                        input_voltage_ripple: float, output_voltage_ripple: float) -> None:
    # clip each mode's duty cycle to that mode's operating range
    buck_dutycycle = (output_voltage / input_voltage / efficiency).bound_to(Range(-float('inf'), 1))
    self.assign(self.buck_dutycycle, buck_dutycycle)
    boost_dutycycle = (1 - input_voltage / output_voltage * efficiency).bound_to(Range(0, float('inf')))
    self.assign(self.boost_dutycycle, boost_dutycycle)

    # Calculate minimum inductance based on worst case values (operating range corners producing maximum inductance)
    # This range must be constructed manually to not double-count the tolerance stackup of the voltages
    buck_inductance_min = (output_voltage.lower * (input_voltage.upper - output_voltage.lower) /
                      (inductor_current_ripple.upper * frequency.lower * input_voltage.upper))
    buck_inductance_max = (output_voltage.lower * (input_voltage.upper - output_voltage.lower) /
                      (inductor_current_ripple.lower * frequency.lower * input_voltage.upper))
    min_current = max(0, output_current.lower - inductor_current_ripple.upper / 2)  # applies to both modes
    buck_peak_current = output_current.upper + inductor_current_ripple.upper / 2
    boost_inductance_min = (input_voltage.lower * (output_voltage.upper - input_voltage.lower) /
                      (inductor_current_ripple.upper * frequency.lower * output_voltage.lower))
    boost_inductance_max = (input_voltage.lower * (output_voltage.upper - input_voltage.lower) /
                      (inductor_current_ripple.lower * frequency.lower * output_voltage.lower))
    boost_peak_current = output_current.upper / (1 - boost_dutycycle.upper) + inductor_current_ripple.upper / 2
    peak_current = max(buck_peak_current, boost_peak_current)
    self.assign(self.peak_current, peak_current)

    inductance_min = max(buck_inductance_min, boost_inductance_min)
    inductance_max = min(buck_inductance_max, boost_inductance_max)
    self.inductor = self.Block(Inductor(
      inductance=(inductance_min, inductance_max)*Henry,
      current=(0, self.peak_current),
      frequency=frequency*Hertz
    ))
    self.connect(self.switch_in, self.inductor.a.adapt_to(VoltageSink(
      voltage_limits=RangeExpr.ALL,
      current_draw=(min_current, peak_current)  # peak currents
    )))
    self.connect(self.switch_out, self.inductor.b.adapt_to(VoltageSink(
      voltage_limits=RangeExpr.ALL,
      current_draw=(-peak_current, -min_current)  # peak currents, flowing out
    )))

    input_buck_min_cap = (output_current.upper * BuckConverterPowerPath.max_d_inverse_d(buck_dutycycle) /
                          (frequency.lower * input_voltage_ripple))
    input_boost_min_cap = ((output_current.upper / (1 - boost_dutycycle.upper)) /
                           (frequency.lower * input_voltage_ripple))
    self.in_cap = self.Block(DecouplingCapacitor(
      capacitance=Range.from_lower(max(input_buck_min_cap, input_boost_min_cap))*Farad,
    )).connected(self.gnd, self.pwr_in)

    # calculated with steady-state ripple
    output_buck_min_cap = inductor_current_ripple.upper / (8 * frequency.lower * output_voltage_ripple)
    output_boost_min_cap = output_current.upper * boost_dutycycle.upper / (frequency.lower * output_voltage_ripple)
    self.out_cap = self.Block(DecouplingCapacitor(
      capacitance=Range.from_lower(max(output_buck_min_cap, output_boost_min_cap))*Farad,
    )).connected(self.gnd, self.pwr_out)
