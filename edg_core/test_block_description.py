import unittest

from . import *


class DescriptionBlock(Block):
    """Block with an EltDict of sub-blocks"""
    def contents(self):
        super().contents()
        self.description = "Test Variable = {variable}."


class DescriptionBlockProtoTestCase(unittest.TestCase):
    def test_description(self):
        pb = DescriptionBlock()._elaborated_def_to_proto()

        self.assertEqual(len(pb.description), 3)

        self.assertEqual(pb.description[0].text, 'Test Variable = ')
        self.assertEqual(pb.description[1].variable, 'variable')
        self.assertEqual(pb.description[2].text, '.')
