from typing import List, cast, Optional, Dict

from ..electronics_model import *
from .Categories import Interface


@abstract_block
class AnalogSwitch(Interface, KiCadImportableBlock, Block):
  """Base class for a n-ported analog switch with passive-typed ports."""
  def symbol_pinning(self, symbol_name: str) -> Dict[str, BasePort]:
    assert symbol_name.startswith('edg_importable:Mux')  # can be any Mux
    count = int(symbol_name.removeprefix('edg_importable:Mux'))
    pins: Dict[str, BasePort] = {
      'C': self.com, 'S': self.control, 'V+': self.pwr,  'V-': self.gnd
    }
    pins.update({str(i+1): self.inputs.request() for i in range(count)})
    return pins

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


class AnalogSwitchTree(AnalogSwitch, GeneratorBlock):
  """Generates an n-ported analog switch by creating a tree of individual, smaller switches.
  Parameterized by the size of the element switches."""
  @init_in_parent
  def __init__(self, switch_size: IntLike = 0):
    super().__init__()
    self.switch_size = self.ArgParameter(switch_size)
    self.generator_param(self.switch_size, self.inputs.requested())

  def generate(self):
    import math
    super().generate()

    switch_size = self.get(self.switch_size)
    elts = self.get(self.inputs.requested())
    assert switch_size > 1, f"switch size {switch_size} must be greater than 1"
    assert len(elts) > 1, "passthrough AnalogSwitchTree not (yet?) supported"
    self.sw = ElementDict[AnalogSwitch]()

    self.inputs.defined()
    self.control.defined()

    stage_num_controls = math.ceil(math.log2(switch_size))  # number of control IOs per stage
    ports = [self.inputs.append_elt(Passive.empty(), str(i)) for i in range(len(elts))]
    all_switches = []
    switch_stage = 0

    while len(ports) > 1:  # stages in the tree
      num_switches = math.ceil(len(ports) / switch_size)
      new_ports = []  # output ports of this current stage

      stage_control_ios = [self.control.append_elt(DigitalSink.empty(), f'{switch_stage}_{i}')
                           for i in range(stage_num_controls)]

      for sw_i in range(num_switches):
        sw = self.sw[f'{switch_stage}_{sw_i}'] = self.Block(AnalogSwitch())
        all_switches.append(sw)
        self.connect(sw.pwr, self.pwr)
        self.connect(sw.gnd, self.gnd)

        for sw_port_i in range(switch_size):
          port_i = sw_i * switch_size + sw_port_i
          if port_i < len(ports):
            self.connect(sw.inputs.request(str(sw_port_i)), ports[port_i])
        new_ports.append(sw.com)

        for (i, control_io) in enumerate(stage_control_ios):
          self.connect(sw.control.request(str(i)), control_io)

      ports = new_ports
      switch_stage += 1

    assert len(ports) == 1
    self.connect(ports[0], self.com)

    # Create bulk tree model
    # Voltage is unchanged
    self.assign(self.analog_voltage_limits, all_switches[0].analog_voltage_limits)
    # Current limit is bottlenecked by the final stage
    self.assign(self.analog_current_limits,
                all_switches[0].analog_current_limits / (switch_size ** (switch_stage - 1)))
    # On resistance sums through each stage
    self.assign(self.analog_on_resistance, all_switches[0].analog_on_resistance * switch_stage)


class AnalogMuxer(Interface, KiCadImportableBlock, GeneratorBlock):
  """Wrapper around AnalogSwitch that provides muxing functionality - multiple sink ports, one source port.
  """
  def symbol_pinning(self, symbol_name: str) -> Dict[str, BasePort]:
    assert symbol_name.startswith('edg_importable:Mux')  # can be any Mux
    count = int(symbol_name.removeprefix('edg_importable:Mux'))
    pins: Dict[str, BasePort] = {
      'C': self.out, 'S': self.control, 'V+': self.pwr, 'V-': self.gnd
    }
    pins.update({str(i+1): self.inputs.request(str(i)) for i in range(count)})
    return pins

  def __init__(self) -> None:
    super().__init__()
    self.device = self.Block(AnalogSwitch())
    self.pwr = self.Export(self.device.pwr, [Power])
    self.gnd = self.Export(self.device.gnd, [Common])
    self.control = self.Export(self.device.control)

    self.inputs = self.Port(Vector(AnalogSink.empty()))
    self.out = self.Export(self.device.com.adapt_to(AnalogSource(
      voltage_out=self.inputs.hull(lambda x: x.link().voltage),
      signal_out=self.inputs.hull(lambda x: x.link().signal),
      current_limits=self.device.analog_current_limits,  # this device only, current draw propagated
      impedance=self.device.analog_on_resistance + self.inputs.hull(lambda x: x.link().source_impedance)
    )))

    self.generator_param(self.inputs.requested())

  def generate(self):
    super().generate()
    self.inputs.defined()
    for elt in self.get(self.inputs.requested()):
      self.connect(
        self.inputs.append_elt(AnalogSink.empty(), elt),
        self.device.inputs.request(elt).adapt_to(AnalogSink(
          voltage_limits=self.device.analog_voltage_limits,  # this device only, voltages propagated
          current_draw=self.out.link().current_drawn,
          impedance=self.out.link().sink_impedance + self.device.analog_on_resistance
        )))

  def mux_to(self, inputs: Optional[List[Port[AnalogLink]]] = None,
             output: Optional[Port[AnalogLink]] = None) -> 'AnalogMuxer':
    if inputs is not None:
      for i, input_port in enumerate(inputs):
        cast(Block, builder.get_enclosing_block()).connect(input_port, self.inputs.request(str(i)))
    if output is not None:
      cast(Block, builder.get_enclosing_block()).connect(output, self.out)
    return self


class AnalogDemuxer(Interface, GeneratorBlock):
  """Wrapper around AnalogSwitch that provides demuxing functionality - multiple source ports, one sink port.
  """
  def __init__(self) -> None:
    super().__init__()
    self.device = self.Block(AnalogSwitch())
    self.pwr = self.Export(self.device.pwr, [Power])
    self.gnd = self.Export(self.device.gnd, [Common])
    self.control = self.Export(self.device.control)

    self.outputs = self.Port(Vector(AnalogSource.empty()))
    self.input = self.Export(self.device.com.adapt_to(AnalogSink(
      voltage_limits=self.device.analog_voltage_limits,  # this device only, voltages propagated
      current_draw=self.outputs.hull(lambda x: x.link().current_drawn),
      impedance=self.device.analog_on_resistance + self.outputs.hull(lambda x: x.link().sink_impedance)
    )))

    self.generator_param(self.outputs.requested())

  def generate(self):
    super().generate()
    self.outputs.defined()
    for elt in self.get(self.outputs.requested()):
      self.connect(
        self.outputs.append_elt(AnalogSource.empty(), elt),
        self.device.inputs.request(elt).adapt_to(AnalogSource(
          voltage_out=self.input.link().voltage,
          signal_out=self.input.link().signal,
          current_limits=self.device.analog_current_limits,  # this device only, voltages propagated
          impedance=self.input.link().source_impedance + self.device.analog_on_resistance
        )))

  def demux_to(self, input: Optional[Port[AnalogLink]] = None,
                   outputs: Optional[List[Port[AnalogLink]]] = None) -> 'AnalogDemuxer':
    if outputs is not None:
      for i, output in enumerate(outputs):
        cast(Block, builder.get_enclosing_block()).connect(output, self.outputs.request(str(i)))
    if input is not None:
      cast(Block, builder.get_enclosing_block()).connect(input, self.input)
    return self
