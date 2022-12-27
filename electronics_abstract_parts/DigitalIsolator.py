from electronics_model import *


@abstract_block
class DigitalIsolator(Block):
  """Multichannel digital isolator, shifts logic signals between different logic voltages
  and isolation domains. Supports arbitrary channels in either direction, but it needs to
  map down to a single chip (or be multipacked).
  in_a -> out_b, and in_b -> out_a must each have the same array elements, which is how
  channels will be matched to pins."""
  def __init__(self):
      super().__init__()
      self.pwr_a = self.Port(VoltageSink.empty())
      self.gnd_a = self.Port(Ground.empty())
      self.in_a = self.Port(Vector(DigitalSink.empty()), optional=True)
      self.out_a = self.Port(Vector(DigitalSource.empty()), optional=True)

      self.pwr_b = self.Port(VoltageSink.empty())
      self.gnd_b = self.Port(Ground.empty())
      self.in_b = self.Port(Vector(DigitalSink.empty()), optional=True)
      self.out_b = self.Port(Vector(DigitalSource.empty()), optional=True)
