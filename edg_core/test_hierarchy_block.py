import unittest

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
    self.assertEqual(self.pb.blocks['source'].lib_elem.target.name, "edg_core.test_common.TestBlockSource")
    self.assertEqual(self.pb.blocks['sink1'].lib_elem.target.name, "edg_core.test_common.TestBlockSink")
    self.assertEqual(self.pb.blocks['sink2'].lib_elem.target.name, "edg_core.test_common.TestBlockSink")

  def test_link_inference(self) -> None:
    self.assertEqual(len(self.pb.links), 1)
    self.assertEqual(self.pb.links['test_net'].lib_elem.target.name, "edg_core.test_common.TestLink")

  def test_link_naming(self) -> None:
    self.assertIn('test_net', self.pb.links)
    # TODO: better name inference

  def test_connectivity(self) -> None:
    self.assertEqual(len(self.pb.constraints), 3)  # TODO: maybe filter by connection types in future for robustness

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'source'
    expected_conn.connected.block_port.ref.steps.add().name = 'source'
    expected_conn.connected.block_port.ref.steps.add().name = 'source'
    self.assertIn(expected_conn, self.pb.constraints.values())

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().reserved_param = edgir.ALLOCATE
    expected_conn.connected.block_port.ref.steps.add().name = 'sink1'
    expected_conn.connected.block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, self.pb.constraints.values())

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().reserved_param = edgir.ALLOCATE
    expected_conn.connected.block_port.ref.steps.add().name = 'sink2'
    expected_conn.connected.block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, self.pb.constraints.values())


class MultiConnectBlock(Block):
  def contents(self):
    super().contents()

    self.source = self.Block(TestBlockSource())
    self.sink1 = self.Block(TestBlockSink())
    self.sink2 = self.Block(TestBlockSink())

    self.test_net = self.connect(self.source.source, self.sink1.sink)
    self.connect(self.source.source, self.sink2.sink)  # not named, to not conflict with the first


class MultiConnectBlockProtoTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = MultiConnectBlock()._elaborated_def_to_proto()

  def test_connectivity(self) -> None:
    self.assertEqual(len(self.pb.constraints), 3)

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'source'
    expected_conn.connected.block_port.ref.steps.add().name = 'source'
    expected_conn.connected.block_port.ref.steps.add().name = 'source'
    self.assertIn(expected_conn, self.pb.constraints.values())

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().reserved_param = edgir.ALLOCATE
    expected_conn.connected.block_port.ref.steps.add().name = 'sink1'
    expected_conn.connected.block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, self.pb.constraints.values())

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().reserved_param = edgir.ALLOCATE
    expected_conn.connected.block_port.ref.steps.add().name = 'sink2'
    expected_conn.connected.block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, self.pb.constraints.values())


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
    self.assertEqual(self.pb.ports['exported'].lib_elem.target.name, "edg_core.test_common.TestPortSink")

  def test_connectivity(self) -> None:
    self.assertEqual(len(self.pb.constraints), 1)

    expected_conn = edgir.ValueExpr()
    expected_conn.exported.exterior_port.ref.steps.add().name = 'exported'
    expected_conn.exported.internal_block_port.ref.steps.add().name = 'sink'
    expected_conn.exported.internal_block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, self.pb.constraints.values())


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
    self.assertEqual(self.pb.ports['exported'].lib_elem.target.name, "edg_core.test_common.TestPortSink")

  def test_connectivity(self) -> None:
    self.assertEqual(len(self.pb.constraints), 1)

    expected_conn = edgir.ValueExpr()
    expected_conn.exported.exterior_port.ref.steps.add().name = 'exported'
    expected_conn.exported.internal_block_port.ref.steps.add().name = 'sink'
    expected_conn.exported.internal_block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, self.pb.constraints.values())


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
    self.assertEqual(self.pb.ports['source_port'].lib_elem.target.name, "edg_core.test_common.TestPortSink")

  def test_connectivity(self) -> None:
    self.assertEqual(len(self.pb.constraints), 4)

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.block_port.ref.steps.add().name = '(bridge)source_port'
    expected_conn.connected.block_port.ref.steps.add().name = 'inner_link'
    expected_conn.connected.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'source'
    self.assertIn(expected_conn, self.pb.constraints.values())

    expected_conn = edgir.ValueExpr()
    expected_conn.exported.exterior_port.ref.steps.add().name = 'source_port'
    expected_conn.exported.internal_block_port.ref.steps.add().name = '(bridge)source_port'
    expected_conn.exported.internal_block_port.ref.steps.add().name = 'outer_port'
    self.assertIn(expected_conn, self.pb.constraints.values())

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.block_port.ref.steps.add().name = 'sink1'
    expected_conn.connected.block_port.ref.steps.add().name = 'sink'
    expected_conn.connected.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().reserved_param = edgir.ALLOCATE
    self.assertIn(expected_conn, self.pb.constraints.values())

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.block_port.ref.steps.add().name = 'sink2'
    expected_conn.connected.block_port.ref.steps.add().name = 'sink'
    expected_conn.connected.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().reserved_param = edgir.ALLOCATE
    self.assertIn(expected_conn, self.pb.constraints.values())
