from __future__ import annotations

from abc import abstractmethod
from functools import reduce
from itertools import chain
from typing import *

import edgir
from .Binding import Binding, ParamBinding, BoolLiteralBinding, IntLiteralBinding, \
  FloatLiteralBinding, RangeLiteralBinding, StringLiteralBinding, RangeBuilderBinding, \
  UnaryOpBinding, UnarySetOpBinding, BinaryOpBinding, BinarySetOpBinding, IfThenElseBinding
from .Binding import NumericOp, BoolOp, EqOp, OrdOp, RangeSetOp
from .Builder import builder
from .Core import Refable
from .IdentityDict import IdentityDict
from .Range import Range

if TYPE_CHECKING:
  from .Ports import BasePort


SelfType = TypeVar('SelfType', bound='ConstraintExpr')
WrappedType = TypeVar('WrappedType', covariant=True)
CastableType = TypeVar('CastableType', contravariant=True)
class ConstraintExpr(Refable, Generic[WrappedType, CastableType]):
  """Base class for constraint expressions. Basically a container for operations.
  Actual meaning is held in the Binding.
  """
  def __repr__(self) -> str:
    if self.binding is not None and self.initializer is not None:
      return f"{super().__repr__()}({self.binding})={self.initializer}"
    if self.initializer is not None:
      return f"{super().__repr__()}={self.initializer}"
    if self.binding is not None:
      return f"{super().__repr__()}({self.binding})"
    else:
      return f"{super().__repr__()}"

  @classmethod
  @abstractmethod
  def _to_expr_type(cls: Type[SelfType], input: Union[SelfType, WrappedType]) -> SelfType:
    """Casts the input from an equivalent-type to the self-type."""
    raise NotImplementedError

  def __init__(self: SelfType, initializer: Optional[Union[SelfType, WrappedType]] = None):
    self.binding: Optional[Binding] = None
    if isinstance(initializer, type(self)) and not initializer._is_bound():  # model passed in
      self.initializer: Optional[SelfType] = initializer.initializer
    elif initializer is None:
      self.initializer = None
    else:
      self.initializer = self._to_expr_type(initializer)
    self.parent = builder.get_curr_context()

  def _get_exprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]:
    assert self.binding is not None
    return chain([self], self.binding.get_subexprs())

  def _new_bind(self: SelfType, binding: Binding) -> SelfType:
    """Returns a clone of this object with the specified binding. Discards existing binding / init data."""
    clone: SelfType = type(self)()
    clone.binding = binding
    return clone

  def _bind(self: SelfType, binding: Binding) -> SelfType:
    """Returns a clone of this object with the specified binding. This object must be unbound."""
    assert not self._is_bound()
    assert builder.get_curr_context() is self.parent, f"can't clone in original context {self.parent} to different new context {builder.get_curr_context()}"
    if not isinstance(binding, ParamBinding):
      assert self.initializer is None, "Only Parameters may have initializers"
    clone: SelfType = type(self)(self.initializer)
    clone.binding = binding
    return clone

  def _is_bound(self) -> bool:
    return self.binding is not None and self.binding.is_bound()

  def _initializer_to(self, target: ConstraintExpr) -> BoolExpr:
    assert type(self) == type(target), "target must be of same type"
    if self.initializer is None:
      return BoolExpr._to_expr_type(True)
    else:
      return target == self.initializer

  @abstractmethod
  def _decl_to_proto(self) -> edgir.ValInit:
    """Returns the protobuf for the definition of this parameter. Must have ParamBinding / ParamVariableBinding"""
    raise NotImplementedError

  def _expr_to_proto(self, ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.ValueExpr:
    assert self.binding is not None
    return self.binding.expr_to_proto(self, ref_map)

  # for now we define that all constraints can be checked for equivalence
  def __eq__(self: SelfType, other: ConstraintExprCastable) -> BoolExpr:  #type: ignore
    # TODO: avoid creating excess BoolExpr
    return BoolExpr()._bind(BinaryOpBinding(self, self._to_expr_type(other), EqOp.eq))


BoolLike = Union[bool, 'BoolExpr']
class BoolExpr(ConstraintExpr[bool, BoolLike]):
  """Boolean expression, can be used as a constraint"""
  @classmethod
  def _to_expr_type(cls, input: BoolLike) -> BoolExpr:
    if isinstance(input, BoolExpr):
      assert input._is_bound()
      return input
    elif isinstance(input, bool):
      return BoolExpr()._bind(BoolLiteralBinding(input))
    else:
      raise ValueError("unexpected type for %s of %s, expected BoolLike" % (input, type(input)))

  def _decl_to_proto(self) -> edgir.ValInit:
    pb = edgir.ValInit()
    pb.boolean.CopyFrom(edgir.Empty())
    return pb

  @classmethod
  def _create_binary_op(cls,
                        lhs: BoolExpr,
                        rhs: BoolExpr,
                        op: Union[NumericOp, BoolOp, EqOp, OrdOp, RangeSetOp]) -> BoolExpr:  # TODO dedup w/ NumLike
    """Creates a new expression that is the result of a binary operation on inputs"""
    if type(lhs) != type(rhs):
      raise TypeError(f"op args must be of same type, "
                      f"got lhs={lhs} of type {type(lhs)} and rhs={rhs} of type {type(rhs)}")

    assert lhs._is_bound() and rhs._is_bound()
    return lhs._new_bind(BinaryOpBinding(lhs, rhs, op))

  def __and__(self, rhs: BoolLike) -> BoolExpr:
    return self._create_binary_op(self, self._to_expr_type(rhs), BoolOp.op_and)

  def __rand__(self, lhs: BoolLike) -> BoolExpr:
    return self._create_binary_op(self._to_expr_type(lhs), self, BoolOp.op_and)

  def __or__(self, rhs: BoolLike) -> BoolExpr:
    return self._create_binary_op(self, self._to_expr_type(rhs), BoolOp.op_or)

  def __ror__(self, lhs: BoolLike) -> BoolExpr:
    return self._create_binary_op(self._to_expr_type(lhs), self, BoolOp.op_or)

  def __xor__(self, rhs: BoolLike) -> BoolExpr:
    return self._create_binary_op(self, self._to_expr_type(rhs), BoolOp.op_xor)

  def __rxor__(self, lhs: BoolLike) -> BoolExpr:
    return self._create_binary_op(self._to_expr_type(lhs), self, BoolOp.op_xor)

  def implies(self, target: BoolLike) -> BoolExpr:
    return self._create_binary_op(self, self._to_expr_type(target), BoolOp.implies)

  def __bnot__(self) -> BoolExpr:
    return self._new_bind(UnaryOpBinding(self,BoolOp.op_not))


  IteType = TypeVar('IteType', bound=ConstraintExpr)
  def then_else(self, then_val: IteType, else_val: IteType) -> IteType:
    assert isinstance(then_val, type(else_val)) and isinstance(else_val, type(then_val)), \
        f"if-then-else results must be of same type, got then={then_val}, else={else_val}"
    assert self._is_bound() and then_val._is_bound() and else_val._is_bound()
    return then_val._new_bind(IfThenElseBinding(self, then_val, else_val))

  def _is_true_lit(self) -> bool:
    assert self._is_bound()
    return isinstance(self.binding, BoolLiteralBinding) and self.binding.value == True

  def _is_lit(self) -> bool:
    assert self._is_bound()
    return isinstance(self.binding, BoolLiteralBinding)

  @classmethod
  def _combine_and(cls, sub_exprs: Iterable[BoolExpr]) -> BoolExpr:
    def combine_exprs(expr1: BoolExpr, expr2: BoolExpr) -> BoolExpr:
      return expr1 & expr2

    sub_exprs = [sub_expr for sub_expr in sub_exprs if not sub_expr._is_true_lit()]
    if len(sub_exprs) == 0:
      return cls._to_expr_type(True)
    else:
      return reduce(combine_exprs, sub_exprs)


NumLikeSelfType = TypeVar('NumLikeSelfType', bound='NumLikeExpr')
NumLikeCastable = TypeVar('NumLikeCastable')  # should include the self type
class NumLikeExpr(ConstraintExpr[WrappedType, NumLikeCastable], Generic[WrappedType, NumLikeCastable]):
  """Trait for numeric-like expressions, providing common arithmetic operations"""

  @classmethod
  @abstractmethod
  def _to_expr_type(cls: Type[NumLikeSelfType],
                    input: Union[NumLikeSelfType, WrappedType, NumLikeCastable]) -> NumLikeSelfType:
    """Casts the input from an equivalent-type to the self-type."""
    raise NotImplementedError

  @classmethod
  def _create_unary_op(cls,
                       var: SelfType,
                       op: NumericOp) -> SelfType:
    """Creates a new expression that is the result of a unary operation on the input"""

    assert var._is_bound()
    return var._new_bind(UnaryOpBinding(var, op))

  @classmethod
  def _create_binary_op(cls,
                        lhs: SelfType,
                        rhs: SelfType,
                        op: Union[NumericOp,RangeSetOp]) -> SelfType:
    """Creates a new expression that is the result of a binary operation on inputs"""
    if type(lhs) != type(rhs):
      raise TypeError(f"op args must be of same type, "
                      f"got lhs={lhs} of type {type(lhs)} and rhs={rhs} of type {type(rhs)}")

    assert lhs._is_bound() and rhs._is_bound()
    return lhs._new_bind(BinaryOpBinding(lhs, rhs, op))

  def __neg__(self: NumLikeSelfType) -> NumLikeSelfType:
    return self._create_unary_op(self, NumericOp.negate)

  def __mul_inv__(self: NumLikeSelfType) -> NumLikeSelfType:
    return self._create_unary_op(self, NumericOp.invert)

  def __add__(self: NumLikeSelfType, rhs: NumLikeCastable) -> NumLikeSelfType:
    return self._create_binary_op(self, self._to_expr_type(rhs), NumericOp.add)

  def __radd__(self: NumLikeSelfType, lhs: NumLikeCastable) -> NumLikeSelfType:
    return self._create_binary_op(self._to_expr_type(lhs), self, NumericOp.add)

  def __sub__(self: NumLikeSelfType, rhs: NumLikeCastable) -> NumLikeSelfType:
    return self.__add__(self._to_expr_type(rhs).__neg__())

  def __rsub__(self: NumLikeSelfType, lhs: NumLikeCastable) -> NumLikeSelfType:
    return self.__neg__().__radd__(self._to_expr_type(lhs))

  def __mul__(self: NumLikeSelfType, rhs: NumLikeCastable) -> NumLikeSelfType:
    return self._create_binary_op(self, self._to_expr_type(rhs), NumericOp.mul)

  def __rmul__(self: NumLikeSelfType, lhs: NumLikeCastable) -> NumLikeSelfType:
    return self._create_binary_op(self._to_expr_type(lhs), self, NumericOp.mul)

  def __truediv__(self: NumLikeSelfType, rhs: NumLikeCastable) -> NumLikeSelfType:
    return self.__mul__(self._to_expr_type(rhs).__mul_inv__())

  def __rtruediv__(self: NumLikeSelfType, lhs: NumLikeCastable) -> NumLikeSelfType:
    return self.__mul_inv__().__mul__(self._to_expr_type(lhs))

  @classmethod
  def _create_bool_op(cls,
                      lhs: ConstraintExpr,
                      rhs: ConstraintExpr,
                      op:  Union[BoolOp,EqOp,OrdOp]) -> BoolExpr:
    if not isinstance(lhs, ConstraintExpr):
      raise TypeError(f"op args must be of type ConstraintExpr, got {lhs} of type {type(lhs)}")
    if not isinstance(rhs, ConstraintExpr):
      raise TypeError(f"op args must be of type ConstraintExpr, got {rhs} of type {type(rhs)}")
    assert lhs._is_bound() and rhs._is_bound()
    return BoolExpr()._bind(BinaryOpBinding(lhs, rhs, op))

  def __ne__(self: NumLikeSelfType, other: NumLikeCastable) -> BoolExpr:  #type: ignore
    return self._create_bool_op(self, self._to_expr_type(other), EqOp.ne)

  def __gt__(self: NumLikeSelfType, other: NumLikeCastable) -> BoolExpr:  #type: ignore
    return self._create_bool_op(self, self._to_expr_type(other), OrdOp.gt)

  def __ge__(self: NumLikeSelfType, other: NumLikeCastable) -> BoolExpr:  #type: ignore
    return self._create_bool_op(self, self._to_expr_type(other), OrdOp.ge)

  def __lt__(self: NumLikeSelfType, other: NumLikeCastable) -> BoolExpr:  #type: ignore
    return self._create_bool_op(self, self._to_expr_type(other), OrdOp.lt)

  def __le__(self: NumLikeSelfType, other: NumLikeCastable) -> BoolExpr:  #type: ignore
    return self._create_bool_op(self, self._to_expr_type(other), OrdOp.le)


IntLike = Union['IntExpr', int]
class IntExpr(NumLikeExpr[int, IntLike]):
  @classmethod
  def _to_expr_type(cls, input: IntLike) -> IntExpr:
    if isinstance(input, IntExpr):
      assert input._is_bound()
      return input
    elif isinstance(input, int):
      return IntExpr()._bind(IntLiteralBinding(input))
    else:
      raise TypeError(f"op arg to IntExpr must be IntLike, got {input} of type {type(input)}")

  def _decl_to_proto(self) -> edgir.ValInit:
    pb = edgir.ValInit()
    pb.integer.CopyFrom(edgir.Empty())
    return pb


FloatLit = Union[float, int]
FloatLike = Union['FloatExpr', float]
class FloatExpr(NumLikeExpr[float, FloatLike]):
  @classmethod
  def _to_expr_type(cls, input: FloatLike) -> FloatExpr:
    if isinstance(input, FloatExpr):
      assert input._is_bound()
      return input
    elif isinstance(input, int) or isinstance(input, float):
      return FloatExpr()._bind(FloatLiteralBinding(input))
    else:
      raise TypeError(f"op arg to FloatExpr must be FloatLike, got {input} of type {type(input)}")

  def _decl_to_proto(self) -> edgir.ValInit:
    pb = edgir.ValInit()
    pb.floating.CopyFrom(edgir.Empty())
    return pb

  def min(self, other: FloatLike) -> FloatExpr:
    return self._create_binary_op(self._to_expr_type(other), self, RangeSetOp.min)

  def max(self, other: FloatLike) -> FloatExpr:
    return self._create_binary_op(self._to_expr_type(other), self, RangeSetOp.max)


RangeLike = Union['RangeExpr', Range, Tuple[FloatLike, FloatLike]]
class RangeExpr(NumLikeExpr[Range, Union[RangeLike, FloatLike]]):
  # Some range literals for defaults
  POSITIVE: Range = Range.from_lower(0.0)
  NEGATIVE: Range = Range.from_upper(0.0)
  ALL: Range = Range.all()
  INF: Range = Range(float('inf'), float('inf'))
  ZERO: Range = Range(0.0, 0.0)
  EMPTY_ZERO: Range = Range(0.0, 0.0)  # PLACEHOLDER, for a proper "empty" range type in future
  EMPTY_DIT: Range = Range(1.5, 1.5)  # PLACEHOLDER, for input thresholds as a typical safe band

  def __init__(self, initializer: Optional[RangeLike] = None) -> None:
    # must cast non-empty initializer type, because range supports wider initializers
    # TODO and must ignore initializers of self-type (because model weirdness) - remove model support!
    if initializer is not None and not isinstance(initializer, RangeExpr):
      initializer = self._to_expr_type(initializer)
    super().__init__(initializer)
    self._lower = FloatExpr()._bind(UnaryOpBinding(self, RangeSetOp.min))
    self._upper = FloatExpr()._bind(UnaryOpBinding(self, RangeSetOp.max))

  @classmethod
  def _to_expr_type(cls, input: Union[RangeLike, FloatLike]) -> RangeExpr:
    if isinstance(input, RangeExpr):
      assert input._is_bound()
      return input
    elif isinstance(input, (int, float, FloatExpr)):
      expr = FloatExpr._to_expr_type(input)
      return RangeExpr()._bind(RangeBuilderBinding(expr, expr))
    elif isinstance(input, tuple) and isinstance(input[0], (int, float)) and isinstance(input[1], (int, float)):
      assert len(input) == 2
      return RangeExpr()._bind(RangeLiteralBinding(Range(input[0], input[1])))
    elif isinstance(input, Range):
      return RangeExpr()._bind(RangeLiteralBinding(input))
    elif isinstance(input, tuple):
      assert len(input) == 2
      return RangeExpr()._bind(RangeBuilderBinding(
        FloatExpr._to_expr_type(input[0]),
        FloatExpr._to_expr_type(input[1])
        ))
    else:
      raise TypeError(f"op arg to RangeExpr must be FloatLike, got {input} of type {type(input)}")

  def _initializer_to(self, target: ConstraintExpr) -> BoolExpr:
    # must also handle initializer mode (subset, superset) here
    assert isinstance(target, type(self)), "target must be of same type"  # TODO don't use isinstance
    if self.initializer is None:
      return BoolExpr._to_expr_type(True)
    else:
      return target == self.initializer

  def _decl_to_proto(self) -> edgir.ValInit:
    pb = edgir.ValInit()
    pb.range.CopyFrom(edgir.Empty())
    return pb

  def within(self, item: RangeLike) -> BoolExpr:
    return self._create_bool_op(self, RangeExpr._to_expr_type(item), OrdOp.within)

  def contains(self, item: Union[RangeLike, FloatLike]) -> BoolExpr:
    if isinstance(item, (RangeExpr, tuple, Range)):
      return RangeExpr._to_expr_type(item).within(self)
    elif isinstance(item, (int, float, FloatExpr)):
      return self._create_bool_op(FloatExpr._to_expr_type(item), self, OrdOp.within)

  def intersect(self, other: RangeLike) -> RangeExpr:
    return self._create_binary_op(self._to_expr_type(other), self, RangeSetOp.intersection)

  def hull(self, other: RangeLike) -> RangeExpr:
    return self._create_binary_op(self._to_expr_type(other), self, RangeSetOp.hull)

  def lower(self) -> FloatExpr:
    return self._lower

  def upper(self) -> FloatExpr:
    return self._upper

  @classmethod
  def _create_range_float_binary_op(cls,
                                    lhs: RangeExpr,
                                    rhs: Union[RangeExpr, FloatExpr],
                                    op: Union[NumericOp]) -> RangeExpr:
    """Creates a new expression that is the result of a binary operation on inputs"""
    if not isinstance(lhs, RangeExpr):
      raise TypeError(f"range mul and div lhs must be range type, "
                      f"got lhs={lhs} of type {type(lhs)} and rhs={rhs} of type {type(rhs)}")

    if not isinstance(rhs, (RangeExpr, FloatExpr)):
      raise TypeError(f"range mul and div rhs must be range or float type, "
                      f"got lhs={lhs} of type {type(lhs)} and rhs={rhs} of type {type(rhs)}")

    assert lhs._is_bound() and rhs._is_bound()
    return lhs._new_bind(BinaryOpBinding(lhs, rhs, op))

  # special option to allow range * float
  def __mul__(self, rhs: Union[RangeLike, FloatLike]) -> RangeExpr:
    if isinstance(rhs, (int, float)):  # TODO clean up w/ literal to expr pass, then type based on that
      rhs_cast: Union[FloatExpr, RangeExpr] = FloatExpr._to_expr_type(rhs)
    elif not isinstance(rhs, FloatExpr):
      rhs_cast = self._to_expr_type(rhs)  # type: ignore
    else:
      rhs_cast = rhs
    return self._create_range_float_binary_op(self, rhs_cast, NumericOp.mul)

  # special option to allow range / float
  def __truediv__(self, rhs: Union[RangeLike, FloatLike]) -> RangeExpr:
    if isinstance(rhs, (int, float)):  # TODO clean up w/ literal to expr pass, then type based on that
      rhs_cast: Union[FloatExpr, RangeExpr] = FloatExpr._to_expr_type(rhs)
    elif not isinstance(rhs, FloatExpr):
      rhs_cast = self._to_expr_type(rhs)  # type: ignore
    else:
      rhs_cast = rhs
    return self * rhs_cast.__mul_inv__()

StringLike = Union['StringExpr', str]
class StringExpr(ConstraintExpr[str, StringLike]):
  """String expression, can be used as a constraint"""
  @classmethod
  def _to_expr_type(cls, input: StringLike) -> StringExpr:
    if isinstance(input, StringExpr):
      assert input._is_bound()
      return input
    elif isinstance(input, str):
      return StringExpr()._bind(StringLiteralBinding(input))
    else:
      raise ValueError("unexpected type for %s of %s, expected StringLike" % (input, type(input)))

  def _decl_to_proto(self) -> edgir.ValInit:
    pb = edgir.ValInit()
    pb.text.CopyFrom(edgir.Empty())
    return pb

  def _is_lit(self) -> bool:
    assert self._is_bound()
    return isinstance(self.binding, StringLiteralBinding)


class AssignExpr(ConstraintExpr[None, None]):
  """Assignment expression, should be an internal type"""
  @classmethod
  def _to_expr_type(cls, input: Any) -> AssignExpr:
    raise ValueError("can't convert to AssignExpr")

  def _decl_to_proto(self) -> edgir.ValInit:
    raise ValueError("can't create parameter from AssignExpr")

  def _is_lit(self) -> bool:
    raise ValueError("can't have literal AssignExpr")


# TODO actually implement dimensional analysis and units type checking
class RangeConstructor:
  def __init__(self, tolerance: float, scale: float = 1, units: str = '') -> None:
    self.tolerance = tolerance
    self.scale = scale
    self.units = units

  @overload
  def __rmul__(self, other: FloatLike) -> RangeExpr: ...
  @overload
  def __rmul__(self, other: RangeLike) -> RangeExpr: ...

  def __rmul__(self, other: Union[FloatLike, RangeLike]) -> RangeExpr:
    if isinstance(other, (int, float)):
      values = [
        other * self.scale * (1 - self.tolerance),
        other * self.scale * (1 + self.tolerance)
      ]
    elif isinstance(other, tuple) and isinstance(other[0], (int, float)) and isinstance(other[1], (int, float)):
      assert other[0] <= other[1]
      if other[0] < 0 and other[1] < 0:
        values = [
          other[0] * self.scale * (1 + self.tolerance),
          other[1] * self.scale * (1 - self.tolerance)
        ]
      elif other[0] < 0 <= other[1]:
        values = [
          other[0] * self.scale * (1 + self.tolerance),
          other[1] * self.scale * (1 + self.tolerance)
        ]
      elif other[0] >= 0 and other[1] >= 0:
        values = [
          other[0] * self.scale * (1 - self.tolerance),
          other[1] * self.scale * (1 + self.tolerance)
        ]
      else:
        assert False, "range tolerance broken =("
      assert values[0] <= values[1]
    else:
      raise TypeError(f"expected Float or Range Literal, got {other} of type {type(other)}")
    return RangeExpr._to_expr_type((min(values), max(values)))


class LiteralConstructor:
  def __init__(self, scale: float = 1, units: str = ''):
    self.scale = scale
    self.units = units

  def __call__(self, dummy=None, tol: Optional[float]=None):
    if tol is not None:
      return RangeConstructor(tol, self.scale, self.units)

  @overload
  def __rmul__(self, other: float) -> FloatExpr: ...
  # can't use RangeLike directly because it overlaps with FloatLike
  @overload
  def __rmul__(self, other: Union[Range, Tuple[float, float]]) -> RangeExpr: ...

  def __rmul__(self, other: Union[float, Range, Tuple[float, float]]) -> Union[FloatExpr, RangeExpr]:
    if isinstance(other, (int, float)):
      return FloatExpr._to_expr_type(other * self.scale)
    elif isinstance(other, Range):
      return RangeExpr._to_expr_type(other * self.scale)
    elif isinstance(other, tuple) and isinstance(other[0], (int, float)) and isinstance(other[1], (int, float)):
      return RangeExpr._to_expr_type(Range(other[0], other[1]) * self.scale)
    else:
      raise TypeError(f"expected Float or Range Literal, got {other} of type {type(other)}")


# TODO this is a placeholder that just returns the constraint itself
# In the future, it should annotate the value with default-ness
DefaultType = TypeVar('DefaultType', bound=Union[BoolLike, IntLike, FloatLike, RangeLike, StringLike])
def Default(constr: DefaultType) -> DefaultType:
  if isinstance(constr, ConstraintExpr):
    assert constr.binding is not None, f"default {constr} must have initializer"
  return constr
