import unittest
from typing import List

import edgir
from . import *
from .ScalaCompilerInterface import ScalaCompiler
from .test_generator import TestPortSink, TestBlockSink, TestBlockSource


class GeneratorInnerBlock(GeneratorBlock):
  def __init__(self) -> None:
    super().__init__()
    self.ports = self.Port(Vector(TestPortSink()))
    self.generator(self.generate, self.ports.allocated())

  def generate(self, elements: List[str]) -> None:
    assert elements == ['0', 'named', '1'], f"bad elements {elements}"
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
    self.connect(self.source0.port, self.block.ports.allocate())
    self.connect(self.source1.port, self.block.ports.allocate('named'))
    self.connect(self.source2.port, self.block.ports.allocate())


class TestGeneratorPortVector(unittest.TestCase):
  def test_generator(self):
    ScalaCompiler.compile(TestGeneratorElements)

  def test_initializer(self):
    compiled = ScalaCompiler.compile(TestGeneratorElements)
    pb = compiled.contents.blocks['block'].hierarchy
    self.assertEqual(
      edgir.AssignLit(['ports', '0', 'range_param'], Range(-1, 1)),
      pb.constraints["(init)ports.0.range_param"])
    self.assertEqual(
      edgir.AssignLit(['ports', 'named', 'range_param'], Range(-5, 5)),
      pb.constraints["(init)ports.named.range_param"])
    self.assertEqual(
      edgir.AssignLit(['ports', '1', 'range_param'], Range(-2, 2)),
      pb.constraints["(init)ports.1.range_param"])


class GeneratorInnerBlockInvalid(GeneratorBlock):
  def __init__(self) -> None:
    super().__init__()
    self.ports = self.Port(Vector(TestPortSink()))
    self.generator(self.generate, self.ports.allocated())

  def generate(self, elements: List[str]) -> None:
    self.ports.append_elt(TestPortSink(), 'haha')


class TestGeneratorElementsInvalid(Block):
  def __init__(self) -> None:
    super().__init__()
    self.block = self.Block(GeneratorInnerBlockInvalid())

    self.source0 = self.Block(TestBlockSource(1.0))
    self.connect(self.source0.port, self.block.ports.allocate('nope'))


class TestGeneratorPortVectorInvalid(unittest.TestCase):
  def test_generator_error(self):
    with self.assertRaises(CompilerCheckError):
      ScalaCompiler.compile(TestGeneratorElementsInvalid)


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
    self.connect(self.source0.port, self.block.ports.allocate())
    self.connect(self.source1.port, self.block.ports.allocate('named'))
    self.connect(self.source2.port, self.block.ports.allocate())


class TestGeneratorWrapper(unittest.TestCase):
  def test_generator(self):
    ScalaCompiler.compile(GeneratorWrapperTest)

  def test_exported_ports(self):
    compiled = ScalaCompiler.compile(GeneratorWrapperTest)
    pb = compiled.contents.blocks['block'].hierarchy
    pb_ports = pb.ports['ports'].array.ports.ports
    self.assertIn('0', pb_ports)
    self.assertIn('named', pb_ports)
    self.assertIn('1', pb_ports)
