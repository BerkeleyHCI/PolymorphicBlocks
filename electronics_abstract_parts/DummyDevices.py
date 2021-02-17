from electronics_model import *
from .Categories import *


class ElectricalLoad(DummyDevice):
  @init_in_parent
  def __init__(self, voltage_limit: RangeLike = Default(RangeExpr.ALL),
               current_draw: RangeLike = Default(RangeExpr.ZERO)) -> None:
    super().__init__()

    self.pwr = self.Port(ElectricalSink(
      voltage_limits=voltage_limit,
      current_draw=current_draw
    ), [Power])


class ForcedElectricalCurrentDraw(DummyDevice, NetBlock):
  @init_in_parent
  def __init__(self, forced_current_draw: RangeLike = RangeExpr()) -> None:
    super().__init__()

    self.pwr_in = self.Port(ElectricalSink(
      current_draw=forced_current_draw,
      voltage_limits=RangeExpr.ALL
    ), [Input])

    self.pwr_out = self.Port(ElectricalSource(
      voltage_out=self.pwr_in.link().voltage,
      current_limits=RangeExpr.ALL
    ), [Output])


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


class MergedElectricalSource(DummyDevice, NetBlock):
  def __init__(self) -> None:
    super().__init__()

    self.source = self.Port(ElectricalSource(
      voltage_out=RangeExpr(),
      current_limits=RangeExpr.ALL
    ))
    self.sink1 = self.Port(ElectricalSink(voltage_limits=RangeExpr.ALL,
                                          current_draw=self.source.link().current_drawn))
    self.sink2 = self.Port(ElectricalSink(voltage_limits=RangeExpr.ALL,
                                          current_draw=self.source.link().current_drawn))

    self.assign(self.source.voltage_out, (
      self.sink1.link().voltage.lower().min(self.sink2.link().voltage.lower()),
      self.sink1.link().voltage.upper().max(self.sink2.link().voltage.upper())))


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
    ))
