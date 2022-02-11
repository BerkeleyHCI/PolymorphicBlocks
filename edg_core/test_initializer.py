import unittest

import edgir
from . import *
from .test_bundle import TestBundle


class TestSingleInitializerBlock(Block):
  def __init__(self) -> None:
    super().__init__()
    self.bundle_port = self.Port(TestBundle(42, 1, -1), optional=True)


class InternalBlock(Block):
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
    self.inner = self.Block(InternalBlock(62, 31))


class TestDefaultBlock(Block):
  def contents(self) -> None:
    super().contents()
    self.inner = self.Block(InternalBlock())


class TestMultipleInstantiationBlock(Block):
  def contents(self) -> None:
    super().contents()
    model = InternalBlock()
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

    self.assertEqual(len(pb.param_defaults), 0)

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

    self.assertEqual(
      edgir.AssignLit(['inner', 'inner_param'], 62.0),
      pb.constraints["(init)inner.inner_param"])
    self.assertEqual(
      edgir.AssignLit(['inner', 'bundle_param'], 31.0),
      pb.constraints["(init)inner.bundle_param"])

    self.assertEqual(len(pb.param_defaults), 0)

  def test_nested_inner(self):
    pb = InternalBlock()._elaborated_def_to_proto()

    self.assertEqual(len(pb.constraints.items()), 3)  # should not generate initializers for constructors

    self.assertEqual(
      edgir.AssignRef(['inner_bundle', 'float_param'], ['bundle_param']),  # even if it's a default
      pb.constraints["(init)inner_bundle.float_param"])
    self.assertIn("(init)inner_bundle.a.float_param", pb.constraints)  # don't care about literal initializers
    self.assertIn("(init)inner_bundle.b.float_param", pb.constraints)  # don't care about literal initializers

    self.assertEqual(len(pb.param_defaults), 1)
    self.assertEqual(pb.param_defaults['float_param'], edgir.lit_to_expr(3.0))

  def test_default_initializer(self):
    pb = TestDefaultBlock()._elaborated_def_to_proto()

    self.assertEqual(len(pb.constraints.items()), 1)
    self.assertEqual(
      edgir.AssignLit(['inner', 'inner_param'], 3.0),
      pb.constraints["(init)inner.inner_param"])

    self.assertEqual(len(pb.param_defaults), 0)

  def test_multiple_initializer(self):
    pb = TestMultipleInstantiationBlock()._elaborated_def_to_proto()

    self.assertEqual(
      edgir.AssignLit(['inner1', 'inner_param'], 3.0),
      pb.constraints["(init)inner1.inner_param"])

    self.assertEqual(
      edgir.AssignLit(['inner2', 'inner_param'], 3.0),
      pb.constraints["(init)inner2.inner_param"])

    self.assertEqual(len(pb.param_defaults), 0)
