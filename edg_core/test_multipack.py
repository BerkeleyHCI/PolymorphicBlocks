import unittest

import edgir
from . import *
from .test_elaboration_common import TestPortSink, TestBlockSink, TestBlockSource


class PartSink(Block):
  def __init__(self) -> None:
    super().__init__()
    self.param = self.Parameter(FloatExpr())
    self.result_param = self.Parameter(IntExpr())
    self.sink = self.Port(TestPortSink(), optional=True)


class MultipackBlockSink(MultipackBlock):
  """Unlike a real multipack block, this is simplified and has no implementation."""
  def __init__(self):
    super().__init__()

    self.sink1 = self.PackedPart(PartSink())
    self.sink2 = self.PackedPart(PartSink())
    self.sink_port1 = self.PackedExport(self.sink1.sink)
    self.sink_port2 = self.PackedExport(self.sink2.sink)
    self.param1 = self.PackedParameter(self.sink1.param)
    self.param2 = self.PackedParameter(self.sink2.param)

    self.result_param = self.Parameter(IntExpr())
    self.unpacked_assign(self.sink1.result_param, self.result_param)
    self.unpacked_assign(self.sink2.result_param, self.result_param)


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
    self.sink1 = self.Block(PartSink())
    self.sink2 = self.Block(TestBlockContainerSink())

  def multipack(self):
    self.packed = self.Block(MultipackBlockSink())
    self.pack(self.packed.sink1, ['sink1'])
    self.pack(self.packed.sink2, ['sink2', 'inner'])


class TopMultipackDesignTestCase(unittest.TestCase):
  def setUp(self) -> None:
    pb = TopMultipackDesign()._elaborated_def_to_proto()
    self.constraints = list(map(lambda pair: pair.value, pb.constraints))

  def test_constraints_count(self) -> None:  # so individual cases (export / assigns) can still pass
    self.assertEqual(len(self.constraints), 6)

  def test_export_tunnel(self) -> None:
    expected_constr = edgir.ValueExpr()
    expected_constr.exportedTunnel.internal_block_port.ref.steps.add().name = 'packed'
    expected_constr.exportedTunnel.internal_block_port.ref.steps.add().name = 'sink_port1'
    expected_constr.exportedTunnel.exterior_port.ref.steps.add().name = 'sink1'
    expected_constr.exportedTunnel.exterior_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_constr, self.constraints)

    expected_constr = edgir.ValueExpr()
    expected_constr.exportedTunnel.internal_block_port.ref.steps.add().name = 'packed'
    expected_constr.exportedTunnel.internal_block_port.ref.steps.add().name = 'sink_port2'
    expected_constr.exportedTunnel.exterior_port.ref.steps.add().name = 'sink2'
    expected_constr.exportedTunnel.exterior_port.ref.steps.add().name = 'inner'
    expected_constr.exportedTunnel.exterior_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_constr, self.constraints)

  def test_assign_tunnel(self) -> None:
    expected_constr = edgir.ValueExpr()
    expected_constr.assignTunnel.dst.steps.add().name = 'packed'
    expected_constr.assignTunnel.dst.steps.add().name = 'param1'
    expected_constr.assignTunnel.src.ref.steps.add().name = 'sink1'
    expected_constr.assignTunnel.src.ref.steps.add().name = 'param'
    self.assertIn(expected_constr, self.constraints)

    expected_constr = edgir.ValueExpr()
    expected_constr.assignTunnel.dst.steps.add().name = 'packed'
    expected_constr.assignTunnel.dst.steps.add().name = 'param2'
    expected_constr.assignTunnel.src.ref.steps.add().name = 'sink2'
    expected_constr.assignTunnel.src.ref.steps.add().name = 'inner'
    expected_constr.assignTunnel.src.ref.steps.add().name = 'param'
    self.assertIn(expected_constr, self.constraints)

  def test_assign_unpacked_tunnel(self) -> None:
    expected_constr = edgir.ValueExpr()
    expected_constr.assignTunnel.dst.steps.add().name = 'sink1'
    expected_constr.assignTunnel.dst.steps.add().name = 'result_param'
    expected_constr.assignTunnel.src.ref.steps.add().name = 'packed'
    expected_constr.assignTunnel.src.ref.steps.add().name = 'result_param'
    self.assertIn(expected_constr, self.constraints)

    expected_constr = edgir.ValueExpr()
    expected_constr.assignTunnel.dst.steps.add().name = 'sink2'
    expected_constr.assignTunnel.dst.steps.add().name = 'inner'
    expected_constr.assignTunnel.dst.steps.add().name = 'result_param'
    expected_constr.assignTunnel.src.ref.steps.add().name = 'packed'
    expected_constr.assignTunnel.src.ref.steps.add().name = 'result_param'
    self.assertIn(expected_constr, self.constraints)


