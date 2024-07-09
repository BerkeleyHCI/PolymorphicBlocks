from __future__ import annotations

import itertools
from abc import abstractmethod
from typing import *
from deprecated import deprecated

from .. import edgir
from .Binding import LengthBinding, AllocatedBinding
from .Builder import builder
from .ConstraintExpr import BoolExpr, ConstraintExpr, FloatExpr, RangeExpr, StringExpr, IntExpr, Binding
from .Core import Refable, non_library
from .IdentityDict import IdentityDict
from .Ports import BaseContainerPort, BasePort, Port
from .ArrayExpr import ArrayExpr, ArrayRangeExpr, ArrayStringExpr, ArrayBoolExpr, ArrayFloatExpr, ArrayIntExpr


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


class FlattenBinding(Binding):
  def __init__(self, elts: ConstraintExpr):
    super().__init__()
    self.elts = elts

  def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]:
    return [self.elts]

  def expr_to_proto(self, expr: ConstraintExpr, ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.ValueExpr:
    pb = edgir.ValueExpr()
    pb.unary_set.op = edgir.UnarySetExpr.Op.FLATTEN
    pb.unary_set.vals.CopyFrom(self.elts._expr_to_proto(ref_map))
    return pb


@non_library
class BaseVector(BaseContainerPort):
  @abstractmethod
  def _get_elt_sample(self) -> BasePort:
    ...


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
    self._elts: Optional[OrderedDict[str, VectorType]] = None  # concrete elements, for boundary ports
    self._elt_next_index = 0
    self._requests: List[Tuple[Optional[str], BasePort]] = []  # used to track request / request_vector for ref_map

    self._length = IntExpr()._bind(LengthBinding(self))
    self._requested = ArrayStringExpr()._bind(AllocatedBinding(self))

  def __repr__(self) -> str:
    # TODO dedup w/ Core.__repr__
    # but this can't depend on get_def_name since that crashes
    return "Array[%s]@%02x" % (self._elt_sample, (id(self) // 4) & 0xff)

  def __getitem__(self, item: str) -> VectorType:
    """Returns a port previously defined by append_elt, indexed by (required) suggested_name.
    Can only be called from the block defining this port (where this is a boundary port),
    and this port must be bound."""
    assert self._is_bound(), "not bound, can't create array elements"
    assert builder.get_enclosing_block() is self._block_parent(), "can only create elts in block parent of array"
    assert self._elts is not None, "no elts defined"
    return self._elts[item]

  def items(self) -> ItemsView[str, VectorType]:
    assert self._elts is not None, "no elts defined"
    return self._elts.items()

  # unlike most other LibraryElement types, the names are stored in _elts and _allocates
  def _name_of_child(self, subelt: Any, allow_unknown: bool = False) -> str:
    from .HierarchyBlock import Block
    block_parent = self._block_parent()
    assert isinstance(block_parent, Block)

    if builder.get_enclosing_block() is block_parent or builder.get_enclosing_block() is None:
      # in block defining this port (direct elt definition), or in test top
      assert self._elts is not None, "can't get name on undefined vector"
      for (name, elt) in self._elts.items():
        if subelt is elt:
          return name
      if allow_unknown:
        return f"(unknown {subelt.__class__.__name__})"
      else:
        raise ValueError(f"no name for {subelt}")
    elif builder.get_enclosing_block() is block_parent._parent:
      # in block enclosing the block defining this port (allocate required)
      for (i, (suggested_name, allocate_elt)) in enumerate(self._requests):
        if subelt is allocate_elt:
          if suggested_name is not None:
            return suggested_name
          else:
            return f"_allocate_{i}"
      if allow_unknown:
        return f"(unknown {subelt.__class__.__name__})"
      else:
        raise ValueError(f"allocated elt not found {subelt}")
    else:
      raise ValueError(f"unknown context of array")

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
        edgir.add_pair(pb.array.ports.ports, name).CopyFrom(elt._instance_to_proto())
    return pb

  def _def_to_proto(self) -> edgir.PortTypes:
    raise RuntimeError()  # this doesn't generate into a library element

  def _get_ref_map(self, prefix: edgir.LocalPath) -> IdentityDict[Refable, edgir.LocalPath]:
    elts_items = self._elts.items() if self._elts is not None else []

    return super()._get_ref_map(prefix) + IdentityDict[Refable, edgir.LocalPath](
      [(self._length, edgir.localpath_concat(prefix, edgir.LENGTH)),
       (self._requested, edgir.localpath_concat(prefix, edgir.ALLOCATED))],
      *[elt._get_ref_map(edgir.localpath_concat(prefix, index)) for (index, elt) in elts_items]) + IdentityDict(
      *[elt._get_ref_map(edgir.localpath_concat(prefix, edgir.Allocate(suggested_name)))
        for (suggested_name, elt) in self._requests]
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
      self._elts = OrderedDict()

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
      self._elts = OrderedDict()
    if suggested_name is None:
      suggested_name = str(self._elt_next_index)
      self._elt_next_index += 1
    assert suggested_name not in self._elts, f"duplicate Port Vector element name {suggested_name}"

    self._elts[suggested_name] = tpe._bind(self)
    return self._elts[suggested_name]

  @deprecated(reason="renamed to request")
  def allocate(self, suggested_name: Optional[str] = None) -> VectorType:
    return self.request(suggested_name)

  def request(self, suggested_name: Optional[str] = None) -> VectorType:
    """Returns a new port of this Vector.
    Can only be called from the block containing the block containing this as a port (used to allocate a
    port of an internal block).
    To create elements where this is the boundary block, use init_elts(...).
    """
    from .HierarchyBlock import Block
    assert self._is_bound(), "not bound, can't allocate array elements"
    block_parent = self._block_parent()
    assert isinstance(block_parent, Block), "can only allocate from ports of a Block"
    assert builder.get_enclosing_block() is block_parent._parent or builder.get_enclosing_block() is None, \
      "can only allocate ports of internal blocks"  # None case is to allow elaborating in unit tests
    # self._elts is ignored, since that defines the inner-facing behavior, which this is outer-facing behavior
    allocated = type(self._tpe).empty()._bind(self)
    self._requests.append((suggested_name, allocated))
    return allocated

  @deprecated(reason="renamed to request_vector")
  def allocate_vector(self, suggested_name: Optional[str] = None) -> Vector[VectorType]:
    return self.request_vector(suggested_name)

  def request_vector(self, suggested_name: Optional[str] = None) -> Vector[VectorType]:
    """Returns a new dynamic-length, array-port slice of this Vector.
    Can only be called from the block containing the block containing this as a port (used to allocate a
    port of an internal block).
    Can only be used as an array elements sink.
    """
    from .HierarchyBlock import Block
    assert self._is_bound(), "not bound, can't allocate array elements"
    block_parent = self._block_parent()
    assert isinstance(block_parent, Block), "can only allocate from ports of a Block"
    assert builder.get_enclosing_block() is block_parent._parent or builder.get_enclosing_block() is None, \
      "can only allocate ports of internal blocks"  # None case is to allow elaborating in unit tests
    # self._elts is ignored, since that defines the inner-facing behavior, which this is outer-facing behavior
    allocated = Vector(type(self._tpe).empty())._bind(self)
    self._requests.append((suggested_name, allocated))
    return allocated

  def length(self) -> IntExpr:
    return self._length

  @deprecated(reason="renamed to requested")
  def allocated(self) -> ArrayStringExpr:
    return self.requested()

  def requested(self) -> ArrayStringExpr:
    return self._requested

  def _type_of(self) -> Hashable:
    return (self._elt_sample._type_of(),)

  def elt_type(self) -> Type[VectorType]:
    """Returns the type of the element."""
    return type(self._elt_sample)

  SelectorType = TypeVar('SelectorType', bound=ConstraintExpr)
  @staticmethod
  def validate_selector(expected: Type[SelectorType], result: ConstraintExpr) -> SelectorType:
    # TODO check returned type is child
    if not isinstance(result, expected):
      raise TypeError(f"selector must return {expected.__name__}, got {result.__class__.__name__}")
    return result

  ExtractPortType = TypeVar('ExtractPortType', bound=Port)
  # See the note in ArrayExpr for why this is expanded.
  @overload
  def map_extract(self, selector: Callable[[VectorType], BoolExpr]) -> ArrayBoolExpr: ...
  @overload
  def map_extract(self, selector: Callable[[VectorType], IntExpr]) -> ArrayIntExpr: ...
  @overload
  def map_extract(self, selector: Callable[[VectorType], FloatExpr]) -> ArrayFloatExpr: ...
  @overload
  def map_extract(self, selector: Callable[[VectorType], RangeExpr]) -> ArrayRangeExpr: ...
  @overload
  def map_extract(self, selector: Callable[[VectorType], StringExpr]) -> ArrayStringExpr: ...
  @overload
  def map_extract(self, selector: Callable[[VectorType], ExtractPortType]) -> DerivedVector[ExtractPortType]: ...

  def map_extract(self, selector: Callable[[VectorType], Union[ConstraintExpr, BasePort]]) -> Union[ArrayExpr, DerivedVector]:
    param = selector(self._elt_sample)
    if isinstance(param, ConstraintExpr):  # TODO check that returned type is child
      return ArrayExpr.array_of_elt(param)._bind(MapExtractBinding(self, param))
    elif isinstance(param, BasePort):
      return DerivedVector(self, param)
    else:
      raise TypeError(f"selector must return ConstraintExpr or BasePort, got {param} of type {type(param)}")

  def any_connected(self) -> BoolExpr:
    return self.any(lambda port: port.is_connected())

  def any(self, selector: Callable[[VectorType], BoolExpr]) -> BoolExpr:
    param = self.validate_selector(BoolExpr, selector(self._elt_sample))
    return ArrayBoolExpr()._bind(MapExtractBinding(self, param)).any()

  def all(self, selector: Callable[[VectorType], BoolExpr]) -> BoolExpr:
    param = self.validate_selector(BoolExpr, selector(self._elt_sample))
    return ArrayBoolExpr()._bind(MapExtractBinding(self, param)).all()

  @overload
  def sum(self, selector: Callable[[VectorType], RangeExpr]) -> RangeExpr: ...
  @overload
  def sum(self, selector: Callable[[VectorType], FloatExpr]) -> FloatExpr: ...
  def sum(self, selector: Callable[[VectorType], Union[RangeExpr, FloatExpr]]) -> Union[RangeExpr, FloatExpr]:
    param = selector(self._elt_sample)
    if isinstance(param, FloatExpr):
      return ArrayFloatExpr()._bind(MapExtractBinding(self, param)).sum()
    elif isinstance(param, RangeExpr):
      return ArrayRangeExpr()._bind(MapExtractBinding(self, param)).sum()
    else:  # TODO check that returned type is child
      raise TypeError(f"selector must return Float/RangeExpr, got {param} of type {type(param)}")

  def min(self, selector: Callable[[VectorType], FloatExpr]) -> FloatExpr:
    param = self.validate_selector(FloatExpr, selector(self._elt_sample))
    return ArrayFloatExpr()._bind(MapExtractBinding(self, param)).min()

  def max(self, selector: Callable[[VectorType], FloatExpr]) -> FloatExpr:
    param = self.validate_selector(FloatExpr, selector(self._elt_sample))
    return ArrayFloatExpr()._bind(MapExtractBinding(self, param)).max()

  def intersection(self, selector: Callable[[VectorType], RangeExpr]) -> RangeExpr:
    param = self.validate_selector(RangeExpr, selector(self._elt_sample))
    return ArrayRangeExpr()._bind(MapExtractBinding(self, param)).intersection()

  def hull(self, selector: Callable[[VectorType], RangeExpr]) -> RangeExpr:
    param = self.validate_selector(RangeExpr, selector(self._elt_sample))
    return ArrayRangeExpr()._bind(MapExtractBinding(self, param)).hull()

  ArrayType = TypeVar('ArrayType', bound=ArrayExpr)
  def flatten(self, selector: Callable[[VectorType], ArrayType]) -> ArrayType:
    param = self.validate_selector(ArrayExpr, selector(self._elt_sample))
    array_of_arrays = ArrayExpr.array_of_elt(param._elt_sample)._bind(MapExtractBinding(self, param))
    return ArrayExpr.array_of_elt(param._elt_sample)._bind(FlattenBinding(array_of_arrays))  # type: ignore
