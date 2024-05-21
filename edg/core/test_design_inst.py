import unittest

from .. import edgir
from . import *
from .test_common import TestBlockSource
from .test_hierarchy_block import TopHierarchyBlock, ExportPortHierarchyBlock, PortBridgeHierarchyBlock


class ExportPortHierarchyBlockTop(Block):
  def __init__(self) -> None:
    super().__init__()
    self.block = self.Block(ExportPortHierarchyBlock())


class PortBridgeHierarchyBlockTop(Block):
  def __init__(self) -> None:
    super().__init__()
    self.block = self.Block(PortBridgeHierarchyBlock())
    self.source = self.Block(TestBlockSource())  # TODO the PortBridge requires a connect, which isn't satisfied here
    self.connect(self.block.source_port, self.source.source)


class DesignInstantiationTestCase(unittest.TestCase):
  def test_single_hierarchy(self):
    """
    Tests design instantiation with a single level of hierarchy blocks.
    Only tests that the contained blocks are instantiated and structurally correct, does not check internal constraints
    """
    compiled_design = ScalaCompiler.compile(TopHierarchyBlock)
    pb = compiled_design.contents

    self.assertEqual(pb.self_class.target.name, 'edg.core.test_hierarchy_block.TopHierarchyBlock')

    self.assertEqual(len(pb.blocks), 3)

    self.assertEqual(pb.blocks[0].name, 'source')
    self.assertEqual(pb.blocks[0].value.hierarchy.self_class.target.name,
                     'edg.core.test_common.TestBlockSource')
    self.assertEqual(pb.blocks[0].value.hierarchy.ports[0].name, 'source')
    self.assertEqual(pb.blocks[0].value.hierarchy.ports[0].value.port.self_class.target.name,
                     'edg.core.test_common.TestPortSource')

    self.assertEqual(pb.blocks[1].name, 'sink1')
    self.assertEqual(pb.blocks[1].value.hierarchy.self_class.target.name,
                     'edg.core.test_common.TestBlockSink')
    self.assertEqual(pb.blocks[1].value.hierarchy.ports[0].name, 'sink')
    self.assertEqual(pb.blocks[1].value.hierarchy.ports[0].value.port.self_class.target.name,
                     'edg.core.test_common.TestPortSink')

    self.assertEqual(pb.blocks[2].name, 'sink2')
    self.assertEqual(pb.blocks[2].value.hierarchy.self_class.target.name,
                     'edg.core.test_common.TestBlockSink')
    self.assertEqual(pb.blocks[2].value.hierarchy.ports[0].name, 'sink')
    self.assertEqual(pb.blocks[2].value.hierarchy.ports[0].value.port.self_class.target.name,
                     'edg.core.test_common.TestPortSink')

    self.assertEqual(pb.links[0].name, 'test_net')
    self.assertEqual(pb.links[0].value.link.self_class.target.name, 'edg.core.test_common.TestLink')
    self.assertEqual(pb.links[0].value.link.ports[0].name, 'source')
    self.assertEqual(pb.links[0].value.link.ports[0].value.port.self_class.target.name,
                     "edg.core.test_common.TestPortSource")
    self.assertEqual(pb.links[0].value.link.ports[1].name, 'sinks')
    self.assertEqual(pb.links[0].value.link.ports[1].value.array.ports.ports[0].name, '0')
    self.assertEqual(pb.links[0].value.link.ports[1].value.array.ports.ports[0].value.port.self_class.target.name,
                     "edg.core.test_common.TestPortSink")
    self.assertEqual(pb.links[0].value.link.ports[1].value.array.ports.ports[1].name, '1')
    self.assertEqual(pb.links[0].value.link.ports[1].value.array.ports.ports[1].value.port.self_class.target.name,
                     "edg.core.test_common.TestPortSink")

    constraints = list(map(lambda pair: pair.value, pb.constraints))

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
    expanded = expected_conn.connected.expanded.add()
    expanded.link_port.ref.steps.add().name = 'test_net'
    expanded.link_port.ref.steps.add().name = 'sinks'
    expanded.link_port.ref.steps.add().name = '0'
    expanded.block_port.ref.steps.add().name = 'sink1'
    expanded.block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, constraints)

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().allocate = ''
    expected_conn.connected.block_port.ref.steps.add().name = 'sink2'
    expected_conn.connected.block_port.ref.steps.add().name = 'sink'
    expanded = expected_conn.connected.expanded.add()
    expanded.link_port.ref.steps.add().name = 'test_net'
    expanded.link_port.ref.steps.add().name = 'sinks'
    expanded.link_port.ref.steps.add().name = '1'
    expanded.block_port.ref.steps.add().name = 'sink2'
    expanded.block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, constraints)

  def test_exported_hierarchy(self):
    compiled_design = ScalaCompiler.compile(ExportPortHierarchyBlockTop)
    self.assertEqual(compiled_design.contents.blocks[0].name, 'block')
    pb = compiled_design.contents.blocks[0].value.hierarchy

    self.assertEqual(pb.self_class.target.name, 'edg.core.test_hierarchy_block.ExportPortHierarchyBlock')

    self.assertEqual(len(pb.ports), 1)
    self.assertEqual(pb.ports[0].name, 'exported')
    self.assertEqual(pb.ports[0].value.port.self_class.target.name,
                     'edg.core.test_common.TestPortSink')

    self.assertEqual(len(pb.blocks), 1)
    self.assertEqual(pb.blocks[0].name, 'sink')
    self.assertEqual(pb.blocks[0].value.hierarchy.self_class.target.name,
                     'edg.core.test_common.TestBlockSink')
    self.assertEqual(pb.blocks[0].value.hierarchy.ports[0].name, 'sink')
    self.assertEqual(pb.blocks[0].value.hierarchy.ports[0].value.port.self_class.target.name,
                     'edg.core.test_common.TestPortSink')

    self.assertEqual(len(pb.links), 0)

    constraints = list(map(lambda pair: pair.value, pb.constraints))

    expected_conn = edgir.ValueExpr()
    expected_conn.exported.exterior_port.ref.steps.add().name = 'exported'
    expected_conn.exported.internal_block_port.ref.steps.add().name = 'sink'
    expected_conn.exported.internal_block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, constraints)

  def test_bridge_hierarchy(self):
    compiled_design = ScalaCompiler.compile(PortBridgeHierarchyBlockTop)
    self.assertEqual(compiled_design.contents.blocks[0].name, 'block')
    pb = compiled_design.contents.blocks[0].value.hierarchy

    self.assertEqual(pb.self_class.target.name, 'edg.core.test_hierarchy_block.PortBridgeHierarchyBlock')

    self.assertEqual(len(pb.ports), 1)
    self.assertEqual(pb.ports[0].name, 'source_port')
    self.assertEqual(pb.ports[0].value.port.self_class.target.name,
                     "edg.core.test_common.TestPortSink")

    self.assertEqual(len(pb.blocks), 3)
    self.assertEqual(pb.blocks[0].name, 'sink1')
    self.assertEqual(pb.blocks[0].value.hierarchy.self_class.target.name,
                     'edg.core.test_common.TestBlockSink')
    self.assertEqual(pb.blocks[0].value.hierarchy.ports[0].name, 'sink')
    self.assertEqual(pb.blocks[0].value.hierarchy.ports[0].value.port.self_class.target.name,
                     'edg.core.test_common.TestPortSink')

    self.assertEqual(pb.blocks[1].name, 'sink2')
    self.assertEqual(pb.blocks[1].value.hierarchy.self_class.target.name,
                     'edg.core.test_common.TestBlockSink')
    self.assertEqual(pb.blocks[1].value.hierarchy.ports[0].name, 'sink')
    self.assertEqual(pb.blocks[1].value.hierarchy.ports[0].value.port.self_class.target.name,
                     'edg.core.test_common.TestPortSink')

    self.assertEqual(pb.blocks[2].name, '(bridge)source_port')
    self.assertEqual(pb.blocks[2].value.hierarchy.self_class.target.name,
                     'edg.core.test_common.TestPortBridge')
    self.assertEqual(pb.blocks[2].value.hierarchy.ports[0].name, 'outer_port')
    self.assertEqual(pb.blocks[2].value.hierarchy.ports[0].value.port.self_class.target.name,
                     "edg.core.test_common.TestPortSink")
    self.assertEqual(pb.blocks[2].value.hierarchy.ports[1].name, 'inner_link')
    self.assertEqual(pb.blocks[2].value.hierarchy.ports[1].value.port.self_class.target.name,
                     "edg.core.test_common.TestPortSource")

    self.assertEqual(len(pb.links), 1)
    self.assertEqual(pb.links[0].name, 'test_net')
    self.assertEqual(pb.links[0].value.link.self_class.target.name, 'edg.core.test_common.TestLink')
    self.assertEqual(pb.links[0].value.link.ports[0].name, 'source')
    self.assertEqual(pb.links[0].value.link.ports[0].value.port.self_class.target.name,
                     "edg.core.test_common.TestPortSource")
    self.assertEqual(pb.links[0].value.link.ports[1].name, 'sinks')
    self.assertEqual(pb.links[0].value.link.ports[1].value.array.ports.ports[0].name, '0')
    self.assertEqual(pb.links[0].value.link.ports[1].value.array.ports.ports[0].value.port.self_class.target.name,
                     "edg.core.test_common.TestPortSink")
    self.assertEqual(pb.links[0].value.link.ports[1].value.array.ports.ports[1].name, '1')
    self.assertEqual(pb.links[0].value.link.ports[1].value.array.ports.ports[1].value.port.self_class.target.name,
                     "edg.core.test_common.TestPortSink")

    constraints = list(map(lambda pair: pair.value, pb.constraints))

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'source'
    expected_conn.connected.block_port.ref.steps.add().name = '(bridge)source_port'
    expected_conn.connected.block_port.ref.steps.add().name = 'inner_link'
    self.assertIn(expected_conn, constraints)

    expected_conn = edgir.ValueExpr()
    expected_conn.exported.exterior_port.ref.steps.add().name = 'source_port'
    expected_conn.exported.internal_block_port.ref.steps.add().name = '(bridge)source_port'
    expected_conn.exported.internal_block_port.ref.steps.add().name = 'outer_port'
    self.assertIn(expected_conn, constraints)

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().allocate = ''
    expected_conn.connected.block_port.ref.steps.add().name = 'sink1'
    expected_conn.connected.block_port.ref.steps.add().name = 'sink'
    expanded = expected_conn.connected.expanded.add()
    expanded.link_port.ref.steps.add().name = 'test_net'
    expanded.link_port.ref.steps.add().name = 'sinks'
    expanded.link_port.ref.steps.add().name = '0'
    expanded.block_port.ref.steps.add().name = 'sink1'
    expanded.block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, constraints)

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().allocate = ''
    expected_conn.connected.block_port.ref.steps.add().name = 'sink2'
    expected_conn.connected.block_port.ref.steps.add().name = 'sink'
    expanded = expected_conn.connected.expanded.add()
    expanded.link_port.ref.steps.add().name = 'test_net'
    expanded.link_port.ref.steps.add().name = 'sinks'
    expanded.link_port.ref.steps.add().name = '1'
    expanded.block_port.ref.steps.add().name = 'sink2'
    expanded.block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, constraints)
