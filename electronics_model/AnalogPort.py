from __future__ import annotations

from edg_core import *
from .CircuitBlock import CircuitLink
from .VoltagePorts import CircuitPort, CircuitPortBridge


class AnalogLink(CircuitLink):
  """Analog signal, a signal that carries information by varying voltage"""
  def __init__(self) -> None:
    super().__init__()

    self.source = self.Port(AnalogSource())
    self.sinks = self.Port(Vector(AnalogSink()))  # TODO only one allowed for now b/c hard to calculate parallel impedances

    self.source_impedance = self.Parameter(RangeExpr(self.source.impedance))
    self.sink_impedance = self.Parameter(RangeExpr())

    self.voltage = self.Parameter(RangeExpr(self.source.voltage_out))
    self.current_drawn = self.Parameter(RangeExpr())

    self.voltage_limits = self.Parameter(RangeExpr())
    self.current_limits = self.Parameter(RangeExpr())

  def contents(self) -> None:
    super().contents()

    self.assign(self.sink_impedance, 1 / (1 / self.sinks.map_extract(lambda x: x.impedance)).sum)
    self.require(self.source.impedance <= self.sink_impedance * 0.1)  # about 10x to ensure signal integrity  # TODO make 100x?
    self.assign(self.current_drawn, self.sinks.sum(lambda x: x.current_draw))

    self.assign(self.voltage_limits, self.sinks.intersection(lambda x: x.voltage_limits))
    self.assign(self.current_limits, self.source.current_limits)
    self.require(self.current_limits.contains(self.current_drawn), "overcurrent")


class AnalogBase(CircuitPort[AnalogLink]):
  def __init__(self) -> None:
    super().__init__()

    self.link_type = AnalogLink


class AnalogSinkBridge(CircuitPortBridge):
  def __init__(self) -> None:
    super().__init__()

    self.outer_port = self.Port(AnalogSink(current_draw=RangeExpr(),
                                           voltage_limits=RangeExpr(),
                                           impedance=RangeExpr()))

    # Here we ignore the current_limits of the inner port, instead relying on the main link to handle it
    # The outer port's voltage_limits is untouched and should be defined in the port def.
    # TODO: it's a slightly optimization to handle them here. Should it be done?
    # TODO: or maybe current_limits / voltage_limits shouldn't be a port, but rather a block property?
    self.inner_link = self.Port(AnalogSource(voltage_out=RangeExpr(),
                                             current_limits=RangeExpr.ALL))

  def contents(self) -> None:
    super().contents()

    self.assign(self.outer_port.impedance, self.inner_link.link().sink_impedance)
    self.assign(self.outer_port.current_draw, self.inner_link.link().current_drawn)
    self.assign(self.outer_port.voltage_limits, self.inner_link.link().voltage_limits)

    self.assign(self.inner_link.voltage_out, self.outer_port.link().voltage)


class AnalogSourceBridge(CircuitPortBridge):  # basic passthrough port, sources look the same inside and outside
  def __init__(self) -> None:
    super().__init__()

    self.outer_port = self.Port(AnalogSource(voltage_out=RangeExpr(),
                                             current_limits=RangeExpr(),
                                             impedance=RangeExpr()))

    # Here we ignore the voltage_limits of the inner port, instead relying on the main link to handle it
    # The outer port's current_limits is untouched and should be defined in tte port def.
    # TODO: it's a slightly optimization to handle them here. Should it be done?
    # TODO: or maybe current_limits / voltage_limits shouldn't be a port, but rather a block property?
    self.inner_link = self.Port(AnalogSink(current_draw=RangeExpr(),
                                           voltage_limits=RangeExpr.ALL))

  def contents(self) -> None:
    super().contents()

    self.assign(self.outer_port.voltage_out, self.inner_link.link().voltage)
    self.assign(self.outer_port.impedance, self.inner_link.link().source_impedance)
    self.require(self.inner_link.link().sink_impedance.lower() > 1e9, "TODO: non-negligible impedances on AnalogSourceBridge")  # TODO calculate this the right way
    self.assign(self.outer_port.current_limits, self.inner_link.link().current_limits)  # TODO compensate for internal current draw

    self.assign(self.inner_link.current_draw, self.outer_port.link().current_drawn)
    self.assign(self.inner_link.impedance, self.outer_port.link().sink_impedance)


class AnalogSink(AnalogBase):
  @staticmethod
  def empty() -> AnalogSink:
    """Returns a new port with no parameters defined (instead of unmodeled defaults),
 such as if the port is to be exported, including as part of a bundle"""
    return AnalogSink(voltage_limits=RangeExpr(), current_draw=RangeExpr(),
                      impedance=RangeExpr())

  def __init__(self, voltage_limits: RangeLike = Default(RangeExpr.ALL),
               current_draw: RangeLike = Default(RangeExpr.ZERO),
               impedance: RangeLike = Default(RangeExpr.INF)) -> None:
    super().__init__()
    self.bridge_type = AnalogSinkBridge

    # TODO maybe separate absolute maximum limits from sensing limits?
    self.voltage_limits = self.Parameter(RangeExpr(voltage_limits))
    self.current_draw = self.Parameter(RangeExpr(current_draw))
    self.impedance = self.Parameter(RangeExpr(impedance))


class AnalogSource(AnalogBase):
  @staticmethod
  def empty() -> AnalogSource:
    """Returns a new port with no parameters defined (instead of unmodeled defaults),
  such as if the port is to be exported, including as part of a bundle"""
    return AnalogSource(voltage_out=RangeExpr(), current_limits=RangeExpr(),
                        impedance=RangeExpr())

  def __init__(self, voltage_out: RangeLike = Default(RangeExpr.EMPTY_ZERO),
               current_limits: RangeLike = Default(RangeExpr.ALL),
               impedance: RangeLike = Default(RangeExpr.ZERO)) -> None:
    super().__init__()
    self.bridge_type = AnalogSourceBridge

    self.voltage_out = self.Parameter(RangeExpr(voltage_out))
    self.current_limits = self.Parameter(RangeExpr(current_limits))
    self.impedance = self.Parameter(RangeExpr(impedance))
