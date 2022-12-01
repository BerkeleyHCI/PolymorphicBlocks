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
    self.assertEqual(pb.blocks[0].name, 'sink[0]')
    self.assertEqual(pb.blocks[0].value.lib_elem.target.name, "edg_core.test_common.TestBlockSink")
    self.assertEqual(pb.blocks[1].name, 'sink[1]')
    self.assertEqual(pb.blocks[1].value.lib_elem.target.name, "edg_core.test_common.TestBlockSink")
    self.assertEqual(pb.blocks[2].name, 'nested[inner][a]')
    self.assertEqual(pb.blocks[2].value.lib_elem.target.name, "edg_core.test_common.TestBlockSink")
    self.assertEqual(pb.blocks[3].name, 'nested[inner][b]')
    self.assertEqual(pb.blocks[3].value.lib_elem.target.name, "edg_core.test_common.TestBlockSink")
