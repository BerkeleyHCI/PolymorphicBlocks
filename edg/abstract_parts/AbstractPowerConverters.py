from abc import abstractmethod
from typing import Optional, NamedTuple, Any, Callable

from deprecated import deprecated

from .AbstractCapacitor import DecouplingCapacitor
from .AbstractInductor import Inductor, TableInductor
from .Categories import *
from .PartsTable import PartsTableRow, ExperimentalUserFnPartsTable
from .Resettable import Resettable
from ..electronics_model import *


@abstract_block_default(lambda: IdealVoltageRegulator)
class VoltageRegulator(PowerConditioner):
  """Structural abstract base class for DC-DC voltage regulators with shared ground (non-isolated).
  This takes some input voltage and produces a stable voltage at output_voltage on its output.

  While this abstract class does not define any limitations on the output voltage, subclasses and concrete
  implementations commonly have restrictions, for example linear regulators can only produce voltages lower
  than the input voltage.
  """
  def __init__(self, output_voltage: RangeLike) -> None:
    super().__init__()

    self.output_voltage = self.ArgParameter(output_voltage)

    self.pwr_in = self.Port(VoltageSink.empty(), [Power, Input])
    self.pwr_out = self.Port(VoltageSource.empty(), [Output])
    self.gnd = self.Port(Ground.empty(), [Common])

  @override
  def contents(self) -> None:
    super().contents()

    self.description = DescriptionString(
      "<b>output voltage:</b> ", DescriptionString.FormatUnits(self.pwr_out.voltage_out, "V"),
      " <b>of spec:</b> ", DescriptionString.FormatUnits(self.output_voltage, "V"), "\n",
      "<b>input voltage:</b> ", DescriptionString.FormatUnits(self.pwr_in.link().voltage, "V")
    )

    self.require(self.pwr_out.voltage_out.within(self.output_voltage),
                 "Output voltage must be within spec")


@non_library
class VoltageRegulatorEnableWrapper(Resettable, VoltageRegulator, GeneratorBlock):
  """Implementation mixin for a voltage regulator wrapper block where the inner device has a reset/enable pin
  (active-high enable / active-low shutdown) that is automatically tied high if not externally connected.
  Mix this into a VoltageRegulator to automatically handle the reset pin."""
  @abstractmethod
  def _generator_inner_reset_pin(self) -> Port[DigitalLink]:
    """Returns the inner device's reset pin, to be connected in the generator.
    Only called within a generator."""

  @override
  def contents(self) -> None:
    super().contents()
    self.generator_param(self.reset.is_connected())

  @override
  def generate(self) -> None:
    super().generate()
    if self.get(self.reset.is_connected()):
      self.connect(self.reset, self._generator_inner_reset_pin())
    else:  # by default tie high to enable regulator
      self.connect(self.pwr_in.as_digital_source(), self._generator_inner_reset_pin())


@abstract_block_default(lambda: IdealLinearRegulator)
class LinearRegulator(VoltageRegulator):
  """Structural abstract base class for linear regulators, a voltage regulator that can produce some
  output voltage lower than its input voltage (minus some dropout) by 'burning' the excess voltage as heat.

  Compared to switching converters like buck and boost converters, linear regulators usually have lower
  complexity, lower parts count, and higher stability. However, depending on the application, they are
  typically less efficient, and at higher loads may require thermal design considerations."""


@abstract_block
class VoltageReference(LinearRegulator):
  """Voltage reference, generally provides high accuracy but limited current"""


class IdealLinearRegulator(Resettable, LinearRegulator, IdealModel):
  """Ideal linear regulator, draws the output current and produces spec output voltage limited by input voltage"""
  @override
  def contents(self) -> None:
    super().contents()
    effective_output_voltage = self.output_voltage.intersect((0, self.pwr_in.link().voltage.upper()))
    self.gnd.init_from(Ground())
    self.pwr_in.init_from(VoltageSink(
      current_draw=self.pwr_out.link().current_drawn))
    self.pwr_out.init_from(VoltageSource(
      voltage_out=effective_output_voltage))
    self.reset.init_from(DigitalSink())


@non_library
class LinearRegulatorDevice(Block):
  """Abstract base class that provides a default model with common functionality for a linear regulator chip.
  Does not include supporting components like capacitors.
  """
  def __init__(self) -> None:
    super().__init__()

    # these device model parameters must be provided by subtypes
    self.actual_dropout = self.Parameter(RangeExpr())
    self.actual_quiescent_current = self.Parameter(RangeExpr())

    self.gnd = self.Port(Ground(), [Common])
    self.pwr_in = self.Port(VoltageSink(
      voltage_limits=RangeExpr(),  # parameters set by subtype
      current_draw=RangeExpr()
    ), [Power, Input])
    self.pwr_out = self.Port(VoltageSource(
      voltage_out=self.RangeExpr(),  # parameters set by subtype
      current_limits=RangeExpr()
    ), [Output])
    self.assign(self.pwr_in.current_draw,
                self.pwr_out.link().current_drawn + self.actual_quiescent_current)

    self.require(self.pwr_out.voltage_out.lower() + self.actual_dropout.upper() <= self.pwr_in.link().voltage.lower(),
                 "excessive dropout")


