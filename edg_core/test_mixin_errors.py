import unittest

from . import *
from .HdlUserExceptions import BlockDefinitionError
from .test_block import TestBlock
from .test_mixin import TestMixin, TestMixinBase, TestMixinConcreteBlock


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


@abstract_block
class UnrelatedAbstractBlock(Block):
    pass


class BadMixinUsageTestCase(unittest.TestCase):
    class StandaloneMixinBlock(Block):
        def contents(self) -> None:
            super().contents()
            self.block = self.Block(TestMixin())

    def test_standalone_mixin(self) -> None:
        with self.assertRaises(TypeError):
            self.StandaloneMixinBlock()._elaborated_def_to_proto()

    class ConcreteMixinBlock(Block):
        def contents(self) -> None:
            super().contents()
            self.block = self.Block(TestMixinConcreteBlock())
            self.mixin = self.block.with_mixin(TestMixin())

    def test_concrete_mixin(self) -> None:
        with self.assertRaises(BlockDefinitionError):
            self.ConcreteMixinBlock()._elaborated_def_to_proto()

    class BadBaseMixin(Block):
        def contents(self) -> None:
            super().contents()
            self.block = self.Block(UnrelatedAbstractBlock())
            self.mixin = self.block.with_mixin(TestMixin())

    def test_bad_base_mixin(self) -> None:
        with self.assertRaises(TypeError):
            self.BadBaseMixin()._elaborated_def_to_proto()
