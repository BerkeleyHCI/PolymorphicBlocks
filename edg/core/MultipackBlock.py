from __future__ import annotations

from typing import TypeVar, NamedTuple, Optional, Union, List, Tuple, Generic, Callable, overload
from deprecated import deprecated

from .Array import Vector
from .ArrayExpr import ArrayExpr, ArrayBoolExpr, ArrayStringExpr, ArrayRangeExpr, ArrayFloatExpr, ArrayIntExpr
from .Binding import InitParamBinding
from .Blocks import BlockElaborationState
from .HdlUserExceptions import BlockDefinitionError
from .IdentityDict import IdentityDict
from .Core import non_library, SubElementDict
from .ConstraintExpr import ConstraintExpr, BoolExpr, IntExpr, FloatExpr, RangeExpr, StringExpr
from .Ports import BasePort, Port
from .HierarchyBlock import Block


class PackedBlockAllocate(NamedTuple):
  parent: PackedBlockArray
  suggested_name: Optional[str]


ArrayPortType = TypeVar('ArrayPortType', bound=Port)
class PackedBlockPortArray(Generic[ArrayPortType]):
  def __init__(self, parent: PackedBlockArray, port: ArrayPortType):
    self.parent = parent
    self.port = port


ArrayParamType = TypeVar('ArrayParamType', bound=ConstraintExpr)
class PackedBlockParamArray(Generic[ArrayParamType]):  # an array of parameters from an array of parts
  def __init__(self, parent: PackedBlockArray, param: ArrayParamType):
    self.parent = parent
    self.param = param


class PackedBlockParam(NamedTuple):  # a parameter replicated from an array of blocks
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

  @deprecated(reason="renamed to request")
  def allocate(self, suggested_name: Optional[str] = None) -> PackedBlockAllocate:
    return self.request(suggested_name)

  def request(self, suggested_name: Optional[str] = None) -> PackedBlockAllocate:
    """External API, to request a new instance for an array element / packed part."""
    assert self._parent is not None, "no parent set, cannot allocate"
    return PackedBlockAllocate(self, suggested_name)

  # TODO does this need to return a narrower type?
  # TODO would it be useful to return a proper Vector type, instead of this special PackedBlockPortArray?
  PortType = TypeVar('PortType', bound=Port)
  def ports_array(self, selector: Callable[[PackedBlockElementType], PortType]) -> PackedBlockPortArray[PortType]:
    """Return an array of ports, packed from the selected port of each array element."""
    assert self._elt_sample is not None, "no sample element set, cannot allocate"
    return PackedBlockPortArray(self, selector(self._elt_sample))

  # TODO does this need to return a narrower type?
  # TODO would it be useful to return a proper ConstraintExpr type, instead of this special PackedBlockParamArray?
  ParamType = TypeVar('ParamType', bound=ConstraintExpr)
  def params_array(self, selector: Callable[[PackedBlockElementType], ParamType]) -> PackedBlockParamArray[ParamType]:
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


# These are all internal-ish APIs (within MultipackBlock - NOT in DesignTop)
PackedBlockTypes = Union[Block, PackedBlockArray]
PackedPortTypes = Union[Port, PackedBlockPortArray]
PackedParamTypes = Union[ConstraintExpr, PackedBlockParamArray]
UnpackedParamTypes = Union[ConstraintExpr, PackedBlockParam]


