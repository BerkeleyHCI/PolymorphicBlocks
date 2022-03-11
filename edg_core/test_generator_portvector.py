import unittest
from typing import List

from . import *
from .ScalaCompilerInterface import ScalaCompiler
from .test_generator import TestPortSink, TestBlockSink, TestBlockSource


class GeneratorInnerBlock(GeneratorBlock):
  def __init__(self) -> None:
    super().__init__()
    self.ports = self.Port(Vector(TestPortSink()))
    self.generator(self.generate, self.ports.elements())

  def generate(self, elements: List[str]) -> None:
    assert(elements == ['0', '1', '2'])
    self.ports.init_elts(elements)


class TestGeneratorElements(Block):
  def __init__(self) -> None:
    super().__init__()
    self.block = self.Block(GeneratorInnerBlock())

    self.source0 = self.Block(TestBlockSource(1.0))
    self.source1 = self.Block(TestBlockSource(1.0))
    self.source2 = self.Block(TestBlockSource(1.0))
    self.connect(self.source0.port, self.block.ports.allocate())
    self.connect(self.source1.port, self.block.ports.allocate())
    self.connect(self.source2.port, self.block.ports.allocate())


class TestGeneratorPortVector(unittest.TestCase):
  def test_generator_assign(self):
    compiled = ScalaCompiler.compile(TestGeneratorElements)
