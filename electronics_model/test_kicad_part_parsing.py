import unittest

from edg_core import Range
from .KiCadSchematicBlock import parse_resistor


class KicadPartParsingTest(unittest.TestCase):
  def test_resistor(self):
    self.assertEqual(parse_resistor("22kR"), Range.from_tolerance(22000, 0.05))
    self.assertEqual(parse_resistor("22k"), Range.from_tolerance(22000, 0.05))
    self.assertEqual(parse_resistor("22 k"), Range.from_tolerance(22000, 0.05))

    self.assertEqual(parse_resistor("22k 10%"), Range.from_tolerance(22000, 0.1))
    self.assertEqual(parse_resistor("22k ±10%"), Range.from_tolerance(22000, 0.1))
    self.assertEqual(parse_resistor("22k 5%"), Range.from_tolerance(22000, 0.05))