class MultipackPackingRule(NamedTuple):
  tunnel_exports: IdentityDict[BasePort, PackedPortTypes]  # exterior port -> packed block port
  tunnel_assigns: IdentityDict[ConstraintExpr, PackedParamTypes]  # my param -> packed block param
  tunnel_unpack_assigns: IdentityDict[ConstraintExpr, UnpackedParamTypes]  # packed block param -> my param


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
    self._packed_connects_by_packed_block = IdentityDict[PackedBlockTypes, IdentityDict[BasePort, PackedPortTypes]]()
    # packed block -> (self param -> packed param) (reverse of assign direction)
    self._packed_assigns_by_packed_block = IdentityDict[PackedBlockTypes, IdentityDict[ConstraintExpr, PackedParamTypes]]()
    # packed block -> (self param -> packed param)
    self._unpacked_assigns_by_packed_block = IdentityDict[PackedBlockTypes, IdentityDict[ConstraintExpr, UnpackedParamTypes]]()

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
    self._packed_connects_by_packed_block[elt] = IdentityDict[BasePort, PackedPortTypes]()
    self._packed_assigns_by_packed_block[elt] = IdentityDict[ConstraintExpr, PackedParamTypes]()
    self._unpacked_assigns_by_packed_block[elt] = IdentityDict[ConstraintExpr, UnpackedParamTypes]()

    return elt  # type: ignore

  def packed_connect(self, exterior_port: BasePort, packed_port: PackedPortTypes) -> None:
    """Defines a packing rule specified as a virtual connection between an exterior port and a PackedBlock port."""
    if self._elaboration_state != BlockElaborationState.init:
      raise BlockDefinitionError(self, "can only define multipack in init")
    if isinstance(packed_port, Port):
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

  PackedPortType = TypeVar('PackedPortType', bound=Port)
  @overload
  def PackedExport(self, packed_port: PackedPortType, *, optional: bool = False) -> PackedPortType: ...
  @overload
  def PackedExport(self, packed_port: PackedBlockPortArray[PackedPortType], *, optional: bool = False) -> Vector[PackedPortType]: ...

  def PackedExport(self, packed_port: PackedPortTypes, *, optional: bool = False) -> BasePort:
    """Defines a Port in this block, by exporting a port from a packed part or packed part array.
    Like self.Export(...), combines self.Port(...) with self.packed_connect(...)."""
    if isinstance(packed_port, Port):
      new_port: BasePort = self.Port(type(packed_port).empty(), optional=optional)
    elif isinstance(packed_port, PackedBlockPortArray):
      new_port = self.Port(Vector(type(packed_port.port).empty()), optional=optional)
    else:
      raise TypeError()
    self.packed_connect(new_port, packed_port)  # all checks happen here
    return new_port

  def packed_assign(self, self_param: ConstraintExpr, packed_param: PackedParamTypes) -> None:
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

  PackedParamType = TypeVar('PackedParamType', bound=ConstraintExpr)
  @overload
  def PackedParameter(self, packed_param: PackedParamType) -> PackedParamType: ...
  @overload
  def PackedParameter(self, packed_param: PackedBlockParamArray[BoolExpr]) -> ArrayBoolExpr: ...
  @overload
  def PackedParameter(self, packed_param: PackedBlockParamArray[IntExpr]) -> ArrayIntExpr: ...
  @overload
  def PackedParameter(self, packed_param: PackedBlockParamArray[FloatExpr]) -> ArrayFloatExpr: ...
  @overload
  def PackedParameter(self, packed_param: PackedBlockParamArray[RangeExpr]) -> ArrayRangeExpr: ...
  @overload
  def PackedParameter(self, packed_param: PackedBlockParamArray[StringExpr]) -> ArrayStringExpr: ...

  def PackedParameter(self, packed_param: PackedParamTypes) -> ConstraintExpr:
    """Defines a Parameter in this block, by exporting a parameter from a packed part or packed part array.
    Combines self.Parameter(...) with self.packed_assign(...), and additionally compatible with generators
    where self.Parameter(...) would error out."""
    if isinstance(packed_param, ConstraintExpr):
      new_param = type(packed_param)()._bind(InitParamBinding(self))
    elif isinstance(packed_param, PackedBlockParamArray):
      new_param = ArrayExpr.array_of_elt(packed_param.param)._bind(InitParamBinding(self))
    else:
      raise TypeError()
    self.packed_assign(new_param, packed_param)
    self._parameters.register(new_param)
    return new_param

  def unpacked_assign(self, packed_param: UnpackedParamTypes, self_param: ConstraintExpr) -> None:
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
