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
    pb = TestSingleInitializerBlock()._elaborated_def_to_proto()

    self.assertEqual(len(pb.constraints.items()), 3)
    self.assertEqual(
      edgir.AssignLit(['bundle_port', 'float_param'], 42.0),
      pb.constraints["(init)bundle_port.float_param"])
    self.assertEqual(
      edgir.AssignLit(['bundle_port', 'a', 'float_param'], 1.0),
      pb.constraints["(init)bundle_port.a.float_param"])
    self.assertEqual(
      edgir.AssignLit(['bundle_port', 'b', 'float_param'], -1.0),
      pb.constraints["(init)bundle_port.b.float_param"])

  def test_nested_initializer(self):
    pb = TestNestedBlock()._elaborated_def_to_proto()

    self.assertEqual(len(pb.constraints.items()), 5)

    self.assertEqual(
      edgir.AssignLit(['outer_bundle', 'float_param'], 21.0),
      pb.constraints["(init)outer_bundle.float_param"])
    self.assertEqual(
      edgir.AssignLit(['outer_bundle', 'a', 'float_param'], 1.0),
      pb.constraints["(init)outer_bundle.a.float_param"])
    self.assertEqual(
      edgir.AssignLit(['outer_bundle', 'b', 'float_param'], -1.0),
      pb.constraints["(init)outer_bundle.b.float_param"])

    self.assertEqual(edgir.AndValueExpr(
      edgir.EqualsValueExpr(['inner', '(constr)container_float_param'], 62),
      edgir.EqualsValueExpr(['inner', '(constr)float_param'], 31),
    ), pb.constraints["(init)inner"])


  def test_default_initializer(self):
    pb = TestDefaultBlock()._elaborated_def_to_proto()

    self.assertEqual(len(pb.constraints.items()), 1)
    self.assertEqual(
      edgir.AssignLit(['inner', '(constr)container_float_param'], 3.0),
      pb.constraints["(init)inner"])

  def test_range_initializer(self):
    pb = TestDefaultRangeBlock((4*0.9, 4*1.1))._elaborated_def_to_proto()

    self.assertEqual(
      edgir.AssignRef(['range_param'], ['(constr)range_init']),
      pb.constraints["(init)range_param"])

  def test_string_initializer(self):
    pb = TestDefaultStringBlock("TEST")._elaborated_def_to_proto()

    self.assertEqual(
      edgir.AssignRef(['string_param'], ['(constr)string_init']),
      pb.constraints["(init)string_param"])

  def test_multiple_initializer(self):
    pb = TestMultipleInstantiationBlock()._elaborated_def_to_proto()

    self.assertEqual(
      edgir.AssignLit(['inner1', '(constr)container_float_param'], 3),
      pb.constraints["(init)inner1"])

    self.assertEqual(
      edgir.AssignLit(['inner2', '(constr)container_float_param'], 3),
      pb.constraints["(init)inner2"])
