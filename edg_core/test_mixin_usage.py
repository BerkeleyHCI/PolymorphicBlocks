import unittest

import edgir
from . import *
from .test_common import TestBlockSource
from .test_mixin import TestMixin, TestMixinBase, TestMixinConcreteBlock


class BadMixinUsageTestCase(unittest.TestCase):
  class MixinBlock(Block):
    def contents(self) -> None:
      super().contents()

      self.block = self.Block(TestMixinBase())

      self.base_source = self.Block(TestBlockSource())
      self.block_net = self.connect(self.block.base_port, self.base_source.source)

      self.mixin = self.block.with_mixin(TestMixin())
      self.mixin_source = self.Block(TestBlockSource())
      self.mixin_net = self.connect(self.mixin.mixin_port, self.mixin_source.source)

  def setUp(self) -> None:
    self.pb = self.MixinBlock()._elaborated_def_to_proto()

  def test_subblock_def(self) -> None:
    self.assertEqual(self.pb.blocks[0].name, 'block')
    self.assertEqual(self.pb.blocks[0].value.lib_elem.base.target.name, "edg_core.test_mixin.TestMixinBase")
    self.assertEqual(self.pb.blocks[0].value.lib_elem.base.target.name, "edg_core.test_mixin.TestMixin")

  def test_connectivity(self) -> None:
    self.assertEqual(len(self.pb.constraints), 5)  # 4 connections + 1 initializer
    constraints = list(map(lambda pair: pair.value, self.pb.constraints))

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'block_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'source'
    expected_conn.connected.block_port.ref.steps.add().name = 'base_source'
    expected_conn.connected.block_port.ref.steps.add().name = 'source'
    self.assertIn(expected_conn, constraints)

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'block_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().allocate = ''
    expected_conn.connected.block_port.ref.steps.add().name = 'block'
    expected_conn.connected.block_port.ref.steps.add().name = 'base_port'
    self.assertIn(expected_conn, constraints)

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'mixin_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'source'
    expected_conn.connected.block_port.ref.steps.add().name = 'mixin_source'
    expected_conn.connected.block_port.ref.steps.add().name = 'source'
    self.assertIn(expected_conn, constraints)

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'mixin_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().allocate = ''
    expected_conn.connected.block_port.ref.steps.add().name = 'block'
    expected_conn.connected.block_port.ref.steps.add().name = 'mixin_port'
    self.assertIn(expected_conn, constraints)

  def test_initializer(self) -> None:
    constraints = list(map(lambda pair: pair.value, self.pb.constraints))

    # default assignment
    self.assertIn(edgir.AssignLit(['block', 'mixin_float'], 1.0), constraints)
