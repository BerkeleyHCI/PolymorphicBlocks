from electronics_model import *
from .Categories import *
from .AbstractPassives import Inductor, DecouplingCapacitor


@abstract_block
class DcDcConverter(PowerConditioner):
  """Base class for all DC-DC converters with shared ground (non-isoalted)."""
  @init_in_parent
  def __init__(self, output_voltage: RangeExpr = RangeExpr()) -> None:
    super().__init__()

    self.spec_output_voltage = self.Parameter(RangeExpr(output_voltage))

    self.pwr_in = self.Port(VoltageSink(
      voltage_limits=RangeExpr(),
      current_draw=RangeExpr()
    ), [Power, Input])  # TODO mark as future-connected here?
    self.pwr_out = self.Port(VoltageSource(
      voltage_out=RangeExpr(),
      current_limits=RangeExpr()
    ), [Output])  # TODO mark as future-connected here?
    self.gnd = self.Port(Ground(), [Common])  # TODO mark as future-connected?

    self.require(self.pwr_out.voltage_out.within(self.spec_output_voltage),
                   "Output voltage must be within spec")


@abstract_block
class LinearRegulator(DcDcConverter):
  @init_in_parent
  def __init__(self, output_voltage: RangeExpr = RangeExpr()) -> None:
    super().__init__(output_voltage)
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
  def __init__(self, output_voltage: RangeExpr = RangeExpr(), ripple_current_factor: RangeLike = RangeExpr(),
               input_ripple_limit: FloatExpr = 75 * mVolt, output_ripple_limit: FloatExpr = 25 * mVolt) -> None:
    # TODO can this be integrated with some kind of AbstractDcDcConverter?
    super().__init__(output_voltage)

    self.ripple_current_factor = self.Parameter(RangeExpr(ripple_current_factor))
    self.input_ripple_limit = self.Parameter(FloatExpr(input_ripple_limit))
    self.output_ripple_limit = self.Parameter(FloatExpr(output_ripple_limit))
    self.efficiency = self.Parameter(RangeExpr())

    self.require(self.pwr_in.current_draw.within((
      self.pwr_out.link().current_drawn * self.pwr_out.voltage_out / self.pwr_in.link().voltage / self.efficiency + (0, 0.01)  # TODO avoid fudge factor
    )))


