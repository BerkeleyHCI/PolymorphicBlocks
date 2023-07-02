from __future__ import annotations

from typing import Optional, Union, Tuple
from edg_core import *
from edg_core.Blocks import DescriptionString
from .CircuitBlock import CircuitLink, CircuitPortBridge, CircuitPortAdapter
from .VoltagePorts import CircuitPort, VoltageLink, VoltageSource
from .Units import Volt


class DigitalLink(CircuitLink):
  """A link for digital IOs. Because of the wide variations on digital IOs, this is kind of a beast.

  Overall, this means a port that deals with signals that can be driven to two levels, high or low.
  The types of ports are:
  - Source: can drive both high or low, but not read.
  - Single source: can drive either high or low, but not the other, and cannot read.
    Example: open-drain outputs, pull-up resistors.
  - Sink: cannot drive, but can read.
  - Bidir: can drive both high and low, and can read.

  Single sources are complex, since they require a complementary weak signal driver (pull-up).
  Pull-ups can either be explicit (discrete resistor) or part of a Bidir (configurable pull-ups
  are common on many microcontroller pins).

  Weak signal drivers (pull up resistors) do not need a complementary single source, since they
  may simply be used to provide a default.
  """
  # can't subclass VoltageLink because the constraint behavior is slightly different with presence of Bidir

  def __init__(self) -> None:
    super().__init__()

    self.source = self.Port(DigitalSource(), optional=True)
    self.single_sources = self.Port(Vector(DigitalSingleSource()), optional=True)
    self.sinks = self.Port(Vector(DigitalSink()), optional=True)
    self.bidirs = self.Port(Vector(DigitalBidir()), optional=True)

    # TODO RangeBuilder initializer for voltage
    self.voltage = self.Parameter(RangeExpr())

    self.voltage_limits = self.Parameter(RangeExpr())

    self.current_drawn = self.Parameter(RangeExpr())
    self.current_limits = self.Parameter(RangeExpr())

    self.output_thresholds = self.Parameter(RangeExpr())
    self.input_thresholds = self.Parameter(RangeExpr())

    self.pullup_capable = self.Parameter(BoolExpr())
    self.pulldown_capable = self.Parameter(BoolExpr())

    # these are only used for internal checks
    self._has_low_signal_driver = self.Parameter(BoolExpr())
    self._has_high_signal_driver = self.Parameter(BoolExpr())

    # these are only used for defining bridges
    # TODO can these be moved into the bridge only so they're not evaluated everywhere?
    self._only_low_single_source_driver = self.Parameter(BoolExpr())
    self._only_high_single_source_driver = self.Parameter(BoolExpr())

  def contents(self):
    super().contents()

    self.description = DescriptionString(
      "<b>voltage</b>: ", DescriptionString.FormatUnits(self.voltage, "V"),
      " <b>of limits</b>: ", DescriptionString.FormatUnits(self.voltage_limits, "V"),
      "\n<b>current</b>: ", DescriptionString.FormatUnits(self.current_drawn, "A"),
      " <b>of limits</b>: ", DescriptionString.FormatUnits(self.current_limits, "A"),
      "\n<b>output thresholds</b>: ", DescriptionString.FormatUnits(self.output_thresholds, "V"),
      ", <b>input thresholds</b>: ", DescriptionString.FormatUnits(self.input_thresholds, "V"))

    self.require(self.source.is_connected() | (self.single_sources.length() > 0) | (self.bidirs.length() > 0),
                 "DigitalLink must have some kind of source")

    # TODO clean this up, massively, like, this needs new constructs to simplify this pattern
    voltage_hull = self.bidirs.hull(lambda x: x.voltage_out)
    voltage_hull = self.single_sources.any_connected().then_else(
      voltage_hull.hull(self.single_sources.hull(lambda x: x.voltage_out)),
      voltage_hull
    )
    voltage_hull = self.source.is_connected().then_else(
      voltage_hull.hull(self.source.voltage_out),
      voltage_hull
    )
    self.assign(self.voltage, voltage_hull)

    self.assign(self.voltage_limits,
      self.sinks.intersection(lambda x: x.voltage_limits).intersect(self.bidirs.intersection(lambda x: x.voltage_limits))
    )
    self.require(self.voltage_limits.contains(self.voltage), "overvoltage")

    self.assign(self.current_drawn,
      self.sinks.sum(lambda x: x.current_draw) + self.bidirs.sum(lambda x: x.current_draw)
    )
    self.assign(self.current_limits, self.source.is_connected().then_else(
      self.source.current_limits.intersect(self.bidirs.intersection(lambda x: x.current_limits)),
      self.bidirs.intersection(lambda x: x.current_limits)
      )
    )
    self.require(self.current_limits.contains(self.current_drawn), "overcurrent")

    source_output_thresholds = self.source.is_connected().then_else(  # TODO: clean up
      self.source.output_thresholds,
      RangeExpr.ALL * Volt
    )
    bidirs_output_thresholds = self.bidirs.any_connected().then_else(
      self.bidirs.intersection(lambda x: x.output_thresholds),
      RangeExpr.ALL * Volt
    )
    single_output_thresholds = self.single_sources.any_connected().then_else(
      self.single_sources.intersection(lambda x: x.output_thresholds),
      RangeExpr.ALL * Volt
    )
    self.assign(self.output_thresholds,
                source_output_thresholds.intersect(
                  bidirs_output_thresholds.intersect(
                    single_output_thresholds)))

    self.assign(self.input_thresholds,
      self.sinks.hull(lambda x: x.input_thresholds).hull(self.bidirs.hull(lambda x: x.input_thresholds)),
    )
    self.require(self.output_thresholds.contains(self.input_thresholds), "incompatible digital thresholds")

    self.assign(self.pullup_capable,
                self.bidirs.any(lambda x: x.pullup_capable) |
                self.source.is_connected().then_else(self.source.pullup_capable,
                                                     BoolExpr._to_expr_type(False)) |
                self.single_sources.any(lambda x: x.pullup_capable))
    self.assign(self.pulldown_capable,
                self.bidirs.any(lambda x: x.pulldown_capable) |
                self.source.is_connected().then_else(self.source.pulldown_capable,
                                                     BoolExpr._to_expr_type(False)) |
                self.single_sources.any(lambda x: x.pulldown_capable))
    self.assign(self._has_low_signal_driver,
                self.single_sources.any_connected().then_else(
                  self.single_sources.any(lambda x: x.low_signal_driver),
                  BoolExpr._to_expr_type(False)
                ))
    self.assign(self._has_high_signal_driver,
                self.single_sources.any_connected().then_else(
                  self.single_sources.any(lambda x: x.high_signal_driver),
                  BoolExpr._to_expr_type(False)
                ))
    self.require(self._has_low_signal_driver.implies(self.pullup_capable), "requires pullup capable connection")
    self.require(self._has_high_signal_driver.implies(self.pulldown_capable), "requires pulldown capable connection")

    only_single_source_driver = ~self.source.is_connected() & (self.bidirs.length() == 1) & \
                                (self.single_sources.length() > 0)
    self.assign(self._only_high_single_source_driver,
                only_single_source_driver &
                self.single_sources.all(lambda x: x.high_signal_driver) &
                ~self.single_sources.all(lambda x: x.low_signal_driver))
    self.assign(self._only_low_single_source_driver,
                only_single_source_driver &
                ~self.single_sources.all(lambda x: x.high_signal_driver) &
                self.single_sources.all(lambda x: x.low_signal_driver))


