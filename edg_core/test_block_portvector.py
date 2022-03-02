import unittest

import edgir
from . import *
from .test_elaboration_common import TestPortBase


@abstract_block
class TestBlockPortVectorBase(Block):
  def __init__(self) -> None:
    super().__init__()
    self.vector = self.Port(Vector(TestPortBase()))


class TestBlockPortVectorConcrete(TestBlockPortVectorBase):
  def __init__(self) -> None:
    super().__init__()
    self.vector.init_elts(2)


class BlockBaseProtoTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = TestBlockPortVectorBase()._elaborated_def_to_proto()

  def test_port_def(self) -> None:
    self.assertEqual(len(self.pb.ports), 1)
    self.assertEqual(self.pb.ports['vector'].array.self_class.target.name, "edg_core.test_elaboration_common.TestPortBase")

  def test_port_init(self) -> None:
    self.assertEqual(len(self.pb.constraints), 1)
    self.assertIn('(reqd)vector', self.pb.constraints)  # only required constraint should generate


class BlockProtoTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = TestBlockPortVectorConcrete()._elaborated_def_to_proto()

  def test_port_def(self) -> None:
    self.assertEqual(len(self.pb.ports), 1)
    self.assertEqual(self.pb.ports['vector'].array.self_class.target.name, "edg_core.test_elaboration_common.TestPortBase")
    array_ports = self.pb.ports['vector'].array.ports
    self.assertEqual(len(array_ports), 2)
    self.assertEqual(array_ports['0'].lib_elem.target.name, "edg_core.test_elaboration_common.TestPortBase")
    self.assertEqual(array_ports['1'].lib_elem.target.name, "edg_core.test_elaboration_common.TestPortBase")
