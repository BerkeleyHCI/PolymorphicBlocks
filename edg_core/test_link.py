from typing import *
import unittest

from . import *
from .test_elaboration_common import TestLink


class LinkTestCase(unittest.TestCase):
  def setUp(self):
    self.pb = TestLink()._elaborated_def_to_proto()

  def test_param_def(self):
    self.assertEqual(len(self.pb.params), 3)
    self.assertTrue(self.pb.params['float_param_sink_sum'].HasField('floating'))
    self.assertTrue(self.pb.params['float_param_sink_range'].HasField('range'))
    self.assertTrue(self.pb.params['range_param_sink_common'].HasField('range'))

  def test_port_def(self):
    self.assertEqual(len(self.pb.ports), 2)
    self.assertEqual(self.pb.ports['source'].lib_elem.target.name, "edg_core.test_elaboration_common.TestPortSource")
    self.assertEqual(self.pb.ports['sinks'].array.self_class.target.name, "edg_core.test_elaboration_common.TestPortSink")

  def test_constraints(self):
    # partial test of constraints, only the ones that are more interesting than tested elsewhere
    # namely, ones that deal with map and reduce operations
    expected_constr = edgir.ValueExpr()
    expected_constr.assign.dst.steps.add().name = 'float_param_sink_range'
    expected_constr.assign.src.binary.op = edgir.BinaryExpr.RANGE

    expected_constr.assign.src.binary.lhs.reduce.op = edgir.ReductionExpr.MINIMUM
    expected_constr.assign.src.binary.lhs.reduce.vals.map_extract.container.ref.steps.add().name = 'sinks'
    expected_constr.assign.src.binary.lhs.reduce.vals.map_extract.path.steps.add().name = 'float_param'

    expected_constr.assign.src.binary.rhs.reduce.op = edgir.ReductionExpr.MAXIMUM
    expected_constr.assign.src.binary.rhs.reduce.vals.map_extract.container.ref.steps.add().name = 'sinks'
    expected_constr.assign.src.binary.rhs.reduce.vals.map_extract.path.steps.add().name = 'float_param'
    self.assertIn(expected_constr, self.pb.constraints.values())

    expected_constr = edgir.ValueExpr()
    expected_constr.binary.op = edgir.BinaryExpr.SUBSET
    expected_constr.binary.lhs.ref.steps.add().name = 'source'
    expected_constr.binary.lhs.ref.steps.add().name = 'float_param'
    expected_constr.binary.rhs.ref.steps.add().name = 'source'
    expected_constr.binary.rhs.ref.steps.add().name = 'float_param_limit'
    self.assertIn(expected_constr, self.pb.constraints.values())

    expected_constr = edgir.ValueExpr()
    expected_name = '(init)range_param_sink_common'
    expected_constr.assign.dst.steps.add().name = 'range_param_sink_common'
    expected_constr.assign.src.reduce.op = edgir.ReductionExpr.INTERSECTION
    expected_constr.assign.src.reduce.vals.map_extract.container.ref.steps.add().name = 'sinks'
    expected_constr.assign.src.reduce.vals.map_extract.path.steps.add().name = 'range_limit'
    self.assertEqual(expected_constr, self.pb.constraints[expected_name])

    expected_constr = edgir.ValueExpr()
    expected_constr.binary.op = edgir.BinaryExpr.SUBSET
    expected_constr.binary.lhs.ref.steps.add().name = 'source'
    expected_constr.binary.lhs.ref.steps.add().name = 'range_param'
    expected_constr.binary.rhs.ref.steps.add().name = 'range_param_sink_common'
    self.assertIn(expected_constr, self.pb.constraints.values())
