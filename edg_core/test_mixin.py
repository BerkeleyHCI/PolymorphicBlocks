import unittest

import edgir
from . import *
from .test_elaboration_common import TestPortBase


class TestMixin(BlockInterfaceMixin):
  @init_in_parent
  def __init__(self, *args, float_value: FloatExpr = 1.0, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.mixin_port = self.Port(TestPortBase())
    self.mixin_float = self.ArgParameter(float_value)


class MixinProtoTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = TestMixin()._elaborated_def_to_proto()

  def test_abstract(self) -> None:
    self.assertEqual(self.pb.is_abstract, True)
    self.assertEqual(self.pb.HasField('default_refinement'), False)

  def test_param_def(self) -> None:
    self.assertEqual(len(self.pb.params), 1)
    self.assertEqual(self.pb.params[0].name, 'base_float')
    self.assertTrue(self.pb.params[0].value.HasField('floating'))

  def test_port_def(self) -> None:
    self.assertEqual(len(self.pb.ports), 2)
    self.assertEqual(self.pb.ports[0].name, 'base_port')
    self.assertEqual(self.pb.ports[0].value.lib_elem.target.name, "edg_core.test_elaboration_common.TestPortBase")
    self.assertEqual(self.pb.ports[1].name, 'base_port_constr')
    self.assertEqual(self.pb.ports[1].value.lib_elem.target.name, "edg_core.test_elaboration_common.TestPortBase")

  def test_connected_constraint(self) -> None:
    expected_constr = edgir.ValueExpr()
    expected_constr.ref.steps.add().name = 'base_port'
    expected_constr.ref.steps.add().reserved_param = edgir.IS_CONNECTED
    self.assertEqual(self.pb.constraints[0].name, "(reqd)base_port")
    self.assertEqual(self.pb.constraints[0].value, expected_constr)

  def test_port_init(self) -> None:
    self.assertEqual(self.pb.constraints[1].name, "(init)base_port_constr.float_param")
    self.assertEqual(self.pb.constraints[1].value, edgir.AssignRef(['base_port_constr', 'float_param'], ['base_float']))
