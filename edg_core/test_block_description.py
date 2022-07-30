import unittest

from . import *
from .Blocks import DescriptionString


class DescriptionBlock(Block):
    """Block with an EltDict of sub-blocks"""
    def contents(self):
        super().contents()
        self.variable = self.Parameter(FloatExpr(5.0))
        self.description = DescriptionString(
            "Test variable = ", DescriptionString.FormatUnits(self.variable, "Units"), ".")


class DescriptionBlockProtoTestCase(unittest.TestCase):
    def test_description(self):
        pb = DescriptionBlock()._elaborated_def_to_proto()

        self.assertEqual(len(pb.description), 3)

        self.assertEqual(pb.description[0].text, 'Test Variable = ')
        self.assertEqual(pb.description[1].param.unit, 'Units')
        self.assertEqual(pb.description[2].text, '.')
