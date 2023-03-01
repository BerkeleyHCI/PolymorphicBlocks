from electronics_model import *
from .Categories import *


class DummyPassive(DummyDevice):
  def __init__(self) -> None:
    super().__init__()
    self.io = self.Port(Passive(), [InOut])


class DummyVoltageSource(DummyDevice):
  @init_in_parent
  def __init__(self, voltage_out: RangeLike = Default(RangeExpr.EMPTY_ZERO),
               current_limits: RangeLike = Default(RangeExpr.ALL)) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSource(
      voltage_out=voltage_out,
      current_limits=current_limits
    ), [Power, InOut])

    self.current_drawn = self.Parameter(RangeExpr(self.pwr.link().current_drawn))
    self.voltage_limits = self.Parameter(RangeExpr(self.pwr.link().voltage_limits))


class DummyVoltageSink(DummyDevice):
  @init_in_parent
  def __init__(self, voltage_limit: RangeLike = Default(RangeExpr.ALL),
               current_draw: RangeLike = Default(RangeExpr.ZERO)) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink(
      voltage_limits=voltage_limit,
      current_draw=current_draw
    ), [Power, InOut])
    self.voltage = self.Parameter(RangeExpr(self.pwr.link().voltage))
    self.current_limits = self.Parameter(RangeExpr(self.pwr.link().current_limits))


class DummyDigitalSink(DummyDevice):
  @init_in_parent
  def __init__(self, voltage_limit: RangeLike = Default(RangeExpr.ALL),
               current_draw: RangeLike = Default(RangeExpr.ZERO)) -> None:
    super().__init__()

    self.io = self.Port(DigitalSink(
      voltage_limits=voltage_limit,
      current_draw=current_draw
    ), [InOut])


class DummyAnalogSink(DummyDevice):
  @init_in_parent
  def __init__(self, voltage_limit: RangeLike = Default(RangeExpr.ALL),
               current_draw: RangeLike = Default(RangeExpr.ZERO),
               impedance: RangeLike = Default(RangeExpr.INF)) -> None:
    super().__init__()

    self.io = self.Port(AnalogSink(
      voltage_limits=voltage_limit,
      current_draw=current_draw,
      impedance=impedance
    ), [InOut])


class ForcedVoltageCurrentDraw(DummyDevice, NetBlock):
  """Forces some input current draw regardless of the output's actual current draw value"""
  @init_in_parent
  def __init__(self, forced_current_draw: RangeLike = RangeExpr()) -> None:
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
  def __init__(self, forced_voltage: RangeLike = RangeExpr()) -> None:
    super().__init__()

    self.pwr_in = self.Port(VoltageSink(
      current_draw=RangeExpr(),
      voltage_limits=RangeExpr.ALL
    ), [Input])

    self.pwr_out = self.Port(VoltageSource(
      voltage_out=forced_voltage,
      current_limits=RangeExpr.ALL
    ), [Output])

    self.assign(self.pwr_in.current_draw, self.pwr_out.link().current_drawn)


class ForcedDigitalSinkCurrentDraw(DummyDevice, NetBlock):
  @init_in_parent
  def __init__(self, forced_current_draw: RangeLike = RangeExpr()) -> None:
    super().__init__()

    self.pwr_in = self.Port(DigitalSink(
      current_draw=forced_current_draw,
      voltage_limits=RangeExpr.ALL,
      input_thresholds=RangeExpr.EMPTY_DIT
    ), [Input])

    self.pwr_out = self.Port(DigitalSource(
      voltage_out=self.pwr_in.link().voltage,
      current_limits=RangeExpr.ALL,
      output_thresholds=self.pwr_in.link().output_thresholds
    ), [Output])