@abstract_block
class BuckConverter(DcDcSwitchingConverter):
  """Step-down switching converter"""
  def __init__(self, ripple_current_factor: RangeLike = (0.2, 0.5), **kwargs) -> None:
    # TODO default ripple is very heuristic, intended 0.3-0.4, loosely adjusted for inductor tolerance
    # TODO can this be integrated with some kind of AbstractDcDcConverter?
    super().__init__(ripple_current_factor=ripple_current_factor, **kwargs)

    self.frequency = self.Parameter(RangeExpr())


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

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.dutycycle = self.Parameter(RangeExpr())  # calculated duty cycle

  def _generate_converter(self, switch_node: VoltageSource, rated_max_current_amps: float,
                          input_voltage: Range, output_voltage: Range,
                          output_current_max: float, frequency: Range,
                          spec_output_ripple: float, spec_input_ripple: float, ripple_factor: Range
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

    in_voltage_min, in_voltage_max = input_voltage
    out_voltage_min, out_voltage_max = output_voltage
    freq_min, freq_max = frequency

    dc_max = out_voltage_max / in_voltage_min / self.WORST_EFFICIENCY_ESTIMATE
    dc_min = out_voltage_min / in_voltage_max
    self.assign(self.dutycycle, (dc_min, dc_max))
    # if these are violated, these generally mean that the converter will start tracking the input
    # these can (maybe?) be waived if tracking (plus losses) is acceptable
    self.require(self.dutycycle.upper() <= self.DUTYCYCLE_MAX_LIMIT, f"dutycycle max outside limit {self.DUTYCYCLE_MAX_LIMIT}")
    self.require(self.dutycycle.lower() >= self.DUTYCYCLE_MIN_LIMIT, f"dutycycle min outside limit {self.DUTYCYCLE_MIN_LIMIT}")

    # these are actual numbers to be used in calculations
    effective_dc_min = max(self.DUTYCYCLE_MIN_LIMIT, dc_min)
    effective_dc_max = min(self.DUTYCYCLE_MAX_LIMIT, dc_max)

    ripple_current_min = output_current_max * ripple_factor[0]  # peak-peak
    ripple_current_max = max(
      output_current_max * ripple_factor[1],  # peak-peak
      rated_max_current_amps * ripple_factor[0]  # see LMR33630 datasheet, use rating if current draw much lower
    )

    # Calculate minimum inductance based on worst case values (operating range corners producing maximum inductance)
    inductance_min = out_voltage_min * (in_voltage_max - out_voltage_min) / ripple_current_max / freq_min / in_voltage_max
    if ripple_current_min == 0:
      inductance_max = float('inf')
    else:
      inductance_max = out_voltage_min * (in_voltage_max - out_voltage_min) / ripple_current_min / freq_min / in_voltage_max

    out_capacitance_min = ripple_current_max / 8 / freq_min / spec_output_ripple  # TODO size based on transient response, add to voltage tolerance stackups
    in_capacitance_min = output_current_max * effective_dc_max * (1 - effective_dc_min) / freq_min / spec_input_ripple

    sw_current_max = output_current_max + ripple_current_max / 2

    self.inductor = self.Block(Inductor(
      inductance=(inductance_min, inductance_max)*Henry,
      current=(0, sw_current_max)*Amp,
      frequency=(freq_min, freq_max)*Hertz
    ))

    # TODO: DC derating
    # Note, implicit connect is not great here because of the different power in / power out rails
    # But maybe something can be done with ground?
    self.in_cap = self.Block(DecouplingCapacitor(
      capacitance=(in_capacitance_min, float('inf'))*Farad,
    ))
    self.out_cap = self.Block(DecouplingCapacitor(
      capacitance=(out_capacitance_min, float('inf'))*Farad,
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
  def __init__(self, ripple_current_factor: RangeLike = (0.2, 0.5), **kwargs) -> None:
    # TODO default ripple is very heuristic, intended 0.3-0.4, loosely adjusted for inductor tolerance
    # TODO can this be integrated with some kind of AbstractDcDcConverter?
    super().__init__(ripple_current_factor=ripple_current_factor, **kwargs)

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

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.dutycycle = self.Parameter(RangeExpr())  # calculated duty cycle

  def _generate_converter(self, switch_node: VoltageSource, rated_max_current_amps: float,
                          input_voltage: Range, output_voltage: Range,
                          output_current_max: float, frequency: Range,
                          spec_output_ripple: float, spec_input_ripple: float, ripple_factor: Range
                          ) -> None:
    """
    - diode needs to be fast, consider forward voltage drop, forward current (> peak inductor current), reverse volts (> Vout)

    Main assumptions in component sizing
    - Operating only in continuous mode TODO: also consider boundary and discontinuous mode

    TODO support capacitor ESR calculation
    """

    in_voltage_min, in_voltage_max = input_voltage
    out_voltage_min, out_voltage_max = output_voltage
    freq_min, freq_max = frequency

    dc_max = 1 - in_voltage_min * self.WORST_EFFICIENCY_ESTIMATE / out_voltage_max
    dc_min = 1 - in_voltage_max / out_voltage_min

    self.assign(self.dutycycle, (dc_min, dc_max))
    # if these are violated, these generally mean that the converter will start tracking the input
    # these can (maybe?) be waived if tracking (plus losses) is acceptable
    self.require(self.dutycycle.upper() <= self.DUTYCYCLE_MAX_LIMIT, f"dutycycle max outside limit {self.DUTYCYCLE_MAX_LIMIT}")
    self.require(self.dutycycle.lower() >= self.DUTYCYCLE_MIN_LIMIT, f"dutycycle min outside limit {self.DUTYCYCLE_MIN_LIMIT}")

    # these are actual numbers to be used in calculations
    effective_dc_min = max(self.DUTYCYCLE_MIN_LIMIT, dc_min)
    effective_dc_max = min(self.DUTYCYCLE_MAX_LIMIT, dc_max)

    ripple_current_min = output_current_max * ripple_factor[0]  # peak-peak
    ripple_current_max = max(
      output_current_max * ripple_factor[1],  # peak-peak
      rated_max_current_amps * ripple_factor[0]  # see LMR33630 datasheet, use rating if current draw much lower
    )

    # Calculate minimum inductance based on worst case values (operating range corners producing maximum inductance)
    inductance_min = in_voltage_min * (out_voltage_max - in_voltage_min) / ripple_current_max / freq_min / out_voltage_min
    inductance_max = in_voltage_min * (out_voltage_max - in_voltage_min) / ripple_current_min / freq_min / out_voltage_min
    out_capacitance_min = output_current_max * effective_dc_max / freq_min / spec_output_ripple
    in_capacitance_min = (output_current_max / effective_dc_min) * (1 - effective_dc_min) / freq_min / spec_input_ripple

    sw_current_max = ripple_current_max / 2 + output_current_max / (1 - effective_dc_max)

    self.inductor = self.Block(Inductor(
      inductance=(inductance_min, inductance_max)*Henry,
      current=(0, sw_current_max)*Amp,
      frequency=(freq_min, freq_max)*Hertz
    ))

    # TODO: DC derating
    # Note, implicit connect is not great here because of the different power in / power out rails
    # But maybe something can be done with ground?
    self.in_cap = self.Block(DecouplingCapacitor(
      capacitance=(in_capacitance_min, float('inf'))*Farad,
    ))
    self.out_cap = self.Block(DecouplingCapacitor(
      capacitance=(out_capacitance_min, float('inf'))*Farad,
    ))
    self.connect(self.pwr_in, self.in_cap.pwr, self.inductor.a.as_voltage_sink())
    self.connect(self.pwr_out, self.out_cap.pwr)
    self.connect(self.gnd, self.in_cap.gnd, self.out_cap.gnd)

    self.connect(switch_node, self.inductor.b.as_voltage_sink())
