import unittest

import edgir
from . import *
from .test_common import TestBlockSource, TestBlockSink, TestPortSink, TestPortSource


class AdapterLink(Link):
  def __init__(self):
    super().__init__()
    
    self.ports = self.Port(Vector(AdapterPort()))


class AdapterPortAdapter(PortAdapter[TestPortSource]):
  def __init__(self):
    super().__init__()

    self.src = self.Port(AdapterPort())
    self.dst = self.Port(TestPortSource())


class AdapterPort(Port[AdapterLink]):
  link_type = AdapterLink

  def as_test_src(self) -> TestPortSource:
    return self._convert(AdapterPortAdapter())


class AdapterBlock(Block):
  def __init__(self):
    super().__init__()
    self.port = self.Port(AdapterPort())


class AdapterTestTop(Block):
  def __init__(self):
    super().__init__()

    self.adapter_src = self.Block(AdapterBlock())
    self.sink = self.Block(TestBlockSink())
    self.test_net = self.connect(self.adapter_src.port.as_test_src(), self.sink.sink)


class ImplicitConnectTestCase(unittest.TestCase):
  def test_connectivity(self) -> None:
    pb = AdapterTestTop()._elaborated_def_to_proto()
    adapter_pb = edgir.pair_get(pb.blocks, '(adapter)adapter_src.port')

    self.assertEqual(adapter_pb.lib_elem.base.target.name, "edg_core.test_port_adapter.AdapterPortAdapter")
    # ignore the other blocks

    self.assertEqual(len(pb.constraints), 4)
    constraints = list(map(lambda pair: pair.value, pb.constraints))

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.block_port.ref.steps.add().name = '(adapter)adapter_src.port'
    expected_conn.connected.block_port.ref.steps.add().name = 'dst'
    expected_conn.connected.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'source'
    self.assertIn(expected_conn, constraints)

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = 'test_net'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().allocate = ''
    expected_conn.connected.block_port.ref.steps.add().name = 'sink'
    expected_conn.connected.block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, constraints)

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.block_port.ref.steps.add().name = 'adapter_src'
    expected_conn.connected.block_port.ref.steps.add().name = 'port'
    expected_conn.connected.link_port.ref.steps.add().name = '_adapter_src_port_link'  # anonymous
    expected_conn.connected.link_port.ref.steps.add().name = 'ports'
    expected_conn.connected.link_port.ref.steps.add().allocate = ''
    self.assertIn(expected_conn, constraints)

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.link_port.ref.steps.add().name = '_adapter_src_port_link'  # anonymous
    expected_conn.connected.link_port.ref.steps.add().name = 'ports'
    expected_conn.connected.block_port.ref.steps.add().name = '(adapter)adapter_src.port'
    expected_conn.connected.block_port.ref.steps.add().name = 'src'
    expected_conn.connected.link_port.ref.steps.add().allocate = ''
    self.assertIn(expected_conn, constraints)