class DigitalBase(CircuitPort[DigitalLink]):
  link_type = DigitalLink


class DigitalSinkBridge(CircuitPortBridge):
  def __init__(self) -> None:
    super().__init__()

    self.outer_port = self.Port(DigitalSink(voltage_limits=RangeExpr(),
                                            current_draw=RangeExpr(),
                                            input_thresholds=RangeExpr()))

    # TODO can we actually define something here? as a pseudoport, this doesn't have limits
    self.inner_link = self.Port(DigitalSource(current_limits=RangeExpr.ALL,
                                              voltage_out=RangeExpr(),
                                              output_thresholds=RangeExpr()))

  def contents(self) -> None:
    super().contents()

    self.assign(self.outer_port.voltage_limits, self.inner_link.link().voltage_limits)
    self.assign(self.outer_port.current_draw, self.inner_link.link().current_drawn)
    self.assign(self.inner_link.voltage_out, self.outer_port.link().voltage)

    self.assign(self.inner_link.output_thresholds, self.outer_port.link().output_thresholds)
    self.assign(self.outer_port.input_thresholds, self.inner_link.link().input_thresholds)


class DigitalSink(DigitalBase):
  bridge_type = DigitalSinkBridge

  @staticmethod
  def from_supply(neg: Port[VoltageLink], pos: Port[VoltageLink], *,
                  voltage_limit_abs: Optional[RangeLike] = None,
                  voltage_limit_tolerance: Optional[RangeLike] = None,
                  current_draw: RangeLike = RangeExpr.ZERO,
                  input_threshold_factor: Optional[RangeLike] = None,
                  input_threshold_abs: Optional[RangeLike] = None) -> DigitalSink:
    voltage_limit: RangeLike
    if voltage_limit_abs is not None:
      assert voltage_limit_tolerance is None
      voltage_limit = voltage_limit_abs
    elif voltage_limit_tolerance is not None:
      voltage_limit = neg.link().voltage.hull(pos.link().voltage) + \
                      RangeExpr._to_expr_type(voltage_limit_tolerance)
    else:  # generic default
      voltage_limit = neg.link().voltage.hull(pos.link().voltage) + \
                      RangeExpr._to_expr_type((-0.3, 0.3))

    input_threshold: RangeLike
    if input_threshold_factor is not None:
      assert input_threshold_abs is None, "can only specify one input threshold type"
      input_threshold_factor = RangeExpr._to_expr_type(input_threshold_factor)  # TODO avoid internal functions?
      input_threshold = pos.link().voltage * input_threshold_factor
    elif input_threshold_abs is not None:
      assert input_threshold_factor is None, "can only specify one input threshold type"
      input_threshold = RangeExpr._to_expr_type(input_threshold_abs)  # TODO avoid internal functions?
    else:
      raise ValueError("no input threshold specified")

    return DigitalSink(  # TODO get rid of to_expr_type w/ dedicated Range conversion
      voltage_limits=neg.link().voltage.hull(pos.link().voltage) + \
                     RangeExpr._to_expr_type(voltage_limit),
      current_draw=current_draw,
      input_thresholds=input_threshold
    )

  @staticmethod
  def from_bidir(model: DigitalBidir) -> DigitalSink:
    return DigitalSink(model.voltage_limits, model.current_draw, input_thresholds=model.input_thresholds)

  def __init__(self, voltage_limits: RangeLike = RangeExpr.ALL,
               current_draw: RangeLike = RangeExpr.ZERO, *,
               input_thresholds: RangeLike = RangeExpr.EMPTY) -> None:
    super().__init__()
    self.voltage_limits: RangeExpr = self.Parameter(RangeExpr(voltage_limits))
    self.current_draw: RangeExpr = self.Parameter(RangeExpr(current_draw))
    self.input_thresholds: RangeExpr = self.Parameter(RangeExpr(input_thresholds))


