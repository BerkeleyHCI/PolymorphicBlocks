import unittest

import edgir
from . import *
from .test_common import TestPortSource, TestPortSink, List


class TestBlockSourceFixedArray(Block):
  def __init__(self) -> None:
    super().__init__()
    self.sources = self.Port(Vector(TestPortSource()))
    self.sources.append_elt(TestPortSource(), "a")
    self.sources.append_elt(TestPortSource(), "b")


class TestBlockSinkElasticArray(GeneratorBlock):
  def __init__(self) -> None:
    super().__init__()
    self.sinks = self.Port(Vector(TestPortSink()))
    self.generator(self.generate1, self.sinks.requested())

  def generate1(self, requests: List[str]):
    for request in requests:
      self.sinks.append_elt(TestPortSink(), request)


class ArrayConnectBlock(Block):
  def contents(self):
    super().contents()

    self.source = self.Block(TestBlockSourceFixedArray())
    self.sink1 = self.Block(TestBlockSinkElasticArray())
    self.sink2 = self.Block(TestBlockSinkElasticArray())
    self.test_net = self.connect(self.source.sources, self.sink1.sinks, self.sink2.sinks)


class ArrayConnectProtoTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = ArrayConnectBlock()._elaborated_def_to_proto()

  def test_link_inference(self) -> None:
    self.assertEqual(len(self.pb.links), 1)
    self.assertEqual(self.pb.links[0].name, 'test_net')
    self.assertEqual(self.pb.links[0].value.array.self_class.target.name, "edg_core.test_common.TestLink")

  def test_connectivity(self) -> None:
    self.assertEqual(len(self.pb.constraints), 3)
    constraints = list(map(lambda pair: pair.value, self.pb.constraints))

    expected_conn = edgir.ValueExpr()
    expected_conn.connectedArray.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connectedArray.link_port.ref.steps.add().name = 'source'
    expected_conn.connectedArray.block_port.ref.steps.add().name = 'source'
    expected_conn.connectedArray.block_port.ref.steps.add().name = 'sources'
    self.assertIn(expected_conn, constraints)

    expected_conn = edgir.ValueExpr()
    expected_conn.connectedArray.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connectedArray.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connectedArray.link_port.ref.steps.add().allocate = ''
    expected_conn.connectedArray.block_port.ref.steps.add().name = 'sink1'
    expected_conn.connectedArray.block_port.ref.steps.add().name = 'sinks'
    self.assertIn(expected_conn, constraints)

    expected_conn = edgir.ValueExpr()
    expected_conn.connectedArray.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connectedArray.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connectedArray.link_port.ref.steps.add().allocate = ''
    expected_conn.connectedArray.block_port.ref.steps.add().name = 'sink2'
    expected_conn.connectedArray.block_port.ref.steps.add().name = 'sinks'
    self.assertIn(expected_conn, constraints)


class ArrayAllocatedConnectBlock(Block):
  def contents(self):
    super().contents()

    self.source1 = self.Block(TestBlockSourceFixedArray())
    self.source2 = self.Block(TestBlockSourceFixedArray())
    self.sink = self.Block(TestBlockSinkElasticArray())
    self.test_net1 = self.connect(self.source1.sources, self.sink.sinks.request_vector())
    self.test_net2 = self.connect(self.source2.sources, self.sink.sinks.request_vector())


class ArrayAllocatedConnectProtoTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = ArrayAllocatedConnectBlock()._elaborated_def_to_proto()

  def test_link_inference(self) -> None:
    self.assertEqual(len(self.pb.links), 2)
    self.assertEqual(self.pb.links[0].name, 'test_net1')
    self.assertEqual(self.pb.links[0].value.array.self_class.target.name, "edg_core.test_common.TestLink")
    self.assertEqual(self.pb.links[1].name, 'test_net2')
    self.assertEqual(self.pb.links[1].value.array.self_class.target.name, "edg_core.test_common.TestLink")

  def test_connectivity(self) -> None:
    self.assertEqual(len(self.pb.constraints), 4)
    constraints = list(map(lambda pair: pair.value, self.pb.constraints))

    expected_conn = edgir.ValueExpr()
    expected_conn.connectedArray.link_port.ref.steps.add().name = 'test_net1'
    expected_conn.connectedArray.link_port.ref.steps.add().name = 'source'
    expected_conn.connectedArray.block_port.ref.steps.add().name = 'source1'
    expected_conn.connectedArray.block_port.ref.steps.add().name = 'sources'
    self.assertIn(expected_conn, constraints)

    expected_conn = edgir.ValueExpr()
    expected_conn.connectedArray.link_port.ref.steps.add().name = 'test_net1'
    expected_conn.connectedArray.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connectedArray.link_port.ref.steps.add().allocate = ''
    expected_conn.connectedArray.block_port.ref.steps.add().name = 'sink'
    expected_conn.connectedArray.block_port.ref.steps.add().name = 'sinks'
    expected_conn.connectedArray.block_port.ref.steps.add().allocate = ''
    self.assertIn(expected_conn, constraints)

    expected_conn = edgir.ValueExpr()
    expected_conn.connectedArray.link_port.ref.steps.add().name = 'test_net2'
    expected_conn.connectedArray.link_port.ref.steps.add().name = 'source'
    expected_conn.connectedArray.block_port.ref.steps.add().name = 'source2'
    expected_conn.connectedArray.block_port.ref.steps.add().name = 'sources'
    self.assertIn(expected_conn, constraints)

    expected_conn = edgir.ValueExpr()
    expected_conn.connectedArray.link_port.ref.steps.add().name = 'test_net2'
    expected_conn.connectedArray.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connectedArray.link_port.ref.steps.add().allocate = ''
    expected_conn.connectedArray.block_port.ref.steps.add().name = 'sink'
    expected_conn.connectedArray.block_port.ref.steps.add().name = 'sinks'
    expected_conn.connectedArray.block_port.ref.steps.add().allocate = ''
    self.assertIn(expected_conn, constraints)
