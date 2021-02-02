from typing import Optional
from edg_core import *
from .CircuitBlock import CircuitLink
from .ElectricalPorts import CircuitPort, CircuitPortBridge


class AnalogLink(CircuitLink):
  """Analog signal, a signal that carries information by varying voltage"""
  def __init__(self) -> None:
    super().__init__()

    self.source = self.Port(AnalogSource())
    self.sinks = self.Port(Vector(AnalogSink()))  # TODO only one allowed for now b/c hard to calculate parallel impedances

    self.source_impedance = self.Parameter(RangeExpr(self.source.impedance))
    self.sink_impedance = self.Parameter(RangeExpr())

    self.voltage = self.Parameter(RangeExpr(self.source.voltage_out))
    self.current_draw = self.Parameter(RangeExpr())


  def contents(self) -> None:
    super().contents()

    self.constrain(self.source.impedance <= self.sink_impedance * 0.1)  # about 10x to ensure signal integrity  # TODO make 100x?
    self.assign(self.current_draw, self.sinks.sum(lambda x: x.current_draw))
    total_conductance = self.sinks.sum(lambda x: x.conductance)
    self.assign(self.sink_impedance, (1 / total_conductance))


class AnalogBase(CircuitPort[AnalogLink]):
  def __init__(self) -> None:
    super().__init__()

    self.link_type = AnalogLink


class AnalogSinkBridge(CircuitPortBridge):
  def __init__(self) -> None:
    super().__init__()

    self.outer_port = self.Port(AnalogSink(impedance=RangeExpr()))

    # Here we ignore the current_limits of the inner port, instead relying on the main link to handle it
    # The outer port's voltage_limits is untouched and should be defined in the port def.
    # TODO: it's a slightly optimization to handle them here. Should it be done?
    # TODO: or maybe current_limits / voltage_limits shouldn't be a port, but rather a block property?
    self.inner_link = self.Port(AnalogSource(current_limits=RangeExpr.ALL))

  def contents(self) -> None:
    super().contents()

    self.assign(self.inner_link.voltage_out, self.outer_port.link().voltage)
    self.assign(self.outer_port.impedance, self.inner_link.link().sink_impedance)


class AnalogSourceBridge(CircuitPortBridge):  # basic passthrough port, sources look the same inside and outside
  def __init__(self) -> None:
    super().__init__()

    self.outer_port = self.Port(AnalogSource(voltage_out=RangeExpr(), impedance=RangeExpr()))

    # Here we ignore the voltage_limits of the inner port, instead relying on the main link to handle it
    # The outer port's current_limits is untouched and should be defined in tte port def.
    # TODO: it's a slightly optimization to handle them here. Should it be done?
    # TODO: or maybe current_limits / voltage_limits shouldn't be a port, but rather a block property?
    self.inner_link = self.Port(AnalogSink(voltage_limits=RangeExpr.ALL))

  def contents(self) -> None:
    super().contents()

    self.assign(self.outer_port.voltage_out, self.inner_link.link().voltage)
    self.assign(self.outer_port.impedance, self.inner_link.link().source_impedance)


class AnalogSink(AnalogBase):
  def __init__(self, voltage_limits: RangeLike = Default(RangeExpr.ALL),
               current_draw: RangeLike = Default(RangeExpr.ZERO),
               impedance: RangeLike = Default(RangeExpr.INF)) -> None:
    super().__init__()
    self.bridge_type = AnalogSinkBridge

    # TODO maybe separate absolute maximum limits from sensing limits?
    self.voltage_limits = self.Parameter(RangeExpr(voltage_limits))
    self.current_draw = self.Parameter(RangeExpr(current_draw))
    self.impedance = self.Parameter(RangeExpr(impedance))
    if isinstance(impedance, RangeExpr) and impedance.binding is None:  # TODO less hacky
      self.conductance = self.Parameter(RangeExpr())  # TODO this is actually an awful idea - should move into the link
    else:
      self.conductance = self.Parameter(RangeExpr(RangeExpr._to_expr_type(1) / impedance))


class AnalogSource(AnalogBase):
  def __init__(self, voltage_out: RangeLike = Default(RangeExpr.EMPTY_ZERO),
               current_limits: RangeLike = Default(RangeExpr.ALL),
               impedance: RangeLike = Default(RangeExpr.ZERO)) -> None:
    super().__init__()
    self.bridge_type = AnalogSourceBridge

    self.voltage_out = self.Parameter(RangeExpr(voltage_out))
    self.current_limits = self.Parameter(RangeExpr(current_limits))
    self.impedance = self.Parameter(RangeExpr(impedance))
