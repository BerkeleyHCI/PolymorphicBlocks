from typing import cast

from electronics_model import *
from electronics_model.CanPort import CanLogicLink
from electronics_model.I2cPort import I2cLink
from .Categories import *


@abstract_block
class TestPoint(GeneratorBlock):
  """A passively-typed test point that provides a value based on the connected link.
  Supports a name parameter that allows it to take a link name from a wrapping block.
  Abstract block, implementing blocks must implement create_test_point to actually make the footprint.
  """
  @init_in_parent
  def __init__(self, name: StringLike = "") -> None:
    super().__init__()
    self.io = self.Port(Passive(), [InOut])

    self.generator(self.generate, name, self.io.link().name())
    self.actual_name = self.Parameter(StringExpr())

  def generate(self, block_name: str, link_name: str) -> None:
    actual_name = block_name if block_name else link_name
    assert actual_name, "test point may not have empty name"  # TODO this shouldn't gate generation
    self.assign(self.actual_name, actual_name)
    self.create_test_point(actual_name)

  def create_test_point(self, name: str) -> None:
    raise NotImplementedError


class VoltageTestPoint(Block):
  """Test point with a VoltageSink port."""
  def __init__(self):
    super().__init__()
    self.io = self.Port(VoltageSink().empty(), [InOut])
    self.tp = self.Block(TestPoint(name=self.io.link().name()))
    self.connect(self.io, self.tp.io.as_voltage_sink())

  def connected(self, io: Port[VoltageLink]) -> 'VoltageTestPoint':
    cast(Block, builder.get_enclosing_block()).connect(io, self.io)
    return self


class DigitalTestPoint(Block):
  """Test point with a DigitalSink port."""
  def __init__(self):
    super().__init__()
    self.io = self.Port(DigitalSink().empty(), [InOut])
    self.tp = self.Block(TestPoint(name=self.io.link().name()))
    self.connect(self.io, self.tp.io.as_digital_sink())

  def connected(self, io: Port[DigitalLink]) -> 'DigitalTestPoint':
    cast(Block, builder.get_enclosing_block()).connect(io, self.io)
    return self


class AnalogTestPoint(Block):
  """Test point with a AnalogSink port."""
  def __init__(self):
    super().__init__()
    self.io = self.Port(AnalogSink().empty(), [InOut])
    self.tp = self.Block(TestPoint(name=self.io.link().name()))
    self.connect(self.io, self.tp.io.as_analog_sink())

  def connected(self, io: Port[AnalogLink]) -> 'AnalogTestPoint':
    cast(Block, builder.get_enclosing_block()).connect(io, self.io)
    return self


class I2cTestPoint(Block):
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


class CanControllerTestPoint(Block):
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
