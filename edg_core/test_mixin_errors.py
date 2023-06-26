import unittest

from . import *
from .HdlUserExceptions import BlockDefinitionError
from .test_mixin import TestMixin


class BadMixinDefinitionTestCase(unittest.TestCase):
    class BaselessMixin(BlockInterfaceMixin):
        pass

    def test_mixin_baseless(self) -> None:
        with self.assertRaises(BlockDefinitionError):
            self.BaselessMixin()._elaborated_def_to_proto()

    class MixinConcreteBase(Block):
        pass

    class ConcreteMixin(BlockInterfaceMixin[MixinConcreteBase]):
        pass

    def test_mixin_concrete_base(self) -> None:
        with self.assertRaises(BlockDefinitionError):
            self.ConcreteMixin()._elaborated_def_to_proto()


class BadMixinUsageTestCase(unittest.TestCase):
    class MixinBlock(Block):
        def contents(self) -> None:
            super().contents()
            self.block = self.Block(TestMixin())

    def test_mixin_block(self) -> None:
        with self.assertRaises(TypeError):
            self.MixinBlock()._elaborated_def_to_proto()
