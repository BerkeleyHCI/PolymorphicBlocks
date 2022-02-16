import unittest

from . import *
from .ScalaCompilerInterface import ScalaCompiler


class BadGeneratorTestCase(unittest.TestCase):
  # These are internal classes to avoid this error case being auto-discovered in a library

  class InvalidMissingGeneratorBlock(GeneratorBlock):
    def __init__(self) -> None:
      super().__init__()
      # this is missing a self.generator statement

  def test_missing_generator(self) -> None:
    with self.assertRaises(AssertionError):
      self.InvalidMissingGeneratorBlock()._elaborated_def_to_proto()


  class InvalidMultiGeneratorBlock(GeneratorBlock):
    def __init__(self) -> None:
      super().__init__()
      self.generator(self.dummy_gen)
      self.generator(self.dummy_gen)

    def dummy_gen(self) -> None:
      pass

  def test_multi_generator(self) -> None:
    with self.assertRaises(AssertionError):
      self.InvalidMultiGeneratorBlock()._elaborated_def_to_proto()


  class InvalidNonArgGeneratorBlock(GeneratorBlock):
    def __init__(self) -> None:
      super().__init__()
      self.param = self.Parameter(FloatExpr())
      self.generator(self.dummy_gen, self.param)

    def dummy_gen(self, x: float) -> None:
      pass

  def test_non_arg_generator(self) -> None:
    with self.assertRaises(AssertionError):
      self.InvalidNonArgGeneratorBlock()._elaborated_def_to_proto()
