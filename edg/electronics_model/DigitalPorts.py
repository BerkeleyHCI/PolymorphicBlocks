from __future__ import annotations

from typing import Optional, Tuple

from deprecated import deprecated

from ..core import *
from .CircuitBlock import CircuitLink, CircuitPortBridge, CircuitPortAdapter
from .GroundPort import GroundLink
from .VoltagePorts import CircuitPort, VoltageLink, VoltageSource
from .Units import Volt


class DigitalLink(CircuitLink):
  """A link for digital IOs. Because of the wide variations on digital IOs, this is kind of a beast.

  Overall, this means a port that deals with signals that can be driven to two levels, high or low.
  Directionality is modeled as signal dataflow.
  The types of ports are:
  - Source: can drive high and/or low (including push-pull, pull-up, and open-drain), but can't read.
    Push-pull sources assumed not able to tri-state and cannot share the line with other push-pull drivers.
  - Sink: cannot drive, but can read.
  - Bidir: can drive both high and low, and can read. Can tri-state, and assumed ports are configured to not conflict.

  Sources can be modeled as high and/or low-side drivers. If not push-pull, an opposite-polarity pull is required.
  Pulls do not need a complementary driver and can be used to provide a default state.
  Sources and bidir are modeled as being pull-capable.
  """
  # can't subclass VoltageLink because the constraint behavior is slightly different with presence of Bidir

  def __init__(self) -> None:
    super().__init__()

    self.sources = self.Port(Vector(DigitalSource()), optional=True)
    self.sinks = self.Port(Vector(DigitalSink()), optional=True)
    self.bidirs = self.Port(Vector(DigitalBidir()), optional=True)

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

  def contents(self):
    super().contents()

    self.description = DescriptionString(
      "<b>voltage</b>: ", DescriptionString.FormatUnits(self.voltage, "V"),
      " <b>of limits</b>: ", DescriptionString.FormatUnits(self.voltage_limits, "V"),
      "\n<b>current</b>: ", DescriptionString.FormatUnits(self.current_drawn, "A"),
      " <b>of limits</b>: ", DescriptionString.FormatUnits(self.current_limits, "A"),
      "\n<b>output thresholds</b>: ", DescriptionString.FormatUnits(self.output_thresholds, "V"),
      ", <b>input thresholds</b>: ", DescriptionString.FormatUnits(self.input_thresholds, "V"))

    # TODO clean this up, massively, like, this needs new constructs to simplify this pattern
    voltage_hull = self.bidirs.hull(lambda x: x.voltage_out)
    voltage_hull = self.sources.any_connected().then_else(
      voltage_hull.hull(self.sources.hull(lambda x: x.voltage_out)),
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
    self.assign(self.current_limits,
                self.sources.intersection(lambda x: x.current_limits)
                .intersect(self.bidirs.intersection(lambda x: x.current_limits)))
    self.require(self.current_limits.contains(self.current_drawn), "overcurrent")

    self.assign(self.output_thresholds,
                self.sources.intersection(lambda x: x.output_thresholds)
                .intersect(self.bidirs.intersection(lambda x: x.output_thresholds),))
    self.assign(self.input_thresholds,
      self.sinks.hull(lambda x: x.input_thresholds).hull(self.bidirs.hull(lambda x: x.input_thresholds)),
    )
    self.require(self.output_thresholds.contains(self.input_thresholds), "incompatible digital thresholds")

    self.require(self.sources.any_connected() | (self.bidirs.length() > 0),
                 "requires connected source or bidir")

    # ensure both digital levels can be driven (but pull-up or -down only connections are allowed)
    self.assign(self.pullup_capable,
                self.sources.any(lambda x: x.pullup_capable) |
                self.sinks.any(lambda x: x.pullup_capable) |
                self.bidirs.any(lambda x: x.pullup_capable))
    self.assign(self.pulldown_capable,
                self.sources.any(lambda x: x.pulldown_capable) |
                self.sinks.any(lambda x: x.pulldown_capable) |
                self.bidirs.any(lambda x: x.pulldown_capable))
    self.assign(self._has_low_signal_driver,  # assumed bidirs are true directional drivers
                self.bidirs.any_connected() | self.sources.any(lambda x: x.low_driver))
    self.assign(self._has_high_signal_driver,
                self.bidirs.any_connected() | self.sources.any(lambda x: x.high_driver))

    is_bridged_internal = (self.sources.any(lambda x: x._bridged_internal) |
                           self.sinks.any(lambda x: x._bridged_internal) |
                           self.bidirs.any(lambda x: x._bridged_internal))
    self.require(is_bridged_internal |
                 self._has_high_signal_driver.implies(self._has_low_signal_driver | self.pulldown_capable), "requires low driver or pulldown")
    self.require(is_bridged_internal |
                 self._has_low_signal_driver.implies(self._has_high_signal_driver | self.pullup_capable), "requires high driver or pullup")

    # when multiple sources, ensure they all drive only one signal direction (eg, open drain)
    self.require((self.sources.count(lambda x: x.high_driver) > 1).implies(~self.sources.any(lambda x: x.low_driver)) &
                 (self.sources.count(lambda x: x.low_driver) > 1).implies(~self.sources.any(lambda x: x.high_driver)),
                 "conflicting source drivers")


class DigitalBase(CircuitPort[DigitalLink]):
  link_type = DigitalLink


class DigitalSinkBridge(CircuitPortBridge):
  def __init__(self) -> None:
    super().__init__()

    self.outer_port = self.Port(DigitalSink(voltage_limits=RangeExpr(),
                                            current_draw=RangeExpr(),
                                            input_thresholds=RangeExpr()))

    self.inner_link = self.Port(DigitalSource(current_limits=RangeExpr.ALL,
                                              voltage_out=RangeExpr(),
                                              output_thresholds=RangeExpr(),
                                              pullup_capable=False, pulldown_capable=False,  # don't create a loop
                                              _bridged_internal=True))

  def contents(self) -> None:
    super().contents()

    self.assign(self.outer_port.voltage_limits, self.inner_link.link().voltage_limits)
    self.assign(self.outer_port.current_draw, self.inner_link.link().current_drawn)
    self.assign(self.outer_port.input_thresholds, self.inner_link.link().input_thresholds)

    self.assign(self.inner_link.voltage_out, self.outer_port.link().voltage)
    self.assign(self.inner_link.output_thresholds, self.outer_port.link().output_thresholds)


class DigitalSink(DigitalBase):
  bridge_type = DigitalSinkBridge

  @staticmethod
  def from_supply(neg: Port[GroundLink], pos: Port[VoltageLink], *,
                  voltage_limit_abs: Optional[RangeLike] = None,
                  voltage_limit_tolerance: Optional[RangeLike] = None,
                  current_draw: RangeLike = RangeExpr.ZERO,
                  input_threshold_factor: Optional[RangeLike] = None,
                  input_threshold_abs: Optional[RangeLike] = None,
                  pullup_capable: BoolLike = False,
                  pulldown_capable: BoolLike = False) -> DigitalSink:
    supply_range = VoltageLink._supply_voltage_range(neg, pos)
    if voltage_limit_abs is not None:
      assert voltage_limit_tolerance is None
      voltage_limit: RangeLike = voltage_limit_abs
    elif voltage_limit_tolerance is not None:
      voltage_limit = supply_range + RangeExpr._to_expr_type(voltage_limit_tolerance)
    else:  # generic default
      voltage_limit = supply_range + RangeExpr._to_expr_type((-0.3, 0.3))

    input_threshold: RangeLike
    if input_threshold_factor is not None:
      assert input_threshold_abs is None, "can only specify one input threshold type"
      input_threshold_factor = RangeExpr._to_expr_type(input_threshold_factor)  # TODO avoid internal functions?
      input_threshold = pos.link().voltage * input_threshold_factor
    elif input_threshold_abs is not None:
      assert input_threshold_factor is None, "can only specify one input threshold type"
      input_threshold = RangeExpr._to_expr_type(input_threshold_abs)  # TODO avoid internal functions?
    else:
      input_threshold = RangeExpr.EMPTY  # ideal

    return DigitalSink(  # TODO get rid of to_expr_type w/ dedicated Range conversion
      voltage_limits=voltage_limit,
      current_draw=current_draw,
      input_thresholds=input_threshold,
      pullup_capable=pullup_capable,
      pulldown_capable=pulldown_capable
    )

  @staticmethod
  def from_bidir(model: DigitalBidir) -> DigitalSink:
    model_is_empty = not model._get_initializers([])
    if not model_is_empty:
      return DigitalSink(model.voltage_limits, model.current_draw, input_thresholds=model.input_thresholds,
                         pulldown_capable=model.pulldown_capable, pullup_capable=model.pullup_capable)
    else:
      return DigitalSink.empty()

  def __init__(self, voltage_limits: RangeLike = RangeExpr.ALL,
               current_draw: RangeLike = RangeExpr.ZERO, *,
               input_thresholds: RangeLike = RangeExpr.EMPTY,
               pullup_capable: BoolLike = False,
               pulldown_capable: BoolLike = False,
               _bridged_internal: BoolLike = False) -> None:
    super().__init__()
    self.voltage_limits: RangeExpr = self.Parameter(RangeExpr(voltage_limits))
    self.current_draw: RangeExpr = self.Parameter(RangeExpr(current_draw))
    self.input_thresholds: RangeExpr = self.Parameter(RangeExpr(input_thresholds))

    self.pullup_capable: BoolExpr = self.Parameter(BoolExpr(pullup_capable))
    self.pulldown_capable: BoolExpr = self.Parameter(BoolExpr(pulldown_capable))
    self._bridged_internal: BoolExpr = self.Parameter(BoolExpr(_bridged_internal))


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
                                            input_thresholds=RangeExpr.EMPTY,
                                            pullup_capable=False, pulldown_capable=False,  # don't create a loop
                                            _bridged_internal=True))

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
      voltage_out=(self.src.link().output_thresholds.upper(), self.src.link().voltage.upper())
    ))
    self.assign(self.src.current_draw, self.dst.link().current_drawn)


