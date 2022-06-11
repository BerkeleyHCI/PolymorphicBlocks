from __future__ import annotations

from typing import *

import edgir
from .Binding import ArrayLiteralBinding, StringLiteralBinding, RangeLiteralBinding, FloatLiteralBinding, \
  BoolLiteralBinding, IntLiteralBinding
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

  def _create_unary_set_op(self, op: Union[NumericOp, BoolOp, RangeSetOp]) -> ArrayEltType:
    return self._elt_type._new_bind(UnarySetOpBinding(self, op))

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

  @classmethod
  def _to_expr_type(cls, input: ArrayBoolLike) -> ArrayBoolExpr:
    if isinstance(input, cls):
      assert input._is_bound()
      return input
    elif isinstance(input, list):
      elt_bindings = [cast(BoolLiteralBinding, cls._elt_type._to_expr_type(elt).binding) for elt in input]
      assert all(isinstance(elt, BoolLiteralBinding) for elt in elt_bindings)
      return cls()._bind(ArrayLiteralBinding(elt_bindings))
    else:
      raise TypeError(f"op arg to ArrayBoolExpr must be ArrayBoolLike, got {input} of type {type(input)}")


  def __init__(self, initializer = None):
    super().__init__(initializer)
    self._elt_sample = BoolExpr()._new_bind(SampleElementBinding())

  def any(self) -> BoolExpr:
    return BoolExpr()._new_bind(UnarySetOpBinding(self, BoolOp.op_or))

  def all(self) -> BoolExpr:
    return BoolExpr()._new_bind(UnarySetOpBinding(self, BoolOp.op_and))


ArrayIntLike = Union['ArrayIntExpr', List[IntLike]]
class ArrayIntExpr(ArrayExpr[IntExpr, List[int], ArrayIntLike]):
  _elt_type = IntExpr

  @classmethod
  def _to_expr_type(cls, input: ArrayIntLike) -> ArrayIntExpr:
    if isinstance(input, cls):
      assert input._is_bound()
      return input
    elif isinstance(input, list):
      elt_bindings = [cast(IntLiteralBinding, cls._elt_type._to_expr_type(elt).binding) for elt in input]
      assert all(isinstance(elt, IntLiteralBinding) for elt in elt_bindings)
      return cls()._bind(ArrayLiteralBinding(elt_bindings))
    else:
      raise TypeError(f"op arg to ArrayIntExpr must be ArrayIntLike, got {input} of type {type(input)}")


ArrayFloatLike = Union['ArrayFloatExpr', List[FloatLike]]
class ArrayFloatExpr(ArrayExpr[FloatExpr, List[float], ArrayFloatLike]):
  _elt_type = FloatExpr

  @classmethod
  def _to_expr_type(cls, input: ArrayFloatLike) -> ArrayFloatExpr:
    if isinstance(input, cls):
      assert input._is_bound()
      return input
    elif isinstance(input, list):
      elt_bindings = [cast(FloatLiteralBinding, cls._elt_type._to_expr_type(elt).binding) for elt in input]
      assert all(isinstance(elt, FloatLiteralBinding) for elt in elt_bindings)
      return cls()._bind(ArrayLiteralBinding(elt_bindings))
    else:
      raise TypeError(f"op arg to ArrayFloatExpr must be ArrayFloatLike, got {input} of type {type(input)}")


ArrayRangeLike = Union['ArrayRangeExpr', List[RangeLike]]
class ArrayRangeExpr(ArrayExpr[RangeExpr, List[Range], ArrayRangeLike]):
  _elt_type = RangeExpr

  @classmethod
  def _to_expr_type(cls, input: ArrayRangeLike) -> ArrayRangeExpr:
    if isinstance(input, cls):
      assert input._is_bound()
      return input
    elif isinstance(input, list):
      elt_bindings = [cast(RangeLiteralBinding, cls._elt_type._to_expr_type(elt).binding) for elt in input]
      assert all(isinstance(elt, RangeLiteralBinding) for elt in elt_bindings)
      return cls()._bind(ArrayLiteralBinding(elt_bindings))
    else:
      raise TypeError(f"op arg to ArrayRangeExpr must be ArrayRangeLike, got {input} of type {type(input)}")

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

  @classmethod
  def _to_expr_type(cls, input: ArrayStringLike) -> ArrayStringExpr:
    if isinstance(input, cls):
      assert input._is_bound()
      return input
    elif isinstance(input, list):
      elt_bindings = [cast(StringLiteralBinding, cls._elt_type._to_expr_type(elt).binding) for elt in input]
      assert all(isinstance(elt, StringLiteralBinding) for elt in elt_bindings)
      return cls()._bind(ArrayLiteralBinding(elt_bindings))
    else:
      raise TypeError(f"op arg to ArrayStringExpr must be ArrayStringLike, got {input} of type {type(input)}")
