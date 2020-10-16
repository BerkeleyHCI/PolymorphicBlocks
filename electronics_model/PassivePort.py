from __future__ import annotations

from edg_core import *

from .Units import Volt, Amp
from .CircuitBlock import CircuitLink, CircuitPortBridge, CircuitPortAdapter
from .ElectricalPorts import CircuitPort, ElectricalSource, ElectricalSink
from .DigitalPorts import DigitalSource, DigitalSink, DigitalBidir, DigitalSingleSource
from .AnalogPort import AnalogSource, AnalogSink


class PassiveLink(CircuitLink):
  """Copper-only connection"""
  def __init__(self):
    super().__init__()
    self.passives = self.Port(Vector(Passive()))


class PassiveAdapterElectricalSource(CircuitPortAdapter[ElectricalSource]):
  @init_in_parent
  def __init__(self, voltage_out: RangeLike = RangeExpr(), current_limits: RangeLike = RangeExpr()):
    super().__init__()
    self.src = self.Port(Passive())
    self.dst = self.Port(ElectricalSource(voltage_out=voltage_out, current_limits=current_limits))


class PassiveAdapterElectricalSink(CircuitPortAdapter[ElectricalSink]):
  @init_in_parent
  def __init__(self, voltage_limits: RangeLike = RangeExpr(), current_draw: RangeLike = RangeExpr()):
    super().__init__()
    self.src = self.Port(Passive())
    self.dst = self.Port(ElectricalSink(voltage_limits=voltage_limits, current_draw=current_draw))


class PassiveAdapterDigitalSource(CircuitPortAdapter[DigitalSource]):
  @init_in_parent
  def __init__(self, **kwargs):
    super().__init__()
    self.src = self.Port(Passive())
    self.dst = self.Port(DigitalSource(**kwargs))


class PassiveAdapterDigitalSink(CircuitPortAdapter[DigitalSink]):
  @init_in_parent
  def __init__(self, **kwargs):
    super().__init__()
    self.src = self.Port(Passive())
    self.dst = self.Port(DigitalSink(**kwargs))


class PassiveAdapterDigitalBidir(CircuitPortAdapter[DigitalBidir]):
  @init_in_parent
  def __init__(self, **kwargs):
    super().__init__()
    self.src = self.Port(Passive())
    self.dst = self.Port(DigitalBidir(**kwargs))


class PassiveAdapterDigitalSingleSource(CircuitPortAdapter[DigitalSingleSource]):
  @init_in_parent
  def __init__(self, **kwargs):
    super().__init__()
    self.src = self.Port(Passive())
    self.dst = self.Port(DigitalSingleSource(**kwargs))


class PassiveAdapterAnalogSource(CircuitPortAdapter[AnalogSource]):
  @init_in_parent
  def __init__(self, **kwargs):
    super().__init__()
    self.src = self.Port(Passive())
    self.dst = self.Port(AnalogSource(**kwargs))


class PassiveAdapterAnalogSink(CircuitPortAdapter[AnalogSink]):
  @init_in_parent
  def __init__(self, **kwargs):
    super().__init__()
    self.src = self.Port(Passive())
    self.dst = self.Port(AnalogSink(**kwargs))


class PassiveBridge(CircuitPortBridge):
  def __init__(self) -> None:
    super().__init__()
    self.outer_port = self.Port(Passive())
    self.inner_link = self.Port(Passive())


class Passive(CircuitPort[PassiveLink]):
  """Copper-only port, which can be adapted to ElectricalPassive/DigitalPassive/AnalogPassive to tack on to a
  typed port"""
  def __init__(self) -> None:
    super().__init__()

    self.link_type = PassiveLink
    self.bridge_type = PassiveBridge
    self.adapter_types = [PassiveAdapterElectricalSource, PassiveAdapterElectricalSink,
                          PassiveAdapterDigitalSource, PassiveAdapterDigitalSink, PassiveAdapterDigitalBidir,
                          PassiveAdapterDigitalSingleSource,
                          PassiveAdapterAnalogSource, PassiveAdapterAnalogSink]

  def as_electrical_source(self, voltage_out: RangeLike = RangeExpr(), current_limits: RangeLike = RangeExpr()) -> ElectricalSource:
    return self._convert(PassiveAdapterElectricalSource(voltage_out=voltage_out, current_limits=current_limits))

  def as_electrical_sink(self, voltage_limits: RangeLike = RangeExpr(), current_draw: RangeLike = RangeExpr()) -> ElectricalSink:
    return self._convert(PassiveAdapterElectricalSink(voltage_limits=voltage_limits, current_draw=current_draw))

  def as_ground(self, current_draw: RangeLike = RangeExpr()) -> ElectricalSink:
    return self._convert(PassiveAdapterElectricalSink(voltage_limits=(0, 0) * Volt, current_draw=current_draw))

  def as_ground_source(self) -> ElectricalSource:
    return self._convert(PassiveAdapterElectricalSource(voltage_out=(0, 0) * Volt))

  def as_digital_source(self, **kwargs) -> DigitalSource:
    return self._convert(PassiveAdapterDigitalSource(**kwargs))

  def as_digital_sink(self, **kwargs) -> DigitalSink:
    return self._convert(PassiveAdapterDigitalSink(**kwargs))

  def as_digital_bidir(self, **kwargs) -> DigitalBidir:
    return self._convert(PassiveAdapterDigitalBidir(**kwargs))

  def as_digital_single_source(self, **kwargs) -> DigitalSingleSource:
    return self._convert(PassiveAdapterDigitalSingleSource(**kwargs))

  def as_analog_source(self, **kwargs) -> AnalogSource:
    return self._convert(PassiveAdapterAnalogSource(**kwargs))

  def as_analog_sink(self, **kwargs) -> AnalogSink:
    return self._convert(PassiveAdapterAnalogSink(**kwargs))
