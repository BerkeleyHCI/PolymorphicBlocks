import unittest

from . import *
from .test_common import TestPortBase


class TestBlockEdgdoc(Block):
  """Test Block Def"""
  def __init__(self) -> None:
    super().__init__()
    self.test_param = self.Parameter(FloatExpr(), desc="Test Param")
    self.test_port = self.Port(TestPortBase(), desc="Test Port")


class BlockEdgdocProtoTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = TestBlockEdgdoc()._elaborated_def_to_proto()

  def test_block_def(self) -> None:
    self.assertEqual(edgir.edgdoc_of(self.pb, 'self'), "Test Block Def")

  def test_param_def(self) -> None:
    self.assertEqual(edgir.edgdoc_of(self.pb, 'test_param'), "Test Param")

  def test_port_def(self) -> None:
    self.assertEqual(edgir.edgdoc_of(self.pb, 'test_port'), "Test Port")
