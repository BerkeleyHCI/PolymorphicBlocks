import unittest

import edgir
from . import *
from .test_elaboration_common import TestPortBase


class TestMixin(BlockInterfaceMixin):
  @init_in_parent
  def __init__(self, *args, mixin_float: FloatLike = 1.0, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.mixin_port = self.Port(TestPortBase())
    self.mixin_float = self.ArgParameter(mixin_float)


class MixinProtoTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = TestMixin()._elaborated_def_to_proto()

  def test_abstract(self) -> None:
    self.assertEqual(self.pb.is_abstract, True)
    self.assertEqual(self.pb.HasField('default_refinement'), False)

  def test_param_def(self) -> None:
    self.assertEqual(len(self.pb.params), 1)
    self.assertEqual(self.pb.params[0].name, 'mixin_float')
    self.assertTrue(self.pb.params[0].value.HasField('floating'))

  def test_port_def(self) -> None:
    self.assertEqual(len(self.pb.ports), 1)
    self.assertEqual(self.pb.ports[0].name, 'mixin_port')
    self.assertEqual(self.pb.ports[0].value.lib_elem.target.name, "edg_core.test_elaboration_common.TestPortBase")

  def test_connected_constraint(self) -> None:
    expected_constr = edgir.ValueExpr()
    expected_constr.ref.steps.add().name = 'mixin_port'
    expected_constr.ref.steps.add().reserved_param = edgir.IS_CONNECTED
    self.assertEqual(self.pb.constraints[0].name, "(reqd)mixin_port")
    self.assertEqual(self.pb.constraints[0].value, expected_constr)
