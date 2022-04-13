from __future__ import annotations

from typing import *

import edgir
from .Builder import builder
from .ConstraintExpr import ConstraintExpr, FloatExpr, RangeExpr, RangeLike, BoolExpr, \
  NumericOp, BoolOp, RangeSetOp, Binding, UnarySetOpBinding, BinarySetOpBinding, ParamBinding
from .Core import Refable
from .IdentityDict import IdentityDict
from .Ports import BasePort
if TYPE_CHECKING:
  from .Array import Vector


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