class DigitalSource(DigitalBase):
  bridge_type = DigitalSourceBridge

  @staticmethod
  def from_supply(neg: Port[GroundLink], pos: Port[VoltageLink],
                  current_limits: RangeLike = RangeExpr.ALL, *,
                  output_threshold_offset: Optional[Tuple[FloatLike, FloatLike]] = None) -> DigitalSource:
    supply_range = VoltageLink._supply_voltage_range(neg, pos)
    if output_threshold_offset is not None:
      output_offset_low = FloatExpr._to_expr_type(output_threshold_offset[0])
      output_offset_high = FloatExpr._to_expr_type(output_threshold_offset[1])
      output_threshold = (GroundLink._voltage_range(neg).lower() + output_offset_low,
                          VoltageLink._voltage_range(pos).lower() + output_offset_high)
    else:
      output_threshold = (GroundLink._voltage_range(neg).upper(), VoltageLink._voltage_range(pos).lower())

    return DigitalSource(
      voltage_out=supply_range,
      current_limits=current_limits,
      output_thresholds=output_threshold
    )

  @staticmethod
  def from_bidir(model: DigitalBidir) -> DigitalSource:
    model_is_empty = not model._get_initializers([])
    if not model_is_empty:  # DigitalSource has additional high_driver and low_driver fields
      return DigitalSource(model.voltage_out, model.current_limits, output_thresholds=model.output_thresholds,
                           pullup_capable=model.pullup_capable, pulldown_capable=model.pulldown_capable)
    else:
      return DigitalSource.empty()

  def __init__(self, voltage_out: RangeLike = RangeExpr.ZERO,
               current_limits: RangeLike = RangeExpr.ALL, *,
               output_thresholds: RangeLike = RangeExpr.ALL,
               high_driver: BoolLike = True,
               low_driver: BoolLike = True,
               pullup_capable: BoolLike = False,
               pulldown_capable: BoolLike = False,
               _bridged_internal: BoolLike = False) -> None:
    super().__init__()
    self.voltage_out: RangeExpr = self.Parameter(RangeExpr(voltage_out))
    self.current_limits: RangeExpr = self.Parameter(RangeExpr(current_limits))
    self.output_thresholds: RangeExpr = self.Parameter(RangeExpr(output_thresholds))

    self.high_driver: BoolExpr = self.Parameter(BoolExpr(high_driver))
    self.low_driver: BoolExpr = self.Parameter(BoolExpr(low_driver))
    self.pullup_capable: BoolExpr = self.Parameter(BoolExpr(pullup_capable))
    self.pulldown_capable: BoolExpr = self.Parameter(BoolExpr(pulldown_capable))

    self._bridged_internal: BoolExpr = self.Parameter(BoolExpr(_bridged_internal))

  @staticmethod
  def low_from_supply(neg: Port[GroundLink], *, current_limits: RangeLike = RangeExpr.ALL) -> DigitalSource:
    """Sink-only digital source, eg open-drain output"""
    return DigitalSource(
      voltage_out=neg.link().voltage,
      current_limits=current_limits,
      output_thresholds=(neg.link().voltage.upper(), float('inf')),
      high_driver=False, low_driver=True,
      pullup_capable=False, pulldown_capable=False
    )

  @staticmethod
  def high_from_supply(pos: Port[VoltageLink], *, current_limits: RangeLike = RangeExpr.ALL) -> DigitalSource:
    """Source-only digital source"""
    return DigitalSource(
      voltage_out=pos.link().voltage,
      current_limits=current_limits,
      output_thresholds=(-float('inf'), pos.link().voltage.lower()),
      high_driver=True, low_driver=False,
      pullup_capable=False, pulldown_capable=False
    )

  @staticmethod
  def pulldown_from_supply(neg: Port[GroundLink]) -> DigitalSource:
    return DigitalSource(
      voltage_out=neg.link().voltage,
      output_thresholds=(neg.link().voltage.upper(), float('inf')),
      high_driver=False, low_driver=False,
      pullup_capable=False, pulldown_capable=True
    )

  @staticmethod
  def pullup_from_supply(pos: Port[VoltageLink]) -> DigitalSource:
    return DigitalSource(
      voltage_out=pos.link().voltage,
      output_thresholds=(-float('inf'), pos.link().voltage.lower()),
      high_driver=False, low_driver=False,
      pullup_capable=True, pulldown_capable=False
    )

  def as_voltage_source(self) -> VoltageSource:
    return self._convert(DigitalSourceAdapterVoltageSource())


