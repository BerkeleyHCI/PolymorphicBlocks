from __future__ import annotations

from typing import TypeVar, Type, Dict

from ..core import *
from .GroundPort import Ground
from .AnalogPort import AnalogSource, AnalogSink
from .CircuitBlock import CircuitLink, CircuitPortBridge, CircuitPortAdapter
from .DigitalPorts import DigitalSource, DigitalSink, DigitalBidir
from .VoltagePorts import CircuitPort, VoltageSource, VoltageSink
from ..core.Ports import PortPrototype


class PassiveLink(CircuitLink):
  """Copper-only connection"""
  def __init__(self):
    super().__init__()
    self.passives = self.Port(Vector(Passive()))


class PassiveAdapterGround(CircuitPortAdapter[Ground]):
  def __init__(self, voltage_limits: RangeLike = RangeExpr.ALL):
    super().__init__()
    self.src = self.Port(Passive())
    self.dst = self.Port(Ground(voltage_limits=voltage_limits))


class PassiveAdapterVoltageSource(CircuitPortAdapter[VoltageSource]):
  # TODO we can't use **kwargs b/c init_in_parent needs the initializer list
  def __init__(self, voltage_out: RangeLike = RangeExpr.ZERO,
               current_limits: RangeLike = RangeExpr.ALL):
    super().__init__()
    self.src = self.Port(Passive())
    self.dst = self.Port(VoltageSource(voltage_out=voltage_out, current_limits=current_limits))


class PassiveAdapterVoltageSink(CircuitPortAdapter[VoltageSink]):
  # TODO we can't use **kwargs b/c the init hook needs an initializer list
  def __init__(self, voltage_limits: RangeLike = RangeExpr.ALL,
               current_draw: RangeLike = RangeExpr.ZERO):
    super().__init__()
    self.src = self.Port(Passive())
    self.dst = self.Port(VoltageSink(voltage_limits=voltage_limits, current_draw=current_draw))


class PassiveAdapterDigitalSource(CircuitPortAdapter[DigitalSource]):
  # TODO we can't use **kwargs b/c the init hook needs an initializer list
  def __init__(self, voltage_out: RangeLike = RangeExpr.ZERO,
               current_limits: RangeLike = RangeExpr.ALL,
               output_thresholds: RangeLike = RangeExpr.ALL,
               pullup_capable: BoolLike = False,
               pulldown_capable: BoolLike = False,
               high_driver: BoolLike = True,
               low_driver: BoolLike = True,
               _bridged_internal: BoolLike = False):
    super().__init__()
    self.src = self.Port(Passive())
    self.dst = self.Port(DigitalSource(voltage_out=voltage_out, current_limits=current_limits,
                                       output_thresholds=output_thresholds,
                                       pullup_capable=pullup_capable, pulldown_capable=pulldown_capable,
                                       high_driver=high_driver, low_driver=low_driver,
                                       _bridged_internal=_bridged_internal))


class PassiveAdapterDigitalSink(CircuitPortAdapter[DigitalSink]):
  # TODO we can't use **kwargs b/c the init hook needs an initializer list
  def __init__(self, voltage_limits: RangeLike = RangeExpr.ALL,
               current_draw: RangeLike = RangeExpr.ZERO,
               input_thresholds: RangeLike = RangeExpr.EMPTY,
               pullup_capable: BoolLike = False,
               pulldown_capable: BoolLike = False,
               _bridged_internal: BoolLike = False):
    super().__init__()
    self.src = self.Port(Passive())
    self.dst = self.Port(DigitalSink(voltage_limits=voltage_limits, current_draw=current_draw,
                                     input_thresholds=input_thresholds,
                                     pullup_capable=pullup_capable,
                                     pulldown_capable=pulldown_capable,
                                     _bridged_internal=_bridged_internal))


