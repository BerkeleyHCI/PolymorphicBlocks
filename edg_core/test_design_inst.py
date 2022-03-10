from typing import *
import unittest

import edgir
from . import *
from edg_core.ScalaCompilerInterface import ScalaCompiler
from .test_common import TestPortSource, TestPortSink, TestBlockSource
from .test_hierarchy_block import TopHierarchyBlock, ExportPortHierarchyBlock, PortBridgeHierarchyBlock
from . import test_common, test_hierarchy_block


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

    self.assertEqual(pb.self_class.target.name, 'edg_core.test_hierarchy_block.TopHierarchyBlock')

    self.assertEqual(len(pb.blocks), 3)

    self.assertEqual(pb.blocks['source'].hierarchy.self_class.target.name,
                     'edg_core.test_common.TestBlockSource')
    self.assertEqual(pb.blocks['source'].hierarchy.ports['source'].port.self_class.target.name,
                     'edg_core.test_common.TestPortSource')

    self.assertEqual(pb.blocks['sink1'].hierarchy.self_class.target.name,
                     'edg_core.test_common.TestBlockSink')
    self.assertEqual(pb.blocks['sink1'].hierarchy.ports['sink'].port.self_class.target.name,
                     'edg_core.test_common.TestPortSink')

    self.assertEqual(pb.blocks['sink2'].hierarchy.self_class.target.name,
                     'edg_core.test_common.TestBlockSink')
    self.assertEqual(pb.blocks['sink2'].hierarchy.ports['sink'].port.self_class.target.name,
                     'edg_core.test_common.TestPortSink')

    self.assertEqual(pb.links['test_net'].link.self_class.target.name, 'edg_core.test_common.TestLink')
    self.assertEqual(pb.links['test_net'].link.ports['source'].port.self_class.target.name,
                     "edg_core.test_common.TestPortSource")
    self.assertEqual(pb.links['test_net'].link.ports['sinks'].array.ports.ports['0'].port.self_class.target.name,
                     "edg_core.test_common.TestPortSink")
    self.assertEqual(pb.links['test_net'].link.ports['sinks'].array.ports.ports['1'].port.self_class.target.name,
                     "edg_core.test_common.TestPortSink")

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'source'
    expected_conn.connected.block_port.ref.steps.add().name = 'source'
    expected_conn.connected.block_port.ref.steps.add().name = 'source'
    self.assertIn(expected_conn, pb.constraints.values())

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().name = '0'
    expected_conn.connected.block_port.ref.steps.add().name = 'sink1'
    expected_conn.connected.block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, pb.constraints.values())

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().name = '1'
    expected_conn.connected.block_port.ref.steps.add().name = 'sink2'
    expected_conn.connected.block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, pb.constraints.values())

  def test_exported_hierarchy(self):
    compiled_design = ScalaCompiler.compile(ExportPortHierarchyBlockTop)
    pb = compiled_design.contents.blocks['block'].hierarchy

    self.assertEqual(pb.self_class.target.name, 'edg_core.test_hierarchy_block.ExportPortHierarchyBlock')

    self.assertEqual(len(pb.ports), 1)
    self.assertEqual(pb.ports['exported'].port.self_class.target.name,
                     'edg_core.test_common.TestPortSink')

    self.assertEqual(len(pb.blocks), 1)
    self.assertEqual(pb.blocks['sink'].hierarchy.self_class.target.name,
                     'edg_core.test_common.TestBlockSink')
    self.assertEqual(pb.blocks['sink'].hierarchy.ports['sink'].port.self_class.target.name,
                     'edg_core.test_common.TestPortSink')

    self.assertEqual(len(pb.links), 0)

    expected_conn = edgir.ValueExpr()
    expected_conn.exported.exterior_port.ref.steps.add().name = 'exported'
    expected_conn.exported.internal_block_port.ref.steps.add().name = 'sink'
    expected_conn.exported.internal_block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, pb.constraints.values())

  def test_bridge_hierarchy(self):
    compiled_design = ScalaCompiler.compile(PortBridgeHierarchyBlockTop)
    pb = compiled_design.contents.blocks['block'].hierarchy

    self.assertEqual(pb.self_class.target.name, 'edg_core.test_hierarchy_block.PortBridgeHierarchyBlock')

    self.assertEqual(len(pb.ports), 1)
    self.assertEqual(pb.ports['source_port'].port.self_class.target.name,
                     "edg_core.test_common.TestPortSink")

    self.assertEqual(len(pb.blocks), 3)
    self.assertEqual(pb.blocks['(bridge)source_port'].hierarchy.self_class.target.name,
                     'edg_core.test_common.TestPortBridge')
    self.assertEqual(pb.blocks['(bridge)source_port'].hierarchy.ports['inner_link'].port.self_class.target.name,
                     "edg_core.test_common.TestPortSource")
    self.assertEqual(pb.blocks['(bridge)source_port'].hierarchy.ports['outer_port'].port.self_class.target.name,
                     "edg_core.test_common.TestPortSink")

    self.assertEqual(pb.blocks['sink1'].hierarchy.self_class.target.name,
                     'edg_core.test_common.TestBlockSink')
    self.assertEqual(pb.blocks['sink1'].hierarchy.ports['sink'].port.self_class.target.name,
                     'edg_core.test_common.TestPortSink')
    self.assertEqual(pb.blocks['sink2'].hierarchy.self_class.target.name,
                     'edg_core.test_common.TestBlockSink')
    self.assertEqual(pb.blocks['sink2'].hierarchy.ports['sink'].port.self_class.target.name,
                     'edg_core.test_common.TestPortSink')

    self.assertEqual(len(pb.links), 1)
    self.assertEqual(pb.links['test_net'].link.self_class.target.name, 'edg_core.test_common.TestLink')
    self.assertEqual(pb.links['test_net'].link.ports['source'].port.self_class.target.name,
                     "edg_core.test_common.TestPortSource")
    self.assertEqual(pb.links['test_net'].link.ports['sinks'].array.ports.ports['0'].port.self_class.target.name,
                     "edg_core.test_common.TestPortSink")
    self.assertEqual(pb.links['test_net'].link.ports['sinks'].array.ports.ports['1'].port.self_class.target.name,
                     "edg_core.test_common.TestPortSink")

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'source'
    expected_conn.connected.block_port.ref.steps.add().name = '(bridge)source_port'
    expected_conn.connected.block_port.ref.steps.add().name = 'inner_link'
    self.assertIn(expected_conn, pb.constraints.values())

    expected_conn = edgir.ValueExpr()
    expected_conn.exported.exterior_port.ref.steps.add().name = 'source_port'
    expected_conn.exported.internal_block_port.ref.steps.add().name = '(bridge)source_port'
    expected_conn.exported.internal_block_port.ref.steps.add().name = 'outer_port'
    self.assertIn(expected_conn, pb.constraints.values())

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().name = '0'
    expected_conn.connected.block_port.ref.steps.add().name = 'sink1'
    expected_conn.connected.block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, pb.constraints.values())

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().name = '1'
    expected_conn.connected.block_port.ref.steps.add().name = 'sink2'
    expected_conn.connected.block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, pb.constraints.values())
