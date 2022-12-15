import unittest

from .PartParserUtil import PartParserUtil


class PartsTableUtilsTest(unittest.TestCase):
  def test_parse_value(self) -> None:
    self.assertEqual(PartParserUtil.parse_value('20 nF', 'F'), 20e-9)
    self.assertEqual(PartParserUtil.parse_value('20 F', 'F'), 20)
    self.assertEqual(PartParserUtil.parse_value('20F', 'F'), 20)
    self.assertEqual(PartParserUtil.parse_value('50 kV', 'V'), 50e3)
    self.assertEqual(PartParserUtil.parse_value('49.9 GΩ', 'Ω'), 49.9e9)
    self.assertEqual(PartParserUtil.parse_value('49.9 GΩ', 'Ω'), 49.9e9)

    with self.assertRaises(PartParserUtil.ParseError):
      self.assertEqual(PartParserUtil.parse_value('50 kA', 'V'), None)
    with self.assertRaises(PartParserUtil.ParseError):
      self.assertEqual(PartParserUtil.parse_value('50 A', 'V'), None)
    with self.assertRaises(PartParserUtil.ParseError):
      self.assertEqual(PartParserUtil.parse_value('50 k', 'V'), None)
    with self.assertRaises(PartParserUtil.ParseError):
      self.assertEqual(PartParserUtil.parse_value('ducks', 'V'), None)
    with self.assertRaises(PartParserUtil.ParseError):
      self.assertEqual(PartParserUtil.parse_value('50.1.2 V', 'V'), None)
    with self.assertRaises(PartParserUtil.ParseError):
      self.assertEqual(PartParserUtil.parse_value('lol 20F', 'F'), None)
    with self.assertRaises(PartParserUtil.ParseError):
      self.assertEqual(PartParserUtil.parse_value('20F no', 'F'), None)

  def test_parse_tolerance(self) -> None:
    self.assertEqual(PartParserUtil.parse_tolerance('±100%'), (-1, 1))
    self.assertEqual(PartParserUtil.parse_tolerance('±10%'), (-0.1, 0.1))
    self.assertEqual(PartParserUtil.parse_tolerance('±10 %'), (-0.1, 0.1))
    self.assertEqual(PartParserUtil.parse_tolerance('±42.1 ppm'), (-42.1e-6, 42.1e-6))
