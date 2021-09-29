from __future__ import annotations

from typing import *

from . import edgir
from .IdentityDict import IdentityDict
from .Core import Refable, non_library
from .ConstraintExpr import BoolExpr, ConstraintExpr, Binding, ReductionOpBinding, ReductionOp, FloatExpr, RangeExpr, \
  ParamBinding, IntExpr, ParamVariableBinding, NumLikeExpr, RangeLike
from .Binding import LengthBinding
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
class ArrayExpr(ConstraintExpr[Any], Generic[ArrayType]):
  def __init__(self, elt: ArrayType) -> None:
    super().__init__()
    # TODO: should array_type really be bound?
    self.elt = elt._new_bind(SampleElementBinding())

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

  def create_reduce_op(self, op: ReductionOp) -> ArrayType:
    return self.elt._new_bind(ReductionOpBinding(self, op))

  def sum(self) -> ArrayType:
    return self.create_reduce_op(ReductionOp.sum)

  def min(self) -> FloatExpr:
    return FloatExpr()._new_bind(ReductionOpBinding(self, ReductionOp.min))

  def max(self) -> FloatExpr:
    return FloatExpr()._new_bind(ReductionOpBinding(self, ReductionOp.max))

  def intersection(self) -> ArrayType:
    return self.create_reduce_op(ReductionOp.intersection)

  def hull(self) -> ArrayType:
    return self.create_reduce_op(ReductionOp.hull)

  def equal_any(self) -> ArrayType:
    return self.create_reduce_op(ReductionOp.equal_any)

  # TODO: not sure if ArrayType is being checked properly =(
  def any(self: ArrayExpr[BoolExpr]) -> BoolExpr:
    return BoolExpr()._new_bind(ReductionOpBinding(self, ReductionOp.op_or))


class ArrayRangeExpr(ArrayExpr[RangeExpr]):
  def __rdiv__(self, other: RangeLike) -> ArrayRangeExpr:
    pass


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
    self.tpe = tpe
    self.elt_sample = tpe._bind(self, ignore_context=True)

    self._length = IntExpr()._bind(ParamVariableBinding(LengthBinding(self)))

  def __repr__(self) -> str:
    # TODO dedup w/ Core.__repr__
    # but this can't depend on get_def_name since that crashes
    return "Array[%s]@%02x" % (self.elt_sample, (id(self) // 4) & 0xff)

  def _get_elt_sample(self) -> BasePort:
    return self.elt_sample

  def _get_def_name(self) -> str:
    raise RuntimeError()  # this doesn't generate into a library element

  def _instance_to_proto(self) -> edgir.PortLike:
    pb = edgir.PortLike()
    pb.array.self_class.target.name = self.elt_sample._get_def_name()
    return pb

  def _def_to_proto(self) -> edgir.PortTypes:
    raise RuntimeError()  # this doesn't generate into a library element

  def _get_contained_ref_map(self) -> IdentityDict[Refable, edgir.LocalPath]:
    return self.elt_sample._get_ref_map(edgir.LocalPath())

  def length(self) -> IntExpr:
    return self._length

  def _type_of(self) -> Hashable:
    return (self.elt_sample._type_of(),)

  ExtractConstraintType = TypeVar('ExtractConstraintType', bound=ConstraintExpr)
  ExtractPortType = TypeVar('ExtractPortType', bound=BasePort)
  @overload
  def map_extract(self, selector: Callable[[VectorType], RangeExpr]) -> ArrayRangeExpr: ...
  @overload
  def map_extract(self, selector: Callable[[VectorType], ExtractConstraintType]) -> ArrayExpr[ExtractConstraintType]: ...
  @overload
  def map_extract(self, selector: Callable[[VectorType], ExtractPortType]) -> DerivedVector[ExtractPortType]: ...

  def map_extract(self, selector: Callable[[VectorType], Union[ConstraintExpr, BasePort]]) -> Union[ArrayExpr, DerivedVector]:
    param = selector(self.elt_sample)
    if isinstance(param, ConstraintExpr):
      return ArrayExpr(param)._bind(MapExtractBinding(self, param))  # TODO check that returned type is child
    elif isinstance(param, BasePort):
      return DerivedVector(self, param)
    else:
      raise TypeError(f"selector to map_extract(...) must return ConstraintExpr or BasePort, got {param} of type {type(param)}")


  def any(self, selector: Callable[[VectorType], BoolExpr]) -> BoolExpr:
    param = selector(self.elt_sample)
    if not isinstance(param, BoolExpr):  # TODO check that returned type is child
      raise TypeError(f"selector to any_true(...) must return BoolExpr, got {param} of type {type(param)}")

    return ArrayExpr(param)._bind(MapExtractBinding(self, param)).any()

  def equal_any(self, selector: Callable[[VectorType], ExtractConstraintType]) -> ExtractConstraintType:
    param = selector(self.elt_sample)
    if not isinstance(param, ConstraintExpr):  # TODO check that returned type is child
      raise TypeError(f"selector to equal_any(...) must return ConstraintExpr, got {param} of type {type(param)}")

    return ArrayExpr(param)._bind(MapExtractBinding(self, param)).equal_any()

  ExtractNumericType = TypeVar('ExtractNumericType', bound=Union[FloatExpr, RangeExpr])
  def sum(self, selector: Callable[[VectorType], ExtractNumericType]) -> ExtractNumericType:
    param = selector(self.elt_sample)
    if not isinstance(param, (FloatExpr, RangeExpr)):  # TODO check that returned type is child
      raise TypeError(f"selector to sum(...) must return Float/RangeExpr, got {param} of type {type(param)}")

    return ArrayExpr(param)._bind(MapExtractBinding(self, param)).sum()  #type:ignore

  def min(self, selector: Callable[[VectorType], FloatExpr]) -> FloatExpr:
    param = selector(self.elt_sample)
    if not isinstance(param, FloatExpr):  # TODO check that returned type is child
      raise TypeError(f"selector to min(...) must return Float, got {param} of type {type(param)}")

    return ArrayExpr(param)._bind(MapExtractBinding(self, param)).min()

  def max(self, selector: Callable[[VectorType], FloatExpr]) -> FloatExpr:
    param = selector(self.elt_sample)
    if not isinstance(param, FloatExpr):  # TODO check that returned type is child
      raise TypeError(f"selector to max(...) must return Float, got {param} of type {type(param)}")

    return ArrayExpr(param)._bind(MapExtractBinding(self, param)).max()

  def intersection(self, selector: Callable[[VectorType], RangeExpr]) -> RangeExpr:
    param = selector(self.elt_sample)
    if not isinstance(param, RangeExpr):  # TODO check that returned type is child
      raise TypeError(f"selector to intersection(...) must return RangeExpr, got {param} of type {type(param)}")

    return ArrayExpr(param)._bind(MapExtractBinding(self, param)).intersection()

  def hull(self, selector: Callable[[VectorType], RangeExpr]) -> RangeExpr:
    param = selector(self.elt_sample)
    if not isinstance(param, RangeExpr):  # TODO check that returned type is child
      raise TypeError(f"selector to hull(...) must return RangeExpr, got {param} of type {type(param)}")

    return ArrayExpr(param)._bind(MapExtractBinding(self, param)).hull()
