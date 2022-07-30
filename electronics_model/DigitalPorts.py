from __future__ import annotations

from typing import Optional, Union, Tuple
from edg_core import *
from edg_core.Blocks import DescriptionString
from .CircuitBlock import CircuitLink, CircuitPortBridge, CircuitPortAdapter
from .VoltagePorts import CircuitPort, VoltageLink, VoltageSource
from .Units import Volt


class DigitalLink(CircuitLink):
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
    self.has_low_signal_driver = self.Parameter(BoolExpr())
    self.has_high_signal_driver = self.Parameter(BoolExpr())

    self.description = DescriptionString(
      "<b>voltage</b>: ", DescriptionString.FormatUnits(self.voltage, "V"),
      " <b>of limits</b>: ", DescriptionString.FormatUnits(self.voltage_limits, "V"),
      "\n<b>current</b>: ", DescriptionString.FormatUnits(self.current_drawn, "A"),
      " <b>of limits</b>: ", DescriptionString.FormatUnits(self.current_limits, "A"),
      "\n<b>output thresholds</b>: ", DescriptionString.FormatUnits(self.output_thresholds, "Ω"),
      ", <b>input thresholds</b>: ", DescriptionString.FormatUnits(self.input_thresholds, "Ω"))

  def contents(self):
    super().contents()

    self.require(self.source.is_connected() | (self.single_sources.length() > 0) | (self.bidirs.length() > 0),
                 "DigitalLink must have some kind of source")

    self.assign(self.voltage, self.source.is_connected().then_else(
      self.bidirs.hull(lambda x: x.voltage_out).hull(self.source.voltage_out),
      self.bidirs.hull(lambda x: x.voltage_out).hull(self.single_sources.hull(lambda x: x.voltage_out))
    ))

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
    bidirs_output_thresholds = self.bidirs.intersection(lambda x: x.output_thresholds)
    single_output_thresholds = self.single_sources.intersection(lambda x: x.output_thresholds)
    self.assign(self.output_thresholds,
                source_output_thresholds.intersect(
                  bidirs_output_thresholds.intersect(
                    single_output_thresholds)))

    self.assign(self.input_thresholds,
      self.sinks.hull(lambda x: x.input_thresholds).hull(self.bidirs.hull(lambda x: x.input_thresholds)),
    )
    self.require(self.output_thresholds.contains(self.input_thresholds), "incompatible digital thresholds")

    self.assign(self.pullup_capable,
                self.bidirs.any(lambda x: x.pullup_capable) | self.single_sources.any(lambda x: x.pullup_capable))
    self.assign(self.pulldown_capable,
                self.bidirs.any(lambda x: x.pulldown_capable) | self.single_sources.any(lambda x: x.pulldown_capable))
    self.assign(self.has_low_signal_driver,
                self.single_sources.any(lambda x: x.low_signal_driver))
    self.assign(self.has_high_signal_driver,
                self.single_sources.any(lambda x: x.high_signal_driver))
    self.require(self.has_low_signal_driver.implies(self.pullup_capable), "requires pullup capable connection")
    self.require(self.has_high_signal_driver.implies(self.pulldown_capable), "requires pulldown capable connection")


class DigitalBase(CircuitPort[DigitalLink]):
  def __init__(self) -> None:
    super().__init__()

    self.link_type = DigitalLink


