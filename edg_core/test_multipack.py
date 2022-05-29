import unittest

import edgir
from . import *
from .test_elaboration_common import TestPortSource, TestBlockSink, TestBlockSource


class MultipackBlockSource(MultipackBlock):
  """Unlike a real multipack block, this is simplified and has no implementation."""
  def __init__(self):
    super().__init__()
    self.source_port1 = self.Port(TestPortSource())
    self.source_port2 = self.Port(TestPortSource())
    self.source1 = self.PackedPart(TestBlockSource())
    self.source2 = self.PackedPart(TestBlockSource())
    self.packed_connect(self.source_port1, self.source1.source)
    self.packed_connect(self.source_port2, self.source2.source)


class TestBlockContainerSource(Block):
  def __init__(self) -> None:
    super().__init__()
    self.inner = self.Block(TestBlockSource())
    self.source = self.Export(self.inner.source)


class TopMultipackDesign(DesignTop):
  def contents(self):
    super().contents()

    self.source1 = self.Block(TestBlockSource())
    self.source2 = self.Block(TestBlockContainerSource())

  def multipack(self):
    self.packed = self.Block(MultipackBlockSource())
    self.pack(self.packed.source1, ['source1'])
    self.pack(self.packed.source2, ['source2', 'inner'])


class TopMultipackDesignTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = TopMultipackDesign()._elaborated_def_to_proto()

  def test_export_tunnel(self) -> None:
    self.assertEqual(len(self.pb.constraints), 4)