class DigitalSourceBridge(CircuitPortBridge):
  def __init__(self) -> None:
    super().__init__()

    self.outer_port = self.Port(DigitalSource(voltage_out=RangeExpr(),
                                              current_limits=RangeExpr(),
                                              output_thresholds=RangeExpr()))

    # Here we ignore the voltage_limits of the inner port, instead relying on the main link to handle it
    # The outer port's current_limits is untouched and should be defined in tte port def.
    # TODO: it's a slightly optimization to handle them here. Should it be done?
    # TODO: or maybe current_limits / voltage_limits shouldn't be a port, but rather a block property?
    self.inner_link = self.Port(DigitalSink(voltage_limits=RangeExpr.ALL,
                                            current_draw=RangeExpr(),
                                            input_thresholds=RangeExpr.EMPTY))

  def contents(self) -> None:
    super().contents()

    self.assign(self.outer_port.voltage_out, self.inner_link.link().voltage)
    self.assign(self.outer_port.current_limits, self.inner_link.link().current_limits)  # TODO subtract internal current drawn
    self.assign(self.inner_link.current_draw, self.outer_port.link().current_drawn)

    self.assign(self.outer_port.output_thresholds, self.inner_link.link().output_thresholds)


class DigitalSourceAdapterVoltageSource(CircuitPortAdapter[VoltageSource]):
  @init_in_parent
  def __init__(self):
    super().__init__()
    self.src = self.Port(DigitalSink(  # otherwise ideal
      current_draw=RangeExpr()
    ))
    self.dst = self.Port(VoltageSource(
      voltage_out=self.src.link().voltage,
      current_limits=(-float('inf'), float('inf'))))
    self.assign(self.src.current_draw, self.dst.link().current_drawn)


