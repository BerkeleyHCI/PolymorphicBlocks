import unittest

import csv
import os
from .PartsTable import *


class PartsTableTest(unittest.TestCase):
  INT_COLUMN = PartsTableColumn(int)

  # TODO don't test using internal variables
  def setUp(self) -> None:
    path = os.path.join(os.path.dirname(__file__), 'resources', 'test_table.csv')
    with open(path, newline='') as csvfile:
      reader = csv.DictReader(csvfile)
      self.table = PartsTable.from_dict_rows([row for row in reader])

  def test_product_table(self) -> None:
    self.assertEqual(len(self.table.rows), 3)
    self.assertEqual(self.table.rows[0].value, {'header1': '1', 'header2': 'foo', 'header3': '9'})
    self.assertEqual(self.table.rows[1].value, {'header1': '2', 'header2': 'bar', 'header3': '8'})
    self.assertEqual(self.table.rows[2].value, {'header1': '3', 'header2': 'ducks', 'header3': '7'})

  def test_multiple(self) -> None:
    path = os.path.join(os.path.dirname(__file__), 'resources', 'test_table.csv')
    with open(path, newline='') as csvfile:
      reader = csv.DictReader(csvfile)
      rows = [row for row in reader]
      table = PartsTable.from_dict_rows(rows, rows)

    self.assertEqual(len(table.rows), 6)
    self.assertEqual(table.rows[0].value, {'header1': '1', 'header2': 'foo', 'header3': '9'})
    self.assertEqual(table.rows[1].value, {'header1': '2', 'header2': 'bar', 'header3': '8'})
    self.assertEqual(table.rows[2].value, {'header1': '3', 'header2': 'ducks', 'header3': '7'})
    self.assertEqual(table.rows[3].value, {'header1': '1', 'header2': 'foo', 'header3': '9'})
    self.assertEqual(table.rows[4].value, {'header1': '2', 'header2': 'bar', 'header3': '8'})
    self.assertEqual(table.rows[5].value, {'header1': '3', 'header2': 'ducks', 'header3': '7'})

  def test_derived_filter(self) -> None:
    table = self.table.filter(lambda row: row['header1'] != '2')
    self.assertEqual(len(table.rows), 2)
    self.assertEqual(table.rows[0].value, {'header1': '1', 'header2': 'foo', 'header3': '9'})
    self.assertEqual(table.rows[1].value, {'header1': '3', 'header2': 'ducks', 'header3': '7'})

  def test_derived_column(self) -> None:
    def parse_int(row: PartsTableRow) -> Dict[PartsTableColumn, Any]:
      return {
        self.INT_COLUMN: int(row['header1'])
      }
    table = self.table.map_new_columns(parse_int)
    self.assertEqual(table.rows[0][self.INT_COLUMN], 1)
    self.assertEqual(table.rows[1][self.INT_COLUMN], 2)
    self.assertEqual(table.rows[2][self.INT_COLUMN], 3)

  def test_derived_column_filter(self) -> None:
    def parse_int(row: PartsTableRow) -> Optional[Dict[PartsTableColumn, Any]]:
      if row['header1'] == '2':
        return None
      else:
        return {}
    table = self.table.map_new_columns(parse_int)
    self.assertEqual(len(table.rows), 2)
    self.assertEqual(table.rows[0].value, {'header1': '1', 'header2': 'foo', 'header3': '9'})
    self.assertEqual(table.rows[1].value, {'header1': '3', 'header2': 'ducks', 'header3': '7'})

  def test_sort(self) -> None:
    table = self.table.sort_by(lambda row: row['header3'])
    self.assertEqual(table.rows[0].value, {'header1': '3', 'header2': 'ducks', 'header3': '7'})
    self.assertEqual(table.rows[1].value, {'header1': '2', 'header2': 'bar', 'header3': '8'})
    self.assertEqual(table.rows[2].value, {'header1': '1', 'header2': 'foo', 'header3': '9'})

  def test_first(self) -> None:
    self.assertEqual(self.table.first().value, {'header1': '1', 'header2': 'foo', 'header3': '9'})


class PartsTableUtilsTest(unittest.TestCase):
  def test_parse_value(self) -> None:
    self.assertEqual(PartsTableUtil.parse_value('20 nF', 'F'), 20e-9)
    self.assertEqual(PartsTableUtil.parse_value('20 F', 'F'), 20)
    self.assertEqual(PartsTableUtil.parse_value('20F', 'F'), 20)
    self.assertEqual(PartsTableUtil.parse_value('50 kV', 'V'), 50e3)
    self.assertEqual(PartsTableUtil.parse_value('49.9 GΩ', 'Ω'), 49.9e9)
    self.assertEqual(PartsTableUtil.parse_value('49.9 GΩ', 'Ω'), 49.9e9)

    with self.assertRaises(PartsTableUtil.ParseError):
      self.assertEqual(PartsTableUtil.parse_value('50 kA', 'V'), None)
    with self.assertRaises(PartsTableUtil.ParseError):
      self.assertEqual(PartsTableUtil.parse_value('50 A', 'V'), None)
    with self.assertRaises(PartsTableUtil.ParseError):
      self.assertEqual(PartsTableUtil.parse_value('50 k', 'V'), None)
    with self.assertRaises(PartsTableUtil.ParseError):
      self.assertEqual(PartsTableUtil.parse_value('ducks', 'V'), None)
    with self.assertRaises(PartsTableUtil.ParseError):
      self.assertEqual(PartsTableUtil.parse_value('50.1.2 V', 'V'), None)
    with self.assertRaises(PartsTableUtil.ParseError):
      self.assertEqual(PartsTableUtil.parse_value('lol 20F', 'F'), None)
    with self.assertRaises(PartsTableUtil.ParseError):
      self.assertEqual(PartsTableUtil.parse_value('20F no', 'F'), None)

  def test_parse_tolerance(self) -> None:
    self.assertEqual(PartsTableUtil.parse_tolerance('±100%'), (-1, 1))
    self.assertEqual(PartsTableUtil.parse_tolerance('±10%'), (-0.1, 0.1))
    self.assertEqual(PartsTableUtil.parse_tolerance('±10 %'), (-0.1, 0.1))
    self.assertEqual(PartsTableUtil.parse_tolerance('±42.1 ppm'), (-42.1e-6, 42.1e-6))
