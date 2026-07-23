import unittest

from typing_extensions import override

from . import *
from .HdlUserExceptions import BlockDefinitionError


class GeneratorErrorTop(DesignTop):
    @override
    def contents(self) -> None:
        super().contents()
        self.generator = self.Block(GeneratorRaises(42, "bad"))


class GeneratorRaises(GeneratorBlock):
    def __init__(self, param: IntLike, str_param: StringLike) -> None:
        super().__init__()
        self.param = self.ArgParameter(param)
        self.str_param = self.ArgParameter(str_param)
        self.generator_param(self.param, self.str_param)

    @override
    def generate(self) -> None:
        super().generate()
        raise ValueError


class BadGeneratorTestCase(unittest.TestCase):
    # These are internal classes to avoid this error case being auto-discovered in a library

    class InvalidMissingGeneratorBlock(GeneratorBlock):
        """This doesn't implement generator()"""

    def test_missing_generator(self) -> None:
        with self.assertRaises(BlockDefinitionError):
            self.InvalidMissingGeneratorBlock()._elaborated_def_to_proto()

    class InvalidNonArgGeneratorBlock(GeneratorBlock):
        def __init__(self) -> None:
            super().__init__()
            self.param = self.Parameter(FloatExpr())
            self.generator_param(self.param)

        @override
        def generate(self) -> None:
            super().generate()

    def test_non_arg_generator(self) -> None:
        with self.assertRaises(BlockDefinitionError):
            self.InvalidNonArgGeneratorBlock()._elaborated_def_to_proto()

    def test_generator_raises(self) -> None:
        with self.assertRaises(CompilerCheckError):
            ScalaCompiler.compile(GeneratorErrorTop)
        # TODO: inspect the exception, note that it is consumed by the Scala compiler
        # and not summarized in the CompilerCheckError
