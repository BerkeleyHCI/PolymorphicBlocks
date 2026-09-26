import unittest

from typing_extensions import override


from . import *
from .HdlUserExceptions import *
from .test_common import TestPortSource, TestBlockSource, TestBlockSink


class HasParamInnerBlock(Block):
    def __init__(self, in_param: IntLike) -> None:
        super().__init__()
        self.in_param = self.ArgParameter(in_param)


class BadLinkTestCase(unittest.TestCase):
    # This needs to be an internal class to avoid this error case being auto-discovered in a library

    class OverconnectedHierarchyBlock(Block):
        """A block with connections that don't fit the link (2 sources connected vs. one in the link)"""

        @override
        def contents(self) -> None:
            super().contents()
            self.source1 = self.Block(TestBlockSource())
            self.source2 = self.Block(TestBlockSource())
            self.sink = self.Block(TestBlockSink())
            self.test_net = self.connect(self.source1.source, self.sink.sink)
            self.connect(self.source1.source, self.source2.source)
            assert (
                False  # the above connect should error (providing a useful traceback), should not reach this statement
            )

    def test_overconnected_link(self) -> None:
        with self.assertRaises(UnconnectableError):
            self.OverconnectedHierarchyBlock()._elaborated_def_to_proto()

    class NoBridgeHierarchyBlock(Block):
        """A block where a bridge can't be inferred (TestPortSource has no bridge)"""

        def __init__(self) -> None:
            super().__init__()
            self.source_port = self.Port(TestPortSource())

        @override
        def contents(self) -> None:
            super().contents()
            self.source = self.Block(TestBlockSource())
            self.sink = self.Block(TestBlockSink())
            self.test_net = self.connect(self.source_port, self.source.source, self.sink.sink)
            assert False  # the above connect should error

    def test_no_bridge_link(self) -> None:
        with self.assertRaises(UnconnectableError):
            self.NoBridgeHierarchyBlock()._elaborated_def_to_proto()

    class UnboundHierarchyBlock(Block):
        """A block that uses a port that isn't bound through self.Port(...)"""

        def __init__(self) -> None:
            super().__init__()
            unbound_port = TestPortSource()
            self.test_net = self.connect(unbound_port)
            assert False  # the above connect should error

    def test_unbound_link(self) -> None:
        with self.assertRaises(UnconnectableError):
            self.NoBridgeHierarchyBlock()._elaborated_def_to_proto()

    class AmbiguousJoinBlock(Block):
        """A block with a connect join that merges two names"""

        @override
        def contents(self) -> None:
            super().contents()
            self.source = self.Block(TestBlockSource())
            self.sink1 = self.Block(TestBlockSink())
            self.sink2 = self.Block(TestBlockSink())
            self.test_net1 = self.connect(self.source.source, self.sink1.sink)
            self.test_net2 = self.connect(self.sink2.sink)
            self.connect(self.test_net1, self.test_net2)

    def test_ambiguous_join(self) -> None:
        with self.assertRaises(UnconnectableError):
            self.AmbiguousJoinBlock()._elaborated_def_to_proto()


class MissingParamTestCase(unittest.TestCase):

    class MissingParamTopBlock(Block):
        """This block doesn't define a parameter value"""

        def __init__(self) -> None:
            super().__init__()
            self.param = self.Parameter(IntExpr())

    def test_missing_param(self) -> None:
        with self.assertRaises(MissingParameterError):
            self.MissingParamTopBlock()._elaborated_def_to_proto()

    class MissingParamInnerBlock(Block):
        """This block defines an arg-param but does not define an output parameter value."""

        def __init__(self, in_param: IntLike) -> None:
            super().__init__()
            self.in_param = self.ArgParameter(in_param)
            self.param = self.Parameter(IntExpr())

    def test_missing_param_inner(self) -> None:
        with self.assertRaises(MissingParameterError):
            self.MissingParamInnerBlock(0)._elaborated_def_to_proto()

    class MissingParamContainerBlock(Block):
        """This block contains a child that defines an arg-param but does not define an output parameter value."""

        def __init__(self) -> None:
            super().__init__()
            self.inner = self.Block(HasParamInnerBlock(IntExpr()))

    def test_missing_param_container(self) -> None:
        with self.assertRaises(MissingParameterError):
            self.MissingParamContainerBlock()._elaborated_def_to_proto()