class DigitalBidirBridge(CircuitPortBridge):
  def __init__(self) -> None:
    super().__init__()

    self.outer_port = self.Port(DigitalBidir(voltage_out=RangeExpr(), current_draw=RangeExpr(),
                                             voltage_limits=RangeExpr(), current_limits=RangeExpr(),
                                             output_thresholds=RangeExpr(), input_thresholds=RangeExpr(),
                                             pulldown_capable=BoolExpr(), pullup_capable=BoolExpr(),
                                             ))
    # TODO can we actually define something here? as a pseudoport, this doesn't have limits
    self.inner_link = self.Port(DigitalBidir(voltage_limits=RangeExpr.ALL, current_limits=RangeExpr.ALL,
                                             pullup_capable=False, pulldown_capable=False,  # don't create a loop
                                             _bridged_internal=True
                                             ))

  def contents(self) -> None:
    super().contents()

    self.assign(self.outer_port.voltage_out, self.inner_link.link().voltage)
    self.assign(self.outer_port.current_draw, self.inner_link.link().current_drawn)
    self.assign(self.outer_port.voltage_limits, self.inner_link.link().voltage_limits)
    self.assign(self.outer_port.current_limits, self.inner_link.link().current_limits)  # TODO compensate for internal current draw

    self.assign(self.outer_port.output_thresholds, self.inner_link.link().output_thresholds)
    self.assign(self.outer_port.input_thresholds, self.inner_link.link().input_thresholds)
    self.assign(self.outer_port.pullup_capable, self.inner_link.link().pullup_capable)
    self.assign(self.outer_port.pulldown_capable, self.inner_link.link().pulldown_capable)


