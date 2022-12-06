import unittest

import edgir
from .test_elaboration_common import TestPortBridge, TestPortSink
from . import *


class PortBridgeProtoTestCase(unittest.TestCase):
  def setUp(self):
    self.pb = TestPortBridge()._elaborated_def_to_proto()

  def test_contains_param(self):
    self.assertEqual(self.pb.ports[0].name, 'outer_port')
    self.assertEqual(self.pb.ports[0].value.lib_elem.target.name, "edg_core.test_elaboration_common.TestPortSink")
    self.assertEqual(self.pb.ports[1].name, 'inner_link')
    self.assertEqual(self.pb.ports[1].value.lib_elem.target.name, "edg_core.test_elaboration_common.TestPortSource")

  def test_constraints(self):
    self.assertEqual(len(self.pb.constraints), 2)
    constraints = list(map(lambda pair: pair.value, self.pb.constraints))

    expected_constr = edgir.ValueExpr()
    expected_constr.assign.dst.steps.add().name = 'outer_port'
    expected_constr.assign.dst.steps.add().name = 'float_param'
    expected_constr.assign.src.ref.steps.add().name = 'inner_link'
    expected_constr.assign.src.ref.steps.add().reserved_param = edgir.CONNECTED_LINK
    expected_constr.assign.src.ref.steps.add().name = 'float_param_sink_sum'
    self.assertIn(expected_constr, constraints)

    expected_constr = edgir.ValueExpr()
    expected_constr.binary.op = edgir.BinaryExpr.EQ
    expected_constr.assign.dst.steps.add().name = 'outer_port'
    expected_constr.assign.dst.steps.add().name = 'range_limit'
    expected_constr.assign.src.ref.steps.add().name = 'inner_link'
    expected_constr.assign.src.ref.steps.add().reserved_param = edgir.CONNECTED_LINK
    expected_constr.assign.src.ref.steps.add().name = 'range_param_sink_common'
    self.assertIn(expected_constr, constraints)


class BadPortBridge(PortBridge):
  def __init__(self):
    super().__init__()
    self.bad_port = self.Port(TestPortSink())


class PortBridgeBadPortsTestCase(unittest.TestCase):
  def test_bad_ports(self):
    with self.assertRaises(AssertionError):
      BadPortBridge()._elaborated_def_to_proto()
