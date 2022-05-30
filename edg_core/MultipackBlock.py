from __future__ import annotations

from typing import TypeVar, NamedTuple, Optional, Union

from .Blocks import BlockElaborationState
from .Exceptions import BlockDefinitionError
from .IdentityDict import IdentityDict
from .Core import non_library, SubElementDict
from .ConstraintExpr import ConstraintExpr
from .Ports import BasePort
from .HierarchyBlock import Block


class MultipackPackingRule(NamedTuple):
  tunnel_exports: IdentityDict[BasePort, BasePort]  # exterior port -> packed block port
  tunnel_assigns: IdentityDict[ConstraintExpr, ConstraintExpr]  # my param -> packed block param


class PackedBlockArray:
  """A container "block" (for multipack packing only) for an arbitrary-length array of Blocks."""
  def __init__(self, tpe: Block):
    self._tpe = tpe
    self._parent: Optional[Block] = None

  def _bind(self, parent: Block) -> PackedBlockArray:
    clone = PackedBlockArray(self._tpe)
    clone._parent = parent
    return clone

  def allocate(self, suggested_name: Optional[str] = None) -> Block:
    """External API, to request a new instance for an array element / packed part."""
    assert self._parent is not None, "no parent set, cannot allocate"
    return self._tpe._bind(self._parent)


PackedBlockType = Union[Block, PackedBlockArray]


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
  def __init__(self):
    super().__init__()
    self._packed_blocks: SubElementDict[PackedBlockType] = self.manager.new_dict((Block, PackedBlockArray))
    # TODO should these be defined in terms of Refs?
    # packed block -> (exterior port -> packed block port)
    self._packed_connects_by_packed_block = IdentityDict[PackedBlockType, IdentityDict[BasePort, BasePort]]()
    # packed block -> (self param -> packed param)
    self._packed_assigns_by_packed_block = IdentityDict[PackedBlockType, IdentityDict[ConstraintExpr, ConstraintExpr]]()

  PackedPartType = TypeVar('PackedPartType', bound=Union[Block, PackedBlockArray])
  def PackedPart(self, tpe: PackedPartType) -> PackedBlockType:
    """Adds a block type that can be packed into this block.
    The block is a "virtual block" that will not appear in the design tree."""
    if not isinstance(tpe, (Block, PackedBlockArray)):
      raise TypeError(f"param to PackedPart(...) must be Block, got {tpe} of type {type(tpe)}")
    if self._elaboration_state != BlockElaborationState.init:
      raise BlockDefinitionError(self, "can only define multipack in init")

    elt = tpe._bind(self)  # TODO: does this actually need to be bound?
    self._packed_blocks.register(elt)
    self._packed_connects_by_packed_block[elt] = IdentityDict[BasePort, BasePort]()
    self._packed_assigns_by_packed_block[elt] = IdentityDict[ConstraintExpr, ConstraintExpr]()

    return elt

  def packed_connect(self, exterior_port: BasePort, packed_port: BasePort) -> None:
    """Defines a packing rule specified as a virtual connection between an exterior port and a PackedBlock port."""
    if self._elaboration_state != BlockElaborationState.init:
      raise BlockDefinitionError(self, "can only define multipack in init")
    block_parent = packed_port._block_parent()
    assert isinstance(block_parent, Block)
    self._packed_connects_by_packed_block[block_parent][exterior_port] = packed_port

  def packed_assign(self, self_param: ConstraintExpr, packed_param: ConstraintExpr) -> None:
    """Defines a packing rule assigning my parameter from a PackedBlock parameter"""
    if self._elaboration_state != BlockElaborationState.init:
      raise BlockDefinitionError(self, "can only define multipack in init")
    block_parent = packed_param.parent
    assert isinstance(block_parent, Block)
    self._packed_assigns_by_packed_block[block_parent][self_param] = packed_param

  def _get_block_packing_rule(self, packed_part: Block) -> MultipackPackingRule:
    """Internal API, returns the packing rules (tunnel exports and assigns) for a constituent PackedPart."""
    self._packed_blocks.finalize()
    self._packed_finalized = True
    return MultipackPackingRule(
      self._packed_connects_by_packed_block[packed_part],
      self._packed_assigns_by_packed_block[packed_part]
    )
