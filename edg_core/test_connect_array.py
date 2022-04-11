import unittest

import edgir
from . import *
from .test_common import TestBlockSource, TestBlockSink, TestPortSource, TestPortSink, List


class TestBlockSourceArray(Block):
  def __init__(self) -> None:
    super().__init__()
    self.sources = self.Port(Vector(TestPortSource()))
    self.sources.append_elt(TestPortSource(), "a")
    self.sources.append_elt(TestPortSource(), "b")


class TestBlockSinkArray(GeneratorBlock):
  def __init__(self) -> None:
    super().__init__()
    self.sinks = self.Port(Vector(TestPortSink()))
    self.generator(self.generate, self.sinks.allocated())

  def generate(self, allocateds: List[str]):
    for allocated in allocateds:
      self.sinks.append_elt(TestPortSink(), allocated)


class ArrayConnectBlock(Block):
  def contents(self):
    super().contents()

    self.source = self.Block(TestBlockSourceArray())
    self.sink1 = self.Block(TestBlockSinkArray())
    self.sink2 = self.Block(TestBlockSinkArray())
    self.test_net = self.connect(self.source.sources, self.sink1.sinks, self.sink2.sinks)


class ArrayConnectProtoTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = ArrayConnectBlock()._elaborated_def_to_proto()

  def test_subblock_def(self) -> None:
    self.assertEqual(self.pb.blocks['source'].lib_elem.target.name, "edg_core.test_connect_array.TestBlockSourceArray")
    self.assertEqual(self.pb.blocks['sink1'].lib_elem.target.name, "edg_core.test_connect_array.TestBlockSinkArray")
    self.assertEqual(self.pb.blocks['sink2'].lib_elem.target.name, "edg_core.test_connect_array.TestBlockSinkArray")

  def test_link_inference(self) -> None:
    self.assertEqual(len(self.pb.links), 1)
    self.assertEqual(self.pb.links['test_net'].array.self_class.target.name, "edg_core.test_common.TestLink")

  def test_connectivity(self) -> None:
    self.assertEqual(len(self.pb.constraints), 3)  # TODO: maybe filter by connection types in future for robustness

    expected_conn = edgir.ValueExpr()
    expected_conn.connectedArray.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connectedArray.link_port.ref.steps.add().name = 'source'
    expected_conn.connectedArray.block_port.ref.steps.add().name = 'source'
    expected_conn.connectedArray.block_port.ref.steps.add().name = 'source'
    self.assertIn(expected_conn, self.pb.constraints.values())

    expected_conn = edgir.ValueExpr()
    expected_conn.connectedArray.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connectedArray.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connectedArray.link_port.ref.steps.add().allocate = ''
    expected_conn.connectedArray.block_port.ref.steps.add().name = 'sink1'
    expected_conn.connectedArray.block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, self.pb.constraints.values())

    expected_conn = edgir.ValueExpr()
    expected_conn.connectedArray.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connectedArray.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connectedArray.link_port.ref.steps.add().allocate = ''
    expected_conn.connectedArray.block_port.ref.steps.add().name = 'sink2'
    expected_conn.connectedArray.block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, self.pb.constraints.values())
