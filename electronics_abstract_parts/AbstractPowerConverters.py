from typing import cast
from electronics_model import *
from .Categories import *
from .AbstractPassives import Inductor, DecouplingCapacitor


@abstract_block
class DcDcConverter(PowerConditioner):
  """Base class for all DC-DC converters with shared ground (non-isoalted)."""
  @init_in_parent
  def __init__(self, output_voltage: RangeLike) -> None:
    super().__init__()

    self.output_voltage = output_voltage

    self.pwr_in = self.Port(VoltageSink(
      voltage_limits=RangeExpr(),
      current_draw=RangeExpr()
    ), [Power, Input])  # TODO mark as future-connected here?
    self.pwr_out = self.Port(VoltageSource(
      voltage_out=RangeExpr(),
      current_limits=RangeExpr()
    ), [Output])  # TODO mark as future-connected here?
    self.gnd = self.Port(Ground(), [Common])  # TODO mark as future-connected?

    self.require(self.pwr_out.voltage_out.within(self.output_voltage),
                   "Output voltage must be within spec")


@abstract_block
class LinearRegulator(DcDcConverter):
  @init_in_parent
  def __init__(self, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.dropout = self.Parameter(RangeExpr())
    self.quiescent_current = self.Parameter(RangeExpr())

    # TODO these constraints establish a theoretical bound, but allows (and demands) subtypes refine to exact values
    self.require(self.pwr_in.current_draw.within(self.pwr_out.link().current_drawn + self.quiescent_current + (0, 0.01)))  # TODO avoid fudge factor
    self.require(self.pwr_in.link().voltage.lower() >= self.pwr_out.link().voltage.upper() + self.dropout.upper())  # TODO more elegant?


@abstract_block
class DcDcSwitchingConverter(DcDcConverter):
  """https://www.ti.com/lit/an/slta055/slta055.pdf: recommends 75mV for maximum peak-peak ripple voltage
  """
  @init_in_parent
  def __init__(self, *args, ripple_current_factor: RangeLike,
               input_ripple_limit: FloatLike = Default(75 * mVolt),
               output_ripple_limit: FloatLike = Default(25 * mVolt),
               **kwargs) -> None:
    # TODO can this be integrated with some kind of AbstractDcDcConverter?
    super().__init__(*args, **kwargs)

    self.ripple_current_factor = cast(RangeExpr, ripple_current_factor)
    self.input_ripple_limit = cast(FloatExpr, input_ripple_limit)
    self.output_ripple_limit = cast(FloatExpr, output_ripple_limit)
    self.efficiency = self.Parameter(RangeExpr())

    self.require(self.pwr_in.current_draw.within((
      self.pwr_out.link().current_drawn * self.pwr_out.voltage_out / self.pwr_in.link().voltage / self.efficiency + (0, 0.01)  # TODO avoid fudge factor
    )))


@abstract_block
class BuckConverter(DcDcSwitchingConverter):
  """Step-down switching converter"""
  def __init__(self, *args, ripple_current_factor: RangeLike = (0.2, 0.5), **kwargs) -> None:
    # TODO default ripple is very heuristic, intended 0.3-0.4, loosely adjusted for inductor tolerance
    # TODO can this be integrated with some kind of AbstractDcDcConverter?
    super().__init__(*args, ripple_current_factor=ripple_current_factor, **kwargs)

    self.frequency = self.Parameter(RangeExpr())


class BuckConverterPowerPath(GeneratorBlock):
  """Provides a helper function to generate the power path for a switching buck converter.

  Heuristic for inductor ripple current is 0.3-0.4 of the output current.
  Per the LMR33630 datasheet, if the actual current is much lower, use the device's rated current.
  Ripple current largely trades off inductor maximum current and inductance.

  Useful resources:
  https://www.ti.com/lit/an/slva477b/slva477b.pdf
    Component sizing in continuous mode
    Listed references go into more detail
  http://www.onmyphd.com/?p=voltage.regulators.buck.step.down.converter
    Very detailed analysis including component sizing, operating modes, calculating losses
  """
  @init_in_parent
  def __init__(self, input_voltage: RangeLike, output_voltage: RangeLike, frequency: RangeLike,
               output_current: FloatLike, inductor_current_ripple: RangeLike, *,
               efficiency: RangeLike = Default((0.9, 1.0)),  # from TI reference
               input_voltage_ripple: FloatLike = Default(75*mVolt),
               output_voltage_ripple: FloatLike = Default(25*mVolt),
               dutycycle_limit: RangeLike = Default((0.1, 0.9))):  # arbitrary
    super().__init__()

    self.pwr_in = self.Port(VoltageSink())  # mainly used for the input capacitor
    self.pwr_out = self.Port(VoltageSource())  # source from the inductor
    self.switch = self.Port(VoltageSink())
    self.gnd = self.Port(Ground(), [Common])

    self.actual_dutycycle = self.Parameter(RangeExpr())

    self.generator(self.generate_passives, input_voltage, output_voltage, frequency, output_current,
                   inductor_current_ripple, efficiency,
                   input_voltage_ripple, output_voltage_ripple, dutycycle_limit)


  def generate_passives(self, input_voltage: Range, output_voltage: Range, frequency: Range,
                        output_current_max: float, inductor_current_ripple: Range,
                        efficiency: Range,
                        input_voltage_ripple: float, output_voltage_ripple: float,
                        dutycycle_limit: Range) -> None:
    """
    Sizes and generates the power stage passives (in and out filter caps, inductor).
    Main assumptions in component sizing:
    - Operating only in continuous mode
    - TODO: also consider boundary and discontinuous mode

    TODO support capacitor ESR calculation
    TODO unify rated max current with something else, perhaps a block param?
    """
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
    inductance = Range(inductance_min, inductance_max)

    # TODO size based on transient response, add to voltage tolerance stackups
    output_capacitance = Range.from_lower(inductor_current_ripple.upper /
                                          (8 * frequency.lower * output_voltage_ripple))
    # TODO pick a single worst-case DC
    input_capacitance = Range.from_lower(output_current_max * effective_dutycycle.upper * (1 - effective_dutycycle.lower) /
                                         (frequency.lower * input_voltage_ripple))

    sw_current_max = output_current_max + inductor_current_ripple.upper / 2

    self.inductor = self.Block(Inductor(
      inductance=inductance*Henry,
      current=(0, sw_current_max)*Amp,
      frequency=frequency*Hertz
    ))

    self.in_cap = self.Block(DecouplingCapacitor(
      capacitance=input_capacitance*Farad,
    ))
    self.out_cap = self.Block(DecouplingCapacitor(
      capacitance=output_capacitance*Farad,
    ))
    self.connect(self.pwr_in, self.in_cap.pwr)
    self.connect(self.pwr_out, self.out_cap.pwr)
    self.connect(self.gnd, self.in_cap.gnd, self.out_cap.gnd)

    self.connect(self.switch, self.inductor.a.as_voltage_sink(
      voltage_limits=RangeExpr.ALL,
      current_draw=(0, sw_current_max)*Amp))
    self.connect(self.pwr_out, self.inductor.b.as_voltage_source(
      voltage_out=output_voltage,  # TODO proper parameter propagation
      current_limits=(0, 1.2)*Amp  # TODO proper parameter propagation
    ))


class BoostConverterPowerPath(GeneratorBlock):
  # TODO IMPLEMENT ME
  pass


@abstract_block
class DiscreteBuckConverter(BuckConverter):
  """Provides a helper function to generate the power path for a switching buck converter.
  TODO: support non-synchronous topologies and non-integrated FETs

  Useful resources:
  https://www.ti.com/lit/an/slva477b/slva477b.pdf
    Component sizing in continuous mode
    Listed references go into more detail
  http://www.onmyphd.com/?p=voltage.regulators.buck.step.down.converter
    Very detailed analysis including component sizing, operating modes, calculating losses
  """
  DUTYCYCLE_MIN_LIMIT = 0.1
  DUTYCYCLE_MAX_LIMIT = 0.9
  WORST_EFFICIENCY_ESTIMATE = 0.9  # from TI reference

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.dutycycle_limit = self.Parameter(RangeExpr((self.DUTYCYCLE_MIN_LIMIT, self.DUTYCYCLE_MAX_LIMIT)))
    self.actual_dutycycle = self.Parameter(RangeExpr())  # calculated duty cycle

  def _generate_converter(self, switch_node: VoltageSource, rated_max_current_amps: float,
                          input_voltage: Range, output_voltage: Range,
                          output_current_max: float, frequency: Range,
                          spec_output_ripple: float, spec_input_ripple: float, ripple_factor: Range,
                          dutycycle_limit: Range
                          ) -> Passive:
    """
    Given the switch node, generates the passive (in and out filter caps, inductor) components,
    connects them, and returns the output of the inductor as a PassivePort.
    The caller must connect the PassivePort.

    Main assumptions in component sizing
    - Operating only in continuous mode TODO: also consider boundary and discontinuous mode

    TODO support capacitor ESR calculation
    TODO unify rated max current with something else, perhaps a block param?
    """
    dutycycle = output_voltage / input_voltage / Range(self.WORST_EFFICIENCY_ESTIMATE, 1)
    self.assign(self.actual_dutycycle, dutycycle)
    # if these are violated, these generally mean that the converter will start tracking the input
    # these can (maybe?) be waived if tracking (plus losses) is acceptable
    self.require(self.actual_dutycycle.within(dutycycle_limit), f"dutycycle {dutycycle} outside limit {dutycycle_limit}")
    # these are actual numbers to be used in calculations
    effective_dutycycle = dutycycle.bound_to(dutycycle_limit)

    ripple_current = (output_current_max * ripple_factor).extend_upper_to(
      rated_max_current_amps * ripple_factor.lower  # see LMR33630 datasheet, use rating if current draw much lower
    )

    # Calculate minimum inductance based on worst case values (operating range corners producing maximum inductance)
    # This range must be constructed manually to not double-count the tolerance stackup of the voltages
    inductance_min = (output_voltage.lower * (input_voltage.upper - output_voltage.lower) /
                      (ripple_current.upper * frequency.lower * input_voltage.upper))
    inductance_max = (output_voltage.lower * (input_voltage.upper - output_voltage.lower) /
                      (ripple_current.lower * frequency.lower * input_voltage.upper))
    inductance = Range(inductance_min, inductance_max)

    # TODO size based on transient response, add to voltage tolerance stackups
    output_capacitance = Range.from_lower(ripple_current.upper / (8 * frequency.lower * spec_output_ripple))
    # TODO pick a single worst-case DC
    input_capacitance = Range.from_lower(output_current_max * effective_dutycycle.upper * (1 - effective_dutycycle.lower) /
                                         (frequency.lower * spec_input_ripple))

    sw_current_max = output_current_max + ripple_current.upper / 2

    self.inductor = self.Block(Inductor(
      inductance=inductance*Henry,
      current=(0, sw_current_max)*Amp,
      frequency=frequency*Hertz
    ))

    # TODO: DC derating
    # Note, implicit connect is not great here because of the different power in / power out rails
    # But maybe something can be done with ground?
    self.in_cap = self.Block(DecouplingCapacitor(
      capacitance=input_capacitance*Farad,
    ))
    self.out_cap = self.Block(DecouplingCapacitor(
      capacitance=output_capacitance*Farad,
    ))
    self._pwr_in_net = self.connect(self.pwr_in, self.in_cap.pwr)
    self._pwr_out_net = self.connect(self.pwr_out, self.out_cap.pwr)
    self._gnd_net = self.connect(self.gnd, self.in_cap.gnd, self.out_cap.gnd)

    self._switch_net = self.connect(switch_node, self.inductor.a.as_voltage_sink(
      voltage_limits=RangeExpr.ALL,
      current_draw=(0, sw_current_max)*Amp))

    return self.inductor.b


@abstract_block
class BoostConverter(DcDcSwitchingConverter):
  """Step-up switching converter"""
  def __init__(self, *args, ripple_current_factor: RangeLike = Default((0.2, 0.5)), **kwargs) -> None:
    # TODO default ripple is very heuristic, intended 0.3-0.4, loosely adjusted for inductor tolerance
    # TODO can this be integrated with some kind of AbstractDcDcConverter?
    super().__init__(*args, ripple_current_factor=ripple_current_factor, **kwargs)

    self.frequency = self.Parameter(RangeExpr())


@abstract_block
class DiscreteBoostConverter(BoostConverter):
  """Step-up switching converter, with provisions for passives sizing.
  TODO: support non-integrated FETs

  Useful resources:
  https://www.ti.com/lit/an/slva372c/slva372c.pdf
    Component sizing in continuous mode
    Listed references go into more detail
  http://www.simonbramble.co.uk/dc_dc_converter_design/boost_converter/boost_converter_design.htm
    Detailed analysis of converter with discrete FET and diode
  """
  DUTYCYCLE_MIN_LIMIT = 0.2  # inferred from Figure 9
  DUTYCYCLE_MAX_LIMIT = 0.85  # by datasheet
  WORST_EFFICIENCY_ESTIMATE = 0.8  # from TI reference

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.dutycycle_limit = self.Parameter(RangeExpr((self.DUTYCYCLE_MIN_LIMIT, self.DUTYCYCLE_MAX_LIMIT)))
    self.dutycycle = self.Parameter(RangeExpr())  # calculated duty cycle

  def _generate_converter(self, switch_node: VoltageSource, rated_max_current_amps: float,
                          input_voltage: Range, output_voltage: Range,
                          output_current_max: float, frequency: Range,
                          spec_output_ripple: float, spec_input_ripple: float, ripple_factor: Range,
                          dutycycle_limit: Range
                          ) -> None:
    """
    - diode needs to be fast, consider forward voltage drop, forward current (> peak inductor current), reverse volts (> Vout)

    Main assumptions in component sizing
    - Operating only in continuous mode TODO: also consider boundary and discontinuous mode

    TODO support capacitor ESR calculation
    """
    dutycycle = 1 - input_voltage / output_voltage * Range(self.WORST_EFFICIENCY_ESTIMATE, 1)
    self.assign(self.dutycycle, dutycycle)
    # if these are violated, these generally mean that the converter will start tracking the input
    # these can (maybe?) be waived if tracking (plus losses) is acceptable
    self.require(self.dutycycle.within(dutycycle_limit), f"dutycycle {dutycycle} outside limit {dutycycle_limit}")
    # these are actual numbers to be used in calculations
    effective_dutycycle = dutycycle.bound_to(dutycycle_limit)

    ripple_current = (output_current_max * ripple_factor).extend_upper_to(
      rated_max_current_amps * ripple_factor.lower  # see LMR33630 datasheet, use rating if current draw much lower
    )

    # Calculate minimum inductance based on worst case values (operating range corners producing maximum inductance)
    # This range must be constructed manually to not double-count the tolerance stackup of the voltages
    inductance_min = (input_voltage.lower * (output_voltage.upper - input_voltage.lower) /
                      (ripple_current.upper * frequency.lower * output_voltage.lower))
    inductance_max = (input_voltage.lower * (output_voltage.upper - input_voltage.lower) /
                      (ripple_current.lower * frequency.lower * output_voltage.lower))
    inductance = Range(inductance_min, inductance_max)
    output_capacitance = Range.from_lower(output_current_max * effective_dutycycle.upper /
                                          (frequency.lower * spec_output_ripple))
    input_capacitance = Range.from_lower((output_current_max / effective_dutycycle.lower) * (1 - effective_dutycycle.lower) /
                                         (frequency.lower * spec_input_ripple))

    sw_current_max = ripple_current.upper / 2 + output_current_max / (1 - effective_dutycycle.upper)

    self.inductor = self.Block(Inductor(
      inductance=inductance*Henry,
      current=(0, sw_current_max)*Amp,
      frequency=frequency*Hertz
    ))

    # TODO: DC derating
    # Note, implicit connect is not great here because of the different power in / power out rails
    # But maybe something can be done with ground?
    self.in_cap = self.Block(DecouplingCapacitor(
      capacitance=input_capacitance*Farad,
    ))
    self.out_cap = self.Block(DecouplingCapacitor(
      capacitance=output_capacitance*Farad,
    ))
    self.connect(self.pwr_in, self.in_cap.pwr, self.inductor.a.as_voltage_sink())
    self.connect(self.pwr_out, self.out_cap.pwr)
    self.connect(self.gnd, self.in_cap.gnd, self.out_cap.gnd)

    self.connect(switch_node, self.inductor.b.as_voltage_sink())
