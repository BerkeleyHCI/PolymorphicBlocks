import unittest

import edgir
from . import *
from .test_elaboration_common import TestPortSink, TestBlockSink


@abstract_block
class TestBlockPortVectorBase(Block):
  def __init__(self) -> None:
    super().__init__()
    self.vector = self.Port(Vector(TestPortSink()))


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
    self.block1 = self.Block(TestBlockSink())
    self.connect(self.block1.sink, vector_elts[0])
    self.block2 = self.Block(TestBlockSink())
    self.connect(self.block2.sink, vector_elts[1])


class BlockVectorBaseProtoTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = TestBlockPortVectorBase()._elaborated_def_to_proto()

  def test_port_def(self) -> None:
    self.assertEqual(len(self.pb.ports), 1)
    self.assertEqual(self.pb.ports['vector'].array.self_class.target.name, "edg_core.test_elaboration_common.TestPortSink")

  def test_port_init(self) -> None:
    self.assertEqual(len(self.pb.constraints), 1)
    self.assertIn('(reqd)vector', self.pb.constraints)  # only required constraint should generate


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
    self.assertEqual(len(self.pb.constraints), 3)  # including required
