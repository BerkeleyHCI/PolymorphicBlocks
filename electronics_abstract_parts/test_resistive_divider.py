import unittest

from .ResistiveDivider import ResistiveDivider

class ResistorDividerTest(unittest.TestCase):
  def test_resistor_divider(self) -> None:
    self.assertEqual(ResistiveDivider._select_resistor(
      ResistiveDivider.E24_SERIES,
      (0, 1), (0.1, 1), 0.01),
      (1, 1))

    self.assertEqual(ResistiveDivider._select_resistor(  # test a tighter range
      ResistiveDivider.E24_SERIES,
      (0.48, 0.52), (0.1, 1), 0.01),
      (1, 1))

    self.assertEqual(ResistiveDivider._select_resistor(
      ResistiveDivider.E24_SERIES,
      (0.106, 0.111), (0.1, 1), 0.01),  # test E12
      (8.2, 1))

    self.assertEqual(ResistiveDivider._select_resistor(
      ResistiveDivider.E24_SERIES,
      (0.208, 0.215), (1, 10), 0.01),  # test E12
      (8.2, 2.2))

    self.assertEqual(ResistiveDivider._select_resistor(
      ResistiveDivider.E24_SERIES,
      (0.7241, 0.7321), (1, 10), 0.01),  # test E12 across decades
      (5.6, 15))

    self.assertEqual(ResistiveDivider._select_resistor(  # test impedance decade shift
      ResistiveDivider.E24_SERIES,
      (0, 1), (10, 100), 0.01),
      (100, 100))

    self.assertEqual(ResistiveDivider._select_resistor(  # test everything
      ResistiveDivider.E24_SERIES,
      (0.106, 0.111), (11, 99), 0.01),  # test E12
      (820, 100))
