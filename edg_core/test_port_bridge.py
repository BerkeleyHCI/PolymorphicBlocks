import unittest

import edgir
from .test_elaboration_common import TestPortBridge, TestPortSink
from . import *


class PortBridgeProtoTestCase(unittest.TestCase):
  def setUp(self):
    self.pb = TestPortBridge()._elaborated_def_to_proto()

  def test_contains_param(self):
    self.assertEqual(self.pb.ports['inner_link'].lib_elem.target.name, "edg_core.test_elaboration_common.TestPortSource")
    self.assertEqual(self.pb.ports['outer_port'].lib_elem.target.name, "edg_core.test_elaboration_common.TestPortSink")

  def test_constraints(self):
    self.assertEqual(len(self.pb.constraints), 2)

    expected_constr = edgir.ValueExpr()
    expected_constr.assign.dst.steps.add().name = 'outer_port'
    expected_constr.assign.dst.steps.add().name = 'float_param'
    expected_constr.assign.src.ref.steps.add().name = 'inner_link'
    expected_constr.assign.src.ref.steps.add().reserved_param = edgir.CONNECTED_LINK
    expected_constr.assign.src.ref.steps.add().name = 'float_param_sink_sum'
    self.assertIn(expected_constr, self.pb.constraints.values())

    expected_constr = edgir.ValueExpr()
    expected_constr.binary.op = edgir.BinaryExpr.EQ
    expected_constr.assign.dst.steps.add().name = 'outer_port'
    expected_constr.assign.dst.steps.add().name = 'range_limit'
    expected_constr.assign.src.ref.steps.add().name = 'inner_link'
    expected_constr.assign.src.ref.steps.add().reserved_param = edgir.CONNECTED_LINK
    expected_constr.assign.src.ref.steps.add().name = 'range_param_sink_common'
    self.assertIn(expected_constr, self.pb.constraints.values())


class BadPortBridge(PortBridge):
  def __init__(self):
    super().__init__()
    self.bad_port = self.Port(TestPortSink())


class PortBridgeBadPortsTestCase(unittest.TestCase):
  def test_bad_ports(self):
    with self.assertRaises(AssertionError):
      BadPortBridge()._elaborated_def_to_proto()
