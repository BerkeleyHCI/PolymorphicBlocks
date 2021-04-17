from typing import *
import unittest

from . import *
from .test_common import TestBlockSource, TestBlockSink, TestPortSink, TestPortSource


class TestBlockChainOutput(Block):
  def __init__(self) -> None:
    super().__init__()
    self.source = self.Port(TestPortSource(), [Output])


class TestBlockChainInOut(Block):
  def __init__(self) -> None:
    super().__init__()
    self.sink = self.Port(TestPortSink(), [InOut])


class TestBlockChainInputOutput(Block):
  def __init__(self) -> None:
    super().__init__()
    self.sink = self.Port(TestPortSink(), [Input])
    self.source = self.Port(TestPortSource(), [Output])


class TestBlockChainInput(Block):
  def __init__(self) -> None:
    super().__init__()
    self.sink = self.Port(TestPortSink(), [Input])


class ChainConnectUnpackNamedBlock(Block):
  """Block with chain connect, where those blocks are declared inline and named by unpack"""
  def contents(self) -> None:
    super().contents()
    (self.output, self.inout, self.inputoutput, self.input), self.test_chain = self.chain(
      self.Block(TestBlockChainOutput()),
      self.Block(TestBlockChainInOut()),
      self.Block(TestBlockChainInputOutput()),
      self.Block(TestBlockChainInput())
    )


class ChainConnectExplicitNamedBlock(Block):
  """Block with chain connect, where those blocks are explicitly (separately) declared and named"""
  def contents(self) -> None:
    super().contents()
    self.output = self.Block(TestBlockChainOutput())
    self.inout = self.Block(TestBlockChainInOut())
    self.inputoutput = self.Block(TestBlockChainInputOutput())
    self.input = self.Block(TestBlockChainInput())

    self.test_chain = self.chain(
      self.output,
      self.inout,
      self.inputoutput,
      self.input
    )


class ImplicitConnectTestCase(unittest.TestCase):
  def verify_pb(self, pb: edgir.HierarchyBlock) -> None:
    self.assertEqual(len(pb.constraints), 5)  # including source export, connect, port required

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'test_chain_0'
    expected_conn.connected.link_port.ref.steps.add().name = 'source'
    expected_conn.connected.block_port.ref.steps.add().name = 'output'
    expected_conn.connected.block_port.ref.steps.add().name = 'source'
    self.assertIn(expected_conn, pb.constraints.values())

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'test_chain_0'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().reserved_param = edgir.ALLOCATE
    expected_conn.connected.block_port.ref.steps.add().name = 'inout'
    expected_conn.connected.block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, pb.constraints.values())

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'test_chain_0'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().reserved_param = edgir.ALLOCATE
    expected_conn.connected.block_port.ref.steps.add().name = 'inputoutput'
    expected_conn.connected.block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, pb.constraints.values())

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'test_chain_1'
    expected_conn.connected.link_port.ref.steps.add().name = 'source'
    expected_conn.connected.block_port.ref.steps.add().name = 'inputoutput'
    expected_conn.connected.block_port.ref.steps.add().name = 'source'
    self.assertIn(expected_conn, pb.constraints.values())

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'test_chain_1'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().reserved_param = edgir.ALLOCATE
    expected_conn.connected.block_port.ref.steps.add().name = 'input'
    expected_conn.connected.block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, pb.constraints.values())

  def test_explicit_named_chain(self) -> None:
    pb = ChainConnectExplicitNamedBlock()._elaborated_def_to_proto()
    self.verify_pb(pb)

  def test_unpack_named_chain(self) -> None:
    pb = ChainConnectUnpackNamedBlock()._elaborated_def_to_proto()
    self.verify_pb(pb)
