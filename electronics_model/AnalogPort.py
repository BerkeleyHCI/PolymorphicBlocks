from __future__ import annotations

from typing import Optional, Tuple

from edg_core import *
from edg_core.Blocks import DescriptionString
from .CircuitBlock import CircuitLink
from .VoltagePorts import CircuitPort, CircuitPortBridge, VoltageLink


class AnalogLink(CircuitLink):
  """Analog signal, a signal that carries information by varying voltage"""
  def __init__(self) -> None:
    super().__init__()

    self.source = self.Port(AnalogSource())
    self.sinks = self.Port(Vector(AnalogSink()))

    self.source_impedance = self.Parameter(RangeExpr(self.source.impedance))
    self.sink_impedance = self.Parameter(RangeExpr())

    self.voltage = self.Parameter(RangeExpr(self.source.voltage_out))
    self.signal = self.Parameter(RangeExpr(self.source.signal_out))
    self.current_drawn = self.Parameter(RangeExpr())

    self.voltage_limits = self.Parameter(RangeExpr())
    self.signal_limits = self.Parameter(RangeExpr())
    self.current_limits = self.Parameter(RangeExpr())

  def contents(self) -> None:
    super().contents()

    self.description = DescriptionString(
      "<b>voltage</b>: ", DescriptionString.FormatUnits(self.voltage, "V"),
      " <b>of limits</b>: ", DescriptionString.FormatUnits(self.voltage_limits, "V"),
      "\n<b>current</b>: ", DescriptionString.FormatUnits(self.current_drawn, "A"),
      " <b>of limits</b>: ", DescriptionString.FormatUnits(self.current_limits, "A"),
      "\n<b>sink impedance</b>: ", DescriptionString.FormatUnits(self.sink_impedance, "Ω"),
      ", <b>source impedance</b>: ", DescriptionString.FormatUnits(self.source_impedance, "Ω"))

    self.assign(self.sink_impedance, 1 / (1 / self.sinks.map_extract(lambda x: x.impedance)).sum())
    self.require(self.source.impedance.upper() <= self.sink_impedance.lower() * 0.1)  # about 10x for signal integrity
    self.assign(self.current_drawn, self.sinks.sum(lambda x: x.current_draw))

    self.assign(self.voltage_limits, self.sinks.intersection(lambda x: x.voltage_limits))
    self.require(self.voltage_limits.contains(self.voltage), "incompatible voltage levels")
    self.assign(self.signal_limits, self.sinks.intersection(lambda x: x.signal_limits))
    self.require(self.voltage.contains(self.signal), "signal levels not contained within voltage")
    self.require(self.signal_limits.contains(self.signal), "incompatible signal levels")
    self.assign(self.current_limits, self.source.current_limits)
    self.require(self.current_limits.contains(self.current_drawn), "overcurrent")


class AnalogBase(CircuitPort[AnalogLink]):
  link_type = AnalogLink


class AnalogSinkBridge(CircuitPortBridge):
  def __init__(self) -> None:
    super().__init__()

    self.outer_port = self.Port(AnalogSink(current_draw=RangeExpr(),
                                           voltage_limits=RangeExpr(),
                                           signal_limits=RangeExpr(),
                                           impedance=RangeExpr()))

    # Here we ignore the current_limits of the inner port, instead relying on the main link to handle it
    # The outer port's voltage_limits is untouched and should be defined in the port def.
    # TODO: it's a slightly optimization to handle them here. Should it be done?
    # TODO: or maybe current_limits / voltage_limits shouldn't be a port, but rather a block property?
    self.inner_link = self.Port(AnalogSource(voltage_out=RangeExpr(), signal_out=RangeExpr(),
                                             current_limits=RangeExpr.ALL))

  def contents(self) -> None:
    super().contents()

    self.assign(self.outer_port.impedance, self.inner_link.link().sink_impedance)
    self.assign(self.outer_port.current_draw, self.inner_link.link().current_drawn)
    self.assign(self.outer_port.voltage_limits, self.inner_link.link().voltage_limits)
    self.assign(self.outer_port.signal_limits, self.inner_link.link().signal_limits)

    self.assign(self.inner_link.voltage_out, self.outer_port.link().voltage)
    self.assign(self.inner_link.signal_out, self.outer_port.link().signal)


class AnalogSourceBridge(CircuitPortBridge):  # basic passthrough port, sources look the same inside and outside
  def __init__(self) -> None:
    super().__init__()

    self.outer_port = self.Port(AnalogSource(voltage_out=RangeExpr(),
                                             signal_out=RangeExpr(),
                                             current_limits=RangeExpr(),
                                             impedance=RangeExpr()))

    # Here we ignore the voltage_limits of the inner port, instead relying on the main link to handle it
    # The outer port's current_limits is untouched and should be defined in tte port def.
    # TODO: it's a slightly optimization to handle them here. Should it be done?
    # TODO: or maybe current_limits / voltage_limits shouldn't be a port, but rather a block property?
    self.inner_link = self.Port(AnalogSink(current_draw=RangeExpr(),
                                           voltage_limits=RangeExpr.ALL,
                                           signal_limits=RangeExpr.ALL,
                                           impedance=RangeExpr()))

  def contents(self) -> None:
    super().contents()

    self.assign(self.outer_port.voltage_out, self.inner_link.link().voltage)
    self.assign(self.outer_port.signal_out, self.inner_link.link().signal)
    self.assign(self.outer_port.impedance, self.inner_link.link().source_impedance)
    self.assign(self.outer_port.current_limits, self.inner_link.link().current_limits)  # TODO compensate for internal current draw

    self.assign(self.inner_link.current_draw, self.outer_port.link().current_drawn)
    self.assign(self.inner_link.impedance, self.outer_port.link().sink_impedance)


