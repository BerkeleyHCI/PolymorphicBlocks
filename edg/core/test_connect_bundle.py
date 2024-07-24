import unittest

from . import *
from .HdlUserExceptions import UnconnectableError
from .test_elaboration_common import TestBlockSource
from .test_bundle import TestBundle


class TestInner(Block):
    def __init__(self) -> None:
        super().__init__()
        self.port = self.Port(TestBundle())


class TestInvalidOuter(Block):
    def __init__(self) -> None:
        super().__init__()
        self.inner = self.Block(TestInner())
        self.source = self.Block(TestBlockSource())
        self.connect(self.inner.port.a, self.source.source)


class BundleConnectError(unittest.TestCase):
    def test_contains_param(self) -> None:
        with self.assertRaises(UnconnectableError):
            TestInvalidOuter()._elaborated_def_to_proto()