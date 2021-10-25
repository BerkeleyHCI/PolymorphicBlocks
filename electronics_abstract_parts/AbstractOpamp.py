from electronics_model import *
from .Categories import *

@abstract_block
class Opamp(Block):
  """Base class for opamps. Parameters need to be more restricted in subclasses.
  """

  @init_in_parent
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink(), [Power])
    self.gnd = self.Port(Ground(), [Common])

    self.inp = self.Port(AnalogSink())
    self.inn = self.Port(AnalogSink())
    self.out = self.Port(AnalogSource())


class OpampFollower(AnalogFilter):
  def __init__(self):
    super().__init__()

    self.amp = self.Block(Opamp())

    self.pwr = self.Export(self.amp.pwr, [Power])
    self.gnd = self.Export(self.amp.gnd, [Common])

    self.input = self.Export(self.amp.inp, [Input])
    self.output = self.Export(self.amp.out, [Output])
    self.connect(self.amp.out, self.amp.inn)


class Amplifier(AnalogFilter):
  """Opamp non-inverting amplifier, outputs a scaled-up version of the input signal."""
  def __init__(self):
    super().__init__()

    self.amp = self.Block(Opamp())

    self.pwr = self.Export(self.amp.pwr, [Power])
    self.gnd = self.Export(self.amp.gnd, [Common])

    self.input = self.Export(self.amp.inp, [Input])
    self.output = self.Export(self.amp.out, [Output])

    # TODO ADD PARAMETERS, IMPLEMENT ME


class DifferentialAmplifier(AnalogFilter):
  """Opamp differential amplifier, outputs the difference between the input nodes, scaled by some factor,
  and offset from some reference node."""
  def __init__(self):
    super().__init__()

    self.amp = self.Block(Opamp())

    self.pwr = self.Export(self.amp.pwr, [Power])
    self.gnd = self.Export(self.amp.gnd, [Common])

    self.input_positive = self.Port(AnalogSink())
    self.input_negative = self.Port(AnalogSink())
    self.output_reference = self.Port(AnalogSink())
    self.output = self.Port(AnalogSource())

    # TODO ADD PARAMETERS, IMPLEMENT ME


class Integrator(AnalogFilter):
  """Opamp integrator, outputs the integral of the input signal, relative to some reference signal.
  Will clip to the input voltage rails."""
  def __init__(self):
    super().__init__()

    self.amp = self.Block(Opamp())

    self.pwr = self.Export(self.amp.pwr, [Power])
    self.gnd = self.Export(self.amp.gnd, [Common])

    self.input = self.Port(AnalogSink())
    self.output = self.Port(AnalogSource())
    self.reference = self.Port(AnalogSink())  # negative reference for the input and output signals

    # TODO ADD PARAMETERS, IMPLEMENT ME
