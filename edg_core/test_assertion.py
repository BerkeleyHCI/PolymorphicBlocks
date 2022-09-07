import unittest

from . import *
from edg_core.ScalaCompilerInterface import ScalaCompiler


class TestAssertionFailureBlock(Block):
  def __init__(self) -> None:
    super().__init__()
    self.require(BoolExpr._to_expr_type(False))


class TestAssertionMissingBlock(Block):
  def __init__(self) -> None:
    super().__init__()
    self.missing = self.Parameter(BoolExpr())
    self.require(self.missing)


class AssertionTestCase(unittest.TestCase):
  def test_failure(self) -> None:
    with self.assertRaises(CompilerCheckError):
      ScalaCompiler.compile(TestAssertionFailureBlock)

  def test_missing(self) -> None:
    with self.assertRaises(CompilerCheckError):
      ScalaCompiler.compile(TestAssertionMissingBlock)
