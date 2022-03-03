import unittest

import edgir
from . import *
from .test_elaboration_common import TestPortSink, TestBlockSink, TestBlockSource


@abstract_block
class TestBlockPortVectorBase(Block):
  def __init__(self) -> None:
    super().__init__()
    self.vector = self.Port(Vector(TestPortSink()), optional=True)  # avoid required constraint


class TestBlockPortVectorConcrete(TestBlockPortVectorBase):
  def __init__(self) -> None:
    super().__init__()
    self.vector.init_elts(2)


class TestBlockPortVectorExport(TestBlockPortVectorBase):
  def __init__(self) -> None:
    super().__init__()
    self.vector.init_elts(2)
    vector_elts = list(self.vector.elts().values())
    assert len(vector_elts) == 2
    self.block0 = self.Block(TestBlockSink())
    self.exported0 = self.connect(self.block0.sink, vector_elts[0])
    self.block1 = self.Block(TestBlockSink())
    self.exported1 = self.connect(self.block1.sink, vector_elts[1])


class TestBlockPortVectorConnect(Block):
  def __init__(self) -> None:
    super().__init__()
    self.sink = self.Block(TestBlockPortVectorBase())
    self.source0 = self.Block(TestBlockSource())
    self.source1 = self.Block(TestBlockSource())
    self.conn0 = self.connect(self.source0.source, self.sink.vector.allocate())
    self.conn1 = self.connect(self.source1.source, self.sink.vector.allocate())


class BlockVectorBaseProtoTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = TestBlockPortVectorBase()._elaborated_def_to_proto()

  def test_port_def(self) -> None:
    self.assertEqual(len(self.pb.ports), 1)
    self.assertEqual(self.pb.ports['vector'].array.self_class.target.name, "edg_core.test_elaboration_common.TestPortSink")

  def test_port_init(self) -> None:
    self.assertEqual(len(self.pb.constraints), 0)  # no constraints should generate


class BlockVectorProtoTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = TestBlockPortVectorConcrete()._elaborated_def_to_proto()

  def test_port_def(self) -> None:
    self.assertEqual(len(self.pb.ports), 1)
    self.assertEqual(self.pb.ports['vector'].array.self_class.target.name, "edg_core.test_elaboration_common.TestPortSink")
    array_ports = self.pb.ports['vector'].array.ports
    self.assertEqual(len(array_ports), 2)
    self.assertEqual(array_ports['0'].lib_elem.target.name, "edg_core.test_elaboration_common.TestPortSink")
    self.assertEqual(array_ports['1'].lib_elem.target.name, "edg_core.test_elaboration_common.TestPortSink")


class VectorExportProtoTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = TestBlockPortVectorExport()._elaborated_def_to_proto()

  def test_export(self) -> None:
    self.assertEqual(len(self.pb.constraints), 2)

    expected_conn = edgir.ValueExpr()
    expected_conn.exported.exterior_port.ref.steps.add().name = 'vector'
    expected_conn.exported.exterior_port.ref.steps.add().name = '0'
    expected_conn.exported.internal_block_port.ref.steps.add().name = 'block0'
    expected_conn.exported.internal_block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, self.pb.constraints.values())

    expected_conn = edgir.ValueExpr()
    expected_conn.exported.exterior_port.ref.steps.add().name = 'vector'
    expected_conn.exported.exterior_port.ref.steps.add().name = '1'
    expected_conn.exported.internal_block_port.ref.steps.add().name = 'block1'
    expected_conn.exported.internal_block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, self.pb.constraints.values())


class VectorConnectProtoTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = TestBlockPortVectorConnect()._elaborated_def_to_proto()

  def test_export(self) -> None:
    self.assertEqual(len(self.pb.constraints), 2)

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.block_port.ref.steps.add().name = 'sink'
    expected_conn.connected.block_port.ref.steps.add().name = 'vector'
    expected_conn.connected.block_port.ref.steps.add().reserved_param = edgir.Reserved.ALLOCATE
    expected_conn.connected.link_port.ref.steps.add().name = 'conn0'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().reserved_param = edgir.Reserved.ALLOCATE
    self.assertIn(expected_conn, self.pb.constraints.values())

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.block_port.ref.steps.add().name = 'source0'
    expected_conn.connected.block_port.ref.steps.add().name = 'source'
    expected_conn.connected.link_port.ref.steps.add().name = 'conn0'
    expected_conn.connected.link_port.ref.steps.add().name = 'source'
    self.assertIn(expected_conn, self.pb.constraints.values())

    raise NotImplementedError  # repeat for elt1