class DigitalBidirNotConnected(InternalBlock, Block):
  """Not-connected dummy block for Digital bidir ports"""
  def __init__(self) -> None:
    super().__init__()
    self.port = self.Port(DigitalBidir(), [InOut])


class DigitalBidir(DigitalBase):
  bridge_type = DigitalBidirBridge
  not_connected_type = DigitalBidirNotConnected

  @staticmethod
  def from_supply(neg: Port[GroundLink], pos: Port[VoltageLink],
                  voltage_limit_abs: Optional[RangeLike] = None,
                  voltage_limit_tolerance: Optional[RangeLike] = None,
                  current_draw: RangeLike = RangeExpr.ZERO,
                  current_limits: RangeLike = RangeExpr.ALL, *,
                  input_threshold_factor: Optional[RangeLike] = None,
                  input_threshold_abs: Optional[RangeLike] = None,
                  output_threshold_factor: Optional[RangeLike] = None,
                  output_threshold_abs: Optional[RangeLike] = None,
                  pullup_capable: BoolLike = False, pulldown_capable: BoolLike = False) -> DigitalBidir:
    supply_range = VoltageLink._supply_voltage_range(neg, pos)
    if voltage_limit_abs is not None:
      assert voltage_limit_tolerance is None
      voltage_limit: RangeLike = voltage_limit_abs
    elif voltage_limit_tolerance is not None:
      voltage_limit = supply_range + RangeExpr._to_expr_type(voltage_limit_tolerance)
    else:  # generic default
      voltage_limit = supply_range + RangeExpr._to_expr_type((-0.3, 0.3))

    neg_base = GroundLink._voltage_range(neg).upper()
    input_threshold: RangeLike
    if input_threshold_factor is not None:
      assert input_threshold_abs is None, "can only specify one input threshold type"
      input_threshold_factor = RangeExpr._to_expr_type(input_threshold_factor)  # TODO avoid internal functions?
      input_range = VoltageLink._voltage_range(pos).lower() - neg_base
      input_threshold = RangeExpr._to_expr_type(neg_base) + RangeExpr._to_expr_type(input_range) * input_threshold_factor
    elif input_threshold_abs is not None:
      assert input_threshold_factor is None, "can only specify one input threshold type"
      input_threshold = RangeExpr._to_expr_type(input_threshold_abs)  # TODO avoid internal functions?
    else:  # assumed ideal
      input_threshold = RangeExpr.EMPTY

    output_threshold: RangeLike
    if output_threshold_factor is not None:
      assert output_threshold_abs is None, "can only specify one output threshold type"
      output_threshold_factor = RangeExpr._to_expr_type(output_threshold_factor)
      # use a pessimistic range
      output_range = VoltageLink._voltage_range(pos).lower() - neg_base
      output_threshold = RangeExpr._to_expr_type(neg_base) + output_threshold_factor * RangeExpr._to_expr_type(output_range)
    elif output_threshold_abs is not None:
      assert output_threshold_factor is None, "can only specify one output threshold type"
      output_threshold = RangeExpr._to_expr_type(output_threshold_abs)  # TODO avoid internal functions?
    else:  # assumed ideal
      output_threshold = (neg_base, VoltageLink._voltage_range(pos).lower())

    return DigitalBidir(  # TODO get rid of to_expr_type w/ dedicated Range conversion
      voltage_limits=voltage_limit,
      current_draw=current_draw,
      voltage_out=supply_range,
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
               pulldown_capable: BoolLike = False,
               _bridged_internal: BoolLike = False) -> None:
    super().__init__()
    self.voltage_limits: RangeExpr = self.Parameter(RangeExpr(voltage_limits))
    self.current_draw: RangeExpr = self.Parameter(RangeExpr(current_draw))
    self.voltage_out: RangeExpr = self.Parameter(RangeExpr(voltage_out))
    self.current_limits: RangeExpr = self.Parameter(RangeExpr(current_limits))
    self.input_thresholds: RangeExpr = self.Parameter(RangeExpr(input_thresholds))
    self.output_thresholds: RangeExpr = self.Parameter(RangeExpr(output_thresholds))

    self.pullup_capable: BoolExpr = self.Parameter(BoolExpr(pullup_capable))
    self.pulldown_capable: BoolExpr = self.Parameter(BoolExpr(pulldown_capable))
    self._bridged_internal: BoolExpr = self.Parameter(BoolExpr(_bridged_internal))


