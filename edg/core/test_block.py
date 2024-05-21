import unittest

from .. import edgir
from . import *
from .test_elaboration_common import TestPortBase


@abstract_block
class TestBlockBase(Block):
  def __init__(self) -> None:
    super().__init__()
    self.base_float = self.Parameter(FloatExpr())
    self.base_port = self.Port(TestPortBase())  # required to test required constraint
    self.base_port_constr = self.Port(TestPortBase(self.base_float), optional=True)


@abstract_block_default(lambda: TestBlock)
class TestBlockSecondBase(Block):
  pass


class TestBlockSecondSub(TestBlockSecondBase):  # test indirect classes
  pass

@non_library
class TestBlockSecondNonLibrary(TestBlockSecondSub):  # test that it can skip the non_library superclass
  pass


class TestBlock(TestBlockBase, TestBlockSecondNonLibrary):
  def __init__(self) -> None:
    super().__init__()
    self.range_init = self.Parameter(RangeExpr((-4.2, -1.3)))
    self.array_init = self.Parameter(ArrayBoolExpr([False, True, False]))
    self.array_empty = self.Parameter(ArrayStringExpr([]))
    self.port_lit = self.Port(TestPortBase(117), optional=True)


class BlockBaseProtoTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = TestBlockBase()._elaborated_def_to_proto()

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
    self.assertEqual(self.pb.ports[0].value.lib_elem.target.name, "edg.core.test_elaboration_common.TestPortBase")
    self.assertEqual(self.pb.ports[1].name, 'base_port_constr')
    self.assertEqual(self.pb.ports[1].value.lib_elem.target.name, "edg.core.test_elaboration_common.TestPortBase")

  def test_connected_constraint(self) -> None:
    expected_constr = edgir.ValueExpr()
    expected_constr.ref.steps.add().name = 'base_port'
    expected_constr.ref.steps.add().reserved_param = edgir.IS_CONNECTED
    self.assertEqual(self.pb.constraints[0].name, "(reqd)base_port")
    self.assertEqual(self.pb.constraints[0].value, expected_constr)

  def test_port_init(self) -> None:
    self.assertEqual(self.pb.constraints[1].name, "(init)base_port_constr.float_param")
    self.assertEqual(self.pb.constraints[1].value, edgir.AssignRef(['base_port_constr', 'float_param'], ['base_float']))


class BlockSecondBaseProtoTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = TestBlockSecondBase()._elaborated_def_to_proto()

  def test_abstract(self) -> None:
    self.assertEqual(self.pb.is_abstract, True)

  def test_default(self) -> None:
    self.assertEqual(self.pb.default_refinement.target.name, "edg.core.test_block.TestBlock")


class BlockProtoTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = TestBlock()._elaborated_def_to_proto()

  def test_not_abstract(self) -> None:
    self.assertEqual(self.pb.is_abstract, False)
    self.assertEqual(self.pb.HasField('default_refinement'), False)

  def test_superclass(self) -> None:
    self.assertEqual(self.pb.self_class.target.name, "edg.core.test_block.TestBlock")
    self.assertEqual(self.pb.prerefine_class.target.name, "edg.core.test_block.TestBlock")
    self.assertEqual(len(self.pb.superclasses), 2)
    self.assertEqual(self.pb.superclasses[0].target.name, "edg.core.test_block.TestBlockBase")
    self.assertEqual(self.pb.superclasses[1].target.name, "edg.core.test_block.TestBlockSecondSub")
    self.assertEqual(len(self.pb.super_superclasses), 1)
    self.assertEqual(self.pb.super_superclasses[0].target.name, "edg.core.test_block.TestBlockSecondBase")

    self.assertEqual(self.pb.params[0].name, "base_float")
    self.assertTrue(self.pb.params[0].value.HasField('floating'))
    self.assertEqual(self.pb.ports[0].name, "base_port")
    self.assertEqual(self.pb.ports[0].value.lib_elem.target.name, "edg.core.test_elaboration_common.TestPortBase")
    self.assertEqual(self.pb.ports[1].name, "base_port_constr")
    self.assertEqual(self.pb.ports[1].value.lib_elem.target.name, "edg.core.test_elaboration_common.TestPortBase")

  def test_port_def(self) -> None:
    self.assertEqual(len(self.pb.ports), 3)
    self.assertEqual(self.pb.ports[2].name, "port_lit")
    self.assertEqual(self.pb.ports[2].value.lib_elem.target.name, "edg.core.test_elaboration_common.TestPortBase")
    self.assertEqual(self.pb.constraints[0].name, "(reqd)base_port")

  def test_param_def(self) -> None:
    self.assertEqual(len(self.pb.params), 4)
    self.assertEqual(self.pb.params[1].name, "range_init")
    self.assertTrue(self.pb.params[1].value.HasField('range'))
    self.assertEqual(self.pb.params[2].name, "array_init")
    self.assertTrue(self.pb.params[2].value.HasField('array'))
    self.assertEqual(self.pb.params[3].name, "array_empty")
    self.assertTrue(self.pb.params[3].value.HasField('array'))

  def test_superclass_init(self) -> None:
    self.assertEqual(self.pb.constraints[1].name, "(init)base_port_constr.float_param")
    self.assertEqual(self.pb.constraints[1].value, edgir.AssignRef(['base_port_constr', 'float_param'], ['base_float']))

  def test_port_init(self) -> None:
    self.assertEqual(self.pb.constraints[2].name, "(init)port_lit.float_param")

  def test_param_init(self) -> None:
    self.assertEqual(self.pb.constraints[3].name, "(init)range_init")
    self.assertEqual(self.pb.constraints[3].value, edgir.AssignLit(['range_init'], Range(-4.2, -1.3)))

    expected_assign = edgir.ValueExpr()
    expected_assign.assign.dst.CopyFrom(edgir.LocalPathList(['array_init']))
    expected_array = expected_assign.assign.src.array
    expected_array.vals.add().CopyFrom(edgir.lit_to_expr(False))
    expected_array.vals.add().CopyFrom(edgir.lit_to_expr(True))
    expected_array.vals.add().CopyFrom(edgir.lit_to_expr(False))
    self.assertEqual(self.pb.constraints[4].name, "(init)array_init")
    self.assertEqual(self.pb.constraints[4].value, expected_assign)

    expected_assign = edgir.ValueExpr()
    expected_assign.assign.dst.CopyFrom(edgir.LocalPathList(['array_empty']))
    expected_assign.assign.src.array.SetInParent()
    self.assertEqual(self.pb.constraints[5].name, "(init)array_empty")
    self.assertEqual(self.pb.constraints[5].value, expected_assign)

