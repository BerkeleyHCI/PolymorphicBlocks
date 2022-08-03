import unittest

import edgir
from . import *
from .Blocks import DescriptionString


class DescriptionBlock(Block):
    """Block with a float parameter and description"""
    def __init__(self) -> None:
        super().__init__()
        self.variable = self.Parameter(FloatExpr(5.0))
        self.description = DescriptionString(
            "Test variable = ", DescriptionString.FormatUnits(self.variable, "Units"), ".")


class DescriptionBlockProtoTestCase(unittest.TestCase):
    def test_description(self):
        pb = DescriptionBlock()._elaborated_def_to_proto()

        self.assertEqual(len(pb.description), 3)

        self.assertEqual(pb.description[0].text, 'Test variable = ')
        expected_ref = edgir.LocalPath()
        expected_ref.steps.add().name = 'variable'
        self.assertEqual(pb.description[1].param.path, expected_ref)
        self.assertEqual(pb.description[1].param.unit, 'Units')
        self.assertEqual(pb.description[2].text, '.')