class DigitalSingleSourceFake:
  @staticmethod
  @deprecated("use DigitalSource.sink_from_supply")
  def low_from_supply(neg: Port[GroundLink], is_pulldown: bool = False) -> DigitalSource:
    if not is_pulldown:
      return DigitalSource.low_from_supply(neg)
    else:
      return DigitalSource.pulldown_from_supply(neg)

  @staticmethod
  @deprecated("use DigitalSource.source_from_supply")
  def high_from_supply(pos: Port[VoltageLink], is_pullup: bool = False) -> DigitalSource:
    if not is_pullup:
      return DigitalSource.high_from_supply(pos)
    else:
      return DigitalSource.pullup_from_supply(pos)

  def __call__(self, voltage_out: RangeLike = RangeExpr.ZERO,
               output_thresholds: RangeLike = RangeExpr.ALL, *,
               pullup_capable: BoolLike = False,
               pulldown_capable: BoolLike = False,
               low_signal_driver: BoolLike = False,
               high_signal_driver: BoolLike = False) -> DigitalSource:
    return DigitalSource(
      voltage_out=voltage_out,
      output_thresholds=output_thresholds,
      pullup_capable=pullup_capable,
      pulldown_capable=pulldown_capable,
      low_driver=low_signal_driver,
      high_driver=high_signal_driver
    )

  def empty(self):
    return DigitalSource.empty()


DigitalSingleSource = DigitalSingleSourceFake()
