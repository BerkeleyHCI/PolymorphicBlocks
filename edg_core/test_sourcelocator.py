import unittest
import os

from . import *
from .test_common import TestPortBase


class TestBlockSourceLocator(Block):
  """Test Block Def"""
  def __init__(self) -> None:
    super().__init__()
    self.test_param = self.Parameter(FloatExpr())
    self.test_port = self.Port(TestPortBase())


class BlockSourceLocatorProtoTestCase(unittest.TestCase):
  def setUp(self) -> None:
    self.pb = TestBlockSourceLocator()._elaborated_def_to_proto()

  def test_block_def(self) -> None:
    sloc = edgir.source_locator_of(self.pb, 'self')
    assert sloc is not None
    sloc_filepath, sloc_line = sloc
    self.assertEqual(os.path.split(sloc_filepath)[-1], 'test_sourcelocator.py')
    self.assertEqual(sloc_line, 0)

  def test_param_def(self) -> None:
    sloc = edgir.source_locator_of(self.pb, 'test_param')
    assert sloc is not None
    sloc_filepath, sloc_line = sloc
    self.assertEqual(os.path.split(sloc_filepath)[-1], 'test_sourcelocator.py')
    self.assertEqual(sloc_line, 12)

  def test_port_def(self) -> None:
    sloc = edgir.source_locator_of(self.pb, 'test_port')
    assert sloc is not None
    sloc_filepath, sloc_line = sloc
    self.assertEqual(os.path.split(sloc_filepath)[-1], 'test_sourcelocator.py')
    self.assertEqual(sloc_line, 13)
