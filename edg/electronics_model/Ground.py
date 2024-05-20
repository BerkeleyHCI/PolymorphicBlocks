from __future__ import annotations

from edg_core import *
from .Units import Volt, Amp
from .VoltagePorts import VoltageSink, VoltageSource


class GroundWrapper:  # a wrapper around VoltageSink to have it behave as Ground
  def __call__(self, current_draw: RangeLike = RangeExpr.ZERO * Amp) -> VoltageSink:
    return VoltageSink(voltage_limits=RangeExpr.ZERO * Volt, current_draw=current_draw)

  def empty(self) -> VoltageSink:
    return VoltageSink.empty()


class GroundSourceWrapper:
  def __call__(self) -> VoltageSource:
    return VoltageSource(voltage_out=RangeExpr.ZERO * Volt, current_limits=RangeExpr.ALL * Amp)

  def empty(self) -> VoltageSource:
    return VoltageSource.empty()


# type checker doesn't recognize it if we use a @staticmethod __call__ and have this directly be Ground
# so it's explicitly instantiated
Ground = GroundWrapper()
GroundSource = GroundSourceWrapper()


# Standard port tags for implicit connection scopes / auto-connecting power supplies
Common = PortTag(VoltageSink)  # Common ground (0v) port
