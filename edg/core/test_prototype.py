import unittest

from .HierarchyBlock import BlockPrototype, Block
from .test_common import TestPortSource
from .Ports import Port, PortPrototype


class TestBlockPrototype(Block):
  def __init__(self) -> None:
    super().__init__()
    port_model = TestPortSource()
    assert isinstance(port_model, PortPrototype)
    self.port = self.Port(port_model)
    assert isinstance(self.port, Port)

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
