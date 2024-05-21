from typing import cast

from ..electronics_model import *
from ..electronics_model.CanPort import CanLogicLink
from ..electronics_model.I2cPort import I2cLink
from .AbstractConnector import RfConnector, RfConnectorTestPoint
from .AbstractResistor import Resistor
from .Categories import *


@abstract_block
class TestPoint(InternalSubcircuit, Block):
  """Abstract test point that can take a name as a string, used as the footprint value.
  """
  @init_in_parent
  def __init__(self, tp_name: StringLike = "") -> None:
    super().__init__()
    self.io = self.Port(Passive(), [InOut])
    self.tp_name = self.ArgParameter(tp_name)


@non_library
class BaseTypedTestPoint(TypedTestPoint, Block):
  """Base class with utility infrastructure for typed test points"""
  @init_in_parent
  def __init__(self, tp_name: StringLike = "") -> None:
    super().__init__()
    self.io: Port
    self.tp_name = self.ArgParameter(tp_name)
    self.tp = self.Block(TestPoint(tp_name=StringExpr()))

  def contents(self):
    super().contents()
    self.assign(self.tp.tp_name, (self.tp_name == "").then_else(self.io.link().name(), self.tp_name))


@non_library
class BaseRfTestPoint(TypedTestPoint, Block):
  """Base class with utility infrastructure for typed RF test points."""
  @init_in_parent
  def __init__(self, tp_name: StringLike = "") -> None:
    super().__init__()
    self.tp_name = self.ArgParameter(tp_name)
    self.conn = self.Block(RfConnector())
    self.gnd = self.Export(self.conn.gnd, [Common])
    self.io: Port

  def contents(self):
    super().contents()
    conn_tp = self.conn.with_mixin(RfConnectorTestPoint(StringExpr()))
    self.assign(conn_tp.tp_name, (self.tp_name == "").then_else(self.io.link().name(), self.tp_name))


class VoltageTestPoint(BaseTypedTestPoint, Block):
  """Test point with a VoltageSink port."""
  def __init__(self, *args):
    super().__init__(*args)
    self.io = self.Port(VoltageSink.empty(), [InOut])
    self.connect(self.io, self.tp.io.adapt_to(VoltageSink()))

  def connected(self, io: Port[VoltageLink]) -> 'VoltageTestPoint':
    cast(Block, builder.get_enclosing_block()).connect(io, self.io)
    return self


class DigitalTestPoint(BaseTypedTestPoint, Block):
  """Test point with a DigitalSink port."""
  def __init__(self, *args):
    super().__init__(*args)
    self.io = self.Port(DigitalSink.empty(), [InOut])
    self.connect(self.io, self.tp.io.adapt_to(DigitalSink()))

  def connected(self, io: Port[DigitalLink]) -> 'DigitalTestPoint':
    cast(Block, builder.get_enclosing_block()).connect(io, self.io)
    return self


class DigitalArrayTestPoint(TypedTestPoint, GeneratorBlock):
  """Creates an array of Digital test points, sized from the port array's connections."""
  @init_in_parent
  def __init__(self, tp_name: StringLike = ''):
    super().__init__()
    self.io = self.Port(Vector(DigitalSink.empty()), [InOut])
    self.tp_name = self.ArgParameter(tp_name)
    self.generator_param(self.io.requested(), self.tp_name)

  def generate(self):
    super().generate()
    self.tp = ElementDict[DigitalTestPoint]()
    for requested in self.get(self.io.requested()):
      # TODO: link() on Vector is not supported, so we leave the naming to the leaf link in the leaf test point
      if self.get(self.tp_name) == '':
        tp = self.tp[requested] = self.Block(DigitalTestPoint())
      else:
        tp = self.tp[requested] = self.Block(DigitalTestPoint(self.tp_name + f'.{requested}'))
      self.connect(self.io.append_elt(DigitalSink.empty(), requested), tp.io)


