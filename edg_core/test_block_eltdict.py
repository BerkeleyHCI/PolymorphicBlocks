import unittest

from . import *
from .test_common import TestBlockSource, TestBlockSink, TestPortSource, TestPortSink


class EltDictBlock(Block):
  """Block with an EltDict of sub-blocks"""
  def contents(self):
    super().contents()
    self.sink = ElementDict[Block]()
    self.sink[0] = self.Block(TestBlockSink())
    self.sink[1] = self.Block(TestBlockSink())

    self.nested = ElementDict[ElementDict[Block]]()
    self.nested['inner'] = ElementDict[Block]()
    self.nested['inner']['a'] = self.Block(TestBlockSink())
    self.nested['inner']['b'] = self.Block(TestBlockSink())


class EltDictBlockProtoTestCase(unittest.TestCase):
  def test_connectivity(self):
    pb = EltDictBlock()._elaborated_def_to_proto()
    self.assertEqual(pb.blocks['sink_0'].lib_elem.target.name, "edg_core.test_common.TestBlockSink")
    self.assertEqual(pb.blocks['sink_1'].lib_elem.target.name, "edg_core.test_common.TestBlockSink")
    self.assertEqual(pb.blocks['nested_inner_a'].lib_elem.target.name, "edg_core.test_common.TestBlockSink")
    self.assertEqual(pb.blocks['nested_inner_b'].lib_elem.target.name, "edg_core.test_common.TestBlockSink")
