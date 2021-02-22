from __future__ import annotations

from typing import *
from edg_core import *
from .CircuitBlock import CircuitPortBridge, CircuitLink, CircuitPortAdapter
from .Units import Volt, Amp, Ohm

if TYPE_CHECKING:
  from .DigitalPorts import DigitalSource
  from .AnalogPort import AnalogSource


class ElectricalLink(CircuitLink):
  def __init__(self) -> None:
    super().__init__()

    self.source = self.Port(ElectricalSource())
    self.sinks = self.Port(Vector(ElectricalSink()))

    self.voltage = self.Parameter(RangeExpr())
    self.voltage_limits = self.Parameter(RangeExpr())
    self.current_drawn = self.Parameter(RangeExpr())

  def contents(self) -> None:
    super().contents()

    self.assign(self.voltage, self.source.voltage_out)
    self.assign(self.voltage_limits, self.sinks.intersection(lambda x: x.voltage_limits))
    self.require(self.voltage_limits.contains(self.voltage), "overvoltage")

    self.assign(self.current_drawn, self.sinks.sum(lambda x: x.current_draw))
    self.require(self.source.current_limits.contains(self.current_drawn), "overcurrent")


class ElectricalSinkBridge(CircuitPortBridge):
  def __init__(self) -> None:
    super().__init__()

    self.outer_port = self.Port(ElectricalSink(current_draw=RangeExpr()))

    # Here we ignore the current_limits of the inner port, instead relying on the main link to handle it
    # The outer port's voltage_limits is untouched and should be defined in the port def.
    # TODO: it's a slightly optimization to handle them here. Should it be done?
    # TODO: or maybe current_limits / voltage_limits shouldn't be a port, but rather a block property?
    self.inner_link = self.Port(ElectricalSource(current_limits=RangeExpr.ALL,
                                                 voltage_out=RangeExpr()))

  def contents(self) -> None:
    super().contents()

    self.assign(self.outer_port.current_draw, self.inner_link.link().current_drawn)
    self.assign(self.inner_link.voltage_out, self.outer_port.link().voltage)


class ElectricalSourceBridge(CircuitPortBridge):  # basic passthrough port, sources look the same inside and outside
  def __init__(self) -> None:
    super().__init__()

    self.outer_port = self.Port(ElectricalSource(voltage_out=RangeExpr()))

    # Here we ignore the voltage_limits of the inner port, instead relying on the main link to handle it
    # The outer port's current_limits is untouched and should be defined in tte port def.
    # TODO: it's a slightly optimization to handle them here. Should it be done?
    # TODO: or maybe current_limits / voltage_limits shouldn't be a port, but rather a block property?
    self.inner_link = self.Port(ElectricalSink(voltage_limits=RangeExpr.ALL,
                                               current_draw=RangeExpr()))

  def contents(self) -> None:
    super().contents()

    self.assign(self.outer_port.voltage_out, self.inner_link.link().voltage)
    self.assign(self.inner_link.current_draw, self.outer_port.link().current_drawn)


CircuitLinkType = TypeVar('CircuitLinkType', bound=Link)
class CircuitPort(Port[CircuitLinkType], Generic[CircuitLinkType]):
  """Electrical connection that represents a single port into a single copper net"""
  pass


class ElectricalBase(CircuitPort[ElectricalLink]):
  def __init__(self) -> None:
    super().__init__()
    self.link_type = ElectricalLink

#     self.isolation_domain = self.Parameter(RefParameter())  # semantics TBD
#     self.reference = self.Parameter(RefParameter())  # semantics TBD, ideally some concept of implicit domains


class ElectricalSink(ElectricalBase):
  def __init__(self, model: Optional[ElectricalSink] = None,
               voltage_limits: RangeLike = Default(RangeExpr.ALL),
               current_draw: RangeLike = Default(RangeExpr.ZERO)) -> None:
    super().__init__()
    self.bridge_type = ElectricalSinkBridge

    if model is not None:
      # TODO check that both model and individual parameters aren't overdefined
      voltage_limits = model.voltage_limits
      current_draw = model.current_draw

    self.voltage_limits: RangeExpr = self.Parameter(RangeExpr(voltage_limits))
    self.current_draw: RangeExpr = self.Parameter(RangeExpr(current_draw))


