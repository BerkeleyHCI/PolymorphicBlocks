import unittest

import edgir
from . import *
from .HdlUserExceptions import BlockDefinitionError
from .test_elaboration_common import TestPortBase
from .test_mixin import TestMixin


class BadMixinUsageTestCase(unittest.TestCase):
    class MixinBlock(Block):
        def contents(self) -> None:
            super().contents()
            self.block = self.Block(TestMixin)

    def test_mixin_block(self) -> None:
        with self.assertRaises(TypeError):
            self.MixinBlock()._elaborated_def_to_proto()
