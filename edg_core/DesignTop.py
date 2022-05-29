from typing import TypeVar

from .Exceptions import BlockDefinitionError
from .IdentityDict import IdentityDict
from .Blocks import BaseBlockEdgirType, BlockElaborationState
from .HierarchyBlock import Block
from .MultipackBlock import MultipackBlock
from .Refinements import Refinements, DesignPath


class DesignTop(Block):
  """A top-level design, which may not have ports (including exports), but may define refinements.
  """
  def __init__(self) -> None:
    super().__init__()
    self._packed_blocks = IdentityDict[Block, DesignPath]()  # multipack part -> packed block (as path)

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

  # TODO make this non-overriding? - this needs to call multipack after contents
  def _elaborated_def_to_proto(self) -> BaseBlockEdgirType:
    assert self._elaboration_state == BlockElaborationState.post_init
    self._elaboration_state = BlockElaborationState.contents
    self.contents()
    self.multipack()
    self._elaboration_state = BlockElaborationState.post_contents
    return self._def_to_proto()

  def _populate_def_proto_block_contents(self, pb: BaseBlockEdgirType) -> BaseBlockEdgirType:
    """Add multipack constraints"""
    pb = super()._populate_def_proto_block_contents(pb)
    for multipack_part, packed_block in self._packed_blocks.items():
      pass
    return pb

  PackedBlockType = TypeVar('PackedBlockType', bound=MultipackBlock)
  def PackedBlock(self, tpe: PackedBlockType) -> PackedBlockType:
    """Instantiates a multipack block, that can be used to pack constituent blocks arbitrarily deep in the design."""
    # TODO: additional checks and enforcement beyond what Block provides - eg disallowing .connect operations
    return self.Block(tpe)

  def pack(self, multipack_part: Block, path: DesignPath) -> None:
    """Packs a block (arbitrarily deep in the design tree, specified as a path) into a PackedBlock multipack block."""
    if self._elaboration_state not in \
        [BlockElaborationState.init, BlockElaborationState.contents, BlockElaborationState.generate]:
      raise BlockDefinitionError(self, "can only define multipack in init, contents, or generate")
    multipack_block = multipack_part._parent
    assert isinstance(multipack_block, MultipackBlock), "block must be a part of a MultipackBlock"
    assert self._blocks.name_of(multipack_block), "containing MultipackBlock must be a PackedBlock"
    self._packed_blocks[multipack_part] = DesignPath
