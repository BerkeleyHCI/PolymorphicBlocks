import unittest

import edgir
from . import *
from .test_common import TestBlockSource, TestBlockSink, TestPortSink


class TopHierarchyBlock(Block):
  def contents(self):
    super().contents()

    self.source = self.Block(TestBlockSource())
    self.sink1 = self.Block(TestBlockSink())
    self.sink2 = self.Block(TestBlockSink())
    self.test_net = self.connect(self.source.source, self.sink1.sink, self.sink2.sink)


class TopHierarchyBlockProtoTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = TopHierarchyBlock()._elaborated_def_to_proto()

  def test_subblock_def(self) -> None:
    self.assertEqual(self.pb.blocks[0].name, 'source')
    self.assertEqual(self.pb.blocks[0].value.lib_elem.base.target.name, "edg_core.test_common.TestBlockSource")
    self.assertFalse(self.pb.blocks[0].value.lib_elem.mixins)
    self.assertEqual(self.pb.blocks[1].name, 'sink1')
    self.assertEqual(self.pb.blocks[1].value.lib_elem.base.target.name, "edg_core.test_common.TestBlockSink")
    self.assertFalse(self.pb.blocks[1].value.lib_elem.mixins)
    self.assertEqual(self.pb.blocks[2].name, 'sink2')
    self.assertEqual(self.pb.blocks[2].value.lib_elem.base.target.name, "edg_core.test_common.TestBlockSink")
    self.assertFalse(self.pb.blocks[2].value.lib_elem.mixins)

  def test_link_inference(self) -> None:
    self.assertEqual(len(self.pb.links), 1)
    self.assertEqual(self.pb.links[0].name, 'test_net')
    self.assertEqual(self.pb.links[0].value.lib_elem.target.name, "edg_core.test_common.TestLink")

  def test_connectivity(self) -> None:
    self.assertEqual(len(self.pb.constraints), 3)  # TODO: maybe filter by connection types in future for robustness
    constraints = list(map(lambda pair: pair.value, self.pb.constraints))

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'source'
    expected_conn.connected.block_port.ref.steps.add().name = 'source'
    expected_conn.connected.block_port.ref.steps.add().name = 'source'
    self.assertIn(expected_conn, constraints)

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().allocate = ''
    expected_conn.connected.block_port.ref.steps.add().name = 'sink1'
    expected_conn.connected.block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, constraints)

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().allocate = ''
    expected_conn.connected.block_port.ref.steps.add().name = 'sink2'
    expected_conn.connected.block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, constraints)


class MultiConnectBlock(Block):
  def contents(self):
    super().contents()

    self.source = self.Block(TestBlockSource())
    self.sink1 = self.Block(TestBlockSink())
    self.sink2 = self.Block(TestBlockSink())
    self.sink3 = self.Block(TestBlockSink())

    self.test_net = self.connect(self.source.source, self.sink1.sink)
    self.connect(self.source.source, self.sink2.sink)  # not named, to not conflict with the first
    self.connect(self.test_net, self.sink3.sink)


class MultiConnectBlockProtoTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = MultiConnectBlock()._elaborated_def_to_proto()

  def test_connectivity(self) -> None:
    self.assertEqual(len(self.pb.constraints), 4)
    constraints = list(map(lambda pair: pair.value, self.pb.constraints))

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'source'
    expected_conn.connected.block_port.ref.steps.add().name = 'source'
    expected_conn.connected.block_port.ref.steps.add().name = 'source'
    self.assertIn(expected_conn, constraints)

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().allocate = ''
    expected_conn.connected.block_port.ref.steps.add().name = 'sink1'
    expected_conn.connected.block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, constraints)

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().allocate = ''
    expected_conn.connected.block_port.ref.steps.add().name = 'sink2'
    expected_conn.connected.block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, constraints)

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().allocate = ''
    expected_conn.connected.block_port.ref.steps.add().name = 'sink3'
    expected_conn.connected.block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, constraints)


class ExportPortHierarchyBlock(Block):
  def __init__(self) -> None:
    super().__init__()
    self.sink = self.Block(TestBlockSink())
    self.exported = self.Export(self.sink.sink, optional=True)  # avoid required constraint


class ExportPortHierarchyBlockTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = ExportPortHierarchyBlock()._elaborated_def_to_proto()

  def test_exported_port_def(self) -> None:
    self.assertEqual(len(self.pb.ports), 1)
    self.assertEqual(self.pb.ports[0].name, 'exported')
    self.assertEqual(self.pb.ports[0].value.lib_elem.target.name, "edg_core.test_common.TestPortSink")

  def test_connectivity(self) -> None:
    self.assertEqual(len(self.pb.constraints), 1)
    constraints = list(map(lambda pair: pair.value, self.pb.constraints))

    expected_conn = edgir.ValueExpr()
    expected_conn.exported.exterior_port.ref.steps.add().name = 'exported'
    expected_conn.exported.internal_block_port.ref.steps.add().name = 'sink'
    expected_conn.exported.internal_block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, constraints)


class IndirectExportPortHierarchyBlock(Block):
  def __init__(self) -> None:
    super().__init__()
    self.exported = self.Port(TestPortSink(), optional=True)  # avoid required constraint

  def contents(self):
    super().contents()
    self.sink = self.Block(TestBlockSink())
    self.test_net = self.connect(self.exported, self.sink.sink)


class IndirectExportPortHierarchyBlockTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = IndirectExportPortHierarchyBlock()._elaborated_def_to_proto()

  def test_exported_port_def(self) -> None:
    self.assertEqual(len(self.pb.ports), 1)
    self.assertEqual(self.pb.ports[0].name, 'exported')
    self.assertEqual(self.pb.ports[0].value.lib_elem.target.name, "edg_core.test_common.TestPortSink")

  def test_connectivity(self) -> None:
    self.assertEqual(len(self.pb.constraints), 1)
    constraints = list(map(lambda pair: pair.value, self.pb.constraints))

    expected_conn = edgir.ValueExpr()
    expected_conn.exported.exterior_port.ref.steps.add().name = 'exported'
    expected_conn.exported.internal_block_port.ref.steps.add().name = 'sink'
    expected_conn.exported.internal_block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, constraints)


class PortBridgeHierarchyBlock(Block):
  def __init__(self) -> None:
    super().__init__()
    self.source_port = self.Port(TestPortSink(), optional=True)

  def contents(self):
    super().contents()
    self.sink1 = self.Block(TestBlockSink())
    self.sink2 = self.Block(TestBlockSink())
    self.test_net = self.connect(self.source_port, self.sink1.sink, self.sink2.sink)


class PortBridgeHierarchyBlockTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = PortBridgeHierarchyBlock()._elaborated_def_to_proto()

  def test_exported_port_def(self) -> None:
    self.assertEqual(len(self.pb.ports), 1)
    self.assertEqual(self.pb.ports[0].name, 'source_port')
    self.assertEqual(self.pb.ports[0].value.lib_elem.target.name, "edg_core.test_common.TestPortSink")

  def test_connectivity(self) -> None:
    self.assertEqual(len(self.pb.constraints), 4)
    constraints = list(map(lambda pair: pair.value, self.pb.constraints))

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.block_port.ref.steps.add().name = '(bridge)source_port'
    expected_conn.connected.block_port.ref.steps.add().name = 'inner_link'
    expected_conn.connected.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'source'
    self.assertIn(expected_conn, constraints)

    expected_conn = edgir.ValueExpr()
    expected_conn.exported.exterior_port.ref.steps.add().name = 'source_port'
    expected_conn.exported.internal_block_port.ref.steps.add().name = '(bridge)source_port'
    expected_conn.exported.internal_block_port.ref.steps.add().name = 'outer_port'
    self.assertIn(expected_conn, constraints)

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.block_port.ref.steps.add().name = 'sink1'
    expected_conn.connected.block_port.ref.steps.add().name = 'sink'
    expected_conn.connected.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().allocate = ''
    self.assertIn(expected_conn, constraints)

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.block_port.ref.steps.add().name = 'sink2'
    expected_conn.connected.block_port.ref.steps.add().name = 'sink'
    expected_conn.connected.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().allocate = ''
    self.assertIn(expected_conn, constraints)