class MultipackArrayBlockSink(MultipackBlock):
  """Same as above, but with array constructs."""
  def __init__(self):
    super().__init__()
    self.sinks = self.PackedPart(PackedBlockArray(PartSink()))
    self.sink_ports = self.PackedExport(self.sinks.ports_array(lambda x: x.sink))
    self.params = self.PackedParameter(self.sinks.params_array(lambda x: x.param))

    self.result_param = self.Parameter(IntExpr())
    self.unpacked_assign(self.sinks.params(lambda x: x.result_param), self.result_param)


class TopMultipackArrayDesign(DesignTop):
  def contents(self):
    super().contents()
    self.sink1 = self.Block(PartSink())
    self.sink2 = self.Block(TestBlockContainerSink())

  def multipack(self):
    self.packed = self.Block(MultipackArrayBlockSink())
    self.pack(self.packed.sinks.request('1'), ['sink1'])
    self.pack(self.packed.sinks.request('2'), ['sink2', 'inner'])


class TopMultipackArrayDesignTestCase(unittest.TestCase):
  def setUp(self) -> None:
    pb = TopMultipackArrayDesign()._elaborated_def_to_proto()
    self.constraints = list(map(lambda pair: pair.value, pb.constraints))

  def test_constraints_count(self) -> None:  # so individual cases (export / assigns) can still pass
    self.assertEqual(len(self.constraints), 5)

  def test_export_tunnel(self) -> None:
    expected_constr = edgir.ValueExpr()
    expected_constr.exportedTunnel.internal_block_port.ref.steps.add().name = 'packed'
    expected_constr.exportedTunnel.internal_block_port.ref.steps.add().name = 'sink_ports'
    expected_constr.exportedTunnel.internal_block_port.ref.steps.add().allocate = '1'
    expected_constr.exportedTunnel.exterior_port.ref.steps.add().name = 'sink1'
    expected_constr.exportedTunnel.exterior_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_constr, self.constraints)

    expected_constr = edgir.ValueExpr()
    expected_constr.exportedTunnel.internal_block_port.ref.steps.add().name = 'packed'
    expected_constr.exportedTunnel.internal_block_port.ref.steps.add().name = 'sink_ports'
    expected_constr.exportedTunnel.internal_block_port.ref.steps.add().allocate = '2'
    expected_constr.exportedTunnel.exterior_port.ref.steps.add().name = 'sink2'
    expected_constr.exportedTunnel.exterior_port.ref.steps.add().name = 'inner'
    expected_constr.exportedTunnel.exterior_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_constr, self.constraints)

  def test_assign_tunnel(self) -> None:
    expected_constr = edgir.ValueExpr()
    expected_constr.assignTunnel.dst.steps.add().name = 'packed'
    expected_constr.assignTunnel.dst.steps.add().name = 'params'
    expected_array = expected_constr.assignTunnel.src.array
    expected_ref1 = expected_array.vals.add().ref
    expected_ref1.steps.add().name = 'sink1'
    expected_ref1.steps.add().name = 'param'
    expected_ref2 = expected_array.vals.add().ref
    expected_ref2.steps.add().name = 'sink2'
    expected_ref2.steps.add().name = 'inner'
    expected_ref2.steps.add().name = 'param'
    self.assertIn(expected_constr, self.constraints)

  def test_assign_unpacked_tunnel(self) -> None:
    expected_constr = edgir.ValueExpr()
    expected_constr.assignTunnel.dst.steps.add().name = 'sink1'
    expected_constr.assignTunnel.dst.steps.add().name = 'result_param'
    expected_constr.assignTunnel.src.ref.steps.add().name = 'packed'
    expected_constr.assignTunnel.src.ref.steps.add().name = 'result_param'
    self.assertIn(expected_constr, self.constraints)

    expected_constr = edgir.ValueExpr()
    expected_constr.assignTunnel.dst.steps.add().name = 'sink2'
    expected_constr.assignTunnel.dst.steps.add().name = 'inner'
    expected_constr.assignTunnel.dst.steps.add().name = 'result_param'
    expected_constr.assignTunnel.src.ref.steps.add().name = 'packed'
    expected_constr.assignTunnel.src.ref.steps.add().name = 'result_param'
    self.assertIn(expected_constr, self.constraints)