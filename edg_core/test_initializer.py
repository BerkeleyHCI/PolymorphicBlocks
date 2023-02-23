import unittest

import edgir
from . import *
from .test_bundle import TestBundle


class TestSingleInitializerBlock(Block):
  def __init__(self) -> None:
    super().__init__()
    self.bundle_port = self.Port(TestBundle(42, 1, -1), optional=True)


class TestInternalBlock(Block):
  @init_in_parent
  def __init__(self, inner_param: FloatLike = 3.0, bundle_param: FloatLike = FloatExpr()) -> None:
    super().__init__()
    self.inner_bundle = self.Port(TestBundle(bundle_param, 0, 24), optional=True)
    self.inner_param = inner_param


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


class TestMultipleInstantiationBlock(Block):
  def contents(self) -> None:
    super().contents()
    model = TestInternalBlock()
    self.inner1 = self.Block(model)
    self.inner2 = self.Block(model)


class InitializerTestCase(unittest.TestCase):
  def test_initializer(self):
    pb = TestSingleInitializerBlock()._elaborated_def_to_proto()

    self.assertEqual(len(pb.constraints), 3)
    self.assertEqual(pb.constraints[0].name, "(init)bundle_port.float_param")
    self.assertEqual(pb.constraints[0].value, edgir.AssignLit(['bundle_port', 'float_param'], 42.0))
    self.assertEqual(pb.constraints[1].name, "(init)bundle_port.a.float_param")
    self.assertEqual(pb.constraints[1].value, edgir.AssignLit(['bundle_port', 'a', 'float_param'], 1.0))
    self.assertEqual(pb.constraints[2].name, "(init)bundle_port.b.float_param")
    self.assertEqual(pb.constraints[2].value, edgir.AssignLit(['bundle_port', 'b', 'float_param'], -1.0))

  def test_nested_initializer(self):
    pb = TestNestedBlock()._elaborated_def_to_proto()

    self.assertEqual(len(pb.constraints), 5)
    self.assertEqual(pb.constraints[0].name, "(init)outer_bundle.float_param")
    self.assertEqual(pb.constraints[0].value, edgir.AssignLit(['outer_bundle', 'float_param'], 21.0))
    self.assertEqual(pb.constraints[1].name, "(init)outer_bundle.a.float_param")
    self.assertEqual(pb.constraints[1].value, edgir.AssignLit(['outer_bundle', 'a', 'float_param'], 1.0))
    self.assertEqual(pb.constraints[2].name, "(init)outer_bundle.b.float_param")
    self.assertEqual(pb.constraints[2].value, edgir.AssignLit(['outer_bundle', 'b', 'float_param'], -1.0))
    self.assertEqual(pb.constraints[3].name, "(init)inner.inner_param")
    self.assertEqual(pb.constraints[3].value, edgir.AssignLit(['inner', 'inner_param'], 62.0))
    self.assertEqual(pb.constraints[4].name, "(init)inner.bundle_param")
    self.assertEqual(pb.constraints[4].value, edgir.AssignLit(['inner', 'bundle_param'], 31.0))

  def test_nested_inner(self):
    pb = TestInternalBlock()._elaborated_def_to_proto()

    self.assertEqual(len(pb.constraints), 3)  # should not generate initializers for constructors
    self.assertEqual(pb.constraints[0].name, "(init)inner_bundle.float_param")
    self.assertEqual(pb.constraints[0].value, edgir.AssignRef(['inner_bundle', 'float_param'], ['bundle_param']))
    # don't care about value of literal initializers
    self.assertEqual(pb.constraints[1].name, "(init)inner_bundle.a.float_param")
    self.assertEqual(pb.constraints[2].name, "(init)inner_bundle.b.float_param")

  def test_default_initializer(self):
    pb = TestDefaultBlock()._elaborated_def_to_proto()

    self.assertEqual(len(pb.constraints), 1)
    self.assertEqual(pb.constraints[0].name, "(init)inner.inner_param")
    self.assertEqual(pb.constraints[0].value, edgir.AssignLit(['inner', 'inner_param'], 3.0))

  def test_multiple_initializer(self):
    pb = TestMultipleInstantiationBlock()._elaborated_def_to_proto()

    self.assertEqual(len(pb.constraints), 2)
    self.assertEqual(pb.constraints[0].name, "(init)inner1.inner_param")
    self.assertEqual(pb.constraints[0].value, edgir.AssignLit(['inner1', 'inner_param'], 3.0))
    self.assertEqual(pb.constraints[1].name, "(init)inner2.inner_param")
    self.assertEqual(pb.constraints[1].value, edgir.AssignLit(['inner2', 'inner_param'], 3.0))
