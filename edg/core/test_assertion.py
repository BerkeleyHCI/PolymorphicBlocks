import unittest

from . import *


class TestAssertionFailureBlock(Block):
    def __init__(self) -> None:
        super().__init__()
        self.require(BoolExpr._to_expr_type(False))


class AssertionTestCase(unittest.TestCase):
    def test_failure(self) -> None:
        with self.assertRaises(CompilerCheckError):
            ScalaCompiler.compile(TestAssertionFailureBlock)
