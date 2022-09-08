from __future__ import annotations

from typing import *

import edgir
from .Binding import EqOp, ArrayBinding
from .ConstraintExpr import ConstraintExpr, IntLike, FloatExpr, FloatLike, RangeExpr, RangeLike, \
  BoolExpr, BoolLike, StringLike, \
  NumericOp, BoolOp, RangeSetOp, Binding, UnarySetOpBinding, BinarySetOpBinding, StringExpr, IntExpr
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
class ArrayExpr(ConstraintExpr[ArrayWrappedType, ArrayCastableType],
                Generic[ArrayEltType, ArrayWrappedType, ArrayCastableType]):
  """An Array-valued ConstraintExpr (a variable-sized list of ConstraintExpr).
  All the cases are explicitly expanded (eg, ArrayBoolExpr, ArrayIntExpr, ...) because ConstraintExpr requires the
  wrapped-type and castable-type (for example, used in Generator.generator(...) args), yet ArrayExpr also needs the
  element type, and there doesn't seem to be any way to express that these are related. So all three are provided,
  explicitly in the subclasses.
  """
  _elt_type: Type[ArrayEltType]

  @classmethod
  def _from_lit(cls, pb: edgir.ValueLit) -> ArrayWrappedType:
    assert pb.HasField('array')
    return [cls._elt_type._from_lit(sub_pb) for sub_pb in pb.array.elts]  # type: ignore

  @classmethod
  def _to_expr_type(cls: Type[SelfType], input: ArrayCastableType) -> SelfType:
    if isinstance(input, cls):
      assert input._is_bound()
      return input
    elif isinstance(input, list):
      elts = [cls._elt_type._to_expr_type(elt) for elt in input]
      return cls()._bind(ArrayBinding(elts))
    else:
      raise TypeError(f"arg to {cls.__name__} must be ArrayCastableType, got {input} of type {type(input)}")

  @classmethod
  def _decl_to_proto(cls) -> edgir.ValInit:
    pb = edgir.ValInit()
    pb.array.CopyFrom(cls._elt_type._decl_to_proto())
    return pb

  @staticmethod
  def array_of_elt(elt: ConstraintExpr) -> ArrayExpr:
    """Returns the ArrayExpr type that wraps some element expr."""
    if isinstance(elt, BoolExpr):
      return ArrayBoolExpr()
    elif isinstance(elt, IntExpr):
      return ArrayIntExpr()
    elif isinstance(elt, FloatExpr):
      return ArrayFloatExpr()
    elif isinstance(elt, RangeExpr):
      return ArrayRangeExpr()
    elif isinstance(elt, StringExpr):
      return ArrayStringExpr()
    else:
      raise TypeError(f"unknown ConstraintExpr type for wrapped param {elt}")

  def __init__(self, initializer=None):
    super().__init__(initializer)
    self._elt_sample: ArrayWrappedType = self._elt_type()._new_bind(SampleElementBinding())

  def _create_unary_set_op(self, op: Union[NumericOp, BoolOp, RangeSetOp, EqOp]) -> ArrayEltType:
    return self._elt_type._new_bind(UnarySetOpBinding(self, op))

  def all_unique(self) -> BoolExpr:
    return BoolExpr()._new_bind(UnarySetOpBinding(self, EqOp.all_unique))

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
class ArrayBoolExpr(ArrayExpr[BoolExpr, List[bool], ArrayBoolLike]):
  _elt_type = BoolExpr

  def any(self) -> BoolExpr:
    return BoolExpr()._new_bind(UnarySetOpBinding(self, BoolOp.op_or))

  def all(self) -> BoolExpr:
    return BoolExpr()._new_bind(UnarySetOpBinding(self, BoolOp.op_and))


ArrayIntLike = Union['ArrayIntExpr', List[IntLike]]
class ArrayIntExpr(ArrayExpr[IntExpr, List[int], ArrayIntLike]):
  _elt_type = IntExpr


ArrayFloatLike = Union['ArrayFloatExpr', List[FloatLike]]
class ArrayFloatExpr(ArrayExpr[FloatExpr, List[float], ArrayFloatLike]):
  _elt_type = FloatExpr


ArrayRangeLike = Union['ArrayRangeExpr', List[RangeLike]]
class ArrayRangeExpr(ArrayExpr[RangeExpr, List[Range], ArrayRangeLike]):
  _elt_type = RangeExpr

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
  def __rtruediv__(self, other: Union[FloatLike, RangeLike]) -> ArrayRangeExpr:
    """Broadcast-pointwise invert-and-multiply (division with array as rhs)"""
    return self._create_binary_set_op(
      self._create_unary_set_op(NumericOp.invert), RangeExpr._to_expr_type(other), NumericOp.mul)


ArrayStringLike = Union['ArrayStringExpr', List[StringLike]]
class ArrayStringExpr(ArrayExpr[StringExpr, List[str], ArrayStringLike]):
  _elt_type = StringExpr
