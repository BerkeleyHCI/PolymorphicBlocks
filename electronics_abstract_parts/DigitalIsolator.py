from electronics_model import *
from .Categories import Interface


@abstract_block
class DigitalIsolator(Interface, GeneratorBlock):
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

      self.in_a_requested = self.GeneratorParam(self.in_a.requested())
      self.out_b_requested = self.GeneratorParam(self.out_b.requested())
      self.in_b_requested = self.GeneratorParam(self.in_b.requested())
      self.out_a_requested = self.GeneratorParam(self.out_a.requested())

  def generate(self):  # validity checks
      super().generate()
      assert self.in_a_requested.get() == self.out_b_requested.get(), \
          f"in_a={self.in_a_requested.get()} and out_b={self.out_b_requested.get()} must be equal"
      assert self.in_b_requested.get() == self.out_a_requested.get(), \
          f"in_b={self.in_b_requested.get()} and out_a={self.out_a_requested.get()} must be equal"
