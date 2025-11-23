import unittest

from .HierarchyBlock import BlockPrototype, Block


class TestBlockPrototype(Block):
  def __init__(self) -> None:
    super().__init__()
    block_model = Block()
    assert isinstance(block_model, BlockPrototype)
    self.subblock = self.Block(block_model)
    assert isinstance(self.subblock, Block)


class BlockPrototypeTestCase(unittest.TestCase):
  def test_args_access(self) -> None:
    block = BlockPrototype(Block, ('pos1', 'pos2'), {'k1': 'v1', 'k2': 'v2'})
    assert block._tpe == Block
    assert block._args == ('pos1', 'pos2')
    assert block._kwargs == {'k1': 'v1', 'k2': 'v2'}

  def test_attribute_access(self) -> None:
    block = BlockPrototype(Block, (), {})

    with self.assertRaises(AttributeError):
      block.attr

    with self.assertRaises(AttributeError):
        block.attr = 2

  def test_prototype_creation(self) -> None:
    TestBlockPrototype()  # check that assertions inside fire
