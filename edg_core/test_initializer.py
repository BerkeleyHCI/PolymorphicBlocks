from typing import *
import sys
import unittest

from . import *
from .test_bundle import TestBundle
from . import test_common, test_bundle


class TestSingleInitializerBlock(Block):
  def __init__(self) -> None:
    super().__init__()
    self.bundle_port = self.Port(TestBundle(42, 1, -1), optional=True)


class TestInternalBlock(Block):
  @init_in_parent
  def __init__(self, container_float_param: FloatLike = 3, float_param: FloatLike = FloatExpr()) -> None:
    super().__init__()
    self.inner_bundle = self.Port(TestBundle(float_param, 0, 24), optional=True)
    self.inner_param = self.Parameter(FloatExpr(container_float_param))


class TestNestedBlock(Block):
  def __init__(self) -> None:
    super().__init__()
    self.outer_bundle = self.Port(TestBundle(21, 1, -1), optional=True)

  def contents(self) -> None:
    super().contents()
    self.inner = self.Block(TestInternalBlock(62, 31))


class TestDefaultBlock(Block):
  def contents(self) -> None:
    super().contents()
    self.inner = self.Block(TestInternalBlock())


class TestDefaultRangeBlock(Block):
  @init_in_parent
  def __init__(self, range_init: RangeLike = RangeExpr()) -> None:
    super().__init__()
    self.range_param = self.Parameter(RangeExpr(range_init))
    self.range_within_param = self.Parameter(RangeExpr(range_init, constr=RangeSubset))


class TestDefaultStringBlock(Block):
  @init_in_parent
  def __init__(self, string_init: StringLike = StringExpr()) -> None:
    super().__init__()
    self.string_param = self.Parameter(StringExpr(string_init))


class TestMultipleInstantiationBlock(Block):
  def contents(self) -> None:
    super().contents()
    model = TestInternalBlock()
    self.inner1 = self.Block(model)
    self.inner2 = self.Block(model)


class InitializerTestCase(unittest.TestCase):
  def test_initializer(self):
    pb = Driver([test_common, test_bundle]).generate_block(TestSingleInitializerBlock()).contents

    self.assertEqual(len(pb.constraints.items()), 1)
    self.assertEqual(edgir.AndValueExpr(
      edgir.EqualsValueExpr(['bundle_port', 'float_param'], 42),
      edgir.EqualsValueExpr(['bundle_port', 'a', 'float_param'], 1),
      edgir.EqualsValueExpr(['bundle_port', 'b', 'float_param'], -1)
    ), pb.constraints["(init)bundle_port"])

  def test_nested_initializer(self):
    # TODO better detection of driver imports
    pb = Driver([test_common, test_bundle, sys.modules[__name__]]).generate_block(TestNestedBlock()).contents

    self.assertEqual(len(pb.constraints.items()), 2)

    self.assertEqual(edgir.AndValueExpr(
      edgir.EqualsValueExpr(['outer_bundle', 'float_param'], 21),
      edgir.EqualsValueExpr(['outer_bundle', 'a', 'float_param'], 1),
      edgir.EqualsValueExpr(['outer_bundle', 'b', 'float_param'], -1),
    ), pb.constraints["(init)outer_bundle"])

    self.assertEqual(edgir.AndValueExpr(
      edgir.EqualsValueExpr(['inner', '(constr)container_float_param'], 62),
      edgir.EqualsValueExpr(['inner', '(constr)float_param'], 31),
    ), pb.constraints["(init)inner"])

    self.assertEqual(len(pb.blocks['inner'].hierarchy.constraints.items()), 2)
    self.assertEqual(edgir.AndValueExpr(
      edgir.EqualsValueExpr(['inner_bundle', 'float_param'], ['(constr)float_param']),
      edgir.EqualsValueExpr(['inner_bundle', 'a', 'float_param'], 0),
      edgir.EqualsValueExpr(['inner_bundle', 'b', 'float_param'], 24)
    ), pb.blocks['inner'].hierarchy.constraints["(init)inner_bundle"])

    self.assertEqual(edgir.EqualsValueExpr(['inner_param'], ['(constr)container_float_param']),
      pb.blocks['inner'].hierarchy.constraints["(init)inner_param"])

  def test_default_initializer(self):
    # TODO better detection of driver imports
    pb = Driver([test_common, test_bundle, sys.modules[__name__]]).generate_block(TestDefaultBlock()).contents

    self.assertEqual(len(pb.constraints.items()), 1)
    self.assertEqual(
      edgir.EqualsValueExpr(['inner', '(constr)container_float_param'], 3),
      pb.constraints["(init)inner"])

  def test_top_initializer(self):
    # TODO better detection of driver imports
    pb = Driver([test_common, test_bundle, sys.modules[__name__]]).generate_block(TestInternalBlock()).contents

    self.assertEqual(
      edgir.EqualsValueExpr(['(constr)container_float_param'], 3),
      pb.constraints["(top_init)"])
    self.assertEqual(
      edgir.EqualsValueExpr(['inner_param'], ['(constr)container_float_param']),
      pb.constraints["(init)inner_param"])

  def test_range_initializer(self):
    # TODO better detection of driver imports
    pb = Driver([sys.modules[__name__]]).generate_block(TestDefaultRangeBlock((4*0.9, 4*1.1))).contents

    self.assertEqual(
      edgir.EqualsValueExpr(['(constr)range_init'], (4 * 0.9, 4 * 1.1)),
      pb.constraints["(top_init)"])
    self.assertEqual(
      edgir.EqualsValueExpr(['range_param'], ['(constr)range_init']),
      pb.constraints["(init)range_param"])
    self.assertEqual(
      edgir.SubsetValueExpr(['range_within_param'], ['(constr)range_init']),
      pb.constraints["(init)range_within_param"])

  def test_string_initializer(self):
    # TODO better detection of driver imports
    pb = Driver([sys.modules[__name__]]).generate_block(TestDefaultStringBlock("TEST")).contents

    self.assertEqual(
      edgir.EqualsValueExpr(['(constr)string_init'], "TEST"),
      pb.constraints["(top_init)"])
    self.assertEqual(
      edgir.EqualsValueExpr(['string_param'], ['(constr)string_init']),
      pb.constraints["(init)string_param"])

  def test_multiple_initializer(self):
    # TODO better detection of driver imports
    pb = Driver([test_common, test_bundle, sys.modules[__name__]]).generate_block(TestMultipleInstantiationBlock()).contents

    self.assertEqual(
      edgir.EqualsValueExpr(['inner1', '(constr)container_float_param'], 3),
      pb.constraints["(init)inner1"])

    self.assertEqual(
      edgir.EqualsValueExpr(['inner2', '(constr)container_float_param'], 3),
      pb.constraints["(init)inner2"])
