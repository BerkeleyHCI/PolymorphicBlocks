import unittest

from typing_extensions import override


from . import *
from .HdlUserExceptions import *
from .test_common import TestPortSource, TestBlockSource, TestBlockSink


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


class HasParamInnerBlock(Block):
    def __init__(self, in_param: IntLike) -> None:
        super().__init__()
        self.in_param = self.ArgParameter(in_param)


class HasParamLink(Link):
    def __init__(self) -> None:
        super().__init__()
        self.source = self.Port(HasParamPort.empty())


class HasParamPort(Port[HasParamLink]):
    link_type = HasParamLink

    def __init__(self, param: IntLike = 0) -> None:
        super().__init__()
        self.param = self.Parameter(IntExpr(param))


class MissingParamTestCase(unittest.TestCase):

    class MissingParamBlock(Block):
        def __init__(self) -> None:
            super().__init__()
            self.param = self.Parameter(IntExpr())  # value never defined

    def test_missing_param(self) -> None:
        with self.assertRaises(MissingParameterError):
            self.MissingParamBlock()._elaborated_def_to_proto()

    class OverassignParamBlock(Block):
        def __init__(self) -> None:
            super().__init__()
            self.param = self.Parameter(IntExpr())
            self.assign(self.param, 1)
            self.assign(self.param, 2)

    def test_overassign_param(self) -> None:
        with self.assertRaises(OverassignParameterError):
            self.OverassignParamBlock()._elaborated_def_to_proto()

    class OverassignInitializerParamBlock(Block):
        """This has a conflicting assign between the initializer and an explicit assign statement."""

        def __init__(self) -> None:
            super().__init__()
            self.param = self.Parameter(IntExpr(1))
            self.assign(self.param, 2)

    def test_overassign_initializer_param(self) -> None:
        with self.assertRaises(OverassignParameterError):
            self.OverassignInitializerParamBlock()._elaborated_def_to_proto()

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

    class MissingParamPortBlock(Block):
        def __init__(self) -> None:
            super().__init__()
            self.port = self.Port(HasParamPort(IntExpr()))

    def test_missing_param_port(self) -> None:
        with self.assertRaises(MissingParameterError):
            self.MissingParamPortBlock()._elaborated_def_to_proto()

    class MissingParamVectorBlock(Block):
        def __init__(self) -> None:
            super().__init__()
            self.port = self.Port(Vector(HasParamPort.empty()))
            self.port.append_elt(HasParamPort(2), "0")
            self.port.append_elt(HasParamPort(IntExpr()), "1")  # missing value
            self.port.defined()

    def test_missing_param_vector(self) -> None:
        with self.assertRaises(MissingParameterError):
            self.MissingParamVectorBlock()._elaborated_def_to_proto()

    class MissingParamLink(Link):
        def __init__(self) -> None:
            super().__init__()
            self.source = self.Port(TestPortSource(), optional=True)
            self.param = self.Parameter(IntExpr())

    def test_missing_param_link(self) -> None:
        with self.assertRaises(MissingParameterError):
            self.MissingParamLink()._elaborated_def_to_proto()
