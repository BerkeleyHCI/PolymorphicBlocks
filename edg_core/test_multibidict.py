import unittest

from . import *


class MultiBiDictTestCase(unittest.TestCase):
  def test_simple(self) -> None:
    mbd: MultiBiDict[int, str] = MultiBiDict()
    mbd.add(1, 'a')
    mbd.add(2, 'b')
    mbd.add(3, 'c')

    self.assertEqual(mbd.get(1), {'a'})
    self.assertEqual(mbd.get(2), {'b'})
    self.assertEqual(mbd.get(3), {'c'})

    self.assertEqual(mbd.get_by_value('a'), {1})
    self.assertEqual(mbd.get_by_value('b'), {2})
    self.assertEqual(mbd.get_by_value('c'), {3})

  def test_multi(self) -> None:
    mbd: MultiBiDict[int, str] = MultiBiDict()
    mbd.add(1, 'a')
    mbd.add(1, 'aa')
    mbd.add(2, 'b')
    mbd.add(3, 'b')

    self.assertEqual(mbd.get(1), {'a', 'aa'})
    self.assertEqual(mbd.get(2), {'b'})
    self.assertEqual(mbd.get(3), {'b'})

    self.assertEqual(mbd.get_by_value('a'), {1})
    self.assertEqual(mbd.get_by_value('aa'), {1})
    self.assertEqual(mbd.get_by_value('b'), {2, 3})

  def test_overlap(self) -> None:
    mbd: MultiBiDict[int, str] = MultiBiDict()
    mbd.add(1, 'a')
    mbd.add(1, 'aa')
    mbd.add(2, 'aa')

    self.assertEqual(mbd.get(1), {'a', 'aa'})
    self.assertEqual(mbd.get(2), {'aa'})

    self.assertEqual(mbd.get_by_value('a'), {1})
    self.assertEqual(mbd.get_by_value('aa'), {1, 2})
