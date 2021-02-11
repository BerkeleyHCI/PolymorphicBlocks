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
  # TODO we can't use **kwargs b/c init_in_parent needs the initializer list
  @init_in_parent
  def __init__(self, voltage_out: RangeLike = Default(RangeExpr.EMPTY_ZERO),
               current_limits: RangeLike = Default(RangeExpr.ALL)):
    super().__init__()
    self.src = self.Port(Passive())
    self.dst = self.Port(ElectricalSource(voltage_out=voltage_out, current_limits=current_limits))


class PassiveAdapterElectricalSink(CircuitPortAdapter[ElectricalSink]):
  # TODO we can't use **kwargs b/c init_in_parent needs the initializer list
  @init_in_parent
  def __init__(self, voltage_limits: RangeLike = Default(RangeExpr.ALL),
               current_draw: RangeLike = Default(RangeExpr.ZERO)):
    super().__init__()
    self.src = self.Port(Passive())
    self.dst = self.Port(ElectricalSink(voltage_limits=voltage_limits, current_draw=current_draw))


class PassiveAdapterDigitalSource(CircuitPortAdapter[DigitalSource]):
  # TODO we can't use **kwargs b/c init_in_parent needs the initializer list
  @init_in_parent
  def __init__(self, voltage_out: RangeLike = Default(RangeExpr.EMPTY_ZERO),
               current_limits: RangeLike = Default(RangeExpr.ALL),
               output_thresholds: RangeLike = Default(RangeExpr.ALL)):
    super().__init__()
    self.src = self.Port(Passive())
    self.dst = self.Port(DigitalSource(voltage_out=voltage_out, current_limits=current_limits,
                                       output_thresholds=output_thresholds))


class PassiveAdapterDigitalSink(CircuitPortAdapter[DigitalSink]):
  # TODO we can't use **kwargs b/c init_in_parent needs the initializer list
  @init_in_parent
  def __init__(self, voltage_limits: RangeLike = Default(RangeExpr.ALL),
               current_draw: RangeLike = Default(RangeExpr.ZERO),
               input_thresholds: RangeLike = Default(RangeExpr.EMPTY_DIT)):
    super().__init__()
    self.src = self.Port(Passive())
    self.dst = self.Port(DigitalSink(voltage_limits=voltage_limits, current_draw=current_draw,
                                     input_thresholds=input_thresholds))


class PassiveAdapterDigitalBidir(CircuitPortAdapter[DigitalBidir]):
  # TODO we can't use **kwargs b/c init_in_parent needs the initializer list
  @init_in_parent
  def __init__(self, voltage_limits: RangeLike = Default(RangeExpr.ALL),
               current_draw: RangeLike = Default(RangeExpr.ZERO),
               voltage_out: RangeLike = Default(RangeExpr.EMPTY_ZERO),
               current_limits: RangeLike = Default(RangeExpr.ALL),
               input_thresholds: RangeLike = Default(RangeExpr.EMPTY_DIT),
               output_thresholds: RangeLike = Default(RangeExpr.ALL),
               *,
               pullup_capable: BoolLike = Default(False),
               pulldown_capable: BoolLike = Default(False)):
    super().__init__()
    self.src = self.Port(Passive())
    self.dst = self.Port(DigitalBidir(voltage_limits=voltage_limits, current_draw=current_draw,
                                      voltage_out=voltage_out, current_limits=current_limits,
                                      input_thresholds=input_thresholds, output_thresholds=output_thresholds),
                                      pullup_capable=pullup_capable, pulldown_capable=pulldown_capable)


class PassiveAdapterDigitalSingleSource(CircuitPortAdapter[DigitalSingleSource]):
  # TODO we can't use **kwargs b/c init_in_parent needs the initializer list
  @init_in_parent
  def __init__(self, voltage_out: RangeLike = Default(RangeExpr.EMPTY_ZERO),
               output_thresholds: RangeLike = Default(RangeExpr.ALL), *,
               pullup_capable: BoolLike = Default(False),
               pulldown_capable: BoolLike = Default(False),
               low_signal_driver: BoolLike = Default(False),
               high_signal_driver: BoolLike = Default(False)):
    super().__init__()
    self.src = self.Port(Passive())
    self.dst = self.Port(DigitalSingleSource(voltage_out=voltage_out, output_thresholds=output_thresholds,
                                             pullup_capable=pullup_capable, pulldown_capable=pulldown_capable,
                                             low_signal_driver=low_signal_driver, high_signal_driver=high_signal_driver))


class PassiveAdapterAnalogSource(CircuitPortAdapter[AnalogSource]):
  # TODO we can't use **kwargs b/c init_in_parent needs the initializer list
  @init_in_parent
  def __init__(self, voltage_out: RangeLike = Default(RangeExpr.EMPTY_ZERO),
               current_limits: RangeLike = Default(RangeExpr.ALL),
               impedance: RangeLike = Default(RangeExpr.ZERO)):
    super().__init__()
    self.src = self.Port(Passive())
    self.dst = self.Port(AnalogSource(voltage_out=voltage_out, current_limits=current_limits,
                                      impedance=impedance))


class PassiveAdapterAnalogSink(CircuitPortAdapter[AnalogSink]):
  # TODO we can't use **kwargs b/c init_in_parent needs the initializer list
  @init_in_parent
  def __init__(self, voltage_limits: RangeLike = Default(RangeExpr.ALL),
               current_draw: RangeLike = Default(RangeExpr.ZERO),
               impedance: RangeLike = Default(RangeExpr.INF)):
    super().__init__()
    self.src = self.Port(Passive())
    self.dst = self.Port(AnalogSink(voltage_limits=voltage_limits, current_draw=current_draw,
                                    impedance=impedance))


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

  def as_electrical_source(self, **kwargs) -> ElectricalSource:
    return self._convert(**kwargs)

  def as_electrical_sink(self, **kwargs) -> ElectricalSink:
    return self._convert(PassiveAdapterElectricalSink(**kwargs))

  def as_ground(self, current_draw: RangeLike = Default(RangeExpr.ZERO)) -> ElectricalSink:
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