class AnalogSink(AnalogBase):
  bridge_type = AnalogSinkBridge

  @staticmethod
  def from_supply(neg: Port[VoltageLink], pos: Port[VoltageLink], *,
                  voltage_limit_tolerance: Optional[RangeLike] = None,
                  voltage_limit_abs: Optional[RangeLike] = None,
                  signal_limit_tolerance: Optional[RangeLike] = None,
                  signal_limit_bound: Optional[Tuple[FloatLike, FloatLike]] = None,
                  signal_limit_abs: Optional[RangeLike] = None,
                  current_draw: RangeLike = RangeExpr.ZERO,
                  impedance: RangeLike = RangeExpr.INF):
    supply_range = neg.link().voltage.hull(pos.link().voltage)

    voltage_limit: RangeLike
    if voltage_limit_tolerance is not None:
      voltage_limit = supply_range + voltage_limit_tolerance
    elif voltage_limit_abs is not None:
      voltage_limit = voltage_limit_abs
    else:
      voltage_limit = supply_range + (-0.3, 0.3)

    signal_limit: RangeLike
    if signal_limit_abs is not None:
      assert signal_limit_tolerance is None
      assert signal_limit_bound is None
      signal_limit = signal_limit_abs
    elif signal_limit_tolerance is not None:
      assert signal_limit_bound is None
      signal_limit = supply_range + signal_limit_tolerance
    elif signal_limit_bound is not None:
      # signal limit bounds specified as (lower bound added to limit, upper bound added to limit)
      # typically (positive, negative)
      signal_limit = (supply_range.lower() + signal_limit_bound[0],
                      supply_range.upper() + signal_limit_bound[1])
    else:  # generic default
      signal_limit = supply_range

    return AnalogSink(
      voltage_limits=voltage_limit,
      signal_limits=signal_limit,
      current_draw=current_draw,
      impedance=impedance
    )

  def __init__(self, voltage_limits: RangeLike = RangeExpr.ALL, signal_limits: RangeLike = RangeExpr.ALL,
               current_draw: RangeLike = RangeExpr.ZERO,
               impedance: RangeLike = RangeExpr.INF) -> None:
    """voltage_limits are the maximum recommended voltage levels of the device (before device damage occurs),
    signal_limits are for proper device functionality (e.g. non-RRIO opamps)"""
    super().__init__()
    self.voltage_limits = self.Parameter(RangeExpr(voltage_limits))
    self.signal_limits = self.Parameter(RangeExpr(signal_limits))
    self.current_draw = self.Parameter(RangeExpr(current_draw))
    self.impedance = self.Parameter(RangeExpr(impedance))


class AnalogSource(AnalogBase):
  bridge_type = AnalogSourceBridge

  @staticmethod
  def from_supply(neg: Port[VoltageLink], pos: Port[VoltageLink], *,
                  signal_out_bound: Optional[Tuple[FloatLike, FloatLike]] = None,
                  current_limits: RangeLike = RangeExpr.ALL,
                  impedance: RangeLike = RangeExpr.ZERO):
    supply_range = neg.link().voltage.hull(pos.link().voltage)

    signal_out: RangeLike
    if signal_out_bound is not None:
      # signal limit bounds specified as (lower bound added to limit, upper bound added to limit)
      # typically (positive, negative)
      signal_out = (supply_range.lower() + signal_out_bound[0],
                    supply_range.upper() + signal_out_bound[1])
    else:  # generic default
      signal_out = supply_range

    return AnalogSource(
      voltage_out=supply_range,
      signal_out=signal_out,
      current_limits=current_limits,
      impedance=impedance
    )

  def __init__(self, voltage_out: RangeLike = RangeExpr.ZERO, signal_out: RangeLike = RangeExpr.EMPTY,
               current_limits: RangeLike = RangeExpr.ALL,
               impedance: RangeLike = RangeExpr.ZERO) -> None:
    """voltage_out is the total voltage range the device can output (typically limited by power rails)
    regardless of controls and including transients, while signal_out is the intended operating range"""
    super().__init__()
    self.voltage_out = self.Parameter(RangeExpr(voltage_out))
    self.signal_out = self.Parameter(RangeExpr(signal_out))
    self.current_limits = self.Parameter(RangeExpr(current_limits))
    self.impedance = self.Parameter(RangeExpr(impedance))