class PassiveAdapterDigitalBidir(CircuitPortAdapter[DigitalBidir]):
  # TODO we can't use **kwargs b/c the init hook needs an initializer list
  def __init__(self, voltage_limits: RangeLike = RangeExpr.ALL,
               current_draw: RangeLike = RangeExpr.ZERO,
               voltage_out: RangeLike = RangeExpr.ZERO,
               current_limits: RangeLike = RangeExpr.ALL,
               input_thresholds: RangeLike = RangeExpr.EMPTY,
               output_thresholds: RangeLike = RangeExpr.ALL,
               *,
               pullup_capable: BoolLike = False,
               pulldown_capable: BoolLike = False,
               _bridged_internal: BoolLike = False):
    super().__init__()
    self.src = self.Port(Passive())
    self.dst = self.Port(DigitalBidir(voltage_limits=voltage_limits, current_draw=current_draw,
                                      voltage_out=voltage_out, current_limits=current_limits,
                                      input_thresholds=input_thresholds, output_thresholds=output_thresholds,
                                      pullup_capable=pullup_capable, pulldown_capable=pulldown_capable,
                                      _bridged_internal=_bridged_internal))


class PassiveAdapterAnalogSource(CircuitPortAdapter[AnalogSource]):
  # TODO we can't use **kwargs b/c the init hook needs an initializer list
  def __init__(self, voltage_out: RangeLike = RangeExpr.ZERO, signal_out: RangeLike = RangeExpr.ZERO,
               current_limits: RangeLike = RangeExpr.ALL, impedance: RangeLike = RangeExpr.ZERO):
    super().__init__()
    self.src = self.Port(Passive())
    self.dst = self.Port(AnalogSource(voltage_out=voltage_out, signal_out=signal_out,
                                      current_limits=current_limits, impedance=impedance))


class PassiveAdapterAnalogSink(CircuitPortAdapter[AnalogSink]):
  # TODO we can't use **kwargs b/c the init hook needs an initializer list
  def __init__(self, voltage_limits: RangeLike = RangeExpr.ALL, signal_limits: RangeLike = RangeExpr.ALL,
               current_draw: RangeLike = RangeExpr.ZERO,
               impedance: RangeLike = RangeExpr.INF):
    super().__init__()
    self.src = self.Port(Passive())
    self.dst = self.Port(AnalogSink(voltage_limits=voltage_limits, signal_limits=signal_limits,
                                    current_draw=current_draw, impedance=impedance))


class PassiveBridge(CircuitPortBridge):
  def __init__(self) -> None:
    super().__init__()
    self.outer_port = self.Port(Passive())
    self.inner_link = self.Port(Passive())


class Passive(CircuitPort[PassiveLink]):
  """Basic copper-only port, which can be adapted to a more strongly typed Voltage/Digital/Analog* port"""
  adapter_type_map: Dict[Type[Port], Type[CircuitPortAdapter]] = {
    Ground: PassiveAdapterGround,
    VoltageSource: PassiveAdapterVoltageSource,
    VoltageSink: PassiveAdapterVoltageSink,
    DigitalSink: PassiveAdapterDigitalSink,
    DigitalSource: PassiveAdapterDigitalSource,
    DigitalBidir: PassiveAdapterDigitalBidir,
    AnalogSink: PassiveAdapterAnalogSink,
    AnalogSource: PassiveAdapterAnalogSource
  }
  link_type = PassiveLink
  bridge_type = PassiveBridge

  AdaptTargetType = TypeVar('AdaptTargetType', bound=CircuitPort)
  def adapt_to(self, that: AdaptTargetType) -> AdaptTargetType:
    # this is an experimental style that takes a port that has initializers but is not bound
    # and automatically creates an adapter from it, by matching the port parameter fields
    # with the adapter constructor argument fields by name
    assert isinstance(that, PortPrototype), 'adapter target must be port'
    assert that._tpe in self.adapter_type_map, f'no adapter to {that.__class__}'
    adapter_cls = self.adapter_type_map[that._tpe]

    assert not that._args, 'adapter target cannot have positional args'
    return self._convert(adapter_cls(**that._kwargs))
