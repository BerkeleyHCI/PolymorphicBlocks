from electronics_model import *
from .DummyDevices import MergedAnalogSource
from .AbstractPassives import Resistor


@abstract_block
class AnalogSwitch(Block):
  """Base class for a SPDT analog switch with passive-typed ports.
  """
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.gnd = self.Port(Ground.empty(), [Common])

    self.control = self.Port(DigitalSink.empty())

    self.com = self.Port(Passive.empty())
    self.no = self.Port(Passive.empty())
    self.nc = self.Port(Passive.empty())

    # TODO: this is a different way of modeling parts - parameters in the part itself
    # instead of on the ports (because this doesn't have typed ports)
    self.analog_voltage_limits = self.Parameter(RangeExpr())  # for all analog ports
    self.analog_current_limits = self.Parameter(RangeExpr())  # for all analog ports
    self.analog_on_resistance = self.Parameter(RangeExpr())


class AnalogMuxer(Block):
  """Wrapper around AnalogSwitch that provides muxing functionality - multiple sink ports, one source port.
  """
  def __init__(self) -> None:
    super().__init__()
    self.device = self.Block(AnalogSwitch())
    self.pwr = self.Export(self.device.pwr, [Power])
    self.gnd = self.Export(self.device.gnd, [Common])
    self.control = self.Export(self.device.control)

    # TODO: ideally this would be in0/in1, but just in (for AnalogDemuxer) is a reserved Python keyword
    self.input0 = self.Export(self.device.nc.as_analog_sink(
      voltage_limits=self.device.analog_voltage_limits,
      current_draw=RangeExpr(),  # forward-declared
      impedance=RangeExpr(),  # forward-declared
    ))
    self.input1 = self.Export(self.device.no.as_analog_sink(
      voltage_limits=self.device.analog_voltage_limits,
      current_draw=RangeExpr(),  # forward-declared
      impedance=RangeExpr(),  # forward-declared
    ))

    self.out = self.Export(self.device.com.as_analog_source(
      voltage_out=self.input0.link().voltage.hull(self.input1.link().voltage),
      current_limits=self.device.analog_current_limits,
      impedance=self.input0.link().source_impedance.hull(self.input1.link().source_impedance) +
                self.device.analog_on_resistance
    ))
    self.assign(self.input0.current_draw, self.out.link().current_drawn)
    self.assign(self.input1.current_draw, self.out.link().current_drawn)
    self.assign(self.input0.impedance, self.out.link().sink_impedance + self.device.analog_on_resistance)
    self.assign(self.input1.impedance, self.out.link().sink_impedance + self.device.analog_on_resistance)


class AnalogDemuxer(Block):
  """Wrapper around AnalogSwitch that provides demuxing functionality - multiple source ports, one sink port.
  """
  def __init__(self) -> None:
    super().__init__()
    self.device = self.Block(AnalogSwitch())
    self.pwr = self.Export(self.device.pwr, [Power])
    self.gnd = self.Export(self.device.gnd, [Common])
    self.control = self.Export(self.device.control)

    self.input = self.Export(self.device.com.as_analog_sink(
      voltage_limits=self.device.analog_voltage_limits,
      current_draw=RangeExpr(),  # forward-declared
      impedance=RangeExpr(),  # forward-declared
    ))
    self.out0 = self.Export(self.device.nc.as_analog_source(
      voltage_out=self.input.link().voltage,
      current_limits=self.device.analog_current_limits,
      impedance=self.input.link().source_impedance + self.device.analog_on_resistance
    ))
    self.out1 = self.Export(self.device.no.as_analog_source(
      voltage_out=self.input.link().voltage,
      current_limits=self.device.analog_current_limits,
      impedance=self.input.link().source_impedance + self.device.analog_on_resistance
    ))
    self.assign(self.input.current_draw,
                self.out0.link().current_drawn.hull(self.out1.link().current_drawn))
    self.assign(self.input.impedance,
                self.out0.link().sink_impedance.hull(self.out1.link().sink_impedance) +
                self.device.analog_on_resistance)
