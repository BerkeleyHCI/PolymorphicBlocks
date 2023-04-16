import unittest

from . import *
from .HdlUserExceptions import BlockDefinitionError


class BadGeneratorTestCase(unittest.TestCase):
  # These are internal classes to avoid this error case being auto-discovered in a library

  class InvalidMissingGeneratorBlock(GeneratorBlock):
    """This doesn't implement generator()"""

  def test_missing_generator(self) -> None:
    with self.assertRaises(BlockDefinitionError):
      self.InvalidMissingGeneratorBlock()._elaborated_def_to_proto()


  class InvalidNonArgGeneratorBlock(GeneratorBlock):
    def __init__(self) -> None:
      super().__init__()
      self.param = self.Parameter(FloatExpr())
      self.param_value = self.GeneratorParam(self.param, float)

    def generate(self) -> None:
      super().generate()

  def test_non_arg_generator(self) -> None:
    with self.assertRaises(BlockDefinitionError):
      self.InvalidNonArgGeneratorBlock()._elaborated_def_to_proto()
