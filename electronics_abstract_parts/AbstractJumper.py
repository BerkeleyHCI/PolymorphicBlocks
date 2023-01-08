from electronics_model import *


class Jumper(Block):
  """A two-ported passive-typed jumper (a disconnect-able connection), though is treated
  as always connected for model purposes.

  Wrapping blocks can add typed port and parameter propagation semantics."""
  def __init__(self):
    super().__init__()

    self.a = self.Port(Passive.empty())
    self.b = self.Port(Passive.empty())


class DigitalJumper(Block):
  def __init__(self):
    super().__init__()
    self.input = self.Port(DigitalSink.empty(), [Input])
    self.output = self.Port(DigitalSource.empty(), [Output])

  def contents(self):
    self.device = self.Block(Jumper())
    self.connect(self.input, self.device.a.adapt_to(DigitalSink(
      current_draw=self.output.link().current_drawn
    )))
    self.connect(self.output, self.device.b.adapt_to(DigitalSource(
      voltage_out=self.input.link().voltage,
      output_thresholds=self.input.link().output_thresholds
    )))