@abstract_block
class SwitchingVoltageRegulator(VoltageRegulator):
  @staticmethod
  @deprecated("ripple calculation moved into the power-path block itself")
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

  def __init__(self, *args: Any,
               input_ripple_limit: FloatLike = 75 * mVolt,
               output_ripple_limit: FloatLike = 25 * mVolt,
               **kwargs: Any) -> None:
    """https://www.ti.com/lit/an/slta055/slta055.pdf: recommends 75mV for maximum peak-peak ripple voltage
    """
    super().__init__(*args, **kwargs)

    self.input_ripple_limit = self.ArgParameter(input_ripple_limit)
    self.output_ripple_limit = self.ArgParameter(output_ripple_limit)

    self.actual_frequency = self.Parameter(RangeExpr())


@abstract_block_default(lambda: IdealBuckConverter)
class BuckConverter(SwitchingVoltageRegulator):
  """Step-down switching converter"""
  def __init__(self, *args: Any, **kwargs: Any) -> None:
    super().__init__(*args, **kwargs)
    self.require(self.pwr_out.voltage_out.upper() <= self.pwr_in.voltage_limits.upper())


@abstract_block_default(lambda: IdealBuckConverter)
class DiscreteBuckConverter(BuckConverter):
  """Category for discrete buck converter subcircuits (as opposed to integrated components)"""


class IdealBuckConverter(Resettable, DiscreteBuckConverter, IdealModel):
  """Ideal buck converter producing the spec output voltage (buck-boost) limited by input voltage
  and drawing input current from conversation of power"""
  @override
  def contents(self) -> None:
    super().contents()
    effective_output_voltage = self.output_voltage.intersect((0, self.pwr_in.link().voltage.upper()))
    self.gnd.init_from(Ground())
    self.pwr_in.init_from(VoltageSink(
      current_draw=effective_output_voltage / self.pwr_in.link().voltage * self.pwr_out.link().current_drawn))
    self.pwr_out.init_from(VoltageSource(
      voltage_out=effective_output_voltage))
    self.reset.init_from(DigitalSink())


