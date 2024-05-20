import unittest

from .. import edgir
from . import *
from .ScalaCompilerInterface import ScalaCompiler
from .test_generator import TestPortSink, TestBlockSource


class GeneratorInnerBlock(GeneratorBlock):
  def __init__(self) -> None:
    super().__init__()
    self.ports = self.Port(Vector(TestPortSink()))
    self.generator_param(self.ports.requested())

  def generate(self) -> None:
    assert self.get(self.ports.requested()) == ['0', 'named', '1']
    self.ports.append_elt(TestPortSink((-1, 1)))
    self.ports.append_elt(TestPortSink((-5, 5)), 'named')
    self.ports.append_elt(TestPortSink((-2, 2)))


class TestGeneratorElements(Block):
  def __init__(self) -> None:
    super().__init__()
    self.block = self.Block(GeneratorInnerBlock())

    self.source0 = self.Block(TestBlockSource(1.0))
    self.source1 = self.Block(TestBlockSource(1.0))
    self.source2 = self.Block(TestBlockSource(1.0))
    self.connect(self.source0.port, self.block.ports.request())
    self.connect(self.source1.port, self.block.ports.request('named'))
    self.connect(self.source2.port, self.block.ports.request())


class TestGeneratorPortVector(unittest.TestCase):
  def test_generator(self):
    ScalaCompiler.compile(TestGeneratorElements)

  def test_initializer(self):
    compiled = ScalaCompiler.compile(TestGeneratorElements)
    pb = compiled.contents.blocks[0].value.hierarchy
    self.assertEqual(pb.constraints[1].name, "(init)ports.0.range_param")
    self.assertEqual(pb.constraints[1].value, edgir.AssignLit(['ports', '0', 'range_param'], Range(-1, 1)))
    self.assertEqual(pb.constraints[2].name, "(init)ports.named.range_param")
    self.assertEqual(pb.constraints[2].value, edgir.AssignLit(['ports', 'named', 'range_param'], Range(-5, 5)))
    self.assertEqual(pb.constraints[3].name, "(init)ports.1.range_param")
    self.assertEqual(pb.constraints[3].value, edgir.AssignLit(['ports', '1', 'range_param'], Range(-2, 2)))


class InnerBlockInvalid(Block):
  def __init__(self) -> None:
    super().__init__()
    self.ports = self.Port(Vector(TestPortSink()))
    self.ports.append_elt(TestPortSink(), 'haha')


class TestElementsInvalid(Block):
  def __init__(self) -> None:
    super().__init__()
    self.block = self.Block(InnerBlockInvalid())

    self.source0 = self.Block(TestBlockSource(1.0))
    self.connect(self.source0.port, self.block.ports.request('nope'))


class TestPortVectorInvalid(unittest.TestCase):
  def test_generator_error(self):
    with self.assertRaises(CompilerCheckError):
      ScalaCompiler.compile(TestElementsInvalid)


class GeneratorWrapperBlock(Block):
  def __init__(self) -> None:
    super().__init__()
    self.block = self.Block(GeneratorInnerBlock())
    self.ports = self.Export(self.block.ports)


class GeneratorWrapperTest(Block):  # same as TestGeneratorElements, but creating a GeneratorInnerBlock
  def __init__(self) -> None:
    super().__init__()
    self.block = self.Block(GeneratorWrapperBlock())

    self.source0 = self.Block(TestBlockSource(1.0))
    self.source1 = self.Block(TestBlockSource(1.0))
    self.source2 = self.Block(TestBlockSource(1.0))
    self.connect(self.source0.port, self.block.ports.request())
    self.connect(self.source1.port, self.block.ports.request('named'))
    self.connect(self.source2.port, self.block.ports.request())


class TestGeneratorWrapper(unittest.TestCase):
  def test_generator(self):
    ScalaCompiler.compile(GeneratorWrapperTest)

  def test_exported_ports(self):
    compiled = ScalaCompiler.compile(GeneratorWrapperTest)
    pb = edgir.pair_get(compiled.contents.blocks, 'block').hierarchy

    # check the inner block too
    inner_block = edgir.pair_get(pb.blocks, 'block').hierarchy
    pb_ports = edgir.pair_get(inner_block.ports, 'ports').array.ports.ports
    self.assertEqual(pb_ports[0].name, '0')
    self.assertEqual(pb_ports[1].name, 'named')
    self.assertEqual(pb_ports[2].name, '1')

    pb_ports = edgir.pair_get(pb.ports, 'ports').array.ports.ports
    self.assertEqual(pb_ports[0].name, '0')
    self.assertEqual(pb_ports[1].name, 'named')
    self.assertEqual(pb_ports[2].name, '1')


class GeneratorArrayParam(GeneratorBlock):
  @init_in_parent
  def __init__(self, param: ArrayRangeLike) -> None:
    super().__init__()
    self.ports = self.Port(Vector(TestPortSink()))
    self.param = self.ArgParameter(param)
    self.generator_param(self.param)

  def generate(self) -> None:
    for elt in self.get(self.param):
      created_port = self.ports.append_elt(TestPortSink(elt))  # any port
    self.require(created_port.link().sinks_range == Range(-2, 1))


class GeneratorArrayParamTop(Block):
  def __init__(self) -> None:
    super().__init__()
    self.block = self.Block(GeneratorArrayParam([
      (-3, 1), (-5, 5), (-2, 2)
    ]))

    self.source = self.Block(TestBlockSource(1.0))
    self.connect(self.source.port,
                 self.block.ports.request(), self.block.ports.request(), self.block.ports.request())


class TestGeneratorArrayParam(unittest.TestCase):
  def test_generator(self):
    ScalaCompiler.compile(GeneratorArrayParamTop)