class ElectricalSinkAdapterDigitalSource(CircuitPortAdapter['DigitalSource']):
  @init_in_parent
  def __init__(self):
    from .DigitalPorts import DigitalSource
    super().__init__()
    self.src = self.Port(ElectricalSink(
      voltage_limits=RangeExpr.ALL * Volt,
      current_draw=RangeExpr()
    ))
    self.dst = self.Port(DigitalSource(
      voltage_out=self.src.link().voltage,
      # TODO propagation of current limits?
      output_thresholds=(0, self.src.link().voltage.lower())
    ))
    self.assign(self.src.current_draw, self.dst.link().current_drawn)  # TODO might be an overestimate


class ElectricalSinkAdapterAnalogSource(CircuitPortAdapter['AnalogSource']):
  @init_in_parent
  def __init__(self):
    from .AnalogPort import AnalogSource
    super().__init__()
    self.src = self.Port(ElectricalSink(
      voltage_limits=(-float('inf'), float('inf'))*Volt,
      current_draw=RangeExpr()
    ))
    self.dst = self.Port(AnalogSource(
      voltage_out=self.src.link().voltage,
      impedance=(0, 0)*Ohm,  # TODO not actually true, but pretty darn low?
    ))

    # TODO might be an overestimate
    self.assign(self.src.current_draw, self.dst.link().current_draw)  # type: ignore


class ElectricalSource(ElectricalBase):
  def __init__(self, model: Optional[ElectricalSource] = None,
               voltage_out: RangeLike = Default(RangeExpr.EMPTY_ZERO),
               current_limits: RangeLike = Default(RangeExpr.ALL)) -> None:
    super().__init__()
    self.bridge_type = ElectricalSourceBridge
    self.adapter_types = [ElectricalSinkAdapterDigitalSource, ElectricalSinkAdapterAnalogSource]

    if model is not None:
      # TODO check that both model and individual parameters aren't overdefined
      voltage_out = model.voltage_out
      current_limits = model.current_limits

    self.voltage_out: RangeExpr = self.Parameter(RangeExpr(voltage_out))
    self.current_limits: RangeExpr = self.Parameter(RangeExpr(current_limits))

  def as_digital_source(self) -> DigitalSource:
    return self._convert(ElectricalSinkAdapterDigitalSource())

  def as_analog_source(self) -> AnalogSource:
    return self._convert(ElectricalSinkAdapterAnalogSource())


def Ground(current_draw: RangeLike = RangeExpr.ZERO * Amp) -> ElectricalSink:
  return ElectricalSink(voltage_limits=RangeExpr.ZERO * Volt, current_draw=current_draw)

def GroundSource() -> ElectricalSource:
  return ElectricalSource(voltage_out=RangeExpr.ZERO * Volt, current_limits=RangeExpr.ZERO * Amp)

# Standard port tags for implicit connection scopes / auto-connecting power supplies
Common = PortTag(ElectricalSink)  # Common ground (0v) port

Power = PortTag(ElectricalSink)  # General positive voltage port, should only be mutually exclusive with the below

# Note: in the current model, no explicit "power tag" is equivalent to digital / noisy supply
# TODO bring these back, on an optional basis
# PowerAnalog = PortTag(ElectricalSink)  # Analog power supply, ideally kept isolated from digital supply
# PowerRf = PortTag(ElectricalSink)  # RF power supply
# Power1v8 = PortTag(ElectricalSink)  # 1.8v tolerant power input port
# Power2v5 = PortTag(ElectricalSink)  # 2.5v tolerant power input port
# Power3v3 = PortTag(ElectricalSink)  # 3.3v tolerant power input port
# Power5v = PortTag(ElectricalSink)  # 5.0v tolerant power input port
# Power12v = PortTag(ElectricalSink)  # 12v tolerant power input port