class DigitalSource(DigitalBase):
  bridge_type = DigitalSourceBridge

  @staticmethod
  def from_supply(neg: Port[VoltageLink], pos: Port[VoltageLink],
                  current_limits: RangeLike = RangeExpr.ALL, *,
                  output_threshold_offset: Optional[Tuple[FloatLike, FloatLike]] = None) -> DigitalSource:
    if output_threshold_offset is not None:
      output_offset_low = FloatExpr._to_expr_type(output_threshold_offset[0])
      output_offset_high = FloatExpr._to_expr_type(output_threshold_offset[1])
      output_threshold = (neg.link().voltage.upper() + output_offset_low,
                          pos.link().voltage.lower() + output_offset_high)
    else:
      output_threshold = (neg.link().voltage.upper(), pos.link().voltage.lower())

    return DigitalSource(
      voltage_out=(neg.link().voltage.lower(), pos.link().voltage.upper()),
      current_limits=current_limits,
      output_thresholds=output_threshold
    )

  @staticmethod
  def from_bidir(model: DigitalBidir) -> DigitalSource:
    return DigitalSource(model.voltage_out, model.current_limits, output_thresholds=model.output_thresholds,
                         pullup_capable=model.pullup_capable, pulldown_capable=model.pulldown_capable)

  def __init__(self, voltage_out: RangeLike = RangeExpr.ZERO,
               current_limits: RangeLike = RangeExpr.ALL, *,
               output_thresholds: RangeLike = RangeExpr.ALL,
               pullup_capable: BoolLike = False,
               pulldown_capable: BoolLike = False) -> None:
    super().__init__()
    self.voltage_out: RangeExpr = self.Parameter(RangeExpr(voltage_out))
    self.current_limits: RangeExpr = self.Parameter(RangeExpr(current_limits))
    self.output_thresholds: RangeExpr = self.Parameter(RangeExpr(output_thresholds))

    self.pullup_capable: BoolExpr = self.Parameter(BoolExpr(pullup_capable))
    self.pulldown_capable: BoolExpr = self.Parameter(BoolExpr(pulldown_capable))

  def as_voltage_source(self) -> VoltageSource:
    return self._convert(DigitalSourceAdapterVoltageSource())


class DigitalBidirBridge(CircuitPortBridge):
  def __init__(self) -> None:
    super().__init__()

    self.outer_port = self.Port(DigitalBidir(voltage_out=RangeExpr(), current_draw=RangeExpr(),
                                             voltage_limits=RangeExpr(), current_limits=RangeExpr(),
                                             output_thresholds=RangeExpr(), input_thresholds=RangeExpr(),
                                             # TODO see issue 58, how do we propagate this in both directions?
                                             # pulldown_capable=BoolExpr(), pullup_capable=BoolExpr(),
                                             ))
    # TODO can we actually define something here? as a pseudoport, this doesn't have limits
    self.inner_link = self.Port(DigitalBidir(voltage_limits=RangeExpr.ALL, current_limits=RangeExpr.ALL,
                                             pulldown_capable=BoolExpr(), pullup_capable=BoolExpr(),
                                             ))

  def contents(self) -> None:
    super().contents()

    self.assign(self.outer_port.voltage_out, self.inner_link.link().voltage)
    self.assign(self.outer_port.current_draw, self.inner_link.link().current_drawn)
    self.assign(self.outer_port.voltage_limits, self.inner_link.link().voltage_limits)
    self.assign(self.outer_port.current_limits, self.inner_link.link().current_limits)  # TODO compensate for internal current draw

    self.assign(self.outer_port.output_thresholds, self.inner_link.link().output_thresholds)
    self.assign(self.outer_port.input_thresholds, self.inner_link.link().input_thresholds)

    # TODO this is a hacktastic in that it's not bidirectional, but it serves the use case for the USB PD CC case
    # TODO this is a bit hacky, but allows a externally disconnected port
    self.assign(self.inner_link.pullup_capable, self.outer_port.is_connected().then_else(
      self.outer_port.link().pullup_capable, BoolExpr._to_expr_type(False)))
    self.assign(self.inner_link.pulldown_capable, self.outer_port.is_connected().then_else(
      self.outer_port.link().pulldown_capable, BoolExpr._to_expr_type(False)))
    # TODO see issue 58, how do we propagate this in both directions?
    # self.assign(self.outer_port.pullup_capable, self.inner_link.link().pullup_capable)
    # self.assign(self.outer_port.pulldown_capable, self.inner_link.link().pulldown_capable)