class BuckConverterPowerPath(InternalSubcircuit, GeneratorBlock):
  """A helper block to generate the power path (inductors, capacitors) for a switching buck converter.

  Useful resources:
  https://www.ti.com/lit/an/slva477b/slva477b.pdf
    Component sizing in continuous mode
  http://www.onmyphd.com/?p=voltage.regulators.buck.step.down.converter
    Very detailed analysis including component sizing, operating modes, calculating losses
  """

  @staticmethod
  def _d_inverse_d(d_range: Range) -> Range:
    """Some power calculations require the maximum of D*(1-D), which has a maximum at D=0.5"""
    # can't use range ops since they will double-count the tolerance of D, so calculate endpoints separately
    range_endpoints = [d_range.lower * (1 - d_range.lower), d_range.upper * (1 - d_range.upper)]
    raw_range = Range(min(range_endpoints), max(range_endpoints))
    if 0.5 in d_range:  # the function has a maximum at 0.5
      return raw_range.hull(Range.exact(0.5 * (1 - 0.5)))
    else:
      return raw_range

  @staticmethod
  def _ripple_current_from_sw_current(sw_current: float, ripple_ratio: Range) -> Range:
    """Calculates the ripple current from a total switch current and ripple ratio."""
    return Range(  # separate range parts to avoid double-counting tolerances
      sw_current / (1 + ripple_ratio.lower) * ripple_ratio.lower,
      sw_current / (1 + ripple_ratio.upper) * ripple_ratio.upper
    )

  class Values(NamedTuple):
    dutycycle: Range
    inductance: Range
    input_capacitance: Range
    output_capacitance: Range

    inductor_avg_current: Range
    ripple_scale: float  # divide this by inductance to get the inductor ripple current
    min_ripple: float  # fallback minimum ripple current for component sizing for light-load, may be 0
    output_capacitance_scale: float  # multiply inductor ripple by this to get required output capacitance

    inductor_peak_currents: Range  # based on the worst case input spec, for unit testing
    effective_dutycycle: Range  # duty cycle adjusted for tracking behavior

  @classmethod
  def _calculate_parameters(cls, input_voltage: Range, output_voltage: Range, frequency: Range, output_current: Range,
                            sw_current_limits: Range, ripple_ratio: Range,
                            input_voltage_ripple: float, output_voltage_ripple: float,
                            efficiency: Range = Range(0.9, 1.0), dutycycle_limit: Range = Range(0.1, 0.9),
                            limit_ripple_ratio: Range = Range(0.1, 0.5)) -> 'BuckConverterPowerPath.Values':
    """Calculates parameters for the buck converter power path.

    This uses the continuous conduction mode (CCM) equations to calculate component sizes.
    DCM is not explicitly calculated since it requires additional parameters like minimum on-time.
    The limit_ripple_ratio provides some broadly sane values for light-load / DCM operation.
    This also ignores higher-order component behavior like capacitor ESR.

    The ripple_ratio is optional and may be set to Range.all(), allowing the inductor selector
    to optimize the inductor by trading off inductance and max current.

    Values for component selections are bounded by:
    - the ripple_ratio at output_current (if ripple_ratio < inf), and
    - the limit_ripple_ratio at sw_current_limits (if sw_current_limits is not zero), as a fallback
      for light-load conditions (where otherwise current goes to zero and inductance goes to the moon)
    """
    dutycycle = output_voltage / input_voltage / efficiency
    effective_dutycycle = dutycycle.bound_to(dutycycle_limit)  # account for tracking behavior

    # calculate minimum inductance based on worst case values (operating range corners producing maximum inductance)
    # worst-case input/output voltages and frequency is used to avoid double-counting tolerances as ranges
    # note, for buck converter, L = (Vin - Vout) * D / (f * Iripple) = Vout (Vin - Vout) / (Iripple * f * Vin)
    # this is at a maximum at Vin,max, and on that curve with a critical point at Vout = Vin,max / 2
    # note, the same formula calculates ripple-from-inductance and inductance-from-ripple
    inductance_scale_candidates = [
      output_voltage.lower * (input_voltage.upper - output_voltage.lower) / input_voltage.upper,
      output_voltage.upper * (input_voltage.upper - output_voltage.upper) / input_voltage.upper,
    ]
    if input_voltage.upper / 2 in output_voltage:
      inductance_scale_candidates.append(
        input_voltage.upper/2 * (input_voltage.upper - input_voltage.upper/2) / input_voltage.upper)
    inductance_scale = max(inductance_scale_candidates) / frequency.lower

    inductance = Range.all()
    min_ripple = 0.0
    if sw_current_limits.upper > 0:  # fallback for light-load
      ripple_current = cls._ripple_current_from_sw_current(sw_current_limits.upper, limit_ripple_ratio)
      inductance = inductance.intersect(inductance_scale / ripple_current)
      min_ripple = ripple_current.lower
    if ripple_ratio.upper < float('inf'):
      assert ripple_ratio.lower > 0, f"invalid non-inf ripple ratio {ripple_ratio}"

      inductance = inductance.intersect(inductance_scale / (output_current.upper * ripple_ratio))
    assert inductance.upper < float('inf'), 'neither ripple_ratio nor fallback sw_current_limits given'

    input_capacitance = Range.from_lower(output_current.upper * cls._d_inverse_d(effective_dutycycle).upper /
                                         (frequency.lower * input_voltage_ripple))
    output_capacitance_scale = 1 / (8 * frequency.lower * output_voltage_ripple)

    # these are static worst-case estimates for the range of specified ripple currents
    # mainly used for unit testing
    inductor_current_ripple = output_current * ripple_ratio.intersect(limit_ripple_ratio)
    inductor_peak_currents = Range(max(0, output_current.lower - inductor_current_ripple.upper / 2),
                                   max(output_current.upper + inductor_current_ripple.upper / 2,
                                       inductor_current_ripple.upper))
    output_capacitance = Range.from_lower(output_capacitance_scale * inductor_current_ripple.upper)

    return cls.Values(dutycycle=dutycycle, inductance=inductance,
                      input_capacitance=input_capacitance, output_capacitance=output_capacitance,
                      inductor_avg_current=output_current / efficiency,
                      ripple_scale=inductance_scale, min_ripple=min_ripple,
                      output_capacitance_scale=output_capacitance_scale,
                      inductor_peak_currents=inductor_peak_currents,
                      effective_dutycycle=effective_dutycycle)

  @staticmethod
  @ExperimentalUserFnPartsTable.user_fn([float, float, float])
  def _buck_inductor_filter(max_avg_current: float, ripple_scale: float, min_ripple: float) -> Callable[[PartsTableRow], bool]:
    """Applies further filtering to inductors using the trade-off between inductance and peak-peak current.
    max_avg_current is the maximum average current (not accounting for ripple) seen by the inductor
    ripple_scale is the scaling factor from 1/L to ripple
    This structure also works for boost converters, which would have its ripple_scale calculated differently."""
    def filter_fn(row: PartsTableRow) -> bool:
      ripple_current = max(ripple_scale / row[TableInductor.INDUCTANCE].lower, min_ripple)
      max_current_pp = max_avg_current + ripple_current / 2
      return max_current_pp in row[TableInductor.CURRENT_RATING]
    return filter_fn

  @staticmethod
  def _ilim_expr(inductor_ilim: RangeExpr, sw_ilim: RangeExpr, inductor_iripple: RangeExpr) -> RangeExpr:
    """Returns the average current limit, as an expression, derived from the inductor and switch (instantaneous)
    current limits."""
    iout_limit_inductor = inductor_ilim - (inductor_iripple.upper() / 2)
    iout_limit_sw = (sw_ilim.upper() > 0).then_else(
      sw_ilim - (inductor_iripple.upper() / 2), Range.all())
    return iout_limit_inductor.intersect(iout_limit_sw).intersect(Range.from_lower(0))

  def __init__(self, input_voltage: RangeLike, output_voltage: RangeLike, frequency: RangeLike,
               output_current: RangeLike, sw_current_limits: RangeLike, *,
               input_voltage_ripple: FloatLike,
               output_voltage_ripple: FloatLike,
               efficiency: RangeLike = (0.9, 1.0),  # from TI reference
               dutycycle_limit: RangeLike = (0.1, 0.9),
               ripple_ratio: RangeLike = Range.all()):
    super().__init__()

    self.pwr_in = self.Port(VoltageSink.empty(), [Power])  # no modeling, input cap only
    self.pwr_out = self.Port(VoltageSource.empty())  # models max output avg. current
    # technically VoltageSink is the wrong model, but this is used to pass the current draw to the chip
    # (and its input pin) without need the top-level to explicitly pass a parameter to the chip
    self.switch = self.Port(VoltageSink.empty())  # models input / inductor avg. current draw
    self.gnd = self.Port(Ground.empty(), [Common])

    self.input_voltage = self.ArgParameter(input_voltage)
    self.output_voltage = self.ArgParameter(output_voltage)
    self.frequency = self.ArgParameter(frequency)
    self.output_current = self.ArgParameter(output_current)
    self.sw_current_limits = self.ArgParameter(sw_current_limits)

    self.efficiency = self.ArgParameter(efficiency)
    self.input_voltage_ripple = self.ArgParameter(input_voltage_ripple)
    self.output_voltage_ripple = self.ArgParameter(output_voltage_ripple)
    self.dutycycle_limit = self.ArgParameter(dutycycle_limit)
    self.ripple_ratio = self.ArgParameter(ripple_ratio)  # only used to force a ripple ratio at the actual currents

    self.generator_param(self.input_voltage, self.output_voltage, self.frequency, self.output_current,
                         self.sw_current_limits, self.input_voltage_ripple, self.output_voltage_ripple,
                         self.efficiency, self.dutycycle_limit, self.ripple_ratio)

    self.actual_dutycycle = self.Parameter(RangeExpr())
    self.actual_inductor_current_ripple = self.Parameter(RangeExpr())
    self.actual_inductor_current_peak = self.Parameter(RangeExpr())

  @override
  def contents(self) -> None:
    super().contents()

    self.description = DescriptionString(
      "<b>duty cycle:</b> ", DescriptionString.FormatUnits(self.actual_dutycycle, ""),
      " <b>of limits:</b> ", DescriptionString.FormatUnits(self.dutycycle_limit, ""), "\n",
      "<b>output current avg:</b> ", DescriptionString.FormatUnits(self.output_current, "A"),
      ", <b>ripple:</b> ", DescriptionString.FormatUnits(self.actual_inductor_current_ripple, "A")
    )

  @override
  def generate(self) -> None:
    super().generate()
    values = self._calculate_parameters(self.get(self.input_voltage), self.get(self.output_voltage),
                                        self.get(self.frequency), self.get(self.output_current),
                                        self.get(self.sw_current_limits), self.get(self.ripple_ratio),
                                        self.get(self.input_voltage_ripple), self.get(self.output_voltage_ripple),
                                        efficiency=self.get(self.efficiency),
                                        dutycycle_limit=self.get(self.dutycycle_limit))
    self.assign(self.actual_dutycycle, values.dutycycle)
    self.require(values.dutycycle == values.effective_dutycycle, "dutycycle outside limit")

    self.inductor = self.Block(Inductor(
      inductance=values.inductance * Henry,
      current=values.inductor_avg_current,  # min-bound only, the real filter happens in the filter_fn
      frequency=self.frequency,
      experimental_filter_fn=ExperimentalUserFnPartsTable.serialize_fn(
        self._buck_inductor_filter, values.inductor_avg_current.upper, values.ripple_scale, values.min_ripple)
    ))
    self.assign(self.actual_inductor_current_ripple, values.ripple_scale / self.inductor.actual_inductance)
    self.assign(self.actual_inductor_current_peak,
                values.inductor_avg_current + self.actual_inductor_current_ripple / 2)

    self.connect(self.switch, self.inductor.a.adapt_to(VoltageSink(
      current_draw=self.output_current * values.effective_dutycycle
    )))
    self.connect(self.pwr_out, self.inductor.b.adapt_to(VoltageSource(
      voltage_out=self.output_voltage,
      current_limits=self._ilim_expr(self.inductor.actual_current_rating, self.sw_current_limits,
                                     self.actual_inductor_current_ripple) * self.efficiency
    )))

    self.in_cap = self.Block(DecouplingCapacitor(
      capacitance=values.input_capacitance * Farad,
      exact_capacitance=True
    )).connected(self.gnd, self.pwr_in)
    self.out_cap = self.Block(DecouplingCapacitor(
      capacitance=(Range.exact(float('inf')) * Farad).hull(
        (values.output_capacitance_scale * self.actual_inductor_current_ripple.upper().max(values.min_ripple))),
      exact_capacitance=True
    )).connected(self.gnd, self.pwr_out)


