import unittest

import csv
import os
from .PartsTable import *


int_column = PartsTableColumn(int)


class PartsTableTest(unittest.TestCase):
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
        int_column: int(row['header1'])
      }
    table = self.table.map_new_columns(parse_int)
    self.assertEqual(table.rows[0][int_column], 1)
    self.assertEqual(table.rows[1][int_column], 2)
    self.assertEqual(table.rows[2][int_column], 3)

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
