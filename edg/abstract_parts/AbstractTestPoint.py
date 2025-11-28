from typing import cast, Any

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
  def __init__(self, tp_name: StringLike = "") -> None:
    super().__init__()
    self.io = self.Port(Passive(), [InOut])
    self.tp_name = self.ArgParameter(tp_name)


@non_library
class BaseTypedTestPoint(TypedTestPoint, Block):
  """Base class with utility infrastructure for typed test points"""
  def __init__(self, tp_name: StringLike = "") -> None:
    super().__init__()
    self.io: Port
    self.tp_name = self.ArgParameter(tp_name)
    self.tp = self.Block(TestPoint(tp_name=StringExpr()))

  @override
  def contents(self) -> None:
    super().contents()
    self.assign(self.tp.tp_name, (self.tp_name == "").then_else(self.io.link().name(), self.tp_name))


@non_library
class BaseRfTestPoint(TypedTestPoint, Block):
  """Base class with utility infrastructure for typed RF test points."""
  def __init__(self, tp_name: StringLike = "") -> None:
    super().__init__()
    self.tp_name = self.ArgParameter(tp_name)
    self.conn = self.Block(RfConnector())
    self.gnd = self.Export(self.conn.gnd, [Common])
    self.io: Port

  @override
  def contents(self) -> None:
    super().contents()
    conn_tp = self.conn.with_mixin(RfConnectorTestPoint(StringExpr()))
    self.assign(conn_tp.tp_name, (self.tp_name == "").then_else(self.io.link().name(), self.tp_name))


class GroundTestPoint(BaseTypedTestPoint, Block):
  """Test point with a VoltageSink port."""
  def __init__(self, *args: Any) -> None:
    super().__init__(*args)
    self.io = self.Port(Ground.empty(), [InOut])
    self.connect(self.io, self.tp.io.adapt_to(Ground()))

  def connected(self, io: Port[GroundLink]) -> 'GroundTestPoint':
    cast(Block, builder.get_enclosing_block()).connect(io, self.io)
    return self


class VoltageTestPoint(BaseTypedTestPoint, Block):
  """Test point with a VoltageSink port."""
  def __init__(self, *args: Any) -> None:
    super().__init__(*args)
    self.io = self.Port(VoltageSink.empty(), [InOut])
    self.connect(self.io, self.tp.io.adapt_to(VoltageSink()))

  def connected(self, io: Port[VoltageLink]) -> 'VoltageTestPoint':
    cast(Block, builder.get_enclosing_block()).connect(io, self.io)
    return self


class DigitalTestPoint(BaseTypedTestPoint, Block):
  """Test point with a DigitalSink port."""
  def __init__(self, *args: Any) -> None:
    super().__init__(*args)
    self.io = self.Port(DigitalSink.empty(), [InOut])
    self.connect(self.io, self.tp.io.adapt_to(DigitalSink()))

  def connected(self, io: Port[DigitalLink]) -> 'DigitalTestPoint':
    cast(Block, builder.get_enclosing_block()).connect(io, self.io)
    return self


class DigitalArrayTestPoint(TypedTestPoint, GeneratorBlock):
  """Creates an array of Digital test points, sized from the port array's connections."""
  def __init__(self, tp_name: StringLike = '') -> None:
    super().__init__()
    self.io = self.Port(Vector(DigitalSink.empty()), [InOut])
    self.tp_name = self.ArgParameter(tp_name)
    self.generator_param(self.io.requested(), self.tp_name)

  @override
  def generate(self) -> None:
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
  def __init__(self, *args: Any) -> None:
    super().__init__(*args)
    self.io = self.Port(AnalogSink.empty(), [InOut])
    self.connect(self.io, self.tp.io.adapt_to(AnalogSink()))

  def connected(self, io: Port[AnalogLink]) -> 'AnalogTestPoint':
    cast(Block, builder.get_enclosing_block()).connect(io, self.io)
    return self


class AnalogCoaxTestPoint(BaseRfTestPoint, Block):
  """Test point with a AnalogSink port and using a coax connector with shielding connected to gnd.
  No impedance matching, this is intended for lower frequency signals where the wavelength would be
  much longer than the test lead length"""
  def __init__(self, *args: Any) -> None:
    super().__init__(*args)
    self.io = self.Export(self.conn.sig.adapt_to(AnalogSink()), [InOut])

  def connected(self, io: Port[AnalogLink]) -> 'AnalogCoaxTestPoint':
    cast(Block, builder.get_enclosing_block()).connect(io, self.io)
    return self


class I2cTestPoint(TypedTestPoint, Block):
  """Two test points for I2C SDA and SCL"""
  def __init__(self, tp_name: StringLike = "") -> None:
    super().__init__()
    self.io = self.Port(I2cTarget(DigitalBidir.empty()), [InOut])
    self.tp_name = self.ArgParameter(tp_name)

  @override
  def contents(self) -> None:
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
  def __init__(self, tp_name: StringLike = "") -> None:
    super().__init__()
    self.io = self.Port(SpiPeripheral(DigitalBidir.empty()), [InOut])
    self.tp_name = self.ArgParameter(tp_name)

  @override
  def contents(self) -> None:
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
  def __init__(self, tp_name: StringLike = "") -> None:
    super().__init__()
    self.io = self.Port(CanPassivePort(DigitalBidir.empty()), [InOut])
    self.tp_name = self.ArgParameter(tp_name)

  @override
  def contents(self) -> None:
    super().contents()
    name_prefix = (self.tp_name == '').then_else(self.io.link().name(), self.tp_name)
    self.tp_txd = self.Block(DigitalTestPoint(name_prefix + '.txd'))
    self.tp_rxd = self.Block(DigitalTestPoint(name_prefix + '.rxd'))
    self.connect(self.tp_txd.io, self.io.txd)
    self.connect(self.tp_rxd.io, self.io.rxd)

  def connected(self, io: Port[CanLogicLink]) -> 'CanControllerTestPoint':
    cast(Block, builder.get_enclosing_block()).connect(io, self.io)
    return self


class CanDiffTestPoint(TypedTestPoint, Block):
  """Two test points for CAN differential-side canh and canl"""
  def __init__(self, tp_name: StringLike = "") -> None:
    super().__init__()
    self.io = self.Port(CanDiffPort(DigitalBidir.empty()), [InOut])
    self.tp_name = self.ArgParameter(tp_name)

  @override
  def contents(self) -> None:
    super().contents()
    name_prefix = (self.tp_name == '').then_else(self.io.link().name(), self.tp_name)
    self.tp_canh = self.Block(DigitalTestPoint(name_prefix + '.canh'))
    self.tp_canl = self.Block(DigitalTestPoint(name_prefix + '.canl'))
    self.connect(self.tp_canh.io, self.io.canh)
    self.connect(self.tp_canl.io, self.io.canl)

  def connected(self, io: Port[CanLogicLink]) -> 'CanDiffTestPoint':
    cast(Block, builder.get_enclosing_block()).connect(io, self.io)
    return self
