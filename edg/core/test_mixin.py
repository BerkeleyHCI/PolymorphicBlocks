import unittest

from .. import edgir
from . import *
from .test_common import TestPortSink


@abstract_block
class TestMixinBase(Block):
  def __init__(self) -> None:
    super().__init__()
    self.base_port = self.Port(TestPortSink())


class TestMixin(BlockInterfaceMixin[TestMixinBase]):
  @init_in_parent
  def __init__(self, *args, mixin_float: FloatLike = 1.0, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.mixin_port = self.Port(TestPortSink())
    self.mixin_float = self.ArgParameter(mixin_float)


class MixinProtoTestCase(unittest.TestCase):
  def setUp(self) -> None:
    cls = TestMixin()
    self.assertEqual(cls._is_mixin(), True)
    self.pb = cls._elaborated_def_to_proto()

  def test_abstract(self) -> None:
    self.assertEqual(self.pb.is_abstract, True)
    self.assertEqual(self.pb.HasField('default_refinement'), False)

  def test_superclass(self) -> None:
    self.assertEqual(self.pb.self_class.target.name, "edg.core.test_mixin.TestMixin")
    self.assertEqual(self.pb.prerefine_class.target.name, "edg.core.test_mixin.TestMixin")
    self.assertEqual(len(self.pb.superclasses), 1)
    self.assertEqual(self.pb.superclasses[0].target.name, "edg.core.test_mixin.TestMixinBase")
    self.assertEqual(len(self.pb.super_superclasses), 0)

  def test_param_def(self) -> None:
    self.assertEqual(len(self.pb.params), 1)
    self.assertEqual(self.pb.params[0].name, 'mixin_float')
    self.assertTrue(self.pb.params[0].value.HasField('floating'))

  def test_port_def(self) -> None:
    self.assertEqual(len(self.pb.ports), 1)
    self.assertEqual(self.pb.ports[0].name, 'mixin_port')
    self.assertEqual(self.pb.ports[0].value.lib_elem.target.name, "edg.core.test_common.TestPortSink")

  def test_connected_constraint(self) -> None:
    expected_constr = edgir.ValueExpr()
    expected_constr.ref.steps.add().name = 'mixin_port'
    expected_constr.ref.steps.add().reserved_param = edgir.IS_CONNECTED
    self.assertEqual(self.pb.constraints[0].name, "(reqd)mixin_port")
    self.assertEqual(self.pb.constraints[0].value, expected_constr)


class TestMixinSubclass(TestMixin):
  pass


class MixinSubclassProtoTestCase(unittest.TestCase):
  def setUp(self) -> None:
    cls = TestMixinSubclass()
    self.assertEqual(cls._is_mixin(), True)
    self.pb = cls._elaborated_def_to_proto()

  def test_abstract(self) -> None:
    self.assertEqual(self.pb.is_abstract, True)
    self.assertEqual(self.pb.HasField('default_refinement'), False)

  def test_superclass(self) -> None:
    self.assertEqual(self.pb.self_class.target.name, "edg.core.test_mixin.TestMixinSubclass")
    self.assertEqual(self.pb.prerefine_class.target.name, "edg.core.test_mixin.TestMixinSubclass")
    self.assertEqual(len(self.pb.superclasses), 1)
    self.assertEqual(self.pb.superclasses[0].target.name, "edg.core.test_mixin.TestMixin")
    self.assertEqual(len(self.pb.super_superclasses), 1)
    self.assertEqual(self.pb.super_superclasses[0].target.name, "edg.core.test_mixin.TestMixinBase")

  # the rest of this tests that it has inherited the mixin's base port and param
  def test_param_def(self) -> None:
    self.assertEqual(len(self.pb.params), 1)
    self.assertEqual(self.pb.params[0].name, 'mixin_float')
    self.assertTrue(self.pb.params[0].value.HasField('floating'))

  def test_port_def(self) -> None:
    self.assertEqual(len(self.pb.ports), 1)
    self.assertEqual(self.pb.ports[0].name, 'mixin_port')
    self.assertEqual(self.pb.ports[0].value.lib_elem.target.name, "edg.core.test_common.TestPortSink")

  def test_connected_constraint(self) -> None:
    expected_constr = edgir.ValueExpr()
    expected_constr.ref.steps.add().name = 'mixin_port'
    expected_constr.ref.steps.add().reserved_param = edgir.IS_CONNECTED
    self.assertEqual(self.pb.constraints[0].name, "(reqd)mixin_port")
    self.assertEqual(self.pb.constraints[0].value, expected_constr)


class TestMixinConcreteBlock(TestMixin, TestMixinBase):
  pass  # doesn't define anything


class MixinConcreteBlockProtoTestCase(unittest.TestCase):  # pretty straightforward test of Python inheritance
  def setUp(self) -> None:
    cls = TestMixinConcreteBlock()
    self.assertEqual(cls._is_mixin(), False)
    self.pb = cls._elaborated_def_to_proto()

  def test_abstract(self) -> None:
    self.assertEqual(self.pb.is_abstract, False)
    self.assertEqual(self.pb.HasField('default_refinement'), False)

  def test_superclass(self) -> None:
    self.assertEqual(self.pb.self_class.target.name, "edg.core.test_mixin.TestMixinConcreteBlock")
    self.assertEqual(self.pb.prerefine_class.target.name, "edg.core.test_mixin.TestMixinConcreteBlock")
    self.assertEqual(len(self.pb.superclasses), 2)
    self.assertEqual(self.pb.superclasses[0].target.name, "edg.core.test_mixin.TestMixin")
    self.assertEqual(self.pb.superclasses[1].target.name, "edg.core.test_mixin.TestMixinBase")

  # the rest of this tests that it has inherited the mixin's base port and param
  def test_param_def(self) -> None:
    self.assertEqual(len(self.pb.params), 1)
    self.assertEqual(self.pb.params[0].name, 'mixin_float')
    self.assertTrue(self.pb.params[0].value.HasField('floating'))

  def test_port_def(self) -> None:
    self.assertEqual(len(self.pb.ports), 2)
    self.assertEqual(self.pb.ports[0].name, 'base_port')
    self.assertEqual(self.pb.ports[0].value.lib_elem.target.name, "edg.core.test_common.TestPortSink")
    self.assertEqual(self.pb.ports[1].name, 'mixin_port')
    self.assertEqual(self.pb.ports[1].value.lib_elem.target.name, "edg.core.test_common.TestPortSink")

  def test_connected_constraint(self) -> None:
    expected_constr = edgir.ValueExpr()
    expected_constr.ref.steps.add().name = 'base_port'
    expected_constr.ref.steps.add().reserved_param = edgir.IS_CONNECTED
    self.assertEqual(self.pb.constraints[0].name, "(reqd)base_port")
    self.assertEqual(self.pb.constraints[0].value, expected_constr)

    expected_constr = edgir.ValueExpr()
    expected_constr.ref.steps.add().name = 'mixin_port'
    expected_constr.ref.steps.add().reserved_param = edgir.IS_CONNECTED
    self.assertEqual(self.pb.constraints[1].name, "(reqd)mixin_port")
    self.assertEqual(self.pb.constraints[1].value, expected_constr)
