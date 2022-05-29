import unittest

import edgir
from . import *
from .test_elaboration_common import TestPortSink, TestBlockSink, TestBlockSource


class PartSink(Block):
  def __init__(self) -> None:
    super().__init__()
    self.param = self.Parameter(FloatExpr())
    self.sink = self.Port(TestPortSink(), optional=True)


class MultipackBlockSink(MultipackBlock):
  """Unlike a real multipack block, this is simplified and has no implementation."""
  def __init__(self):
    super().__init__()
    self.sink_port1 = self.Port(TestPortSink())
    self.sink_port2 = self.Port(TestPortSink())
    self.param1 = self.Parameter(FloatExpr())
    self.param2 = self.Parameter(FloatExpr())
    self.sink1 = self.PackedPart(PartSink())
    self.sink2 = self.PackedPart(PartSink())
    self.packed_connect(self.sink_port1, self.sink1.sink)
    self.packed_connect(self.sink_port2, self.sink2.sink)
    self.packed_assign(self.param1, self.sink1.param)
    self.packed_assign(self.param2, self.sink2.param)


class TestBlockContainerSink(Block):
  def __init__(self) -> None:
    super().__init__()
    self.inner = self.Block(PartSink())
    self.param = self.Parameter(FloatExpr())
    self.sink = self.Export(self.inner.sink)
    self.assign(self.inner.param, self.param)


class TopMultipackDesign(DesignTop):
  def contents(self):
    super().contents()
    self.source = self.Block(TestBlockSource())
    self.sink1 = self.Block(PartSink())
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
    expected_constr = edgir.ValueExpr()

    expected_constr.exportedTunnel.internal_block_port.ref.steps.add().name = 'packed'
    expected_constr.exportedTunnel.internal_block_port.ref.steps.add().name = 'sink_port1'
    expected_constr.exportedTunnel.exterior_port.ref.steps.add().name = 'sink1'
    expected_constr.exportedTunnel.exterior_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_constr, self.pb.constraints.values())

    expected_constr.assignTunnel.dst.steps.add().name = 'packed'
    expected_constr.assignTunnel.dst.steps.add().name = 'param1'
    expected_constr.assignTunnel.src.ref.steps.add().name = 'sink1'
    expected_constr.assignTunnel.src.ref.steps.add().name = 'param'
    self.assertIn(expected_constr, self.pb.constraints.values())

    expected_constr.exportedTunnel.internal_block_port.ref.steps.add().name = 'packed'
    expected_constr.exportedTunnel.internal_block_port.ref.steps.add().name = 'sink_port2'
    expected_constr.exportedTunnel.exterior_port.ref.steps.add().name = 'sink2'
    expected_constr.exportedTunnel.exterior_port.ref.steps.add().name = 'inner'
    expected_constr.exportedTunnel.exterior_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_constr, self.pb.constraints.values())

    expected_constr.assignTunnel.dst.steps.add().name = 'packed'
    expected_constr.assignTunnel.dst.steps.add().name = 'param2'
    expected_constr.assignTunnel.src.ref.steps.add().name = 'sink2'
    expected_constr.assignTunnel.src.ref.steps.add().name = 'inner'
    expected_constr.assignTunnel.src.ref.steps.add().name = 'param'
    self.assertIn(expected_constr, self.pb.constraints.values())
