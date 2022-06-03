from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TypeVar, NamedTuple, Optional, Union, List, Tuple, Generic, Callable

import edgir
from .Array import Vector
from .ArrayExpr import ArrayExpr
from .Blocks import BlockElaborationState
from .Exceptions import BlockDefinitionError
from .IdentityDict import IdentityDict
from .Core import non_library, SubElementDict
from .ConstraintExpr import ConstraintExpr
from .Ports import BasePort, Port
from .HierarchyBlock import Block


# These define internal data structures for multipack components.
# The external interface is the typical blocks and constraints, except for the array case where
# there is no standard construct, and these are exposed as the interface.
# The overall goal is to look and feel like array ports, even if the implementation is different.

class PackedBlockPartBase(metaclass=ABCMeta):
  """Abstract base class for any packed block (part), defining common APIs"""
  @abstractmethod
  def name(self) -> str: ...  # user-friendly (non-ref) name in parent
  @abstractmethod
  def parent(self) -> MultipackBlock: ...  # returns the containing multipack device


class PackedPortBase(metaclass=ABCMeta):
  """Abstract base class for a port on a packed block, defining common APIs"""
  @abstractmethod
  def name(self) -> str: ...  # name of port in parent
  @abstractmethod
  def ref(self, multipack_ref_base: edgir.LocalPath) -> edgir.LocalPath: ...  # ref of this port


class PackedParamBase(metaclass=ABCMeta):
  """Abstract base class for a param on a packed block, defining common APIs"""
  @abstractmethod
  def name(self) -> str: ...  # name of param in parent
  @abstractmethod
  def ref(self, multipack_ref_base: edgir.LocalPath) -> edgir.LocalPath: ...  # ref of this param - even if an array


class PackedBlockPart(PackedBlockPartBase):  # internal API
  def __init__(self, parent: MultipackBlock):
    self.container = parent

  def name(self) -> str:
    return self.parent()._name_of(self)

  def parent(self) -> MultipackBlock:
    return self.container


class PackedBlockAllocate(PackedBlockPartBase):  # DesignTop API
  def __init__(self, parent: MultipackBlock, suggested_name: str):
    self.container = parent
    self.suggested_name = suggested_name  # required for now, so ports on the same part are enforced consistent

  def name(self) -> str:
    return f"{self.parent()._name_of(self)}[{self.suggested_name}]"

  def parent(self) -> MultipackBlock:
    return self.container


class PackedBlockParam(PackedParamBase):  # MultipackBlock API; a parameter on a single (non-array) packed part
  def __init__(self, param: ConstraintExpr, part_parent: Block):
    self.param = param
    self.part_parent = part_parent

  def name(self) -> str:
    return self.part_parent._name_of(self.param)

  def ref(self, multipack_ref_base: edgir.LocalPath) -> edgir.LocalPath:
    return self.part_parent._get_ref_map(multipack_ref_base)[self.param]


class PackedBlockParamArray(PackedParamBase):  # MultipackBlock API; packed-array parameter on an array of parts
  def __init__(self, param: ConstraintExpr, elt_parent: Block, part_parent: PackedBlockArray):
    self.param = param
    self.elt_parent = elt_parent
    self.part_parent = part_parent

  def name(self) -> str:
    return self.elt_parent._name_of(self.param)

  def ref(self, multipack_ref_base: edgir.LocalPath) -> edgir.LocalPath:
    return self.elt_parent._get_ref_map(multipack_ref_base)[self.param]


class PackedBlockParamReplicate(PackedParamBase):  # MultipackBlock API; replicated parameter for an array of parts
  def __init__(self, param: ConstraintExpr, elt_parent: Block, part_parent: PackedBlockArray):
    self.param = param
    self.elt_parent = elt_parent
    self.part_parent = part_parent

  def name(self) -> str:
    return self.elt_parent._name_of(self.param)

  def ref(self, multipack_ref_base: edgir.LocalPath) -> edgir.LocalPath:
    return self.elt_parent._get_ref_map(multipack_ref_base)[self.param]


