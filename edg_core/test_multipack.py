import unittest

import edgir
from . import *
from .test_elaboration_common import TestPortSink, TestBlockSink, TestBlockSource


class MultipackBlockSink(MultipackBlock):
  """Unlike a real multipack block, this is simplified and has no implementation."""
  def __init__(self):
    super().__init__()
    self.sink_port1 = self.Port(TestPortSink())
    self.sink_port2 = self.Port(TestPortSink())
    self.sink1 = self.PackedPart(TestBlockSink())
    self.sink2 = self.PackedPart(TestBlockSink())
    self.packed_connect(self.sink_port1, self.sink1.sink)
    self.packed_connect(self.sink_port2, self.sink2.sink)


class TestBlockContainerSink(Block):
  def __init__(self) -> None:
    super().__init__()
    self.inner = self.Block(TestBlockSink())
    self.sink = self.Export(self.inner.sink)


class TopMultipackDesign(DesignTop):
  def contents(self):
    super().contents()
    self.source = self.Block(TestBlockSource())
    self.sink1 = self.Block(TestBlockSink())
    self.sink2 = self.Block(TestBlockContainerSink())

    self.connect(self.source.source, self.sink1.sink, self.sink2.sink)

  def multipack(self):
    self.packed = self.Block(MultipackBlockSink())
    self.pack(self.packed.sink1, ['sink1'])
    self.pack(self.packed.sink2, ['sink2', 'inner'])


class TopMultipackDesignTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = TopMultipackDesign()._elaborated_def_to_proto()

  def test_export_tunnel(self) -> None:
    self.assertEqual(len(self.pb.constraints), 4)
