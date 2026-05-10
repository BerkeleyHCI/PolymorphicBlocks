import unittest
from typing import cast

from . import *
from .CompiledDesignExport import CompiledPort


class CompiledDesignExportTestCase(unittest.TestCase):
    def test_hierarchy(self) -> None:
        from .test_hierarchy_block import TopHierarchyBlock

        compiled = ScalaCompiler.compile(TopHierarchyBlock)
        result = CompiledDesignExportTransform(compiled).transform()
        self.assertEqual(result.blocks["source"].cls, "edg.core.test_common.TestBlockSource")
        self.assertEqual(result.blocks["source"].doc, "Source block")
        self.assertEqual(result.blocks["sink1"].cls, "edg.core.test_common.TestBlockSink")
        self.assertEqual(result.blocks["sink1"].doc, "Sink block")
        self.assertEqual(result.blocks["sink2"].cls, "edg.core.test_common.TestBlockSink")
        self.assertEqual(result.blocks["sink2"].doc, "Sink block")
        self.assertEqual(result.links["test_net"].cls, "edg.core.test_common.TestLink")
        self.assertEqual(cast(CompiledPort, result.blocks["source"].ports["source"]).connected_path, "test_net.source")
        self.assertEqual(cast(CompiledPort, result.blocks["source"].ports["source"]).doc, "Source port")
        self.assertEqual(cast(CompiledPort, result.blocks["sink1"].ports["sink"]).connected_path, "test_net.sinks.0")
        self.assertEqual(cast(CompiledPort, result.blocks["sink1"].ports["sink"]).doc, "Sink port")
        self.assertEqual(cast(CompiledPort, result.blocks["sink2"].ports["sink"]).connected_path, "test_net.sinks.1")
        self.assertEqual(cast(CompiledPort, result.blocks["sink2"].ports["sink"]).doc, "Sink port")

    def test_param_values(self) -> None:
        from .test_simple_expr_eval import TestEvalReductionBlock

        compiled = ScalaCompiler.compile(TestEvalReductionBlock)
        result = CompiledDesignExportTransform(compiled).transform()
        self.assertEqual(result.links["link"].params["range_sum"].value, (6.0, 130.0))
        self.assertEqual(result.links["link"].params["range_intersection"].value, (5.0, 10.0))

    def test_param_error(self) -> None:
        from .test_simple_expr_eval import TestEvalExprErrorBlock

        compiled = ScalaCompiler.compile(TestEvalExprErrorBlock, ignore_errors=True)
        result = CompiledDesignExportTransform(compiled).transform()
        self.assertIn("overassign", result.params["overassign_float"].error)
        self.assertEqual(result.params["overassign_float"].value, None)
