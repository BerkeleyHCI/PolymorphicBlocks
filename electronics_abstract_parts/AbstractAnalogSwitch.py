from typing import List, cast, Optional

from electronics_model import *
from .DummyDevices import MergedAnalogSource
from .AbstractPassives import Resistor


@abstract_block
class AnalogSwitch(Block):
  """Base class for a n-ported analog switch with passive-typed ports."""
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.gnd = self.Port(Ground.empty(), [Common])

    self.control = self.Port(Vector(DigitalSink.empty()))  # length source

    self.com = self.Port(Passive.empty())
    self.inputs = self.Port(Vector(Passive.empty()))

    # TODO: this is a different way of modeling parts - parameters in the part itself
    # instead of on the ports (because this doesn't have typed ports)
    self.analog_voltage_limits = self.Parameter(RangeExpr())  # for all analog ports
    self.analog_current_limits = self.Parameter(RangeExpr())  # for all analog ports
    self.analog_on_resistance = self.Parameter(RangeExpr())


class AnalogMuxer(GeneratorBlock):
  """Wrapper around AnalogSwitch that provides muxing functionality - multiple sink ports, one source port.
  """
  def __init__(self) -> None:
    super().__init__()
    self.device = self.Block(AnalogSwitch())
    self.pwr = self.Export(self.device.pwr, [Power])
    self.gnd = self.Export(self.device.gnd, [Common])
    self.control = self.Export(self.device.control)

    self.inputs = self.Port(Vector(AnalogSink.empty()))
    self.out = self.Export(self.device.com.as_analog_source(
      voltage_out=self.inputs.hull(lambda x: x.link().voltage),
      current_limits=self.device.analog_current_limits,
      # impedance=self.device.analog_on_resistance + self.inputs.hull(lambda x: x.link().source_impedance)
    ))

    self.generator(self.generate, self.inputs.allocated())

  def generate(self, elts: List[str]):
    self.inputs.defined()
    for elt in elts:
      self.connect(
        self.inputs.append_elt(AnalogSink().empty(), elt),
        self.device.inputs.allocate(elt).as_analog_sink(
          voltage_limits=self.device.analog_voltage_limits,
          current_draw=self.out.link().current_drawn,
          impedance=self.out.link().sink_impedance + self.device.analog_on_resistance
        ))

  def mux_to(self, inputs: Optional[List[Port[AnalogLink]]] = None,
             output: Optional[Port[AnalogLink]] = None) -> 'AnalogMuxer':
    if inputs is not None:
      for i, input_port in enumerate(inputs):
        cast(Block, builder.get_enclosing_block()).connect(input_port, self.inputs.allocate(str(i)))
    if output is not None:
      cast(Block, builder.get_enclosing_block()).connect(output, self.out)
    return self


class AnalogDemuxer(GeneratorBlock):
  """Wrapper around AnalogSwitch that provides demuxing functionality - multiple source ports, one sink port.
  """
  def __init__(self) -> None:
    super().__init__()
    self.device = self.Block(AnalogSwitch())
    self.pwr = self.Export(self.device.pwr, [Power])
    self.gnd = self.Export(self.device.gnd, [Common])
    self.control = self.Export(self.device.control)

    self.outputs = self.Port(Vector(AnalogSource.empty()))
    self.input = self.Export(self.device.com.as_analog_sink(
      voltage_limits=self.device.analog_voltage_limits,
      current_draw=self.outputs.hull(lambda x: x.link().current_drawn),
      impedance=self.device.analog_on_resistance + self.outputs.hull(lambda x: x.link().sink_impedance)
    ))

    self.generator(self.generate, self.outputs.allocated())

  def generate(self, elts: List[str]):
    self.outputs.defined()
    for elt in elts:
      self.connect(
        self.outputs.append_elt(AnalogSource().empty(), elt),
        self.device.inputs.allocate(elt).as_analog_source(
          voltage_out=self.input.link().voltage,
          current_limits=self.device.analog_current_limits,
          impedance=self.input.link().source_impedance + self.device.analog_on_resistance
        ))

  def demux_to(self, input: Optional[Port[AnalogLink]] = None,
                   outputs: Optional[List[Port[AnalogLink]]] = None) -> 'AnalogDemuxer':
    if outputs is not None:
      for i, output in enumerate(outputs):
        cast(Block, builder.get_enclosing_block()).connect(output, self.outputs.allocate(str(i)))
    if input is not None:
      cast(Block, builder.get_enclosing_block()).connect(input, self.input)
    return self
