from __future__ import annotations

from typing import *

import edgir
from .Builder import builder
from .ConstraintExpr import ConstraintExpr, IntLike, FloatExpr, FloatLike, RangeExpr, RangeLike, \
  BoolExpr, BoolLike, StringLike, \
  NumericOp, BoolOp, RangeSetOp, Binding, UnarySetOpBinding, BinarySetOpBinding, ParamBinding, StringExpr, \
  ConstraintExtractable, ConstraintAssignable
from .Core import Refable
from .IdentityDict import IdentityDict
from .Ports import BasePort
from .Range import Range


class SampleElementBinding(Binding):
  def __init__(self):
    super().__init__()

  def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]:  # element should be returned by the containing ConstraintExpr
    return []

  def expr_to_proto(self, expr: ConstraintExpr, ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.ValueExpr:
    raise ValueError  # can't be used directly


SelfType = TypeVar('SelfType', bound='ArrayExpr')
ArrayEltType = TypeVar('ArrayEltType', bound=ConstraintExpr, covariant=True)
ArrayWrappedType = TypeVar('ArrayWrappedType', covariant=True)
ArrayCastableType = TypeVar('ArrayCastableType', contravariant=True)
class ArrayExpr(ConstraintExpr, Generic[ArrayEltType]):
  _elt_sample: ArrayEltType

  def _new_bind(self: SelfType, binding: Binding) -> SelfType:  # type: ignore
    # TODO dedup w/ ConstraintExpr, but here the constructor arg is elt
    clone: SelfType = type(self)(self._elt_sample)
    clone.binding = binding
    return clone

  def _bind(self: SelfType, binding: Binding) -> SelfType:  # type: ignore
    # TODO dedup w/ ConstraintExpr, but here the constructor arg is elt
    assert not self._is_bound()
    assert builder.get_curr_context() is self.parent, f"can't clone in original context {self.parent} to different new context {builder.get_curr_context()}"
    if not isinstance(binding, ParamBinding):
      assert self.initializer is None, "Only Parameters may have initializers"
    clone: SelfType = type(self)(self._elt_sample)
    clone.binding = binding
    return clone

  def _decl_to_proto(self) -> edgir.ValInit:
    raise ValueError  # currently not possible to declare an array in the frontend

  def _create_unary_set_op(self, op: Union[NumericOp,BoolOp,RangeSetOp]) -> ArrayEltType:
    return self._elt_sample._new_bind(UnarySetOpBinding(self, op))

  def sum(self) -> ArrayEltType:
    return self._create_unary_set_op(NumericOp.sum)

  def min(self) -> FloatExpr:
    return FloatExpr()._new_bind(UnarySetOpBinding(self, RangeSetOp.min))

  def max(self) -> FloatExpr:
    return FloatExpr()._new_bind(UnarySetOpBinding(self, RangeSetOp.max))

  def intersection(self) -> ArrayEltType:
    return self._create_unary_set_op(RangeSetOp.intersection)

  def hull(self) -> ArrayEltType:
    return self._create_unary_set_op(RangeSetOp.hull)


ArrayBoolLike = Union['ArrayBoolExpr', List[BoolLike]]
class ArrayBoolExpr(ArrayExpr[BoolExpr], ConstraintExtractable[List[bool], ArrayBoolLike], ConstraintAssignable[ArrayBoolLike]):
  @classmethod
  def _to_expr_type(cls, input):
    raise NotImplementedError

  def __init__(self, initializer = None):
    super().__init__(initializer)
    self._elt_sample = BoolExpr()._new_bind(SampleElementBinding())

  def any(self) -> BoolExpr:
    return BoolExpr()._new_bind(UnarySetOpBinding(self, BoolOp.op_or))

  def all(self) -> BoolExpr:
    return BoolExpr()._new_bind(UnarySetOpBinding(self, BoolOp.op_and))


ArrayRangeLike = Union['ArrayRangeExpr', List[RangeLike]]
class ArrayRangeExpr(ArrayExpr[RangeExpr], ConstraintExtractable[List[RangeLike], ArrayRangeLike], ConstraintAssignable[ArrayRangeLike]):
  @classmethod
  def _to_expr_type(cls, input):
    raise NotImplementedError

  def __init__(self, initializer = None):
    super().__init__(initializer)
    self._elt_sample = RangeExpr()._new_bind(SampleElementBinding())

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


ArrayStringLike = Union['ArrayStringExpr', List[StringLike]]
class ArrayStringExpr(ArrayExpr[StringExpr], ConstraintExtractable[List[str], ArrayStringLike], ConstraintAssignable[ArrayStringLike]):
  @classmethod
  def _to_expr_type(cls, input):
    raise NotImplementedError

  def __init__(self, initializer = None):
    super().__init__(initializer)
    self._elt_sample = StringExpr()._new_bind(SampleElementBinding())