class DigitalBidirNotConnected(InternalBlock, Block):
  """Not-connected dummy block for Digital bidir ports"""
  def __init__(self) -> None:
    super().__init__()
    self.port = self.Port(DigitalBidir(), [InOut])


class DigitalBidir(DigitalBase):
  bridge_type = DigitalBidirBridge
  not_connected_type = DigitalBidirNotConnected

  @staticmethod
  def from_supply(neg: Port[VoltageLink], pos: Port[VoltageLink],
                  voltage_limit_abs: Optional[RangeLike] = None,
                  voltage_limit_tolerance: Optional[RangeLike] = None,
                  current_draw: RangeLike = RangeExpr.ZERO,
                  current_limits: RangeLike = RangeExpr.ALL, *,
                  input_threshold_factor: Optional[RangeLike] = None,
                  input_threshold_abs: Optional[RangeLike] = None,
                  output_threshold_factor: Optional[RangeLike] = None,
                  pullup_capable: BoolLike = False, pulldown_capable: BoolLike = False) -> DigitalBidir:
    voltage_limit: RangeLike
    if voltage_limit_abs is not None:
      assert voltage_limit_tolerance is None
      voltage_limit = voltage_limit_abs
    elif voltage_limit_tolerance is not None:
      voltage_limit = neg.link().voltage.hull(pos.link().voltage) + \
                      RangeExpr._to_expr_type(voltage_limit_tolerance)
    else:  # generic default
      voltage_limit = neg.link().voltage.hull(pos.link().voltage) + \
                      RangeExpr._to_expr_type((-0.3, 0.3))

    input_threshold: RangeLike
    if input_threshold_factor is not None:
      assert input_threshold_abs is None, "can only specify one input threshold type"
      input_threshold_factor = RangeExpr._to_expr_type(input_threshold_factor)  # TODO avoid internal functions?
      input_threshold = pos.link().voltage * input_threshold_factor
    elif input_threshold_abs is not None:
      assert input_threshold_factor is None, "can only specify one input threshold type"
      input_threshold = RangeExpr._to_expr_type(input_threshold_abs)  # TODO avoid internal functions?
    else:
      raise ValueError("no input threshold specified")

    if output_threshold_factor is not None:
      output_threshold_factor = RangeExpr._to_expr_type(output_threshold_factor)
      output_threshold = (output_threshold_factor.lower() * pos.link().voltage.upper(),
                          output_threshold_factor.upper() * pos.link().voltage.lower())
    else:  # assumed ideal
      output_threshold = (neg.link().voltage.upper(), pos.link().voltage.lower())

    return DigitalBidir(  # TODO get rid of to_expr_type w/ dedicated Range conversion
      voltage_limits=voltage_limit,
      current_draw=current_draw,
      voltage_out=(neg.link().voltage.upper(), pos.link().voltage.lower()),
      current_limits=current_limits,
      input_thresholds=input_threshold,
      output_thresholds=output_threshold,
      pullup_capable=pullup_capable, pulldown_capable=pulldown_capable
    )

  def __init__(self, *, voltage_limits: RangeLike = RangeExpr.ALL,
               current_draw: RangeLike = RangeExpr.ZERO,
               voltage_out: RangeLike = RangeExpr.ZERO,
               current_limits: RangeLike = RangeExpr.ALL,
               input_thresholds: RangeLike = RangeExpr.EMPTY,
               output_thresholds: RangeLike = RangeExpr.ALL,
               pullup_capable: BoolLike = False,
               pulldown_capable: BoolLike = False) -> None:
    super().__init__()
    self.voltage_limits: RangeExpr = self.Parameter(RangeExpr(voltage_limits))
    self.current_draw: RangeExpr = self.Parameter(RangeExpr(current_draw))
    self.voltage_out: RangeExpr = self.Parameter(RangeExpr(voltage_out))
    self.current_limits: RangeExpr = self.Parameter(RangeExpr(current_limits))
    self.input_thresholds: RangeExpr = self.Parameter(RangeExpr(input_thresholds))
    self.output_thresholds: RangeExpr = self.Parameter(RangeExpr(output_thresholds))

    self.pullup_capable: BoolExpr = self.Parameter(BoolExpr(pullup_capable))
    self.pulldown_capable: BoolExpr = self.Parameter(BoolExpr(pulldown_capable))

  def as_open_drain(self) -> DigitalSingleSource:
    """Adapts this DigitalBidir to a DigitalSingleSource open-drain (low-side-only) driver.
    Not that not all digital ports can be driven in open-drain mode, check your particular IO's capabilities."""
    return self._convert(DigitalBidirAdapterOpenDrain())


