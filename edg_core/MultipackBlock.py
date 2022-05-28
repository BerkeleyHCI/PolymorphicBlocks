from __future__ import annotations

from typing import TypeVar

from . import BasePort
from .Core import non_library
from .HierarchyBlock import Block


@non_library
class MultipackBlock(Block):
  """A block that represents a packed single device that is composed of other blocks - for example,
  a dual-pack opamp or quad-pack (or n-pack) resistor array.

  This allows the single element blocks (eg, single opamp or single resistor) to be packed into these as
  a type of cross-hierarchy optimization, specified at the top level.

  While this block can be directly instantiated (and will do what you think) anywhere, using this in libraries
  is not recommended - instead use the single-element blocks (to make libraries as general as possible, without
  premature optimization), then specify the multipack optimization at the top-level.

  This block contains both the implementation (like any normal block - for example, a dual-pack opamp would
  implement the application circuit, containing sub-blocks for both the decoupling cap and the chip) and the
  packing definition (specific to this class - but does not contribute to the block implementation).
  """

  BlockType = TypeVar('BlockType', bound='Block')
  def PackedBlock(self, tpe: BlockType) -> BlockType:
    """Adds a block type that can be packed into this block."""
    pass

  def packed_connect(self):
    """Defines a packing rule specified as a virtual connection between a port on a PackedBlock and
    an exterior port."""
    pass
