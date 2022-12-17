import unittest

from edg_core import Range
from .AbstractResistor import Resistor
from .AbstractCapacitor import Capacitor


class KicadPartParsingTest(unittest.TestCase):
  def test_resistor(self):
    self.assertEqual(Resistor.parse_resistor("51"), Range.from_tolerance(51, 0.05))
    self.assertEqual(Resistor.parse_resistor("22kR"), Range.from_tolerance(22000, 0.05))
    self.assertEqual(Resistor.parse_resistor("22k"), Range.from_tolerance(22000, 0.05))
    self.assertEqual(Resistor.parse_resistor("22 k"), Range.from_tolerance(22000, 0.05))

    self.assertEqual(Resistor.parse_resistor("22k 10%"), Range.from_tolerance(22000, 0.1))
    self.assertEqual(Resistor.parse_resistor("22k ±10%"), Range.from_tolerance(22000, 0.1))
    self.assertEqual(Resistor.parse_resistor("22k 5%"), Range.from_tolerance(22000, 0.05))

  def test_capacitor(self):
    self.assertEqual(Capacitor.parse_capacitor("0.1uF 6.3V"), (Range.from_tolerance(0.1e-6, 0.20),
                                                               Range.zero_to_upper(6.3)))
    self.assertEqual(Capacitor.parse_capacitor("4.7u 6.3V"), (Range.from_tolerance(4.7e-6, 0.20),
                                                              Range.zero_to_upper(6.3)))
    self.assertEqual(Capacitor.parse_capacitor("0.1uF 10% 12V"), (Range.from_tolerance(0.1e-6, 0.10),
                                                                  Range.zero_to_upper(12)))