class DigitalSingleSourceBridge(CircuitPortBridge):
  def __init__(self) -> None:
    super().__init__()

    self.outer_port = self.Port(DigitalSingleSource(
      voltage_out=RangeExpr(),
      output_thresholds=RangeExpr(),
      pulldown_capable=False,
      pullup_capable=False,
      low_signal_driver=BoolExpr(),
      high_signal_driver=BoolExpr(),
    ))

    self.inner_link = self.Port(DigitalBidir(
      voltage_out=RangeExpr.EMPTY,  # don't contribute to the link voltage
      voltage_limits=RangeExpr.ALL,
      current_draw=RangeExpr.ZERO,  # single source does not draw any current
      input_thresholds=RangeExpr.EMPTY,
      output_thresholds=RangeExpr.ALL,  # don't contribute to the link thresholds
      pulldown_capable=True, pullup_capable=True  # ideal port, checked at upper link
    ))

  def contents(self) -> None:
    super().contents()

    self.assign(self.outer_port.voltage_out, self.inner_link.link().voltage)
    self.assign(self.outer_port.output_thresholds, self.inner_link.link().output_thresholds)
    self.assign(self.outer_port.low_signal_driver, self.inner_link.link()._only_low_single_source_driver)
    self.assign(self.outer_port.high_signal_driver, self.inner_link.link()._only_high_single_source_driver)
    self.require(self.outer_port.low_signal_driver | self.outer_port.high_signal_driver &
                 ~(self.outer_port.low_signal_driver & self.outer_port.high_signal_driver),
                 "must have either (exclusive or) high or low signal drivers internally")


class DigitalSingleSource(DigitalBase):
  bridge_type = DigitalSingleSourceBridge

  @staticmethod
  def low_from_supply(neg: Port[VoltageLink], is_pulldown: bool = False) -> DigitalSingleSource:
    return DigitalSingleSource(
      voltage_out=neg.link().voltage,
      output_thresholds=(neg.link().voltage.upper(), float('inf')),
      pulldown_capable=is_pulldown,
      low_signal_driver=not is_pulldown
    )

  @staticmethod
  def high_from_supply(pos: Port[VoltageLink], is_pullup: bool = False) -> DigitalSingleSource:
    return DigitalSingleSource(
      voltage_out=pos.link().voltage,
      output_thresholds=(-float('inf'), pos.link().voltage.lower()),
      pullup_capable=is_pullup,
      high_signal_driver=not is_pullup
    )

  def __init__(self, voltage_out: RangeLike = RangeExpr.ZERO,
               output_thresholds: RangeLike = RangeExpr.ALL, *,
               pullup_capable: BoolLike = False,
               pulldown_capable: BoolLike = False,
               low_signal_driver: BoolLike = False,
               high_signal_driver: BoolLike = False) -> None:
    super().__init__()

    self.voltage_out: RangeExpr = self.Parameter(RangeExpr(voltage_out))
    self.output_thresholds: RangeExpr = self.Parameter(RangeExpr(output_thresholds))

    self.pullup_capable = self.Parameter(BoolExpr(pullup_capable))
    self.pulldown_capable = self.Parameter(BoolExpr(pulldown_capable))

    self.low_signal_driver = self.Parameter(BoolExpr(low_signal_driver))
    self.high_signal_driver = self.Parameter(BoolExpr(high_signal_driver))


class DigitalBidirAdapterOpenDrain(CircuitPortAdapter[DigitalSingleSource]):
  """Adapter where a DigitalBidir is run as an open-drain (low-side single source) port."""
  @init_in_parent
  def __init__(self):
    super().__init__()
    self.src = self.Port(DigitalBidir(  # otherwise ideal
      voltage_out=RangeExpr(),
      current_draw=RangeExpr()
    ))
    self.dst = self.Port(DigitalSingleSource(
      voltage_out=(0, 0)*Volt,  # TODO should propagate from src voltage lower, but creates a circular dependency
      output_thresholds=(self.src.link().output_thresholds.lower(), float('inf')),
      pulldown_capable=False,
      low_signal_driver=True
    ))
    self.assign(self.src.voltage_out, self.dst.link().voltage)
    self.assign(self.src.current_draw, self.dst.link().current_drawn)
