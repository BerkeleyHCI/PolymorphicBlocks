import unittest

from .. import edgir
from . import *
from .test_common import TestBlockSource, TestBlockSink, TestPortSink, ImplicitSink, TestBlockImplicitSink
from .HdlUserExceptions import EdgContextError


class ImplicitConnectBlock(Block):
  """Block with implicit scope containing some blocks"""
  def contents(self) -> None:
    super().contents()
    self.block_source = self.Block(TestBlockSource())
    self.implicit_net = self.connect(self.block_source.source)  # TODO better syntax for naming

    with self.implicit_connect(
      ImplicitConnect(self.block_source.source, [ImplicitSink])
    ) as imp:
      self.imp_block_sink = imp.Block(TestBlockImplicitSink())  # should have implicit connect
      self.int_block_sink = imp.Block(TestBlockSink())  # should not have implicit connect (untagged)
      self.int_block_source = imp.Block(TestBlockSource())  # should not have implicit connect


class ImplicitConnectTestCase(unittest.TestCase):
  def test_connectivity(self) -> None:
    pb = ImplicitConnectBlock()._elaborated_def_to_proto()

    self.assertEqual(len(pb.constraints), 2)
    constraints = list(map(lambda pair: pair.value, pb.constraints))

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'implicit_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().allocate = ''
    expected_conn.connected.block_port.ref.steps.add().name = 'imp_block_sink'
    expected_conn.connected.block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, constraints)

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'implicit_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'source'
    expected_conn.connected.block_port.ref.steps.add().name = 'block_source'
    expected_conn.connected.block_port.ref.steps.add().name = 'source'
    self.assertIn(expected_conn, constraints)


class ExportedImplicitConnectBlock(Block):
  """Block with implicit external port that is bridged"""
  def __init__(self) -> None:
    super().__init__()
    self.sink_in = self.Port(TestPortSink())

  def contents(self) -> None:
    super().contents()
    self.implicit_net = self.connect(self.sink_in)
    with self.implicit_connect(
      ImplicitConnect(self.sink_in, [ImplicitSink])
    ) as imp:
      # Note, we have two so this generates as a link instead of export
      self.block_sink_0 = imp.Block(TestBlockImplicitSink())  # should have implicit connect
      self.block_sink_1 = imp.Block(TestBlockImplicitSink())  # should have implicit connect
      self.block_sink_2 = imp.Block(TestBlockSink())  # should not have implicit connect (untagged)
      self.block_source = imp.Block(TestBlockSource())  # should not have implicit connect


class ExportedImplicitConnectTestCase(unittest.TestCase):
  def test_connectivity(self) -> None:
    pb = ExportedImplicitConnectBlock()._elaborated_def_to_proto()

    self.assertEqual(len(pb.constraints), 5)  # including source export, connect, port required
    constraints = list(map(lambda pair: pair.value, pb.constraints))

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'implicit_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().allocate = ''
    expected_conn.connected.block_port.ref.steps.add().name = 'block_sink_0'
    expected_conn.connected.block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, constraints)

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'implicit_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().allocate = ''
    expected_conn.connected.block_port.ref.steps.add().name = 'block_sink_1'
    expected_conn.connected.block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, constraints)


class ImplicitConnectOutsideScopeErrorBlock(Block):
  """Block with implicit scope containing some blocks"""
  def contents(self) -> None:
    super().contents()
    self.block_source = self.Block(TestBlockSource())

    with self.implicit_connect(
            ImplicitConnect(self.block_source.source, [ImplicitSink])
    ) as imp:
      pass

    self.imp_block_sink = imp.Block(TestBlockImplicitSink())  # should have implicit connect


class ImplicitConnectOutsideScopeErrorTestCase(unittest.TestCase):
  def test_error(self) -> None:
    with self.assertRaises(EdgContextError) as context:
      ImplicitConnectOutsideScopeErrorBlock()._elaborated_def_to_proto()
