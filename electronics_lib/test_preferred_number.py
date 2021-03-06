import unittest

from .Passives import Resistor, choose_preferred_number, zigzag_range

class PreferredNumberTestCase(unittest.TestCase):
  def test_zigzag_range(self) -> None:
    self.assertEqual(zigzag_range(0, 1), [0])
    self.assertEqual(zigzag_range(0, 2), [0, 1])
    self.assertEqual(zigzag_range(0, 3), [1, 0, 2])
    self.assertEqual(zigzag_range(0, 4), [1, 0, 2, 3])

  def test_preferred_number(self) -> None:
    # Test a few different powers
    self.assertEqual(choose_preferred_number((0.09, 0.11), 0.01, Resistor.E24_SERIES_ZIGZAG, 2), 0.1)
    self.assertEqual(choose_preferred_number((0.9, 1.1), 0.01, Resistor.E24_SERIES_ZIGZAG, 2), 1)
    self.assertEqual(choose_preferred_number((9, 11), 0.01, Resistor.E24_SERIES_ZIGZAG, 2), 10)
    self.assertEqual(choose_preferred_number((900, 1100), 0.01, Resistor.E24_SERIES_ZIGZAG, 2), 1000)

    # Test a few different numbers
    self.assertEqual(choose_preferred_number((8100, 8300), 0.01, Resistor.E24_SERIES_ZIGZAG, 2), 8200)
    self.assertEqual(choose_preferred_number((460, 480), 0.01, Resistor.E24_SERIES_ZIGZAG, 2), 470)

    # Test preference for lower E-series first
    self.assertEqual(choose_preferred_number((101, 9999), 0.01, Resistor.E24_SERIES_ZIGZAG, 2), 1000)
    self.assertEqual(choose_preferred_number((220, 820), 0.01, Resistor.E24_SERIES_ZIGZAG, 2), 470)

    # Test dynamic range edge cases
    self.assertEqual(choose_preferred_number((999, 1500), 0.01, Resistor.E24_SERIES_ZIGZAG, 2), 1200)
    self.assertEqual(choose_preferred_number((680, 1001), 0.01, Resistor.E24_SERIES_ZIGZAG, 2), 820)
