from typing import TypeVar

from .HierarchyBlock import Block
from .MultipackBlock import MultipackBlock
from .Refinements import Refinements, DesignPath


class DesignTop(Block):
  """A top-level design, which may not have ports (including exports), but may define refinements.
  """
  def Port(self, *args, **kwargs):
    raise ValueError("Can't create ports on design top")

  def Export(self, *args, **kwargs):
    raise ValueError("Can't create ports on design top")

  def refinements(self) -> Refinements:
    """Defines top-level refinements.
    Subclasses should define refinements by stacking new refinements on a super().refinements() call."""
    return Refinements()

  def multipack(self):
    """Defines multipack packing rules, by defining multipack devices and providing packing connections.
    Subclasses should define multipack by stacking on top of super().multipack()."""
    pass

  PackedBlockType = TypeVar('PackedBlockType', bound=MultipackBlock)
  def PackedBlock(self, tpe: PackedBlockType) -> PackedBlockType:
    """Instantiates a multipack block, that can be used to pack constituent blocks arbitrarily deep in the design."""
    # TODO: additional checks and enforcement beyond what Block provides - eg disallowing .connect operations
    return self.Block(tpe)

  def pack(self, tpe: Block, path: DesignPath) -> None:
    """Packs a block (arbitrarily deep in the design tree, specified as a path) into a PackedBlock multipack block."""
    pass
