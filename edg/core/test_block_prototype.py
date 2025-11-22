import unittest

from .HierarchyBlock import BlockPrototype, Block


class BlockPrototypeTestCase(unittest.TestCase):
  def test_args_access(self) -> None:
    block = BlockPrototype(Block, ['pos1', 'pos2'], {'k1': 'v1', 'k2': 'v2'})
    assert block._tpe == Block
    assert block._args == ['pos1', 'pos2']
    assert block._kwargs == {'k1': 'v1', 'k2': 'v2'}


  def test_attribute_access(self) -> None:
    block = BlockPrototype(Block, [], {})

    with self.assertRaises(AttributeError):
      block.attr

    with self.assertRaises(AttributeError):
        block.attr = 2