class DigitalSink(DigitalBase):
  @staticmethod
  def from_supply(neg: Port[VoltageLink], pos: Port[VoltageLink], *,
                  voltage_limit_tolerance: RangeLike = Default((-0.3, 0.3)),
                  current_draw: RangeLike = Default(RangeExpr.ZERO),
                  input_threshold_abs: Optional[RangeLike] = None) -> DigitalSink:
    if input_threshold_abs is not None:
      input_threshold_abs = RangeExpr._to_expr_type(input_threshold_abs)  # TODO avoid internal functions?
      return DigitalSink(  # TODO get rid of to_expr_type w/ dedicated Range conversion
        voltage_limits=(neg.link().voltage.upper(), pos.link().voltage.lower()) +
                       RangeExpr._to_expr_type(voltage_limit_tolerance),
        current_draw=current_draw,
        input_thresholds=input_threshold_abs
      )
    else:
      raise ValueError("no input threshold specified")

  @staticmethod
  def from_bidir(model: DigitalBidir) -> DigitalSink:
    return DigitalSink(model.voltage_limits, model.current_draw, input_thresholds=model.input_thresholds)

  def __init__(self, voltage_limits: RangeLike = Default(RangeExpr.ALL),
               current_draw: RangeLike = Default(RangeExpr.ZERO), *,
               input_thresholds: RangeLike = Default(RangeExpr.EMPTY_DIT)) -> None:
    super().__init__()
    self.bridge_type = DigitalSinkBridge

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
                                            input_thresholds=RangeExpr.EMPTY_DIT))

  def contents(self) -> None:
    super().contents()

    self.assign(self.outer_port.voltage_out, self.inner_link.link().voltage)
    self.assign(self.outer_port.current_limits, self.inner_link.link().current_limits)  # TODO subtract internal current drawn
    self.assign(self.inner_link.current_draw, self.outer_port.link().current_drawn)

    self.assign(self.outer_port.output_thresholds, self.inner_link.link().output_thresholds)


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


class DigitalSourceAdapterVoltageSource(CircuitPortAdapter[VoltageSource]):
  @init_in_parent
  def __init__(self):
    super().__init__()
    self.src = self.Port(DigitalSink())
    self.dst = self.Port(VoltageSource(
      voltage_out=self.src.link().voltage,
      current_limits=(-float('inf'), float('inf'))))
    self.assign(self.src.current_draw, self.dst.link().current_drawn)