class PackedBlockPort(PackedPortBase):  # MultipackBlock API; a port on a single (non-array) packed part
  def __init__(self, port: BasePort, part_parent: Block):
    self.port = port
    self.part_parent = part_parent

  def name(self) -> str:
    return self.part_parent._name_of(self.port)

  def ref(self, multipack_ref_base: edgir.LocalPath) -> edgir.LocalPath:
    return self.part_parent._get_ref_map(multipack_ref_base)[self.port]


class PackedBlockPortArray(PackedPortBase):  # MultipackBlock API; packed-array parameter on an array of parts
  def __init__(self, port: BasePort, elt_parent: Block, part_parent: PackedBlockArray):
    self.port = port
    self.elt_parent = elt_parent
    self.part_parent = part_parent

  def name(self) -> str:
    return self.elt_parent._name_of(self.port)

  def ref(self, multipack_ref_base: edgir.LocalPath) -> edgir.LocalPath:
    return self.elt_parent._get_ref_map(multipack_ref_base)[self.port]


PackedBlockElementType = TypeVar('PackedBlockElementType', bound=Block)
class PackedBlockArray(PackedBlockPartBase, Generic[PackedBlockElementType]):
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

  def allocate(self, suggested_name: Optional[str] = None) -> PackedBlockAllocate:
    """External API, to request a new instance for an array element / packed part."""
    assert self._parent is not None, "no parent set, cannot allocate"
    return PackedBlockAllocate(self, suggested_name)

  # TODO does this need to return a narrower type?
  # TODO would it be useful to return a proper Vector type, instead of this special PackedBlockPortArray?
  def ports_array(self, selector: Callable[[PackedBlockElementType], Port]) -> PackedBlockPortArray:
    """Return an array of ports, packed from the selected port of each array element."""
    assert self._elt_sample is not None, "no sample element set, cannot allocate"
    return PackedBlockPortArray(self, selector(self._elt_sample))

  # TODO does this need to return a narrower type?
  # TODO would it be useful to return a proper ConstraintExpr type, instead of this special PackedBlockParamArray?
  def params_array(self, selector: Callable[[PackedBlockElementType], ConstraintExpr]) -> PackedBlockParamArray:
    """Return an array of params, packed from the selected param of each array element."""
    assert self._elt_sample is not None, "no sample element set, cannot allocate"
    return PackedBlockParamArray(self, selector(self._elt_sample))

  # TODO does this need to return a narrower type?
  # TODO would it be useful to return a proper ConstraintExpr type, instead of this special PackedBlockParamArray?
  def params(self, selector: Callable[[PackedBlockElementType], ConstraintExpr]) -> PackedBlockParam:
    """Return the selected param on each array element. Only valid for unpacked assign, where the assign
    is replicated to the selected param on each packed block."""
    assert self._elt_sample is not None, "no sample element set, cannot allocate"
    return PackedBlockParam(self, selector(self._elt_sample))


class MultipackPackingRule(NamedTuple):
  tunnel_exports: IdentityDict[BasePort, PackedPortBase]  # exterior port -> packed block port
  tunnel_assigns: IdentityDict[ConstraintExpr, PackedParamBase]  # my param -> packed block param
  tunnel_unpack_assigns: IdentityDict[ConstraintExpr, PackedParamBase]  # my param -> packed block param


