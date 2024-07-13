from typing import Dict

from ..electronics_model import *
from .Categories import *


class DummyPassive(DummyDevice):
  def __init__(self) -> None:
    super().__init__()
    self.io = self.Port(Passive(), [InOut])


class DummyGround(DummyDevice):
  def __init__(self) -> None:
    super().__init__()
    self.gnd = self.Port(Ground(), [Common, InOut])


class DummyVoltageSource(DummyDevice):
  @init_in_parent
  def __init__(self, voltage_out: RangeLike = RangeExpr.ZERO,
               current_limits: RangeLike = RangeExpr.ALL) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSource(
      voltage_out=voltage_out,
      current_limits=current_limits
    ), [Power, InOut])

    self.current_drawn = self.Parameter(RangeExpr(self.pwr.link().current_drawn))
    self.voltage_limits = self.Parameter(RangeExpr(self.pwr.link().voltage_limits))


class DummyVoltageSink(DummyDevice):
  @init_in_parent
  def __init__(self, voltage_limit: RangeLike = RangeExpr.ALL,
               current_draw: RangeLike = RangeExpr.ZERO) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink(
      voltage_limits=voltage_limit,
      current_draw=current_draw
    ), [Power, InOut])
    self.voltage = self.Parameter(RangeExpr(self.pwr.link().voltage))
    self.current_limits = self.Parameter(RangeExpr(self.pwr.link().current_limits))


class DummyDigitalSink(DummyDevice):
  @init_in_parent
  def __init__(self, voltage_limit: RangeLike = RangeExpr.ALL,
               current_draw: RangeLike = RangeExpr.ZERO) -> None:
    super().__init__()

    self.io = self.Port(DigitalSink(
      voltage_limits=voltage_limit,
      current_draw=current_draw
    ), [InOut])


class DummyAnalogSource(DummyDevice):
  @init_in_parent
  def __init__(self, voltage_out: RangeLike = RangeExpr.ZERO,
               signal_out: RangeLike = RangeExpr.EMPTY,
               current_limits: RangeLike = RangeExpr.ALL,
               impedance: RangeLike = RangeExpr.ZERO) -> None:
    super().__init__()

    self.io = self.Port(AnalogSource(
      voltage_out=voltage_out,
      signal_out=signal_out,
      current_limits=current_limits,
      impedance=impedance
    ), [InOut])


class DummyAnalogSink(DummyDevice):
  @init_in_parent
  def __init__(self, voltage_limit: RangeLike = RangeExpr.ALL,
               signal_limit: RangeLike = RangeExpr.ALL,
               current_draw: RangeLike = RangeExpr.ZERO,
               impedance: RangeLike = RangeExpr.INF) -> None:
    super().__init__()

    self.io = self.Port(AnalogSink(
      voltage_limits=voltage_limit,
      signal_limits=signal_limit,
      current_draw=current_draw,
      impedance=impedance
    ), [InOut])


class ForcedVoltageCurrentDraw(DummyDevice, NetBlock):
  """Forces some input current draw regardless of the output's actual current draw value"""
  @init_in_parent
  def __init__(self, forced_current_draw: RangeLike) -> None:
    super().__init__()

    self.pwr_in = self.Port(VoltageSink(
      current_draw=forced_current_draw,
      voltage_limits=RangeExpr.ALL
    ), [Input])

    self.pwr_out = self.Port(VoltageSource(
      voltage_out=self.pwr_in.link().voltage,
      current_limits=RangeExpr.ALL
    ), [Output])


class ForcedVoltage(DummyDevice, NetBlock):
  """Forces some voltage on the output regardless of the input's actual voltage.
  Current draw is passed through unchanged."""
  @init_in_parent
  def __init__(self, forced_voltage: RangeLike) -> None:
    super().__init__()

    self.pwr_in = self.Port(VoltageSink(
      current_draw=RangeExpr()
    ), [Input])

    self.pwr_out = self.Port(VoltageSource(
      voltage_out=forced_voltage
    ), [Output])

    self.assign(self.pwr_in.current_draw, self.pwr_out.link().current_drawn)


class ForcedVoltageCurrent(DummyDevice, NetBlock):
  """Forces some voltage and current on the output regardless of the input's actual parameters."""
  @init_in_parent
  def __init__(self, forced_voltage: RangeLike, forced_current: RangeLike) -> None:
    super().__init__()

    self.pwr_in = self.Port(VoltageSink(
      current_draw=forced_current
    ), [Input])

    self.pwr_out = self.Port(VoltageSource(
      voltage_out=forced_voltage
    ), [Output])


class ForcedAnalogVoltage(DummyDevice, NetBlock):
  @init_in_parent
  def __init__(self, forced_voltage: RangeLike = RangeExpr()) -> None:
    super().__init__()

    self.signal_in = self.Port(AnalogSink(
      current_draw=RangeExpr()
    ), [Input])

    self.signal_out = self.Port(AnalogSource(
      voltage_out=forced_voltage,
      signal_out=self.signal_in.link().signal
    ), [Output])

    self.assign(self.signal_in.current_draw, self.signal_out.link().current_drawn)


class ForcedAnalogSignal(KiCadImportableBlock, DummyDevice, NetBlock):
  @init_in_parent
  def __init__(self, forced_signal: RangeLike = RangeExpr()) -> None:
    super().__init__()

    self.signal_in = self.Port(AnalogSink(
      current_draw=RangeExpr()
    ), [Input])

    self.signal_out = self.Port(AnalogSource(
      voltage_out=self.signal_in.link().voltage,
      signal_out=forced_signal,
      current_limits=self.signal_in.link().current_limits
    ), [Output])

    self.assign(self.signal_in.current_draw, self.signal_out.link().current_drawn)

  def symbol_pinning(self, symbol_name: str) -> Dict[str, BasePort]:
    assert symbol_name == 'edg_importable:Adapter'
    return {'1': self.signal_in, '2': self.signal_out}


class ForcedDigitalSinkCurrentDraw(DummyDevice, NetBlock):
  @init_in_parent
  def __init__(self, forced_current_draw: RangeLike = RangeExpr()) -> None:
    super().__init__()

    self.pwr_in = self.Port(DigitalSink(
      current_draw=forced_current_draw,
      voltage_limits=RangeExpr.ALL,
      input_thresholds=RangeExpr.EMPTY
    ), [Input])

    self.pwr_out = self.Port(DigitalSource(
      voltage_out=self.pwr_in.link().voltage,
      current_limits=RangeExpr.ALL,
      output_thresholds=self.pwr_in.link().output_thresholds
    ), [Output])