class DigitalSource(DigitalBase):
  @staticmethod
  def from_supply(neg: Port[VoltageLink], pos: Port[VoltageLink],
                  current_limits: RangeLike = Default(RangeExpr.ALL), *,
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
    return DigitalSource(model.voltage_out, model.current_limits, output_thresholds=model.output_thresholds)

  def __init__(self, voltage_out: RangeLike = Default(RangeExpr.EMPTY_ZERO),
               current_limits: RangeLike = Default(RangeExpr.ALL), *,
               output_thresholds: RangeLike = Default(RangeExpr.ALL)) -> None:
    super().__init__()
    self.bridge_type = DigitalSourceBridge
    self.adapter_types = [DigitalSourceAdapterVoltageSource]

    self.voltage_out: RangeExpr = self.Parameter(RangeExpr(voltage_out))
    self.current_limits: RangeExpr = self.Parameter(RangeExpr(current_limits))
    self.output_thresholds: RangeExpr = self.Parameter(RangeExpr(output_thresholds))

  def as_voltage_source(self) -> VoltageSource:
    return self._convert(DigitalSourceAdapterVoltageSource())


class DigitalBidirNotConnected(NotConnectableBlock['DigitalBidir']):
  """Not-connected dummy block for Digital bidir ports"""
  def __init__(self) -> None:
    super().__init__()
    self.port = self.Port(DigitalBidir())


class DigitalBidir(DigitalBase, NotConnectablePort):
  @staticmethod
  def from_supply(neg: Port[VoltageLink], pos: Port[VoltageLink],
                  voltage_limit_abs: Optional[RangeLike] = None,
                  voltage_limit_tolerance: Optional[RangeLike] = None,
                  current_draw: RangeLike = Default(RangeExpr.ZERO),
                  current_limits: RangeLike = Default(RangeExpr.ALL), *,
                  input_threshold_factor: Optional[RangeLike] = None,
                  input_threshold_abs: Optional[RangeLike] = None,
                  output_threshold_factor: Optional[RangeLike] = None,
                  pullup_capable: BoolLike = False, pulldown_capable: BoolLike = False) -> DigitalBidir:
    voltage_limit: RangeLike
    if voltage_limit_abs is not None:
      assert voltage_limit_tolerance is None
      voltage_limit = voltage_limit_abs
    elif voltage_limit_tolerance is not None:
      voltage_limit = (neg.link().voltage.upper(), pos.link().voltage.lower()) + \
                      RangeExpr._to_expr_type(voltage_limit_tolerance)
    else:
      raise ValueError("no voltage limit specified")

    input_threshold: RangeLike
    if input_threshold_factor is not None:
      assert input_threshold_abs is None, "can only specify one input threshold type"
      input_threshold_factor = RangeExpr._to_expr_type(input_threshold_factor)  # TODO avoid internal functions?
      input_threshold = (input_threshold_factor.lower() * pos.link().voltage.lower(),
                         input_threshold_factor.upper() * pos.link().voltage.upper())
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

  def __init__(self, *, voltage_limits: RangeLike = Default(RangeExpr.ALL),
               current_draw: RangeLike = Default(RangeExpr.ZERO),
               voltage_out: RangeLike = Default(RangeExpr.EMPTY_ZERO),
               current_limits: RangeLike = Default(RangeExpr.ALL),
               input_thresholds: RangeLike = Default(RangeExpr.EMPTY_DIT),
               output_thresholds: RangeLike = Default(RangeExpr.ALL),
               pullup_capable: BoolLike = Default(False),
               pulldown_capable: BoolLike = Default(False)) -> None:
    super().__init__()
    self.bridge_type = DigitalBidirBridge
    self.not_connected_type = DigitalBidirNotConnected

    self.voltage_limits: RangeExpr = self.Parameter(RangeExpr(voltage_limits))
    self.current_draw: RangeExpr = self.Parameter(RangeExpr(current_draw))
    self.voltage_out: RangeExpr = self.Parameter(RangeExpr(voltage_out))
    self.current_limits: RangeExpr = self.Parameter(RangeExpr(current_limits))
    self.input_thresholds: RangeExpr = self.Parameter(RangeExpr(input_thresholds))
    self.output_thresholds: RangeExpr = self.Parameter(RangeExpr(output_thresholds))

    self.pullup_capable: BoolExpr = self.Parameter(BoolExpr(pullup_capable))
    self.pulldown_capable: BoolExpr = self.Parameter(BoolExpr(pulldown_capable))


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


class DigitalSingleSource(DigitalBase):
  @staticmethod
  def low_from_supply(neg: Port[VoltageLink]) -> DigitalSingleSource:
    return DigitalSingleSource(
      voltage_out=neg.link().voltage,
      output_thresholds=(neg.link().voltage.upper(), float('inf')),
      pulldown_capable=False,
      low_signal_driver=True
    )

  @staticmethod
  def high_from_supply(pos: Port[VoltageLink]) -> DigitalSingleSource:
    return DigitalSingleSource(
      voltage_out=pos.link().voltage,
      output_thresholds=(-float('inf'), pos.link().voltage.lower()),
      pullup_capable=False,
      high_signal_driver=True
    )

  def __init__(self, voltage_out: RangeLike = Default(RangeExpr.EMPTY_ZERO),
               output_thresholds: RangeLike = Default(RangeExpr.ALL), *,
               pullup_capable: BoolLike = Default(False),
               pulldown_capable: BoolLike = Default(False),
               low_signal_driver: BoolLike = Default(False),
               high_signal_driver: BoolLike = Default(False)) -> None:
    super().__init__()

    self.voltage_out: RangeExpr = self.Parameter(RangeExpr(voltage_out))
    self.output_thresholds: RangeExpr = self.Parameter(RangeExpr(output_thresholds))

    self.pullup_capable = self.Parameter(BoolExpr(pullup_capable))
    self.pulldown_capable = self.Parameter(BoolExpr(pulldown_capable))

    self.low_signal_driver = self.Parameter(BoolExpr(low_signal_driver))
    self.high_signal_driver = self.Parameter(BoolExpr(high_signal_driver))
