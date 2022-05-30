from __future__ import annotations

from typing import TypeVar, NamedTuple, Optional, Union, List, Tuple, Generic, Callable

from .Array import Vector
from .Blocks import BlockElaborationState
from .Exceptions import BlockDefinitionError
from .IdentityDict import IdentityDict
from .Core import non_library, SubElementDict
from .ConstraintExpr import ConstraintExpr
from .Ports import BasePort, Port
from .HierarchyBlock import Block


class MultipackPackingRule(NamedTuple):
  tunnel_exports: IdentityDict[BasePort, BasePort]  # exterior port -> packed block port
  tunnel_assigns: IdentityDict[ConstraintExpr, ConstraintExpr]  # my param -> packed block param


class PackedBlockPortArray(NamedTuple):
  parent: PackedBlockArray
  port: Port


class PackedBlockParamArray(NamedTuple):
  parent: PackedBlockArray
  param: ConstraintExpr


PackedBlockElementType = TypeVar('PackedBlockElementType', bound=Block)
class PackedBlockArray(Generic[PackedBlockElementType]):
  """A container "block" (for multipack packing only) for an arbitrary-length array of Blocks.
  This is meant to be analogous to Vector (port arrays), though there isn't an use case for this in general
  (non-multipack) core infrastructure yet."""
  def __init__(self, tpe: PackedBlockElementType):
    self._tpe = tpe
    self._elt_sample: Optional[PackedBlockElementType] = None  # inner facing only
    self._parent: Optional[Block] = None
    self._allocates: List[Tuple[Optional[str], Block]] = []  # outer facing only, to track allocate for ref_map

  def _bind(self, parent: Block) -> PackedBlockArray:
    clone = PackedBlockArray(self._tpe)
    clone._parent = parent
    clone._elt_sample = self._tpe._bind(parent)
    return clone

  def allocate(self, suggested_name: Optional[str] = None) -> Block:
    """External API, to request a new instance for an array element / packed part."""
    assert self._parent is not None, "no parent set, cannot allocate"
    allocated = self._tpe._bind(self._parent)
    self._allocates.append((suggested_name, allocated))
    return allocated

  # TODO does this need to return a narrower type?
  # TODO would it be useful to return a proper Vector type, instead of this special PackedBlockPortArray?
  def ports_array(self, selector: Callable[[PackedBlockElementType], Port]) -> PackedBlockPortArray:
    assert self._elt_sample is not None, "no sample element set, cannot allocate"
    return PackedBlockPortArray(self, selector(self._elt_sample))


  # TODO does this need to return a narrower type?
  # TODO would it be useful to return a proper ConstraintExpr type, instead of this special PackedBlockParamArray?
  def params_array(self, selector: Callable[[PackedBlockElementType], ConstraintExpr]) -> PackedBlockParamArray:
    assert self._elt_sample is not None, "no sample element set, cannot allocate"
    return PackedBlockParamArray(self, selector(self._elt_sample))


PackedBlockType = Union[Block, PackedBlockArray]
PackedPortType = Union[Port, PackedBlockPortArray]
PackedParamType = Union[ConstraintExpr, PackedBlockParamArray]


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
  def PackedPart(self, tpe: PackedPartType) -> PackedPartType:
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

    return elt  # type: ignore

  def packed_connect(self, exterior_port: BasePort, packed_port: PackedPortType) -> None:
    """Defines a packing rule specified as a virtual connection between an exterior port and a PackedBlock port."""
    if self._elaboration_state != BlockElaborationState.init:
      raise BlockDefinitionError(self, "can only define multipack in init")
    block_parent = packed_port._block_parent()
    assert isinstance(block_parent, Block)
    self._packed_connects_by_packed_block[block_parent][exterior_port] = packed_port

  def packed_assign(self, self_param: ConstraintExpr, packed_param: PackedParamType) -> None:
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