@abstract_block_default(lambda: IdealBoostConverter)
class BoostConverter(SwitchingVoltageRegulator):
  """Step-up switching converter"""
  def __init__(self, *args: Any, **kwargs: Any) -> None:
    super().__init__(*args, **kwargs)
    self.require(self.pwr_out.voltage_out.lower() >= self.pwr_in.voltage_limits.lower())


@abstract_block_default(lambda: IdealBoostConverter)
class DiscreteBoostConverter(BoostConverter):
  """Category for discrete boost converter subcircuits (as opposed to integrated components)"""


class IdealBoostConverter(Resettable, DiscreteBoostConverter, IdealModel):
  """Ideal boost converter producing the spec output voltage (buck-boost) limited by input voltage
  and drawing input current from conversation of power"""
  @override
  def contents(self) -> None:
    super().contents()
    effective_output_voltage = self.output_voltage.intersect((self.pwr_in.link().voltage.lower(), float('inf')))
    self.gnd.init_from(Ground())
    self.pwr_in.init_from(VoltageSink(
      current_draw=effective_output_voltage / self.pwr_in.link().voltage * self.pwr_out.link().current_drawn))
    self.pwr_out.init_from(VoltageSource(
      voltage_out=effective_output_voltage))
    self.reset.init_from(DigitalSink())


