import unittest
import sys

from . import *
from .SimpleConstProp import *


class TestEvalExprBlock(Block):
  def __init__(self) -> None:
    super().__init__()
    self.sum_float = self.Parameter(FloatExpr())
    self.sum_range = self.Parameter(RangeExpr())

  def contents(self):
    self.constrain(self.sum_float == 2 * LiteralConstructor(1) + 3 * LiteralConstructor(1))
    self.constrain(self.sum_range == (2, 6) * LiteralConstructor(1) + (7, 8) * LiteralConstructor(1))


class EvalExprTestCase(unittest.TestCase):
  def setUp(self) -> None:
    driver = Driver([sys.modules[__name__]])
    design = driver.generate_block(TestEvalExprBlock())
    with open("TestConstPropExprBlock.edg", 'wb') as f:
      f.write(design.SerializeToString())

    self.const_prop = SimpleConstPropTransform()
    self.const_prop.transform_design(design)

  def test_sum(self) -> None:
    self.assertEqual(self.const_prop.resolve_param(tfu.Path.empty().append_param('sum_float')),
                     5.0)
    self.assertEqual(self.const_prop.resolve_param(tfu.Path.empty().append_param('sum_range')),
                     Interval(9, 14))


class TestReductionLink(Link):
  def __init__(self) -> None:
    super().__init__()
    self.ports = self.Port(Vector(TestReductionPort()), optional=True)

    self.range_sum = self.Parameter(RangeExpr(self.ports.map_extract(lambda p: p.range_param).sum()))
    self.range_intersection = self.Parameter(RangeExpr(self.ports.map_extract(lambda p: p.range_param).intersection()))


class TestReductionPort(Port[TestReductionLink]):
  def __init__(self, range_param: RangeLike = RangeExpr()) -> None:
    super().__init__()
    self.link_type = TestReductionLink
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
    driver = Driver([sys.modules[__name__]])
    design = driver.generate_block(TestEvalReductionBlock())
    with open("TestConstPropReductionBlock.edg", 'wb') as f:
      f.write(design.SerializeToString())

    self.const_prop = SimpleConstPropTransform()
    self.const_prop.transform_design(design)

  def test_reduce(self) -> None:
    self.assertEqual(self.const_prop.resolve_param(tfu.Path.empty().append_link('link').append_param('range_sum')),
                     Interval(6, 130))
    self.assertEqual(self.const_prop.resolve_param(tfu.Path.empty().append_link('link').append_param('range_intersection')),
                     Interval(5, 10))
