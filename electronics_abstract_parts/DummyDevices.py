from typing import List, cast, Dict

from electronics_model import *
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


class MergedVoltageSource(DummyDevice, NetBlock, GeneratorBlock):
  def __init__(self) -> None:
    super().__init__()

    self.pwr_ins = self.Port(Vector(VoltageSink.empty()))
    self.pwr_out = self.Port(VoltageSource(
      voltage_out=RangeExpr(),
      current_limits=RangeExpr.ALL
    ))
    self.generator(self.generate, self.pwr_ins.requested())

  def generate(self, in_requests: List[str]):
    self.pwr_ins.defined()
    for in_request in in_requests:
      self.pwr_ins.append_elt(VoltageSink(
        voltage_limits=RangeExpr.ALL,
        current_draw=self.pwr_out.link().current_drawn
      ), in_request)

    self.assign(self.pwr_out.voltage_out,
                self.pwr_ins.hull(lambda x: x.link().voltage))

  def connected_from(self, *pwr_ins: Port[VoltageLink]) -> 'MergedVoltageSource':
    for pwr_in in pwr_ins:
      cast(Block, builder.get_enclosing_block()).connect(pwr_in, self.pwr_ins.request())
    return self


class MergedAnalogSource(KiCadImportableBlock, DummyDevice, NetBlock, GeneratorBlock):
  def symbol_pinning(self, symbol_name: str) -> Dict[str, Port]:
    assert symbol_name.startswith('edg_importable:Merge')  # can be merge any
    count = int(symbol_name.removeprefix('edg_importable:Merge'))
    pins = {'0': self.output}
    pins.update({str(i+1): self.inputs.request() for i in range(count)})
    return pins

  def __init__(self) -> None:
    super().__init__()

    self.output = self.Port(AnalogSource(
      voltage_out=RangeExpr(),
      current_limits=RangeExpr.ALL,  # limits checked in the link, this port is ideal
      impedance=RangeExpr()
    ))
    self.inputs = self.Port(Vector(AnalogSink.empty()))

    self.generator(self.generate, self.inputs.requested())

  def generate(self, in_requests: List[str]):
    self.inputs.defined()
    for in_request in in_requests:
      self.inputs.append_elt(AnalogSink(
        voltage_limits=RangeExpr.ALL,
        current_draw=self.output.link().current_drawn,
        impedance=self.output.link().sink_impedance
      ), in_request)

    self.assign(self.output.voltage_out,
                self.inputs.hull(lambda x: x.link().voltage))
    self.assign(self.output.impedance,  # covering cases of any or all sources driving
                self.inputs.hull(lambda x: x.link().source_impedance).hull(
                1 / (1 / self.inputs.map_extract(lambda x: x.link().source_impedance)).sum()))

  def connected_from(self, *inputs: Port[AnalogLink]) -> 'MergedAnalogSource':
    for input in inputs:
      cast(Block, builder.get_enclosing_block()).connect(input, self.inputs.request())
    return self


class DummyPassive(DummyDevice):
  def __init__(self) -> None:
    super().__init__()
    self.io = self.Port(Passive(), [InOut])


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
    ), [Input])