class BoostConverterPowerPath(InternalSubcircuit, GeneratorBlock):
  """A helper block to generate the power path (inductors, capacitors) for a synchronous boost converter.

  Useful resources:
  https://www.ti.com/lit/an/slva372c/slva372c.pdf
    Component sizing in continuous mode
  http://www.simonbramble.co.uk/dc_dc_converter_design/boost_converter/boost_converter_design.htm
    Detailed analysis of converter with discrete FET and diode
  """

  class Values(NamedTuple):
    dutycycle: Range
    inductance: Range
    input_capacitance: Range
    output_capacitance: Range

    inductor_avg_current: Range
    ripple_scale: float  # divide this by inductance to get the inductor ripple current
    min_ripple: float  # fallback minimum ripple current for component sizing for light-load, may be 0

    inductor_peak_currents: Range  # based on the worst case input spec, for unit testing
    effective_dutycycle: Range

  @classmethod
  def _calculate_parameters(cls, input_voltage: Range, output_voltage: Range, frequency: Range, output_current: Range,
                            sw_current_limits: Range, ripple_ratio: Range,
                            input_voltage_ripple: float, output_voltage_ripple: float,
                            efficiency: Range = Range(0.8, 1.0), dutycycle_limit: Range = Range(0.1, 0.9),
                            limit_ripple_ratio: Range = Range(0.1, 0.5)) -> 'BoostConverterPowerPath.Values':
    """See BuckConverterPowerPath._calculate_parameters, this performs a similar function."""
    dutycycle = 1 - input_voltage / output_voltage * efficiency
    effective_dutycycle = dutycycle.bound_to(dutycycle_limit)  # account for tracking behavior
    inductor_avg_current = output_current / (1 - effective_dutycycle)

    # calculate minimum inductance based on worst case values (operating range corners producing maximum inductance)
    # worst-case input/output voltages and frequency is used to avoid double-counting tolerances as ranges
    # note, for boost converter, L = Vin * D / (f * Iripple) = Vin (Vout - Vin) / (Iripple * f * Vout)
    # this is at a maximum at Vout,max, and on that curve with a critical point at Vin = Vout,max / 2
    inductance_scale_candidates = [
      input_voltage.lower * (output_voltage.upper - input_voltage.lower) / output_voltage.upper,
      input_voltage.upper * (output_voltage.upper - input_voltage.upper) / output_voltage.upper,
    ]
    if output_voltage.upper / 2 in input_voltage:
      inductance_scale_candidates.append(
        output_voltage.upper/2 * (output_voltage.upper - output_voltage.upper/2) / output_voltage.upper)
    inductance_scale = max(inductance_scale_candidates) / frequency.lower

    inductance = Range.all()
    min_ripple = 0.0
    if sw_current_limits.upper > 0:  # fallback for light-load
      ripple_current = BuckConverterPowerPath._ripple_current_from_sw_current(sw_current_limits.upper, limit_ripple_ratio)
      inductance = inductance.intersect(inductance_scale / ripple_current)
      min_ripple = ripple_current.lower
    if ripple_ratio.upper < float('inf'):
      assert ripple_ratio.lower > 0, f"invalid non-inf ripple ratio {ripple_ratio}"
      inductance = inductance.intersect(inductance_scale / (inductor_avg_current.upper * ripple_ratio))
    assert inductance.upper < float('inf'), 'neither ripple_ratio nor fallback sw_current_limits given'

    inductor_current_ripple = inductor_avg_current * ripple_ratio.intersect(limit_ripple_ratio)
    inductor_peak_currents = Range(max(0, inductor_current_ripple.lower - inductor_current_ripple.upper / 2),
                                   max(inductor_avg_current.upper + inductor_current_ripple.upper / 2,
                                       inductor_current_ripple.upper))

    # Capacitor equation Q = CV => i = C dv/dt => for constant current, i * t = C dV => dV = i * t / C
    # C = i * t / dV => C = i / (f * dV)
    # Boost converter draws current from input throughout the entire cycle, and by conversation of power
    # the average input current is Iin = Vout/Vin * Iout = 1/(1-D) * Iout
    # Boost converter current should be much less spikey than buck converter current and probably
    # less filtering than this is acceptable
    input_capacitance = Range.from_lower((output_current.upper / (1 - effective_dutycycle.upper)) /
                                         (frequency.lower * input_voltage_ripple))
    output_capacitance = Range.from_lower(output_current.upper * effective_dutycycle.upper /
                                          (frequency.lower * output_voltage_ripple))

    return cls.Values(dutycycle=dutycycle, inductance=inductance,
                      input_capacitance=input_capacitance, output_capacitance=output_capacitance,
                      inductor_avg_current=inductor_avg_current, ripple_scale=inductance_scale, min_ripple=min_ripple,
                      inductor_peak_currents=inductor_peak_currents,
                      effective_dutycycle=effective_dutycycle)

  def __init__(self, input_voltage: RangeLike, output_voltage: RangeLike, frequency: RangeLike,
               output_current: RangeLike, sw_current_limits: RangeLike, *,
               input_voltage_ripple: FloatLike,
               output_voltage_ripple: FloatLike,
               efficiency: RangeLike = (0.8, 1.0),  # from TI reference
               dutycycle_limit: RangeLike = (0.1, 0.9),  # arbitrary
               ripple_ratio: RangeLike = Range.all()):
    super().__init__()

    self.pwr_in = self.Port(VoltageSink.empty(), [Power])  # models input / inductor avg. current draw
    self.pwr_out = self.Port(VoltageSink.empty())  # no modeling, output cap only
    self.switch = self.Port(VoltageSource.empty())  # models maximum output avg. current
    self.gnd = self.Port(Ground.empty(), [Common])

    self.input_voltage = self.ArgParameter(input_voltage)
    self.output_voltage = self.ArgParameter(output_voltage)
    self.frequency = self.ArgParameter(frequency)
    self.output_current = self.ArgParameter(output_current)
    self.sw_current_limits = self.ArgParameter(sw_current_limits)

    self.efficiency = self.ArgParameter(efficiency)
    self.input_voltage_ripple = self.ArgParameter(input_voltage_ripple)
    self.output_voltage_ripple = self.ArgParameter(output_voltage_ripple)
    self.dutycycle_limit = self.ArgParameter(dutycycle_limit)
    self.ripple_ratio = self.ArgParameter(ripple_ratio)  # only used to force a ripple ratio at the actual currents

    self.generator_param(self.input_voltage, self.output_voltage, self.frequency, self.output_current,
                         self.sw_current_limits, self.input_voltage_ripple, self.output_voltage_ripple,
                         self.efficiency, self.dutycycle_limit, self.ripple_ratio)

    self.actual_dutycycle = self.Parameter(RangeExpr())
    self.actual_inductor_current_ripple = self.Parameter(RangeExpr())
    self.actual_inductor_current_peak = self.Parameter(RangeExpr())

  @override
  def contents(self) -> None:
    super().contents()

    self.description = DescriptionString(
      "<b>duty cycle:</b> ", DescriptionString.FormatUnits(self.actual_dutycycle, ""),
      " <b>of limits:</b> ", DescriptionString.FormatUnits(self.dutycycle_limit, ""), "\n",
      "<b>output current avg:</b> ", DescriptionString.FormatUnits(self.output_current, "A"),
      ", <b>ripple:</b> ", DescriptionString.FormatUnits(self.actual_inductor_current_ripple, "A")
    )

  @override
  def generate(self) -> None:
    super().generate()
    values = self._calculate_parameters(self.get(self.input_voltage), self.get(self.output_voltage),
                                        self.get(self.frequency), self.get(self.output_current),
                                        self.get(self.sw_current_limits), self.get(self.ripple_ratio),
                                        self.get(self.input_voltage_ripple), self.get(self.output_voltage_ripple),
                                        efficiency=self.get(self.efficiency),
                                        dutycycle_limit=self.get(self.dutycycle_limit))
    self.assign(self.actual_dutycycle, values.dutycycle)
    self.require(values.dutycycle == values.effective_dutycycle, "dutycycle outside limit")

    self.inductor = self.Block(Inductor(
      inductance=values.inductance * Henry,
      current=values.inductor_avg_current,  # min-bound only, the real filter happens in the filter_fn
      frequency=self.frequency,
      experimental_filter_fn=ExperimentalUserFnPartsTable.serialize_fn(
        BuckConverterPowerPath._buck_inductor_filter,
        values.inductor_avg_current.upper, values.ripple_scale, values.min_ripple)
    ))
    self.assign(self.actual_inductor_current_ripple, values.ripple_scale / self.inductor.actual_inductance)
    self.assign(self.actual_inductor_current_peak,
                values.inductor_avg_current + self.actual_inductor_current_ripple / 2)

    self.connect(self.pwr_in, self.inductor.a.adapt_to(VoltageSink(
      current_draw=values.inductor_avg_current
    )))
    self.connect(self.switch, self.inductor.b.adapt_to(VoltageSource(
      voltage_out=self.output_voltage,
      current_limits=BuckConverterPowerPath._ilim_expr(self.inductor.actual_current_rating, self.sw_current_limits,
                                                       self.actual_inductor_current_ripple)
                     * (1 - values.effective_dutycycle.upper)
    )))

    self.in_cap = self.Block(DecouplingCapacitor(
      capacitance=values.input_capacitance * Farad,
      exact_capacitance=True
    )).connected(self.gnd, self.pwr_in)

    self.out_cap = self.Block(DecouplingCapacitor(
      capacitance=values.output_capacitance * Farad,
      exact_capacitance=True
    )).connected(self.gnd, self.pwr_out)


