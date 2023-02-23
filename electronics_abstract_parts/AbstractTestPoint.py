from typing import cast, List

from electronics_model import *
from electronics_model.CanPort import CanLogicLink
from electronics_model.I2cPort import I2cLink
from .Categories import *


@abstract_block
class TestPoint(Testing, Block):
  """Abstract test point that can take a name as a string, used as the footprint value.
  """
  @init_in_parent
  def __init__(self, name: StringLike = "") -> None:
    super().__init__()
    self.io = self.Port(Passive(), [InOut])
    self.tp_name = self.ArgParameter(name)


class VoltageTestPoint(TypedTestPoint, Block):
  """Test point with a VoltageSink port."""
  def __init__(self):
    super().__init__()
    self.io = self.Port(VoltageSink().empty(), [InOut])
    self.tp = self.Block(TestPoint(name=self.io.link().name()))
    self.connect(self.io, self.tp.io.adapt_to(VoltageSink()))

  def connected(self, io: Port[VoltageLink]) -> 'VoltageTestPoint':
    cast(Block, builder.get_enclosing_block()).connect(io, self.io)
    return self


class DigitalTestPoint(TypedTestPoint, Block):
  """Test point with a DigitalSink port."""
  def __init__(self):
    super().__init__()
    self.io = self.Port(DigitalSink().empty(), [InOut])
    self.tp = self.Block(TestPoint(name=self.io.link().name()))
    self.connect(self.io, self.tp.io.adapt_to(DigitalSink()))

  def connected(self, io: Port[DigitalLink]) -> 'DigitalTestPoint':
    cast(Block, builder.get_enclosing_block()).connect(io, self.io)
    return self


class DigitalArrayTestPoint(TypedTestPoint, GeneratorBlock):
  """Creates an array of Digital test points, sized from the port array's connections."""
  def __init__(self):
    super().__init__()
    self.io = self.Port(Vector(DigitalSink().empty()), [InOut])
    self.generator(self.generate, self.io.requested())

  def generate(self, requesteds: List[str]):
    self.tp = ElementDict[DigitalTestPoint]()
    for requested in requesteds:
      tp = self.tp[requested] = self.Block(DigitalTestPoint())
      self.connect(self.io.append_elt(DigitalSink.empty(), requested), tp.io)


class AnalogTestPoint(TypedTestPoint, Block):
  """Test point with a AnalogSink port."""
  def __init__(self):
    super().__init__()
    self.io = self.Port(AnalogSink().empty(), [InOut])
    self.tp = self.Block(TestPoint(name=self.io.link().name()))
    self.connect(self.io, self.tp.io.adapt_to(AnalogSink()))

  def connected(self, io: Port[AnalogLink]) -> 'AnalogTestPoint':
    cast(Block, builder.get_enclosing_block()).connect(io, self.io)
    return self


class I2cTestPoint(TypedTestPoint, Block):
  """Two test points for I2C SDA and SCL"""
  def __init__(self):
    super().__init__()
    self.io = self.Port(I2cSlave(DigitalBidir.empty()), [InOut])
    self.tp_scl = self.Block(DigitalTestPoint())
    self.connect(self.tp_scl.io, self.io.scl)
    self.tp_sda = self.Block(DigitalTestPoint())
    self.connect(self.tp_sda.io, self.io.sda)

  def connected(self, io: Port[I2cLink]) -> 'I2cTestPoint':
    cast(Block, builder.get_enclosing_block()).connect(io, self.io)
    return self


class CanControllerTestPoint(TypedTestPoint, Block):
  """Two test points for CAN controller-side TXD and RXD"""
  def __init__(self):
    super().__init__()
    self.io = self.Port(CanPassivePort(DigitalBidir.empty()), [InOut])
    self.tp_txd = self.Block(DigitalTestPoint())
    self.connect(self.tp_txd.io, self.io.txd)
    self.tp_rxd = self.Block(DigitalTestPoint())
    self.connect(self.tp_rxd.io, self.io.rxd)

  def connected(self, io: Port[CanLogicLink]) -> 'CanControllerTestPoint':
    cast(Block, builder.get_enclosing_block()).connect(io, self.io)
    return self
