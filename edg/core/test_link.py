import unittest

from .. import edgir
from . import *
from .test_elaboration_common import TestLink


class LinkTestCase(unittest.TestCase):
  def setUp(self):
    self.pb = TestLink()._elaborated_def_to_proto()

  def test_self_class(self):
    self.assertEqual(self.pb.self_class.target.name, "edg_core.test_elaboration_common.TestLink")

  def test_superclasses(self):
    self.assertEqual(len(self.pb.superclasses), 1)
    self.assertEqual(self.pb.superclasses[0].target.name, "edg_core.test_elaboration_common.TestLinkBase")
    self.assertEqual(len(self.pb.super_superclasses), 0)

  def test_param_def(self):
    self.assertEqual(len(self.pb.params), 3)
    self.assertTrue(self.pb.params[0].name, 'float_param_sink_sum')
    self.assertTrue(self.pb.params[0].value.HasField('floating'))
    self.assertTrue(self.pb.params[1].name, 'float_param_sink_range')
    self.assertTrue(self.pb.params[1].value.HasField('range'))
    self.assertTrue(self.pb.params[2].name, 'range_param_sink_common')
    self.assertTrue(self.pb.params[2].value.HasField('range'))

  def test_port_def(self):
    self.assertEqual(len(self.pb.ports), 2)
    self.assertTrue(self.pb.ports[0].name, 'source')
    self.assertEqual(self.pb.ports[0].value.lib_elem.target.name, "edg_core.test_elaboration_common.TestPortSource")
    self.assertTrue(self.pb.ports[1].name, 'sinks')
    self.assertEqual(self.pb.ports[1].value.array.self_class.target.name, "edg_core.test_elaboration_common.TestPortSink")

  def test_constraints(self):
    # partial test of constraints, only the ones that are more interesting than tested elsewhere
    # namely, ones that deal with map and reduce operations
    constraints = list(map(lambda pair: pair.value, self.pb.constraints))

    expected_constr = edgir.ValueExpr()
    expected_constr.assign.dst.steps.add().name = 'float_param_sink_range'
    expected_constr.assign.src.binary.op = edgir.BinaryExpr.RANGE

    expected_constr.assign.src.binary.lhs.unary_set.op = edgir.UnarySetExpr.MINIMUM
    expected_constr.assign.src.binary.lhs.unary_set.vals.map_extract.container.ref.steps.add().name = 'sinks'
    expected_constr.assign.src.binary.lhs.unary_set.vals.map_extract.path.steps.add().name = 'float_param'

    expected_constr.assign.src.binary.rhs.unary_set.op = edgir.UnarySetExpr.MAXIMUM
    expected_constr.assign.src.binary.rhs.unary_set.vals.map_extract.container.ref.steps.add().name = 'sinks'
    expected_constr.assign.src.binary.rhs.unary_set.vals.map_extract.path.steps.add().name = 'float_param'
    self.assertIn(expected_constr, constraints)

    expected_constr = edgir.ValueExpr()
    expected_constr.binary.op = edgir.BinaryExpr.WITHIN
    expected_constr.binary.lhs.ref.steps.add().name = 'source'
    expected_constr.binary.lhs.ref.steps.add().name = 'float_param'
    expected_constr.binary.rhs.ref.steps.add().name = 'source'
    expected_constr.binary.rhs.ref.steps.add().name = 'float_param_limit'
    self.assertIn(expected_constr, constraints)

    expected_constr = edgir.ValueExpr()
    expected_constr.assign.dst.steps.add().name = 'range_param_sink_common'
    expected_constr.assign.src.unary_set.op = edgir.UnarySetExpr.INTERSECTION
    expected_constr.assign.src.unary_set.vals.map_extract.container.ref.steps.add().name = 'sinks'
    expected_constr.assign.src.unary_set.vals.map_extract.path.steps.add().name = 'range_limit'
    self.assertIn(expected_constr, constraints)

    expected_constr = edgir.ValueExpr()
    expected_constr.binary.op = edgir.BinaryExpr.WITHIN
    expected_constr.binary.lhs.ref.steps.add().name = 'source'
    expected_constr.binary.lhs.ref.steps.add().name = 'range_param'
    expected_constr.binary.rhs.ref.steps.add().name = 'range_param_sink_common'
    self.assertIn(expected_constr, constraints)