@abstract_block_default(lambda: IdealVoltageRegulator)
class BuckBoostConverter(SwitchingVoltageRegulator):
  """Step-up or switch-down switching converter"""


@abstract_block_default(lambda: IdealVoltageRegulator)
class DiscreteBuckBoostConverter(BuckBoostConverter):
  """Category for discrete buck-boost converter subcircuits (as opposed to integrated components)"""


class IdealVoltageRegulator(Resettable, DiscreteBuckBoostConverter, IdealModel):
  """Ideal buck-boost / general DC-DC converter producing the spec output voltage
  and drawing input current from conversation of power"""
  @override
  def contents(self) -> None:
    super().contents()
    self.gnd.init_from(Ground())
    self.pwr_in.init_from(VoltageSink(
      current_draw=self.output_voltage / self.pwr_in.link().voltage * self.pwr_out.link().current_drawn))
    self.pwr_out.init_from(VoltageSource(
      voltage_out=self.output_voltage))
    self.reset.init_from(DigitalSink())


class BuckBoostConverterPowerPath(InternalSubcircuit, GeneratorBlock):
  """A helper block to generate the power path (inductors, capacitors) for a 4-switch buck-boost converter.

  Main assumptions in component sizing
  - Operating only in continuous mode, TODO: also consider boundary and discontinuous mode
  - TODO: account for capacitor ESR?

  Useful resources:
  https://www.ti.com/lit/an/slva535b/slva535b.pdf
    Largely based on this document, the tl;dr of which is combine the buck and boost equations
  """
  def __init__(self, input_voltage: RangeLike, output_voltage: RangeLike, frequency: RangeLike,
               output_current: RangeLike, sw_current_limits: RangeLike, *,
               efficiency: RangeLike = (0.8, 1.0),  # from TI reference
               input_voltage_ripple: FloatLike = 75*mVolt,
               output_voltage_ripple: FloatLike = 25*mVolt,  # arbitrary
               ripple_ratio: RangeLike = Range.all()):
    super().__init__()

    self.pwr_in = self.Port(VoltageSink.empty(), [Power])  # no modeling, input cap only
    self.switch_in = self.Port(VoltageSink.empty())  # models input / inductor avg. current draw
    self.switch_out = self.Port(VoltageSource.empty())  # models maximum output avg. current
    self.pwr_out = self.Port(VoltageSink.empty())  # no modeling, output cap only
    self.gnd = self.Port(Ground.empty(), [Common])

    self.input_voltage = self.ArgParameter(input_voltage)
    self.output_voltage = self.ArgParameter(output_voltage)
    self.frequency = self.ArgParameter(frequency)
    self.output_current = self.ArgParameter(output_current)
    self.sw_current_limits = self.ArgParameter(sw_current_limits)
    self.efficiency = self.ArgParameter(efficiency)
    self.input_voltage_ripple = self.ArgParameter(input_voltage_ripple)
    self.output_voltage_ripple = self.ArgParameter(output_voltage_ripple)
    self.ripple_ratio = self.ArgParameter(ripple_ratio)  # only used to force a ripple ratio at the actual currents

    # duty cycle limits not supported, since the crossover point has a dutycycle of 0 (boost) and 1 (buck)
    self.generator_param(self.input_voltage, self.output_voltage, self.frequency, self.output_current,
                         self.sw_current_limits, self.input_voltage_ripple, self.output_voltage_ripple,
                         self.efficiency, self.ripple_ratio)

    self.actual_buck_dutycycle = self.Parameter(RangeExpr())  # possible actual duty cycle in buck mode
    self.actual_boost_dutycycle = self.Parameter(RangeExpr())  # possible actual duty cycle in boost mode
    self.actual_inductor_current_ripple = self.Parameter(RangeExpr())
    self.actual_inductor_current_peak = self.Parameter(RangeExpr())  # inductor current accounting for ripple (upper is peak)

  @override
  def contents(self) -> None:
    super().contents()

    self.description = DescriptionString(
      "<b>duty cycle:</b> ", DescriptionString.FormatUnits(self.actual_buck_dutycycle, ""), " (buck)",
      ", ", DescriptionString.FormatUnits(self.actual_boost_dutycycle, ""), " (boost)\n",
      "<b>output current avg:</b> ", DescriptionString.FormatUnits(self.output_current, "A"),
      ", <b>ripple:</b> ", DescriptionString.FormatUnits(self.actual_inductor_current_ripple, "A")
    )

  @override
  def generate(self) -> None:
    super().generate()
    buck_values = BuckConverterPowerPath._calculate_parameters(
      self.get(self.input_voltage), self.get(self.output_voltage),
      self.get(self.frequency), self.get(self.output_current),
      self.get(self.sw_current_limits), self.get(self.ripple_ratio),
      self.get(self.input_voltage_ripple), self.get(self.output_voltage_ripple),
      efficiency=self.get(self.efficiency), dutycycle_limit=Range(0, 1))
    boost_values = BoostConverterPowerPath._calculate_parameters(
      self.get(self.input_voltage), self.get(self.output_voltage),
      self.get(self.frequency), self.get(self.output_current),
      self.get(self.sw_current_limits), self.get(self.ripple_ratio),
      self.get(self.input_voltage_ripple), self.get(self.output_voltage_ripple),
      efficiency=self.get(self.efficiency), dutycycle_limit=Range(0, 1))
    self.assign(self.actual_buck_dutycycle, buck_values.effective_dutycycle)
    self.assign(self.actual_boost_dutycycle, boost_values.effective_dutycycle)

    combined_ripple_scale = max(buck_values.ripple_scale, boost_values.ripple_scale)
    combined_inductor_avg_current = boost_values.inductor_avg_current.hull(boost_values.inductor_avg_current)
    combined_min_ripple = max(buck_values.min_ripple, boost_values.min_ripple)

    self.inductor = self.Block(Inductor(
      inductance=buck_values.inductance.intersect(boost_values.inductance) * Henry,
      current=buck_values.inductor_avg_current.hull(boost_values.inductor_avg_current),
      frequency=self.frequency,
      experimental_filter_fn=ExperimentalUserFnPartsTable.serialize_fn(
        BuckConverterPowerPath._buck_inductor_filter,
        combined_inductor_avg_current.upper, combined_ripple_scale, combined_min_ripple)
    ))
    self.connect(self.switch_in, self.inductor.a.adapt_to(VoltageSink(
      current_draw=combined_inductor_avg_current
    )))
    self.connect(self.switch_out, self.inductor.b.adapt_to(VoltageSource(
      voltage_out=self.output_voltage,
      current_limits=BuckConverterPowerPath._ilim_expr(self.inductor.actual_current_rating, self.sw_current_limits,
                                                       self.actual_inductor_current_ripple)
                     * (1 - boost_values.effective_dutycycle.upper)
    )))
    self.assign(self.actual_inductor_current_ripple, combined_ripple_scale / self.inductor.actual_inductance)
    self.assign(self.actual_inductor_current_peak,
                combined_inductor_avg_current + self.actual_inductor_current_ripple / 2)

    self.in_cap = self.Block(DecouplingCapacitor(
      capacitance=buck_values.input_capacitance.intersect(boost_values.input_capacitance) * Farad,
      exact_capacitance=True
    )).connected(self.gnd, self.pwr_in)
    self.out_cap = self.Block(DecouplingCapacitor(
      capacitance=(Range.exact(float('inf')) * Farad).hull(
        (buck_values.output_capacitance_scale * self.actual_inductor_current_ripple.upper()).max(
        boost_values.output_capacitance.lower)
      ),
      exact_capacitance=True
    )).connected(self.gnd, self.pwr_out)