PackedBlockTypes = Union[Block, PackedBlockArray]


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
    self._packed_blocks: SubElementDict[PackedBlockTypes] = self.manager.new_dict((Block, PackedBlockArray))
    # TODO should these be defined in terms of Refs?
    # packed block -> (exterior port -> packed block port)
    self._packed_connects_by_packed_block = IdentityDict[PackedBlockTypes, IdentityDict[BasePort, PackedPortBase]]()
    # packed block -> (self param -> packed param) (reverse of assign direction)
    self._packed_assigns_by_packed_block = IdentityDict[PackedBlockTypes, IdentityDict[ConstraintExpr, PackedParamBase]]()
    # packed block -> (self param -> packed param)
    self._unpacked_assigns_by_packed_block = IdentityDict[PackedBlockTypes, IdentityDict[ConstraintExpr, PackedParamBase]]()

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
    self._packed_connects_by_packed_block[elt] = IdentityDict[BasePort, PackedPortBase]()
    self._packed_assigns_by_packed_block[elt] = IdentityDict[ConstraintExpr, PackedParamBase]()
    self._unpacked_assigns_by_packed_block[elt] = IdentityDict[ConstraintExpr, PackedParamBase]()

    return elt  # type: ignore

  def packed_connect(self, exterior_port: BasePort, packed_port: Union[BasePort, PackedBlockPortArray]) -> None:
    """Defines a packing rule specified as a virtual connection between an exterior port and a PackedBlock port."""
    if self._elaboration_state != BlockElaborationState.init:
      raise BlockDefinitionError(self, "can only define multipack in init")

    if isinstance(packed_port, BasePort):
      assert type(exterior_port) == type(packed_port), "packed_connect ports must be of the same type"
      block_parent = packed_port._block_parent()
      assert isinstance(block_parent, Block)
      self._packed_connects_by_packed_block[block_parent][exterior_port] = packed_port
    elif isinstance(packed_port, PackedBlockPortArray):
      assert isinstance(exterior_port, Vector), "can only connect vector from packed port array"
      assert type(exterior_port._elt_sample) == type(packed_port.port), "packed_connect ports must be of the same type"
      self._packed_connects_by_packed_block[packed_port.parent][exterior_port] = packed_port
    else:
      raise TypeError()

  def packed_assign(self, self_param: ConstraintExpr, packed_param: Union[ConstraintExpr, PackedParamBase]) -> None:
    """Defines a packing rule assigning my parameter from a PackedBlock parameter.
    IMPORTANT: for packed arrays, no ordering on elements is guaranteed, and must be treated as an unordered set."""
    if self._elaboration_state != BlockElaborationState.init:
      raise BlockDefinitionError(self, "can only define multipack in init")
    if isinstance(packed_param, ConstraintExpr):
      assert type(self_param) == type(packed_param), "packed_assign parameters must be of the same type"
      block_parent = packed_param.parent
      assert isinstance(block_parent, Block)
      self._packed_assigns_by_packed_block[block_parent][self_param] = packed_param
    elif isinstance(packed_param, PackedBlockParamArray):
      assert isinstance(self_param, ArrayExpr), "can only assign array expr from packed param array"
      assert self_param._elt_type == type(packed_param.param), "packed_assign parameters must be of the same type"
      self._packed_assigns_by_packed_block[packed_param.parent][self_param] = packed_param
    else:
      raise TypeError()

  def unpacked_assign(self, packed_param: Union[ConstraintExpr, PackedParamBase], self_param: ConstraintExpr) -> None:
    """Defines an (un)packing rule assigning a Packed parameter from my parameter (reverse of packed_assign).
    Only direct parameter-to-parameter assignment allowed, even for packed block arrays,
    """
    if self._elaboration_state != BlockElaborationState.init:
      raise BlockDefinitionError(self, "can only define multipack in init")
    if isinstance(packed_param, ConstraintExpr):
      assert type(packed_param) == type(self_param), "unpacked_assign parameters must be of the same type"
      block_parent = packed_param.parent
      assert isinstance(block_parent, Block)
      self._unpacked_assigns_by_packed_block[block_parent][self_param] = packed_param
    elif isinstance(packed_param, PackedBlockParam):
      assert type(packed_param.param) == type(self_param), "unpacked_assign parameters must be of the same type"
      self._unpacked_assigns_by_packed_block[packed_param.parent][self_param] = packed_param
    else:
      raise TypeError()

  def _get_block_packing_rule(self, packed_part: Union[Block, PackedBlockAllocate]) -> MultipackPackingRule:
    """Internal API, returns the packing rules (tunnel exports and assigns) for a constituent PackedPart."""
    self._packed_blocks.finalize()
    if isinstance(packed_part, PackedBlockAllocate):
      packed_block: PackedBlockTypes = packed_part.parent
    else:
      packed_block = packed_part

    return MultipackPackingRule(
      self._packed_connects_by_packed_block[packed_block],
      self._packed_assigns_by_packed_block[packed_block],
      self._unpacked_assigns_by_packed_block[packed_block]
    )
