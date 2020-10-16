from typing import *
import unittest

from . import *
from .test_common import TestPortSource, TestPortSink, problem_name_from_module_file


class TestBlockSource(Block):
  def __init__(self) -> None:
    super().__init__()
    self.source = self.Port(TestPortSource(float_param_limit=(1, 2), range_param=(4, 5)))

class TestBlockSink1(Block):
  def __init__(self) -> None:
    super().__init__()
    self.sink = self.Port(TestPortSink(float_param=1, range_limit=(3, 5)))

class TestBlockSink2(Block):
  def __init__(self) -> None:
    super().__init__()
    self.sink = self.Port(TestPortSink(float_param=2, range_limit=(4, 6)))

class TestTopDesign(Block):
  def contents(self) -> None:
    super().contents()
    self.source = self.Block(TestBlockSource())
    self.sink1 = self.Block(TestBlockSink1())
    self.sink2 = self.Block(TestBlockSink2())
    self.test_net = self.connect(self.source.source, self.sink1.sink, self.sink2.sink)

    # expected float_param_sink_sum: 3
    # expected float_param_sink_range: (1, 2)
    # expected range_limit_sink_common: (4, 5)

class TopHierarchyBlockProtoTestCase(unittest.TestCase):
  def setUp(self) -> None:
    import sys
    self.driver = Driver([sys.modules[__name__]])
    self.proto = self.driver.generate_library_proto()

  def test_problem(self) -> None:
    with open(problem_name_from_module_file(__file__), 'wb') as f:
      f.write(self.proto.SerializeToString())
