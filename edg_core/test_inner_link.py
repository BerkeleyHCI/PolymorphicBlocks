import unittest

import edgir
from . import *
from .test_elaboration_common import TestPortSource, TestPortSink
from . import test_common


class TestBundleLink(Link):
  def __init__(self) -> None:
    super().__init__()

    self.source = self.Port(TestBundleSource())
    self.sinks = self.Port(Vector(TestBundleSink()))

    self.a_net = self.connect(self.source.a, self.sinks.map_extract(lambda x: x.a))
    self.b_net = self.connect(self.source.b, self.sinks.map_extract(lambda x: x.b))


class TestBundleSource(Bundle[TestBundleLink]):
  def __init__(self) -> None:
    super().__init__()
    self.link_type = TestBundleLink

    self.a = self.Port(TestPortSource())
    self.b = self.Port(TestPortSource())


class TestBundleSink(Bundle[TestBundleLink]):
  def __init__(self) -> None:
    super().__init__()
    self.link_type = TestBundleLink

    self.a = self.Port(TestPortSink())
    self.b = self.Port(TestPortSink())


class InnerLinkTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = TestBundleLink()._elaborated_def_to_proto()

  def test_inner_links(self) -> None:
    self.assertEqual(self.pb.links['a_net'].lib_elem.target.name, "edg_core.test_elaboration_common.TestLink")
    self.assertEqual(self.pb.links['b_net'].lib_elem.target.name, "edg_core.test_elaboration_common.TestLink")

  def test_connects(self) -> None:
    self.assertEqual(len(self.pb.constraints), 6)  # TODO: maybe filter by connection types in future for robustness

    expected_conn = edgir.ValueExpr()
    expected_conn.exported.exterior_port.ref.steps.add().name = 'source'
    expected_conn.exported.exterior_port.ref.steps.add().name = 'a'
    expected_conn.exported.internal_block_port.ref.steps.add().name = 'a_net'
    expected_conn.exported.internal_block_port.ref.steps.add().name = 'source'
    self.assertIn(expected_conn, self.pb.constraints.values())

    expected_conn = edgir.ValueExpr()
    expected_conn.exported.exterior_port.map_extract.container.ref.steps.add().name = 'sinks'
    expected_conn.exported.exterior_port.map_extract.path.steps.add().name = 'a'
    expected_conn.exported.internal_block_port.ref.steps.add().name = 'a_net'
    expected_conn.exported.internal_block_port.ref.steps.add().name = 'sinks'
    expected_conn.exported.internal_block_port.ref.steps.add().allocate = ''
    self.assertIn(expected_conn, self.pb.constraints.values())

    expected_conn = edgir.ValueExpr()
    expected_conn.exported.exterior_port.ref.steps.add().name = 'source'
    expected_conn.exported.exterior_port.ref.steps.add().name = 'b'
    expected_conn.exported.internal_block_port.ref.steps.add().name = 'b_net'
    expected_conn.exported.internal_block_port.ref.steps.add().name = 'source'
    self.assertIn(expected_conn, self.pb.constraints.values())

    expected_conn = edgir.ValueExpr()
    expected_conn.exported.exterior_port.map_extract.container.ref.steps.add().name = 'sinks'
    expected_conn.exported.exterior_port.map_extract.path.steps.add().name = 'b'
    expected_conn.exported.internal_block_port.ref.steps.add().name = 'b_net'
    expected_conn.exported.internal_block_port.ref.steps.add().name = 'sinks'
    expected_conn.exported.internal_block_port.ref.steps.add().allocate = ''
    self.assertIn(expected_conn, self.pb.constraints.values())
