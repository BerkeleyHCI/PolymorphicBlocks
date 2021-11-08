from electronics_model import *
from .AbstractPassives import *
from .Categories import *


class VoltageLoad(DummyDevice):
  @init_in_parent
  def __init__(self, voltage_limit: RangeLike = Default(RangeExpr.ALL),
               current_draw: RangeLike = Default(RangeExpr.ZERO)) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink(
      voltage_limits=voltage_limit,
      current_draw=current_draw
    ), [Power])


class ForcedVoltageCurrentDraw(DummyDevice, NetBlock):
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


class MergedVoltageSource(DummyDevice, NetBlock):
  def __init__(self) -> None:
    super().__init__()

    self.source = self.Port(VoltageSource(
      voltage_out=RangeExpr(),
      current_limits=RangeExpr.ALL
    ))
    self.sink1 = self.Port(VoltageSink(voltage_limits=RangeExpr.ALL,
                                       current_draw=self.source.link().current_drawn))
    self.sink2 = self.Port(VoltageSink(voltage_limits=RangeExpr.ALL,
                                       current_draw=self.source.link().current_drawn))

    self.assign(self.source.voltage_out,
                self.sink1.link().voltage.hull(self.sink2.link().voltage))


class MergedAnalogSource(DummyDevice, NetBlock):
  def __init__(self) -> None:
    super().__init__()

    self.source = self.Port(AnalogSource(
      voltage_out=RangeExpr(),
      current_limits=RangeExpr.ALL,
      impedance=RangeExpr()
    ))
    self.sink1 = self.Port(AnalogSink(
      voltage_limits=RangeExpr.ALL,
      current_draw=self.source.link().current_drawn,
      impedance=self.source.link().sink_impedance
    ))
    self.sink2 = self.Port(AnalogSink(
      voltage_limits=RangeExpr.ALL,
      current_draw=self.source.link().current_drawn,
      impedance=self.source.link().sink_impedance
    ))

    self.assign(self.source.voltage_out,
                self.sink1.link().voltage.hull(self.sink2.link().voltage))
    self.assign(self.source.impedance,
                1 / (1 / self.sink1.link().source_impedance + 1 / self.sink2.link().source_impedance))


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
