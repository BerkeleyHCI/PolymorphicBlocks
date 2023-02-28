import unittest

import edgir
from . import *
from edg_core.ScalaCompilerInterface import ScalaCompiler


class TestEvalExprBlock(Block):
  def __init__(self) -> None:
    super().__init__()
    # Test both the initializer form and the assign form
    self.sum_float = self.Parameter(FloatExpr(2 * LiteralConstructor(1) + 3 * LiteralConstructor(1)))
    self.sum_range = self.Parameter(RangeExpr())

  def contents(self):
    self.assign(self.sum_range, (2, 6) * LiteralConstructor(1) + (7, 8) * LiteralConstructor(1))


class EvalExprTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.compiled = ScalaCompiler.compile(TestEvalExprBlock)

  def test_sum(self) -> None:
    self.assertEqual(self.compiled.get_value(['sum_float']), 5.0)
    self.assertEqual(self.compiled.get_value(['sum_range']), Range(9.0, 14.0))


class TestReductionLink(Link):
  def __init__(self) -> None:
    super().__init__()
    self.ports = self.Port(Vector(TestReductionPort()), optional=True)

    self.range_sum = self.Parameter(RangeExpr(self.ports.map_extract(lambda p: p.range_param).sum()))
    self.range_intersection = self.Parameter(RangeExpr(self.ports.map_extract(lambda p: p.range_param).intersection()))


class TestReductionPort(Port[TestReductionLink]):
  link_type = TestReductionLink

  def __init__(self, range_param: RangeLike = RangeExpr()) -> None:
    super().__init__()
    self.range_param = self.Parameter(RangeExpr(range_param))


class TestEvalPortBlock(Block):
  @init_in_parent
  def __init__(self, range_param: RangeLike = RangeExpr()) -> None:
    super().__init__()
    self.port = self.Port(TestReductionPort(range_param))


class TestEvalReductionBlock(Block):
  def __init__(self) -> None:
    super().__init__()
    self.block1 = self.Block(TestEvalPortBlock((0, 100)))
    self.block2 = self.Block(TestEvalPortBlock((1, 10)))
    self.block3 = self.Block(TestEvalPortBlock((5, 20)))
    self.link = self.connect(self.block1.port, self.block2.port, self.block3.port)


class EvalReductionTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.compiled = ScalaCompiler.compile(TestEvalReductionBlock)

  def test_reduce(self) -> None:
    self.assertEqual(self.compiled.get_value(['link', 'range_sum']), Range(6.0, 130.0))
    self.assertEqual(self.compiled.get_value(['link', 'range_intersection']), Range(5.0, 10.0))
    self.assertEqual(self.compiled.get_value(['link', 'ports', edgir.LENGTH]), 3)
