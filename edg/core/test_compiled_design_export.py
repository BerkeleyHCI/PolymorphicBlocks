import unittest

from edg import ScalaCompiler, CompiledDesignExportTransform


class CompiledDesignExportTestCase(unittest.TestCase):
    def test_export(self) -> None:
        from .test_simple_expr_eval import TestEvalReductionBlock

        compiled = ScalaCompiler.compile(TestEvalReductionBlock)
        result = CompiledDesignExportTransform(compiled).transform()
