import unittest

import csv
import os
from .PartsTable import *


class PartsTableTest(unittest.TestCase):
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

  # def test_derived_column(self) -> None:
  #   table = self.table.derived_column('header1_num', ParseValue(Column('header1'), ''))
  #   self.assertEqual(table.header, ['header1', 'header2', 'header3', 'header1_num'])
  #   self.assertEqual(table.rows, [
  #     ['1', 'foo', '9', 1],
  #     ['2', 'bar', '8', 2],
  #     ['3', 'ducks', '7', 3],
  #   ])
  #
  # def test_range_contains(self) -> None:
  #   table = self.table.derived_column('header1_range', RangeFromUpper(ParseValue(Column('header1'), ''))) \
  #       .filter(RangeContains(RangeFromUpper(Lit(1.5)), Column('header1_range')))
  #   self.assertEqual(table.rows, [
  #     ['1', 'foo', '9', (-float('inf'), 1)],
  #   ])
  #
  # def test_map_dict(self) -> None:
  #   self.assertEqual(MapDict(Lit('foo'), {'foo': 'bar', 'bar': 'foo'})({}), 'bar')
  #   self.assertEqual(MapDict(Lit('bar'), {'foo': 'bar', 'bar': 'foo'})({}), 'foo')
  #   self.assertEqual(MapDict(Lit('lol'), {'foo': 'bar', 'bar': 'foo'})({}), None)
  #
  # def test_sort(self) -> None:
  #   table = self.table.sort(Column('header3'))
  #   self.assertEqual(table.rows, [
  #     ['3', 'ducks', '7'],
  #     ['2', 'bar', '8'],
  #     ['1', 'foo', '9'],
  #   ])
  #
  # def test_first(self) -> None:
  #   self.assertEqual(self.table.first(), {'header1': '1', 'header2': 'foo', 'header3': '9'})
  #
  # def test_regex(self) -> None:
  #   self.assertEqual(FormatRegex(Lit('foo123'), "([\D~\s]+)(\d+)", "{0} {1}")({}), 'foo 123')
  #   self.assertEqual(FormatRegex(Lit('foo123a'), "([\D~\s]+)(\d+)", "{0} {1}")({}), 'foo 123')
  #   self.assertEqual(FormatRegex(Lit('foo123a'), "^([\D~\s]+)(\d+)$", "{0} {1}")({}), None)
  #
  # def test_tolerance(self) -> None:
  #   self.assertEqual(RangeFromTolerance(Lit(10), Lit('±5%'))({}), (10 * .95, 10 * 1.05))
  #   self.assertEqual(RangeFromTolerance(Lit(20), Lit('±25%'))({}), (20 * .75, 20 * 1.25))
  #
  # def test_parse_value(self) -> None:
  #   self.assertEqual(ParseValue(Lit('1.21GW'), 'W')({}), 1.21e9)
  #   self.assertEqual(ParseValue(Lit('18pF'), 'F')({}), 18e-12)
  #   self.assertEqual(ParseValue(Lit('62 mA'), 'A')({}), 62e-3)
  #   self.assertEqual(ParseValue(Lit('4 V'), 'V')({}), 4)
  #   self.assertEqual(ParseValue(Lit('4 A'), 'V')({}), None)
  #
  # def test_column(self) -> None:
  #   self.assertEqual(Column('foo')({'foo': 1, 'bar': 2}), 1)
  #   self.assertEqual(Column('bar')({'foo': '1', 'bar': '2'}), '2')