class AnalogTestPoint(BaseTypedTestPoint, Block):
  """Test point with a AnalogSink port"""
  def __init__(self, *args):
    super().__init__(*args)
    self.io = self.Port(AnalogSink.empty(), [InOut])
    self.connect(self.io, self.tp.io.adapt_to(AnalogSink()))

  def connected(self, io: Port[AnalogLink]) -> 'AnalogTestPoint':
    cast(Block, builder.get_enclosing_block()).connect(io, self.io)
    return self


class AnalogRfTestPoint(BaseRfTestPoint, Block):
  """Test point with a AnalogSink port and 50-ohm matching resistor."""
  def __init__(self, *args):
    super().__init__(*args)
    self.res = self.Block(Resistor(50*Ohm(tol=0.05)))
    self.io = self.Export(self.res.a.adapt_to(AnalogSink()), [InOut])
    self.connect(self.res.b, self.conn.sig)

  def connected(self, io: Port[AnalogLink]) -> 'AnalogRfTestPoint':
    cast(Block, builder.get_enclosing_block()).connect(io, self.io)
    return self


class I2cTestPoint(TypedTestPoint, Block):
  """Two test points for I2C SDA and SCL"""
  @init_in_parent
  def __init__(self, tp_name: StringLike = ""):
    super().__init__()
    self.io = self.Port(I2cTarget(DigitalBidir.empty()), [InOut])
    self.tp_name = self.ArgParameter(tp_name)

  def contents(self):
    super().contents()
    name_prefix = (self.tp_name == '').then_else(self.io.link().name(), self.tp_name)
    self.tp_scl = self.Block(DigitalTestPoint(name_prefix + '.scl'))
    self.tp_sda = self.Block(DigitalTestPoint(name_prefix + '.sda'))
    self.connect(self.tp_scl.io, self.io.scl)
    self.connect(self.tp_sda.io, self.io.sda)

  def connected(self, io: Port[I2cLink]) -> 'I2cTestPoint':
    cast(Block, builder.get_enclosing_block()).connect(io, self.io)
    return self


class SpiTestPoint(TypedTestPoint, Block):
  """Test points for SPI"""
  @init_in_parent
  def __init__(self, tp_name: StringLike = ""):
    super().__init__()
    self.io = self.Port(SpiPeripheral(DigitalBidir.empty()), [InOut])
    self.tp_name = self.ArgParameter(tp_name)

  def contents(self):
    super().contents()
    name_prefix = (self.tp_name == '').then_else(self.io.link().name(), self.tp_name)
    self.tp_sck = self.Block(DigitalTestPoint(name_prefix + '.sck'))
    self.tp_mosi = self.Block(DigitalTestPoint(name_prefix + '.mosi'))
    self.tp_miso = self.Block(DigitalTestPoint(name_prefix + '.miso'))
    self.connect(self.tp_sck.io, self.io.sck)
    self.connect(self.tp_mosi.io, self.io.mosi)
    self.connect(self.tp_miso.io, self.io.miso)

  def connected(self, io: Port[SpiLink]) -> 'SpiTestPoint':
    cast(Block, builder.get_enclosing_block()).connect(io, self.io)
    return self


class CanControllerTestPoint(TypedTestPoint, Block):
  """Two test points for CAN controller-side TXD and RXD"""
  @init_in_parent
  def __init__(self, tp_name: StringLike = ""):
    super().__init__()
    self.io = self.Port(CanPassivePort(DigitalBidir.empty()), [InOut])
    self.tp_name = self.ArgParameter(tp_name)

  def contents(self):
    super().contents()
    name_prefix = (self.tp_name == '').then_else(self.io.link().name(), self.tp_name)
    self.tp_txd = self.Block(DigitalTestPoint(name_prefix + '.txd'))
    self.tp_rxd = self.Block(DigitalTestPoint(name_prefix + '.rxd'))
    self.connect(self.tp_txd.io, self.io.txd)
    self.connect(self.tp_rxd.io, self.io.rxd)

  def connected(self, io: Port[CanLogicLink]) -> 'CanControllerTestPoint':
    cast(Block, builder.get_enclosing_block()).connect(io, self.io)
    return self
