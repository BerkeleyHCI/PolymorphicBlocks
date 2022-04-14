from __future__ import annotations

import itertools
from typing import *

import edgir
from .Binding import LengthBinding, AllocatedBinding
from .Builder import builder
from .ConstraintExpr import BoolExpr, ConstraintExpr, FloatExpr, RangeExpr, StringExpr, IntExpr, Binding
from .Core import Refable, non_library
from .IdentityDict import IdentityDict
from .Ports import BaseContainerPort, BasePort, Port
from .ArrayExpr import ArrayExpr, ArrayRangeExpr, ArrayStringExpr


class MapExtractBinding(Binding):
  def __init__(self, container: Vector, elt: ConstraintExpr):
    super().__init__()
    self.container = container
    self.elt = elt

  def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]:
    return [self.container]

  def expr_to_proto(self, expr: ConstraintExpr, ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.ValueExpr:
    contained_map = self.container._get_contained_ref_map()
    pb = edgir.ValueExpr()
    pb.map_extract.container.ref.CopyFrom(ref_map[self.container])  # TODO support arbitrary refs
    pb.map_extract.path.CopyFrom(contained_map[self.elt])
    return pb


@non_library
class BaseVector(BaseContainerPort):
  def _get_elt_sample(self) -> BasePort:
    pass


# A 'fake'/'intermediate'/'view' vector object used as a return in map_extract operations.
VectorType = TypeVar('VectorType', bound='Port')
@non_library
class DerivedVector(BaseVector, Generic[VectorType]):
  # TODO: Library types need to be removed from the type hierarchy, because this does not generate into a library elt
  def __init__(self, base: BaseVector, target: VectorType) -> None:
    if not isinstance(base, BaseVector):
      raise TypeError(f"base of DerivedVector(...) must be BaseVector, got {base} of type {type(base)}")
    if not isinstance(target, BasePort):
      raise TypeError(f"target of DerivedVector(...) must be BasePort, got {target} of type {type(target)}")

    super().__init__()

    assert base._is_bound()
    assert target._is_bound()  # TODO check target in base, TODO check is elt sample type
    self.base = base
    self.target = target
    assert base._parent is not None  # to satisfy type checker, though kind of duplicates _is_bound
    self._bind_in_place(base._parent)

  def _type_of(self) -> Hashable:
    return (self.target._type_of(),)

  def _get_elt_sample(self) -> BasePort:
    return self.target

  def _instance_to_proto(self) -> edgir.PortLike:
    raise RuntimeError()  # this doesn't generate into a library element

  def _def_to_proto(self) -> edgir.PortTypes:
    raise RuntimeError()  # this doesn't generate into a library element

  def _get_initializers(self, path_prefix: List[str]) -> List[Tuple[ConstraintExpr, List[str], ConstraintExpr]]:
    raise RuntimeError()  # should never happen


# An 'elastic' array of ports type, with unspecified length at declaration time, and length
# determined by connections in the parent block.
@non_library
class Vector(BaseVector, Generic[VectorType]):
  # TODO: Library types need to be removed from the type hierarchy, because this does not generate into a library elt
  def __init__(self, tpe: VectorType) -> None:
    if not isinstance(tpe, BasePort):
      raise TypeError(f"arg to Vector(...) must be BasePort, got {tpe} of type {type(tpe)}")

    super().__init__()

    assert not tpe._is_bound()
    self._tpe = tpe
    self._elt_sample = tpe._bind(self)
    self._elts: Optional[Dict[str, VectorType]] = None  # concrete elements, for boundary ports
    self._elt_next_index = 0
    self._allocates: List[Tuple[Optional[str], VectorType]] = []  # used to track .allocate() for ref_map

    self._length = IntExpr()._bind(LengthBinding(self))
    self._allocated = ArrayExpr(StringExpr())._bind(AllocatedBinding(self))

  def __repr__(self) -> str:
    # TODO dedup w/ Core.__repr__
    # but this can't depend on get_def_name since that crashes
    return "Array[%s]@%02x" % (self._elt_sample, (id(self) // 4) & 0xff)

  # unlike most other LibraryElement types, the names are stored in _elts and _allocates
  def _name_of_child(self, subelt: Any) -> str:
    assert self._elts is not None, "can't get name on undefined vector"
    for (name, elt) in self._elts.items():
      if subelt is elt:
        return name
    raise ValueError(f"no name for {subelt}")

  def _get_elt_sample(self) -> BasePort:
    return self._elt_sample

  def _get_def_name(self) -> str:
    raise RuntimeError()  # this doesn't generate into a library element

  def _instance_to_proto(self) -> edgir.PortLike:
    pb = edgir.PortLike()
    pb.array.self_class.target.name = self._elt_sample._get_def_name()
    if self._elts is not None:
      pb.array.ports.SetInParent()  # mark as defined, even if empty
      for name, elt in self._elts.items():
        pb.array.ports.ports[name].CopyFrom(elt._instance_to_proto())
    return pb

  def _def_to_proto(self) -> edgir.PortTypes:
    raise RuntimeError()  # this doesn't generate into a library element

  def _get_ref_map(self, prefix: edgir.LocalPath) -> IdentityDict[Refable, edgir.LocalPath]:
    elts_items = self._elts.items() if self._elts is not None else []

    return super()._get_ref_map(prefix) + IdentityDict(
      [(self._length, edgir.localpath_concat(prefix, edgir.LENGTH)),
       (self._allocated, edgir.localpath_concat(prefix, edgir.ALLOCATED))],
      *[elt._get_ref_map(edgir.localpath_concat(prefix, index)) for (index, elt) in elts_items]) + IdentityDict(
      *[elt._get_ref_map(edgir.localpath_concat(prefix, edgir.Allocate(suggested_name)))
        for (suggested_name, elt) in self._allocates]
    )

  def _get_initializers(self, path_prefix: List[str]) -> List[Tuple[ConstraintExpr, List[str], ConstraintExpr]]:
    if self._elts is not None:
      return list(itertools.chain(*[
        elt._get_initializers(path_prefix + [name]) for (name, elt) in self._elts.items()]))
    else:
      return []

  def _get_contained_ref_map(self) -> IdentityDict[Refable, edgir.LocalPath]:
    return self._elt_sample._get_ref_map(edgir.LocalPath())

  def defined(self) -> None:
    """Marks this vector as defined, even if it is empty. Can be called multiple times, and append_elt can continue
    to be used.
    Can only be called from the block defining this port (where this is a boundary port),
    and this port must be bound."""
    assert self._is_bound(), "not bound, can't create array elements"
    assert builder.get_enclosing_block() is self._block_parent(), "can only create elts in block parent of array"

    if self._elts is None:
      self._elts = {}

  def append_elt(self, tpe: VectorType, suggested_name: Optional[str] = None) -> VectorType:
    """Appends a new element of this array (if this is not to be a dynamically-sized array - including
    when subclassing a base class with a dynamically-sized array) with either the number of elements
    or with specific names of elements.
    Argument is the port model (optionally with initializers) and an optional suggested name.
    Can only be called from the block defining this port (where this is a boundary port),
    and this port must be bound."""
    assert self._is_bound(), "not bound, can't create array elements"
    assert builder.get_enclosing_block() is self._block_parent(), "can only create elts in block parent of array"
    assert type(tpe) is type(self._tpe), f"created elts {type(tpe)} must be same type as array type {type(self._tpe)}"

    if self._elts is None:
      self._elts = {}
    if suggested_name is None:
      suggested_name = str(self._elt_next_index)
      self._elt_next_index += 1
    assert suggested_name not in self._elts, f"duplicate Port Vector element name {suggested_name}"

    self._elts[suggested_name] = tpe._bind(self)
    return self._elts[suggested_name]

  def allocate(self, suggested_name: Optional[str] = None) -> VectorType:
    """Returns a new port of this Vector.
    Can only be called from the block containing the block containing this as a port (used to allocate a
    port of an internal block).
    To create elements where this is the boundary block, use init_elts(...).
    """
    from .HierarchyBlock import Block
    assert self._is_bound(), "not bound, can't allocate array elements"
    block_parent = self._block_parent()
    assert isinstance(block_parent, Block), "can only allocate from ports of a Block"
    assert builder.get_enclosing_block() is block_parent._parent, "can only allocate ports of internal blocks"
    # self._elts is ignored, since that defines the inner-facing behavior, which this is outer-facing behavior
    allocated = type(self._tpe).empty()._bind(self)
    self._allocates.append((suggested_name, allocated))
    return allocated

  def allocate_vector(self) -> Vector[VectorType]:
    """Returns a new dynamic-length, array-port slice of this Vector.
    Can only be called from the block containing the block containing this as a port (used to allocate a
    port of an internal block).
    """
    raise NotImplementedError

  def length(self) -> IntExpr:
    return self._length

  def allocated(self) -> ArrayStringExpr:
    return self._allocated

  def _type_of(self) -> Hashable:
    return (self._elt_sample._type_of(),)

  def elt_type(self) -> Type[VectorType]:
    """Returns the type of the element."""
    return type(self._elt_sample)

  ExtractConstraintType = TypeVar('ExtractConstraintType', bound=ConstraintExpr)
  ExtractPortType = TypeVar('ExtractPortType', bound=Port)
  @overload
  def map_extract(self, selector: Callable[[VectorType], RangeExpr]) -> ArrayRangeExpr: ...
  @overload
  def map_extract(self, selector: Callable[[VectorType], ExtractConstraintType]) -> ArrayExpr[ExtractConstraintType]: ...
  @overload
  def map_extract(self, selector: Callable[[VectorType], ExtractPortType]) -> DerivedVector[ExtractPortType]: ...

  def map_extract(self, selector: Callable[[VectorType], Union[ConstraintExpr, BasePort]]) -> Union[ArrayExpr, DerivedVector]:
    param = selector(self._elt_sample)
    if isinstance(param, RangeExpr):
      return ArrayRangeExpr(param)._bind(MapExtractBinding(self, param))  # TODO check that returned type is child
    elif isinstance(param, ConstraintExpr):
      return ArrayExpr(param)._bind(MapExtractBinding(self, param))  # TODO check that returned type is child
    elif isinstance(param, BasePort):
      return DerivedVector(self, param)
    else:
      raise TypeError(f"selector to map_extract(...) must return ConstraintExpr or BasePort, got {param} of type {type(param)}")


  def any(self, selector: Callable[[VectorType], BoolExpr]) -> BoolExpr:
    param = selector(self._elt_sample)
    if not isinstance(param, BoolExpr):  # TODO check that returned type is child
      raise TypeError(f"selector to any_true(...) must return BoolExpr, got {param} of type {type(param)}")

    return ArrayExpr(param)._bind(MapExtractBinding(self, param)).any()

  def equal_any(self, selector: Callable[[VectorType], ExtractConstraintType]) -> ExtractConstraintType:
    param = selector(self._elt_sample)
    if not isinstance(param, ConstraintExpr):  # TODO check that returned type is child
      raise TypeError(f"selector to equal_any(...) must return ConstraintExpr, got {param} of type {type(param)}")

    return ArrayExpr(param)._bind(MapExtractBinding(self, param)).equal_any()

  ExtractNumericType = TypeVar('ExtractNumericType', bound=Union[FloatExpr, RangeExpr])
  def sum(self, selector: Callable[[VectorType], ExtractNumericType]) -> ExtractNumericType:
    param = selector(self._elt_sample)
    if not isinstance(param, (FloatExpr, RangeExpr)):  # TODO check that returned type is child
      raise TypeError(f"selector to sum(...) must return Float/RangeExpr, got {param} of type {type(param)}")

    return ArrayExpr(param)._bind(MapExtractBinding(self, param)).sum()  #type:ignore

  def min(self, selector: Callable[[VectorType], FloatExpr]) -> FloatExpr:
    param = selector(self._elt_sample)
    if not isinstance(param, FloatExpr):  # TODO check that returned type is child
      raise TypeError(f"selector to min(...) must return Float, got {param} of type {type(param)}")

    return ArrayExpr(param)._bind(MapExtractBinding(self, param)).min()

  def max(self, selector: Callable[[VectorType], FloatExpr]) -> FloatExpr:
    param = selector(self._elt_sample)
    if not isinstance(param, FloatExpr):  # TODO check that returned type is child
      raise TypeError(f"selector to max(...) must return Float, got {param} of type {type(param)}")

    return ArrayExpr(param)._bind(MapExtractBinding(self, param)).max()

  def intersection(self, selector: Callable[[VectorType], RangeExpr]) -> RangeExpr:
    param = selector(self._elt_sample)
    if not isinstance(param, RangeExpr):  # TODO check that returned type is child
      raise TypeError(f"selector to intersection(...) must return RangeExpr, got {param} of type {type(param)}")

    return ArrayExpr(param)._bind(MapExtractBinding(self, param)).intersection()

  def hull(self, selector: Callable[[VectorType], RangeExpr]) -> RangeExpr:
    param = selector(self._elt_sample)
    if not isinstance(param, RangeExpr):  # TODO check that returned type is child
      raise TypeError(f"selector to hull(...) must return RangeExpr, got {param} of type {type(param)}")

    return ArrayExpr(param)._bind(MapExtractBinding(self, param)).hull()
