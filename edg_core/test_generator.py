import unittest
import sys

from . import *
from .Driver import EmptyRefinement
from .test_common import TestPortSink, TestBlockSource, TestBlockSink
from . import test_common
from .ScalaCompilerInterface import ScalaCompiler
from .CompilerUtils import *


class TestGeneratorAssign(GeneratorBlock):
  def __init__(self) -> None:
    super().__init__()
    self.float_param = self.Parameter(FloatExpr())
    self.add_generator(self.float_gen, self.float_param)

  def float_gen(self) -> None:
    self.assign(self.float_param, 2.0)
    # TODO add an internal constraint


class TestGenerator(unittest.TestCase):
  def test_generator_assign(self):
    compiled_design = ScalaCompiler.compile(TestGeneratorAssign)
    solved = designSolvedValues(compiled_design)
    self.assertIn(makeSolved(['float_param'], 2.0), solved)



# class TestGenerator(GeneratorBlock):
#   def __init__(self) -> None:
#     super().__init__()
#     self.float_param = self.Parameter(FloatExpr())
#     self.range_param = self.Parameter(RangeExpr())
#     self.bool_param = self.Parameter(BoolExpr())
#     self.string_param = self.Parameter(StringExpr())
#     self.port = self.Port(TestPortSink())
#
#   def generate(self) -> None:
#     super().generate()
#     self.sink = self.Block(TestBlockSink())
#     self.test_net = self.connect(self.port, self.sink.sink)
#     # TODO add an internal constraint
#
#
# class GeneratorBlockTestCase(unittest.TestCase):
#   def setUp(self) -> None:
#     self.driver = Driver([test_common])
#     self.design = self.driver.elaborate_toplevel(TestGenerator())
#
#     # Simulate a solver setting constraints
#     self.design.contents.constraints['set_float_param'].CopyFrom(
#       edgir.EqualsValueExpr(['float_param'], 4.2))
#     self.design.contents.constraints['set_range_param'].CopyFrom(
#       edgir.EqualsValueExpr(['range_param'], (-2.4, -1.2)))
#     self.design.contents.constraints['set_bool_param'].CopyFrom(
#       edgir.EqualsValueExpr(['bool_param'], True))
#     self.design.contents.constraints['set_string_param'].CopyFrom(
#       edgir.EqualsValueExpr(['string_param'], "TeSt"))
#
#     self.design.contents.constraints['set_port_float_param'].CopyFrom(
#       edgir.EqualsValueExpr(['port', 'float_param'], 3.1))
#
#   def test_get(self) -> None:
#     # This is very much whitebox testing, since .get(...) should only be valid inside generate
#     from .Blocks import BlockElaborationState
#
#     generator = TestGenerator()
#     generator._parse_from_proto(self.design.contents)
#     generator._elaboration_state = BlockElaborationState.generate
#
#     self.assertEqual(generator.get(generator.float_param), 4.2)
#     self.assertEqual(generator.get(generator.range_param), (-2.4, -1.2))
#     self.assertEqual(generator.get(generator.range_param.lower()), -2.4)
#     self.assertEqual(generator.get(generator.range_param.upper()), -1.2)
#     self.assertEqual(generator.get(generator.bool_param), True)
#     self.assertEqual(generator.get(generator.string_param), "TeSt")
#
#     raise NotImplementedError
#     # self.assertEqual(generator.get(generator.port.float_param), 3.1)
#
#     self.assertEqual(generator.get(generator.port.is_connected()), False)
#
#   def test_generator(self) -> None:
#     pb = self.driver._generate_design(self.design, EmptyRefinement, False, 'TestGenerator')[0].contents  # TODO avoid internal method use
#
#     # Check that constraints still exist
#     self.assertEqual(pb.constraints['set_float_param'], self.design.contents.constraints['set_float_param'])
#     self.assertEqual(pb.constraints['set_range_param'], self.design.contents.constraints['set_range_param'])
#     self.assertEqual(pb.constraints['set_bool_param'], self.design.contents.constraints['set_bool_param'])
#     self.assertEqual(pb.constraints['set_string_param'], self.design.contents.constraints['set_string_param'])
#
#     self.assertEqual(pb.constraints['set_port_float_param'], self.design.contents.constraints['set_port_float_param'])
#
#     # Check that metadata generator is marked as completed
#     self.assertIn('done', pb.meta.members.node['generator'].members.node)
#
#     # Check that the structural ports and parameters are still there
#     self.assertEqual(len(pb.ports), 1)
#     self.assertEqual(pb.ports['port'].port.superclasses[0].target.name,
#                      'edg_core.test_common.TestPortSink')
#
#     self.assertEqual(len(pb.params), 4)
#     self.assertTrue(pb.params['float_param'].HasField('floating'))
#     self.assertTrue(pb.params['range_param'].HasField('range'))
#     self.assertTrue(pb.params['bool_param'].HasField('boolean'))
#     self.assertTrue(pb.params['string_param'].HasField('text'))
#
#     # Check that the generated blocks and constraints exist
#     self.assertEqual(len(pb.blocks), 1)
#     self.assertEqual(pb.blocks['sink'].hierarchy.superclasses[0].target.name,
#                      'edg_core.test_common.TestBlockSink')
#     self.assertEqual(pb.blocks['sink'].hierarchy.ports['sink'].port.superclasses[0].target.name,
#                      'edg_core.test_common.TestPortSink')
#
#     self.assertEqual(len(pb.links), 0)
#
#     expected_conn = edgir.ValueExpr()
#     expected_conn.exported.exterior_port.ref.steps.add().name = 'port'
#     expected_conn.exported.internal_block_port.ref.steps.add().name = 'sink'
#     expected_conn.exported.internal_block_port.ref.steps.add().name = 'sink'
#     self.assertIn(expected_conn, pb.constraints.values())
#
#
# class TestGeneratorNotConnected(GeneratorBlock):
#   def __init__(self) -> None:
#     super().__init__()
#     self.port = self.Port(TestPortSink(), optional=True)
#
#   def generate(self) -> None:
#     assert not self.get(self.port.is_connected())
#
#
# class TestGeneratorNotConnectedTop(Block):
#   def __init__(self) -> None:
#     super().__init__()
#     self.port = self.Port(TestPortSink())  # TODO replace with internal dummy block
#
#   def contents(self) -> None:
#     super().contents()
#     self.exported_block = self.Block(TestGeneratorNotConnected())  # export without connection treated as not connected
#     self.connect(self.port, self.exported_block.port)
#
#     self.notconnected_block = self.Block(TestGeneratorNotConnected())
#
#
# class GeneratorNotConnectTestCase(unittest.TestCase):
#   def test_notconnected(self) -> None:
#     self.driver = Driver([test_common, sys.modules[__name__]])
#     self.design = self.driver.generate_block(TestGeneratorNotConnectedTop())  # assertion in the design
#
#
# class TestGeneratorConnected(GeneratorBlock):
#   def __init__(self) -> None:
#     super().__init__()
#     self.port = self.Port(TestPortSink())
#
#   def generate(self) -> None:
#     super().generate()
#     assert self.get(self.port.is_connected())
#
#
# class TestGeneratorConnectedTop(Block):
#   def __init__(self) -> None:
#     super().__init__()
#
#   def contents(self) -> None:
#     super().contents()
#     self.src_block = self.Block(TestBlockSource())
#     self.connected_block = self.Block(TestGeneratorConnected())
#     self.connect(self.src_block.source, self.connected_block.port)
#
#
# class GeneratorConnectedTestCase(unittest.TestCase):
#   def test_connected(self) -> None:
#     self.driver = Driver([test_common, sys.modules[__name__]])
#     self.design = self.driver.generate_block(TestGeneratorConnectedTop())  # assertion in the design
#
#
# class TestGeneratorException(BaseException):
#   pass
#
#
# class TestGeneratorFailure(GeneratorBlock):
#   def __init__(self) -> None:
#     super().__init__()
#
#   def generate(self) -> None:
#     super().generate()
#     raise TestGeneratorException("test_text")
#
#
# class GeneratorFailureTestCase(unittest.TestCase):
#   def test_metadata(self) -> None:
#     self.driver = Driver([])
#     self.design = self.driver.generate_block(TestGeneratorFailure(), continue_on_error=True)
#     self.assertIn("TestGeneratorException",
#                   self.design.contents.meta.members.node['error'].members.node['generator'].text_leaf)
#     self.assertIn("test_text",
#                   self.design.contents.meta.members.node['error'].members.node['generator'].text_leaf)
#     self.assertIn("in generate at (root) for edg_core.test_generator.TestGeneratorFailure",
#                   self.design.contents.meta.members.node['error'].members.node['generator'].text_leaf)
#     self.assertIn('traceback', self.design.contents.meta.members.node)
