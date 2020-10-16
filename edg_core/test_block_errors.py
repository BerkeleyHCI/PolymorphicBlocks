import unittest

from . import *
from .Exception import *
from .test_common import TestPortSource, TestBlockSource, TestBlockSink, TestBlockImplicitSink


class BadLinkTestCase(unittest.TestCase):
  # This needs to be an internal class to avoid this error case being auto-discovered in a library

  class OverconnectedHierarchyBlock(Block):
    """A block with connections that don't fit the link (2 sources connected vs. one in the link)"""
    def contents(self) -> None:
      super().contents()
      self.source1 = self.Block(TestBlockSource())
      self.source2 = self.Block(TestBlockSource())
      self.sink = self.Block(TestBlockSink())
      self.test_net = self.connect(self.source1.source, self.source2.source, self.sink.sink)

  def test_overconnected_link(self) -> None:
    with self.assertRaises(UnconnectableError):
      self.OverconnectedHierarchyBlock()._elaborated_def_to_proto()

  class NoBridgeHierarchyBlock(Block):
    """A block where a bridge can't be inferred (TestPortSource has no bridge)"""
    def __init__(self) -> None:
      super().__init__()
      self.source_port = self.Port(TestPortSource())

    def contents(self) -> None:
      super().contents()
      self.source = self.Block(TestBlockSource())
      self.sink = self.Block(TestBlockSink())
      self.test_net = self.connect(self.source_port, self.source.source, self.sink.sink)

  def test_no_bridge_link(self) -> None:
    with self.assertRaises(UnconnectableError):
      self.NoBridgeHierarchyBlock()._elaborated_def_to_proto()

  class UnboundHierarchyBlock(Block):
    """A block that uses a port that isn't bound through self.Port(...)"""
    def __init__(self) -> None:
      super().__init__()
      unbound_port = TestPortSource()
      self.test_net = self.connect(unbound_port)

  def test_unbound_link(self) -> None:
    with self.assertRaises(UnconnectableError):
      self.NoBridgeHierarchyBlock()._elaborated_def_to_proto()

  class AboveConnectBlock(Block):
    """A block that directly tries to connect to a parent port (passed in through the constructor)"""
    class BadInnerBlock(Block):  # TODO this is kind of nasty?
      def __init__(self, above_port: TestPortSource) -> None:
        super().__init__()
        self.connect(above_port)

    def __init__(self) -> None:
      super().__init__()
      self.source = self.Port(TestPortSource())

    def contents(self) -> None:
      super().contents()
      self.inner = self.Block(self.BadInnerBlock(self.source))

  def test_above_connect(self) -> None:
    with self.assertRaises(UnconnectableError):
      self.AboveConnectBlock()._elaborated_def_to_proto()


class RequiredPortTestCase(unittest.TestCase):
  # This needs to be an internal class to avoid this error case being auto-discovered in a library
  class BadRequiredPortBlock(Block):
    """A block that does not have the required ports of sub-blocks connected"""
    def contents(self) -> None:
      super().contents()
      self.sink = self.Block(TestBlockImplicitSink())
      self.connect(self.sink.sink, self.sink.sink)  # just in case

  def test_bad_link(self) -> None:
    with self.assertRaises(UnconnectedRequiredPortError):
      self.BadRequiredPortBlock()._elaborated_def_to_proto()


class InaccessibleParamTestCase(unittest.TestCase):
  class BadParamReferenceBlock(Block):
    """A block that tries to access deeply nested block parameters"""
    class BadInnerBlock(Block):
      def __init__(self, in_range: RangeExpr) -> None:
        super().__init__()
        self.constrain(in_range == (0, 1))

    def __init__(self) -> None:
      super().__init__()
      self.range = self.Parameter(RangeExpr())

    def contents(self) -> None:
      super().contents()
      self.inner = self.Block(self.BadInnerBlock(self.range))

  def test_bad_param_reference(self) -> None:
    with self.assertRaises(UnreachableParameterError):
      self.BadParamReferenceBlock()._elaborated_def_to_proto()

  class BadParamInitBlock(Block):
    """A block that does initialization without @init_in_parent"""
    class BadInnerBlock(Block):
      def __init__(self, in_range: RangeExpr) -> None:
        super().__init__()
        self.range = self.Parameter(RangeExpr(in_range))

    def __init__(self) -> None:
      super().__init__()
      self.range = self.Parameter(RangeExpr())

    def contents(self) -> None:
      super().contents()
      self.inner = self.Block(self.BadInnerBlock(self.range))

  def test_bad_param_initializer(self) -> None:
    with self.assertRaises(UnreachableParameterError):
      self.BadParamInitBlock()._elaborated_def_to_proto()
