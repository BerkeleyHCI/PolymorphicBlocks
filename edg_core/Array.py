from __future__ import annotations

from typing import *

import edgir
from .IdentityDict import IdentityDict
from .Core import Refable, non_library
from .ConstraintExpr import NumericOp, BoolOp, EqOp, OrdOp, RangeSetOp, BoolExpr, ConstraintExpr, Binding, \
  UnaryOpBinding, UnarySetOpBinding, BinaryOpBinding, BinarySetOpBinding, \
  FloatExpr, RangeExpr, StringExpr, \
  ParamBinding, IntExpr, NumLikeExpr, RangeLike
from .Binding import LengthBinding, BinaryOpBinding, ElementsBinding
from .Ports import BaseContainerPort, BasePort, Port
from .Builder import builder


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


class SampleElementBinding(Binding):
  def __init__(self):
    super().__init__()

  def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]:  # element should be returned by the containing ConstraintExpr
    return []

  def expr_to_proto(self, expr: ConstraintExpr, ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.ValueExpr:
    raise ValueError  # can't be used directly


SelfType = TypeVar('SelfType', bound='ArrayExpr')
ArrayType = TypeVar('ArrayType', bound=ConstraintExpr)
class ArrayExpr(ConstraintExpr[Any, Any], Generic[ArrayType]):
  def __init__(self, elt: ArrayType) -> None:
    super().__init__()
    # TODO: should array_type really be bound?
    self.elt: ArrayType = elt._new_bind(SampleElementBinding())

  def _new_bind(self: SelfType, binding: Binding) -> SelfType:
    # TODO dedup w/ ConstraintExpr, but here the constructor arg is elt
    clone: SelfType = type(self)(self.elt)
    clone.binding = binding
    return clone

  def _bind(self: SelfType, binding: Binding) -> SelfType:
    # TODO dedup w/ ConstraintExpr, but here the constructor arg is elt
    assert not self._is_bound()
    assert builder.get_curr_context() is self.parent, f"can't clone in original context {self.parent} to different new context {builder.get_curr_context()}"
    if not isinstance(binding, ParamBinding):
      assert self.initializer is None, "Only Parameters may have initializers"
    clone: SelfType = type(self)(self.elt)
    clone.binding = binding
    return clone

  @classmethod
  def _to_expr_type(cls, input: ArrayExpr) -> ArrayExpr:
    return input

  def _decl_to_proto(self) -> edgir.ValInit:
    raise ValueError  # currently not possible to declare an array in the frontend

  def _create_unary_set_op(self, op: Union[NumericOp,BoolOp,RangeSetOp]) -> ArrayType:
    return self.elt._new_bind(UnarySetOpBinding(self, op))

  def sum(self) -> ArrayType:
    return self._create_unary_set_op(NumericOp.sum)

  def min(self) -> FloatExpr:
    return FloatExpr()._new_bind(UnarySetOpBinding(self, RangeSetOp.min))

  def max(self) -> FloatExpr:
    return FloatExpr()._new_bind(UnarySetOpBinding(self, RangeSetOp.max))

  def intersection(self) -> ArrayType:
    return self._create_unary_set_op(RangeSetOp.intersection)

  def hull(self) -> ArrayType:
    return self._create_unary_set_op(RangeSetOp.hull)

  def equal_any(self) -> ArrayType:
    return self._create_unary_set_op(RangeSetOp.equal_any)

  # TODO: not sure if ArrayType is being checked properly =(
  def any(self: ArrayExpr[BoolExpr]) -> BoolExpr:
    return BoolExpr()._new_bind(UnarySetOpBinding(self, BoolOp.op_or))

  def all(self: ArrayExpr[BoolExpr]) -> BoolExpr:
    return BoolExpr()._new_bind(UnarySetOpBinding(self, BoolOp.op_and))


class ArrayRangeExpr(ArrayExpr[RangeExpr]):
  def _create_binary_set_op(self,
                        lhs: ConstraintExpr,
                        rhs: ConstraintExpr,
                        op: NumericOp) -> ArrayRangeExpr:
    """Creates a new expression that is the result of a binary operation on inputs, and returns my own type.
    Any operand can be of any type (eg, scalar-array, array-array, array-scalar), and it is up to the caller
    to ensure this makes sense. No type checking happens here."""
    assert lhs._is_bound() and rhs._is_bound()
    return self._new_bind(BinarySetOpBinding(lhs, rhs, op))

  # TODO support pointwise multiply in the future
  def __rtruediv__(self, other: RangeLike) -> ArrayRangeExpr:
    """Broadcast-pointwise invert-and-multiply (division with array as rhs)"""
    return self._create_binary_set_op(
      self._create_unary_set_op(NumericOp.invert), RangeExpr._to_expr_type(other), NumericOp.mul)


@non_library
class BaseVector(BaseContainerPort):
  def _get_elt_sample(self) -> BasePort:
    pass


# A 'fake'/'intermediate'/'view' vector object used as a return in map_extract operations.
VectorType = TypeVar('VectorType', bound='BasePort', covariant=True)
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
    assert base.parent is not None  # to satisfy type checker, though kind of duplicates _is_bound
    self._bind_in_place(base.parent)

  def _get_elt_sample(self) -> BasePort:
    return self.target

  def _instance_to_proto(self) -> edgir.PortLike:
    raise RuntimeError()  # this doesn't generate into a library element

  def _def_to_proto(self) -> edgir.PortTypes:
    raise RuntimeError()  # this doesn't generate into a library element

  def _type_of(self) -> Hashable:
    return (self.target._type_of(),)


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
    self._elt_sample = tpe._bind(self, ignore_context=True)
    self._elts: Optional[Dict[str, VectorType]] = None
    self._allocates: List[VectorType] = []  # used to track .allocate() for ref_map purposes

    self._length = IntExpr()._bind(LengthBinding(self))
    self._elements = ArrayExpr(StringExpr())._bind(ElementsBinding(self))

  def __repr__(self) -> str:
    # TODO dedup w/ Core.__repr__
    # but this can't depend on get_def_name since that crashes
    return "Array[%s]@%02x" % (self._elt_sample, (id(self) // 4) & 0xff)

  def _get_elt_sample(self) -> BasePort:
    return self._elt_sample

  def _get_def_name(self) -> str:
    raise RuntimeError()  # this doesn't generate into a library element

  def _instance_to_proto(self) -> edgir.PortLike:
    pb = edgir.PortLike()
    pb.array.self_class.target.name = self._elt_sample._get_def_name()
    if self._elts is not None:
      array_ports = pb.array.ports.ports
      for name, elt in self._elts.items():
        array_ports[name].CopyFrom(elt._instance_to_proto())
    return pb

  def _def_to_proto(self) -> edgir.PortTypes:
    raise RuntimeError()  # this doesn't generate into a library element

  def _get_ref_map(self, prefix: edgir.LocalPath) -> IdentityDict[Refable, edgir.LocalPath]:
    elts_items = self._elts.items() if self._elts is not None else []
    return super()._get_ref_map(prefix) + IdentityDict(
      [(self._length, edgir.localpath_concat(prefix, edgir.LENGTH)),
       (self._elements, edgir.localpath_concat(prefix, edgir.ELEMENTS))],
      *[elt._get_ref_map(edgir.localpath_concat(prefix, index)) for (index, elt) in elts_items]) + IdentityDict(
      *[elt._get_ref_map(edgir.localpath_concat(prefix, edgir.Allocate())) for elt in self._allocates]
    )

  def _get_contained_ref_map(self) -> IdentityDict[Refable, edgir.LocalPath]:
    return self._elt_sample._get_ref_map(edgir.LocalPath())

  def init_elts(self, length: Union[List[str], int]) -> None:
    """Initializes elements of this array (if this is not to be a dynamically-sized array - including
    when subclassing a base class with a dynamically-sized array) with either the number of elements
    or with specific names of elements.
    Items can be accessed (from inside the containing block) by indexing (__getitem__).
    Can only be called from the block defining this port (where this is a boundary port),
    and this port must be bound."""
    assert self._is_bound(), "not bound, can't create array elements"
    assert builder.get_curr_block() is self._block_parent(), "can only init_elts in block parent of array"
    assert self._elts is None, "cannot double init_elts"
    if isinstance(length, int):
      length_list = [str(elt) for elt in range(length)]
    elif isinstance(length, list):
      length_list = length
    else:
      raise TypeError(f"unknown length type {length}")

    self._elts = {elt: self._tpe._bind(self, ignore_context=True) for elt in length_list}

  def elts(self) -> Dict[str, VectorType]:
    """Returns the items (as a list of (str, Port)) resulting from init_elts."""
    assert self._elts is not None, "must init_elts before getting items"
    assert builder.get_curr_block() is self._block_parent(), "can only get items in block parent of array"
    return self._elts

  def allocate(self) -> VectorType:
    """Returns a new port of this Vector.
    Can only be called from the block containing the block containing this as a port (used to allocate a
    port of an internal block).
    To create elements where this is the boundary block, use init_elts(...).
    """
    from .HierarchyBlock import Block
    assert self._is_bound(), "not bound, can't allocate array elements"
    block_parent = self._block_parent()
    assert isinstance(block_parent, Block), "can only allocate from ports of a Block"
    assert builder.get_curr_block() is block_parent.parent, "can only allocate ports of internal blocks"
    # self._elts is ignored, since that defines the inner-facing behavior, which this is outer-facing behavior
    allocated = self._tpe._bind(self, ignore_context=True)
    self._allocates.append(allocated)
    return allocated

  def allocate_vector(self) -> Vector[VectorType]:
    """Returns a new dynamic-length, array-port slice of this Vector.
    Can only be called from the block containing the block containing this as a port (used to allocate a
    port of an internal block).
    """
    raise NotImplementedError

  def length(self) -> IntExpr:
    return self._length

  def elements(self) -> ArrayExpr[StringExpr]:
    return self._elements

  def _type_of(self) -> Hashable:
    return (self._elt_sample._type_of(),)

  ExtractConstraintType = TypeVar('ExtractConstraintType', bound=ConstraintExpr)
  ExtractPortType = TypeVar('ExtractPortType', bound=BasePort)
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
