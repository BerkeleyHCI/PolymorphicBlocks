import unittest

from . import *
from .test_common import TestPortBase


class TestBlockBase(Block):
  def __init__(self) -> None:
    super().__init__()
    self.base_float = self.Parameter(FloatExpr())
    self.base_port = self.Port(TestPortBase())  # required to test required constraint
    self.base_port_constr = self.Port(TestPortBase(self.base_float), optional=True)


class TestBlock(TestBlockBase):
  def __init__(self) -> None:
    super().__init__()
    self.range_init = self.Parameter(RangeExpr((-4.2, -1.3)))
    self.port_lit = self.Port(TestPortBase(117), optional=True)


class BlockBaseProtoTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = TestBlockBase()._elaborated_def_to_proto()

  def test_param_def(self) -> None:
    self.assertEqual(len(self.pb.params), 1)
    self.assertTrue(self.pb.params['base_float'].HasField('floating'))

  def test_port_def(self) -> None:
    self.assertEqual(len(self.pb.ports), 2)
    self.assertEqual(self.pb.ports['base_port'].lib_elem.target.name, "edg_core.test_common.TestPortBase")
    self.assertEqual(self.pb.ports['base_port_constr'].lib_elem.target.name, "edg_core.test_common.TestPortBase")

  def test_port_init(self) -> None:
    self.assertEqual(
      edgir.EqualsValueExpr(['base_port_constr', 'float_param'], ['base_float']),
      self.pb.constraints["(init)base_port_constr"])

  def test_connected_constraint(self) -> None:
    expected_constr = edgir.ValueExpr()
    expected_constr.ref.steps.add().name = 'base_port'
    expected_constr.ref.steps.add().reserved_param = edgir.IS_CONNECTED
    self.assertIn(expected_constr, self.pb.constraints.values())

    expected_constr = edgir.ValueExpr()
    expected_constr.ref.steps.add().name = 'base_port_constr'
    expected_constr.ref.steps.add().reserved_param = edgir.IS_CONNECTED
    self.assertNotIn(expected_constr, self.pb.constraints.values())


class BlockProtoTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = TestBlock()._elaborated_def_to_proto()

  def test_superclass(self) -> None:
    self.assertEqual(len(self.pb.superclasses), 1)
    self.assertEqual(self.pb.superclasses[0].target.name, "edg_core.test_block.TestBlockBase")

    self.assertTrue(self.pb.params['base_float'].HasField('floating'))
    self.assertEqual(self.pb.ports['base_port'].lib_elem.target.name, "edg_core.test_common.TestPortBase")
    self.assertEqual(self.pb.ports['base_port_constr'].lib_elem.target.name, "edg_core.test_common.TestPortBase")

  def test_superclass_init(self) -> None:
    self.assertEqual(
      edgir.EqualsValueExpr(['base_port_constr', 'float_param'], ['base_float']),
      self.pb.constraints["(init)base_port_constr"])

  def test_port_def(self) -> None:
    self.assertEqual(len(self.pb.ports), 3)
    self.assertEqual(self.pb.ports['port_lit'].lib_elem.target.name, "edg_core.test_common.TestPortBase")

  def test_param_def(self) -> None:
    self.assertEqual(len(self.pb.params), 2)
    self.assertTrue(self.pb.params['range_init'].HasField('range'))

  def test_param_init(self) -> None:
    self.assertEqual(
      edgir.EqualsValueExpr(['range_init'], (-4.2, -1.3)),
      self.pb.constraints["(init)range_init"])
