import unittest

from .. import edgir
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
    self.vector.append_elt(TestPortSink())
    self.vector.append_elt(TestPortSink())


class TestBlockPortVectorEmpty(TestBlockPortVectorBase):
  def __init__(self) -> None:
    super().__init__()
    self.vector.defined()


class TestBlockPortVectorExport(TestBlockPortVectorBase):
  def __init__(self) -> None:
    super().__init__()
    vector0 = self.vector.append_elt(TestPortSink())
    vector1 = self.vector.append_elt(TestPortSink())
    self.block0 = self.Block(TestBlockSink())
    self.exported0 = self.connect(self.block0.sink, vector0)
    self.block1 = self.Block(TestBlockSink())
    self.exported1 = self.connect(self.block1.sink, vector1)


class TestBlockPortVectorBridged(TestBlockPortVectorBase):
  def __init__(self) -> None:
    super().__init__()
    vector_port = self.vector.append_elt(TestPortSink())
    self.block0 = self.Block(TestBlockSink())
    self.block1 = self.Block(TestBlockSink())
    self.conn = self.connect(self.block0.sink, self.block1.sink, vector_port)


class TestBlockPortVectorConnect(Block):
  def __init__(self) -> None:
    super().__init__()
    self.sink = self.Block(TestBlockPortVectorBase())
    self.source0 = self.Block(TestBlockSource())
    self.source1 = self.Block(TestBlockSource())
    self.conn0 = self.connect(self.source0.source, self.sink.vector.request())
    self.conn1 = self.connect(self.source1.source, self.sink.vector.request())


class TestBlockPortVectorConstraint(TestBlockPortVectorBase):
  def __init__(self) -> None:
    super().__init__()
    # check reduction ops work on block-side as well
    self.float_param_sink_sum = self.Parameter(FloatExpr(self.vector.sum(lambda p: p.float_param)))


class BlockVectorBaseProtoTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = TestBlockPortVectorBase()._elaborated_def_to_proto()

  def test_port_def(self) -> None:
    self.assertEqual(len(self.pb.ports), 1)
    self.assertEqual(self.pb.ports[0].name, 'vector')
    self.assertEqual(self.pb.ports[0].value.array.self_class.target.name, "edg.core.test_elaboration_common.TestPortSink")

  def test_port_init(self) -> None:
    self.assertEqual(len(self.pb.constraints), 0)  # no constraints should generate


class BlockVectorProtoTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = TestBlockPortVectorConcrete()._elaborated_def_to_proto()

  def test_port_def(self) -> None:
    self.assertEqual(len(self.pb.ports), 1)
    self.assertEqual(self.pb.ports[0].name, 'vector')
    self.assertEqual(self.pb.ports[0].value.array.self_class.target.name, "edg.core.test_elaboration_common.TestPortSink")
    array_ports = self.pb.ports[0].value.array.ports.ports
    self.assertEqual(len(array_ports), 2)
    self.assertEqual(array_ports[0].name, '0')
    self.assertEqual(array_ports[0].value.lib_elem.target.name, "edg.core.test_elaboration_common.TestPortSink")
    self.assertEqual(array_ports[1].name, '1')
    self.assertEqual(array_ports[1].value.lib_elem.target.name, "edg.core.test_elaboration_common.TestPortSink")


class BlockVectorEmptyProtoTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = TestBlockPortVectorEmpty()._elaborated_def_to_proto()

  def test_port_def(self) -> None:
    self.assertEqual(len(self.pb.ports), 1)
    self.assertEqual(self.pb.ports[0].value.array.self_class.target.name, "edg.core.test_elaboration_common.TestPortSink")
    self.assertTrue(self.pb.ports[0].value.array.HasField('ports'))
    array_ports = self.pb.ports[0].value.array.ports.ports
    self.assertEqual(len(array_ports), 0)


class VectorExportProtoTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = TestBlockPortVectorExport()._elaborated_def_to_proto()

  def test_export(self) -> None:
    self.assertEqual(len(self.pb.constraints), 2)
    constraints = list(map(lambda x: x.value, self.pb.constraints))

    expected_conn = edgir.ValueExpr()
    expected_conn.exported.exterior_port.ref.steps.add().name = 'vector'
    expected_conn.exported.exterior_port.ref.steps.add().name = '0'
    expected_conn.exported.internal_block_port.ref.steps.add().name = 'block0'
    expected_conn.exported.internal_block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, constraints)

    expected_conn = edgir.ValueExpr()
    expected_conn.exported.exterior_port.ref.steps.add().name = 'vector'
    expected_conn.exported.exterior_port.ref.steps.add().name = '1'
    expected_conn.exported.internal_block_port.ref.steps.add().name = 'block1'
    expected_conn.exported.internal_block_port.ref.steps.add().name = 'sink'
    self.assertIn(expected_conn, constraints)


class VectorBridgedProtoTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = TestBlockPortVectorBridged()._elaborated_def_to_proto()

  def test_bridged(self) -> None:
    self.assertEqual(len(self.pb.constraints), 4)
    constraints = list(map(lambda x: x.value, self.pb.constraints))

    expected_conn = edgir.ValueExpr()
    expected_conn.exported.exterior_port.ref.steps.add().name = 'vector'
    expected_conn.exported.exterior_port.ref.steps.add().name = '0'
    expected_conn.exported.internal_block_port.ref.steps.add().name = '(bridge)vector.0'
    expected_conn.exported.internal_block_port.ref.steps.add().name = 'outer_port'
    self.assertIn(expected_conn, constraints)

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.block_port.ref.steps.add().name = '(bridge)vector.0'
    expected_conn.connected.block_port.ref.steps.add().name = 'inner_link'
    expected_conn.connected.link_port.ref.steps.add().name = 'conn'
    expected_conn.connected.link_port.ref.steps.add().name = 'source'
    self.assertIn(expected_conn, constraints)

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.block_port.ref.steps.add().name = 'block0'
    expected_conn.connected.block_port.ref.steps.add().name = 'sink'
    expected_conn.connected.link_port.ref.steps.add().name = 'conn'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().allocate = ''
    self.assertIn(expected_conn, constraints)

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.block_port.ref.steps.add().name = 'block1'
    expected_conn.connected.block_port.ref.steps.add().name = 'sink'
    expected_conn.connected.link_port.ref.steps.add().name = 'conn'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().allocate = ''
    self.assertIn(expected_conn, constraints)


class VectorConnectProtoTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = TestBlockPortVectorConnect()._elaborated_def_to_proto()

  def test_export(self) -> None:
    self.assertEqual(len(self.pb.constraints), 4)
    constraints = list(map(lambda x: x.value, self.pb.constraints))

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.block_port.ref.steps.add().name = 'sink'
    expected_conn.connected.block_port.ref.steps.add().name = 'vector'
    expected_conn.connected.block_port.ref.steps.add().allocate = ''
    expected_conn.connected.link_port.ref.steps.add().name = 'conn0'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().allocate = ''
    self.assertIn(expected_conn, constraints)

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.block_port.ref.steps.add().name = 'source0'
    expected_conn.connected.block_port.ref.steps.add().name = 'source'
    expected_conn.connected.link_port.ref.steps.add().name = 'conn0'
    expected_conn.connected.link_port.ref.steps.add().name = 'source'
    self.assertIn(expected_conn, constraints)

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.block_port.ref.steps.add().name = 'sink'
    expected_conn.connected.block_port.ref.steps.add().name = 'vector'
    expected_conn.connected.block_port.ref.steps.add().allocate = ''
    expected_conn.connected.link_port.ref.steps.add().name = 'conn1'
    expected_conn.connected.link_port.ref.steps.add().name = 'sinks'
    expected_conn.connected.link_port.ref.steps.add().allocate = ''
    self.assertIn(expected_conn, constraints)

    expected_conn = edgir.ValueExpr()
    expected_conn.connected.block_port.ref.steps.add().name = 'source1'
    expected_conn.connected.block_port.ref.steps.add().name = 'source'
    expected_conn.connected.link_port.ref.steps.add().name = 'conn1'
    expected_conn.connected.link_port.ref.steps.add().name = 'source'
    self.assertIn(expected_conn, constraints)


class VectorConstraintProtoTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = TestBlockPortVectorConstraint()._elaborated_def_to_proto()

  def test_port_def(self) -> None:
    self.assertEqual(len(self.pb.constraints), 1)
    constraints = list(map(lambda x: x.value, self.pb.constraints))

    expected_constr = edgir.ValueExpr()
    expected_constr.assign.dst.steps.add().name = 'float_param_sink_sum'
    expected_constr.assign.src.unary_set.op = edgir.UnarySetExpr.SUM
    expected_constr.assign.src.unary_set.vals.map_extract.container.ref.steps.add().name = 'vector'
    expected_constr.assign.src.unary_set.vals.map_extract.path.steps.add().name = 'float_param'
    self.assertIn(expected_constr, constraints)
