import unittest

from .TransformUtil import Path


class PathTestCase(unittest.TestCase):
  def test_startswith(self) -> None:
    path = Path.empty()
    self.assertTrue(path.append_block('a', 'b').startswith(path.append_block('a')))
    self.assertFalse(path.append_block('a').startswith(path.append_block('a', 'b')))
    self.assertTrue(path.append_block('a').startswith(path.append_block('a')))
    self.assertTrue(path.append_block('a', 'b').startswith(path.append_block('a', 'b')))

    self.assertFalse(path.append_block('a').startswith(path.append_link('a')))

    self.assertTrue(path.append_block('a').append_link('b').startswith(path.append_block('a')))
    self.assertTrue(path.append_block('a').append_link('b').startswith(path.append_block('a').append_link('b')))
    self.assertTrue(path.append_block('a').append_link('b', 'c').startswith(path.append_block('a').append_link('b')))
    self.assertTrue(path.append_block('a').append_link('b', 'c').startswith(path.append_block('a').append_link('b', 'c')))
    self.assertFalse(path.append_block('a').append_link('b').startswith(path.append_link('b')))
    self.assertFalse(path.append_block('a').append_link('b').startswith(path.append_block('a', 'b')))
