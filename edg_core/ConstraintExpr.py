from __future__ import annotations

from typing import *
from abc import abstractmethod
from enum import Enum
from numbers import Number
from itertools import chain
from functools import reduce

from . import edgir
from .IdentityDict import IdentityDict
from .Builder import builder

from .Core import Refable
if TYPE_CHECKING:
  from .Ports import BasePort, Port
  from .Array import Vector
  from .Blocks import BaseBlock


class ReductionOp(Enum):
  min = 0
  max = 1
  sum = 2
  equal_any = 3
  all_equal = 4
  all_unique = 5
  intersection = 6
  hull = 7
  op_and = 8
  op_or = 9


class BinaryNumOp(Enum):
  add = 0
  sub = 1
  mul = 2
  div = 3


class BinaryBoolOp(Enum):
  eq = 0
  ne = 1
  lt = 2
  le = 3
  gt = 4
  ge = 5
  subset = 6
  op_and = 7,
  op_or = 8,
  op_xor = 9,
  implies = 10,


class Binding:
  """Base class for bindings that indicate what a ConstraintExpr means"""
  def is_bound(self) -> bool:
    return True

  @abstractmethod
  def expr_to_proto(self, expr: ConstraintExpr, ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.ValueExpr: ...

  @abstractmethod
  def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]: ...


ParamParentTypes = Union['Port', 'BaseBlock']  # creates a circular module dependency on Core
class ParamBinding(Binding):
  """Binding that indicates this is a parameter"""
  def __repr__(self) -> str:
    return f"Param({self.parent})"

  def __init__(self, parent: ParamParentTypes):
    super().__init__()
    self.parent = parent

  def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]:  # element should be returned by the containing ConstraintExpr
    return []

  def is_bound(self) -> bool:
    # TODO clarify binding logic
    from .Ports import Port
    if isinstance(self.parent, Port):  # ports can be a model
      return self.parent._is_bound()
    else:
      return True

  def expr_to_proto(self, expr: ConstraintExpr, ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.ValueExpr:
    pb = edgir.ValueExpr()
    pb.ref.CopyFrom(ref_map[expr])
    return pb


class ParamVariableBinding(Binding):
  """Variable internal to a parameter, treated as a pseudo-parameter"""
  def __repr__(self) -> str:
    return f"ParamVar({self.binding})"

  def __init__(self, binding: Binding):
    super().__init__()
    self.binding = binding

  def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]:  # element should be returned by the containing ConstraintExpr
    return []

  def expr_to_proto(self, expr: ConstraintExpr, ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.ValueExpr:
    return self.binding.expr_to_proto(expr, ref_map)


class LiteralBinding(Binding):
  """Base class for literal bindings"""
  def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]:
    return []


class BoolLiteralBinding(LiteralBinding):
  def __repr__(self) -> str:
    return f"Lit({self.value})"

  def __init__(self, value: bool):
    super().__init__()
    self.value = value

  def expr_to_proto(self, expr: ConstraintExpr, ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.ValueExpr:
    pb = edgir.ValueExpr()
    pb.literal.boolean.val = self.value
    return pb


class IntLiteralBinding(LiteralBinding):
  def __repr__(self) -> str:
    return f"Lit({self.value})"

  def __init__(self, value: int):
    self.value = value

  def expr_to_proto(self, expr: ConstraintExpr, ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.ValueExpr:
    pb = edgir.ValueExpr()
    pb.literal.integer.val = self.value
    return pb


class FloatLiteralBinding(LiteralBinding):
  def __repr__(self) -> str:
    return f"Lit({self.value})"

  def __init__(self, value: Union[float, int]):
    self.value: float = float(value)

  def expr_to_proto(self, expr: ConstraintExpr, ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.ValueExpr:
    pb = edgir.ValueExpr()
    pb.literal.floating.val = self.value
    return pb


class RangeLiteralBinding(LiteralBinding):
  def __repr__(self) -> str:
    return f"Lit({self.lower, self.upper})"

  def __init__(self, value: Tuple[Union[float, int], Union[float, int]]):
    self.lower = value[0]
    self.upper = value[1]

  def expr_to_proto(self, expr: ConstraintExpr, ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.ValueExpr:
    pb = edgir.ValueExpr()
    pb.literal.range.minimum.floating.val = self.lower
    pb.literal.range.maximum.floating.val = self.upper
    return pb


class StringLiteralBinding(LiteralBinding):
  def __repr__(self) -> str:
    return f"Lit({self.value})"

  def __init__(self, value: str):
    super().__init__()
    self.value = value

  def expr_to_proto(self, expr: ConstraintExpr, ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.ValueExpr:
    pb = edgir.ValueExpr()
    pb.literal.text.val = self.value
    return pb


class RangeBuilderBinding(Binding):
  def __repr__(self) -> str:
    return f"RangeBuilder({self.lower}, {self.upper})"

  def __init__(self, lower: FloatExpr, upper: FloatExpr):
    super().__init__()
    self.lower = lower
    self.upper = upper

  def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]:
    return chain(self.lower._get_exprs(), self.lower._get_exprs())

  def expr_to_proto(self, expr: ConstraintExpr, ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.ValueExpr:
    pb = edgir.ValueExpr()
    pb.binary.op = edgir.BinaryExpr.RANGE
    pb.binary.lhs.CopyFrom(self.lower._expr_to_proto(ref_map))
    pb.binary.rhs.CopyFrom(self.upper._expr_to_proto(ref_map))
    return pb


class ReductionOpBinding(Binding):
  def __repr__(self) -> str:
    return f"ReductionOp({self.op}, ...)"

  def __init__(self, src: ConstraintExpr, op: ReductionOp):
    self.op_map = {
      ReductionOp.min: edgir.ReductionExpr.MINIMUM,
      ReductionOp.max: edgir.ReductionExpr.MAXIMUM,
      ReductionOp.sum: edgir.ReductionExpr.SUM,
      ReductionOp.equal_any: edgir.ReductionExpr.SET_EXTRACT,
      ReductionOp.all_equal: edgir.ReductionExpr.ALL_EQ,
      ReductionOp.all_unique: edgir.ReductionExpr.ALL_UNIQUE,
      ReductionOp.intersection: edgir.ReductionExpr.INTERSECTION,
      ReductionOp.hull: edgir.ReductionExpr.HULL,
      ReductionOp.op_and: edgir.ReductionExpr.ALL_TRUE,
      ReductionOp.op_or: edgir.ReductionExpr.ANY_TRUE,
    }

    super().__init__()
    self.src = src
    self.op = op

  def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]:
    return chain(self.src._get_exprs())

  def expr_to_proto(self, expr: ConstraintExpr, ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.ValueExpr:
    pb = edgir.ValueExpr()
    pb.reduce.op = self.op_map[self.op]
    pb.reduce.vals.CopyFrom(self.src._expr_to_proto(ref_map))
    return pb


class BinaryOpBinding(Binding):
  def __repr__(self) -> str:
    return f"BinaryOp({self.op}, ...)"

  def __init__(self, lhs: ConstraintExpr, rhs: ConstraintExpr, op: Union[BinaryNumOp, BinaryBoolOp, ReductionOp]):
    self.op_map = {
      BinaryNumOp.add: edgir.BinaryExpr.ADD,
      BinaryNumOp.sub: edgir.BinaryExpr.SUB,
      BinaryNumOp.mul: edgir.BinaryExpr.MULT,
      BinaryNumOp.div: edgir.BinaryExpr.DIV,
      BinaryBoolOp.eq: edgir.BinaryExpr.EQ,
      BinaryBoolOp.ne: edgir.BinaryExpr.NEQ,
      BinaryBoolOp.lt: edgir.BinaryExpr.LT,
      BinaryBoolOp.le: edgir.BinaryExpr.LTE,
      BinaryBoolOp.gt: edgir.BinaryExpr.GT,
      BinaryBoolOp.ge: edgir.BinaryExpr.GTE,
      BinaryBoolOp.subset: edgir.BinaryExpr.SUBSET,
      BinaryBoolOp.op_and: edgir.BinaryExpr.AND,
      BinaryBoolOp.op_or: edgir.BinaryExpr.OR,
      BinaryBoolOp.op_xor: edgir.BinaryExpr.XOR,
      BinaryBoolOp.implies: edgir.BinaryExpr.IMPLIES,
      ReductionOp.min: edgir.BinaryExpr.MIN,
      ReductionOp.max: edgir.BinaryExpr.MAX,
      ReductionOp.intersection: edgir.BinaryExpr.INTERSECTION,
      ReductionOp.hull: edgir.BinaryExpr.HULL,
    }

    super().__init__()
    self.lhs = lhs
    self.rhs = rhs
    self.op = op

  def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]:
    return chain(self.lhs._get_exprs(), self.rhs._get_exprs())

  def expr_to_proto(self, expr: ConstraintExpr, ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.ValueExpr:
    pb = edgir.ValueExpr()
    pb.binary.op = self.op_map[self.op]
    pb.binary.lhs.CopyFrom(self.lhs._expr_to_proto(ref_map))
    pb.binary.rhs.CopyFrom(self.rhs._expr_to_proto(ref_map))
    return pb


class IfThenElseBinding(Binding):
  def __repr__(self) -> str:
    return f"IfThenElse(...)"

  def __init__(self, cond: BoolExpr, then_val: ConstraintExpr, else_val: ConstraintExpr):
    super().__init__()
    self.cond = cond
    self.then_val = then_val
    self.else_val = else_val

  def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]:
    return chain(self.cond._get_exprs(), self.then_val._get_exprs(), self.else_val._get_exprs())

  def expr_to_proto(self, expr: ConstraintExpr, ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.ValueExpr:
    pb = edgir.ValueExpr()
    pb.ifThenElse.cond.CopyFrom(self.cond._expr_to_proto(ref_map))
    pb.ifThenElse.tru.CopyFrom(self.then_val._expr_to_proto(ref_map))
    pb.ifThenElse.fal.CopyFrom(self.else_val._expr_to_proto(ref_map))
    return pb


class IsConnectedBinding(Binding):
  def __repr__(self) -> str:
    return f"IsConnected"

  def __init__(self, src: Port):
    super().__init__()
    self.src = src

  def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]:
    return [self.src]

  def expr_to_proto(self, expr: ConstraintExpr, ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.ValueExpr:
    pb = edgir.ValueExpr()
    pb.ref.CopyFrom(ref_map[self.src])
    pb.ref.steps.add().reserved_param = edgir.IS_CONNECTED
    return pb


class NameBinding(Binding):
  def __repr__(self) -> str:
    return f"Name"

  def __init__(self, src: Union[BaseBlock, BasePort]):
    super().__init__()
    self.src = src

  def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]:
    return []

  def expr_to_proto(self, expr: ConstraintExpr, ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.ValueExpr:
    pb = edgir.ValueExpr()
    pb.ref.CopyFrom(ref_map[self.src])
    pb.ref.steps.add().reserved_param = edgir.NAME
    return pb


class LengthBinding(Binding):
  def __repr__(self) -> str:
    return f"Length"

  def __init__(self, src: Vector):
    super().__init__()
    self.src = src

  def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]:
    return [self.src]

  def expr_to_proto(self, expr: ConstraintExpr, ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.ValueExpr:
    pb = edgir.ValueExpr()
    pb.ref.CopyFrom(ref_map[self.src])
    pb.ref.steps.add().reserved_param = edgir.LENGTH
    return pb


class AssignBinding(Binding):
  # Convenience method to make an assign expr without the rest of this proto infrastructure
  @staticmethod
  def make_assign(target: ConstraintExpr, value: ConstraintExpr, ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.ValueExpr:
    pb = edgir.ValueExpr()
    pb.assign.dst.CopyFrom(ref_map[target])
    pb.assign.src.CopyFrom(value._expr_to_proto(ref_map))
    return pb

  def __repr__(self) -> str:
    return f"Assign({self.target}, ...)"

  def __init__(self, target: ConstraintExpr, value: ConstraintExpr):
    super().__init__()
    self.target = target
    self.value = value

  def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]:
    return [self.value]

  def expr_to_proto(self, expr: ConstraintExpr, ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.ValueExpr:
    return self.make_assign(self.target, self.value, ref_map)


ConstraintExprCastable = TypeVar('ConstraintExprCastable')
SelfType = TypeVar('SelfType', bound='ConstraintExpr')
GetType = TypeVar('GetType', covariant=True)
class ConstraintExpr(Refable, Generic[SelfType, ConstraintExprCastable, GetType]):
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
  def _to_expr_type(cls, input: ConstraintExprCastable) -> SelfType:
    """Casts the input from an equivalent-type to the self-type."""
    raise NotImplementedError

  def __init__(self: SelfType, initializer: Optional[ConstraintExprCastable] = None):
    self.binding: Optional[Binding] = None
    if isinstance(initializer, type(self)) and not initializer._is_bound():  # model passed in
      self.initializer: Optional[SelfType] = initializer.initializer
    elif initializer is None:
      self.initializer = None
    else:  # of type ConstraintExprCastable, bound
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
    return BoolExpr()._bind(BinaryOpBinding(self, self._to_expr_type(other), BinaryBoolOp.eq))


BoolLike = Union[bool, 'BoolExpr']
class BoolExpr(ConstraintExpr['BoolExpr', BoolLike, bool]):
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
  def _create_binary_op(cls, lhs: BoolExpr, rhs: BoolExpr, op: BinaryBoolOp) -> BoolExpr:  # TODO dedup w/ NumLike
    """Creates a new expression that is the result of a binary operation on inputs"""
    if type(lhs) != type(rhs):
      raise TypeError(f"op args must be of same type, "
                      f"got lhs={lhs} of type {type(lhs)} and rhs={rhs} of type {type(rhs)}")

    assert lhs._is_bound() and rhs._is_bound()
    return lhs._new_bind(BinaryOpBinding(lhs, rhs, op))

  def __and__(self, rhs: BoolLike) -> BoolExpr:
    return self._create_binary_op(self, self._to_expr_type(rhs), BinaryBoolOp.op_and)

  def __rand__(self, lhs: BoolLike) -> BoolExpr:
    return self._create_binary_op(self._to_expr_type(lhs), self, BinaryBoolOp.op_and)

  def __or__(self, rhs: BoolLike) -> BoolExpr:
    return self._create_binary_op(self, self._to_expr_type(rhs), BinaryBoolOp.op_or)

  def __ror__(self, lhs: BoolLike) -> BoolExpr:
    return self._create_binary_op(self._to_expr_type(lhs), self, BinaryBoolOp.op_or)

  def __xor__(self, rhs: BoolLike) -> BoolExpr:
    return self._create_binary_op(self, self._to_expr_type(rhs), BinaryBoolOp.op_xor)

  def __rxor__(self, lhs: BoolLike) -> BoolExpr:
    return self._create_binary_op(self._to_expr_type(lhs), self, BinaryBoolOp.op_xor)

  def implies(self, target: BoolLike) -> BoolExpr:
    return self._create_binary_op(self, self._to_expr_type(target), BinaryBoolOp.implies)

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


NumSelfType = TypeVar('NumSelfType', bound='NumLikeExpr')
class NumLikeExpr(ConstraintExpr[NumSelfType, ConstraintExprCastable, GetType],
    Generic[NumSelfType, ConstraintExprCastable, GetType]):
  """Trait for numeric-like expressions, providing common arithmetic operations"""

  @classmethod
  def _create_binary_op(cls, lhs: NumSelfType, rhs: NumSelfType, op: Union[BinaryNumOp, ReductionOp]) -> NumSelfType:
    """Creates a new expression that is the result of a binary operation on inputs"""
    if type(lhs) != type(rhs):
      raise TypeError(f"op args must be of same type, "
                      f"got lhs={lhs} of type {type(lhs)} and rhs={rhs} of type {type(rhs)}")

    assert lhs._is_bound() and rhs._is_bound()
    return lhs._new_bind(BinaryOpBinding(lhs, rhs, op))

  def __add__(self: NumSelfType, rhs: ConstraintExprCastable) -> NumSelfType:
    return self._create_binary_op(self, self._to_expr_type(rhs), BinaryNumOp.add)

  def __radd__(self: NumSelfType, lhs: ConstraintExprCastable) -> NumSelfType:
    return self._create_binary_op(self._to_expr_type(lhs), self, BinaryNumOp.add)

  def __sub__(self: NumSelfType, rhs: ConstraintExprCastable) -> NumSelfType:
    return self._create_binary_op(self, self._to_expr_type(rhs), BinaryNumOp.sub)

  def __rsub__(self: NumSelfType, lhs: ConstraintExprCastable) -> NumSelfType:
    return self._create_binary_op(self._to_expr_type(lhs), self, BinaryNumOp.sub)

  def __mul__(self: NumSelfType, rhs: ConstraintExprCastable) -> NumSelfType:
    return self._create_binary_op(self, self._to_expr_type(rhs), BinaryNumOp.mul)

  def __rmul__(self: NumSelfType, lhs: ConstraintExprCastable) -> NumSelfType:
    return self._create_binary_op(self._to_expr_type(lhs), self, BinaryNumOp.mul)

  def __truediv__(self: NumSelfType, rhs: ConstraintExprCastable) -> NumSelfType:
    return self._create_binary_op(self, self._to_expr_type(rhs), BinaryNumOp.div)

  def __rtruediv__(self: NumSelfType, lhs: ConstraintExprCastable) -> NumSelfType:
    return self._create_binary_op(self._to_expr_type(lhs), self, BinaryNumOp.div)

  @classmethod
  def _create_bool_op(cls, lhs: ConstraintExpr, rhs: ConstraintExpr, op: BinaryBoolOp) -> BoolExpr:
    if not isinstance(lhs, ConstraintExpr):
      raise TypeError(f"op args must be of type ConstraintExpr, got {lhs} of type {type(lhs)}")
    if not isinstance(rhs, ConstraintExpr):
      raise TypeError(f"op args must be of type ConstraintExpr, got {rhs} of type {type(rhs)}")
    assert lhs._is_bound() and rhs._is_bound()
    return BoolExpr()._bind(BinaryOpBinding(lhs, rhs, op))

  def __ne__(self: NumSelfType, other: ConstraintExprCastable) -> BoolExpr:  #type: ignore
    return self._create_bool_op(self, self._to_expr_type(other), BinaryBoolOp.ne)

  def __gt__(self: NumSelfType, other: ConstraintExprCastable) -> BoolExpr:  #type: ignore
    return self._create_bool_op(self, self._to_expr_type(other), BinaryBoolOp.gt)

  def __ge__(self: NumSelfType, other: ConstraintExprCastable) -> BoolExpr:  #type: ignore
    return self._create_bool_op(self, self._to_expr_type(other), BinaryBoolOp.ge)

  def __lt__(self: NumSelfType, other: ConstraintExprCastable) -> BoolExpr:  #type: ignore
    return self._create_bool_op(self, self._to_expr_type(other), BinaryBoolOp.lt)

  def __le__(self: NumSelfType, other: ConstraintExprCastable) -> BoolExpr:  #type: ignore
    return self._create_bool_op(self, self._to_expr_type(other), BinaryBoolOp.le)


IntLit = Union[int]
IntLike = Union[IntLit, 'IntExpr']
class IntExpr(NumLikeExpr['IntExpr', IntLike, int]):
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


FloatLit = Union[int, float]
FloatLike = Union[FloatLit, 'FloatExpr']
class FloatExpr(NumLikeExpr['FloatExpr', FloatLike, float]):
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
    return self._create_binary_op(self._to_expr_type(other), self, ReductionOp.min)

  def max(self, other: FloatLike) -> FloatExpr:
    return self._create_binary_op(self._to_expr_type(other), self, ReductionOp.max)


class RangeConstrMode:
  pass

RangeSubset = RangeConstrMode()
RangeSuperset = RangeConstrMode()


RangeLit = Tuple[FloatLit, FloatLit]
RangeLike = Union[RangeLit, FloatLike, FloatLike, Tuple[FloatLike, FloatLike], 'RangeExpr']
class RangeExpr(NumLikeExpr['RangeExpr', RangeLike, Tuple[float, float]]):
  # Some range literals for defaults
  POSITIVE = (0.0, float('inf'))
  NEGATIVE = (float('-inf'), 0.0)
  ALL = (float('-inf'), float('inf'))
  INF = (float('inf'), float('inf'))
  ZERO = (0.0, 0.0)
  EMPTY_ZERO = (0.0, 0.0)  # PLACEHOLDER, for a proper "empty" range type in future
  EMPTY_DIT = (1.5, 1.5)  # PLACEHOLDER, for input thresholds as a typical safe band
  EMPTY_ALL = (float('-inf'), float('inf'))  # PLACEHOLDER, for a proper "empty" range type in future

  def __init__(self, initializer: Optional[RangeLike]=None):
    super().__init__(initializer)
    self._lower = FloatExpr()._bind(ParamVariableBinding(ReductionOpBinding(self, ReductionOp.min)))
    self._upper = FloatExpr()._bind(ParamVariableBinding(ReductionOpBinding(self, ReductionOp.max)))

  @classmethod
  def _to_expr_type(cls, input: RangeLike) -> RangeExpr:
    if isinstance(input, RangeExpr):
      assert input._is_bound()
      return input
    elif isinstance(input, (int, float, FloatExpr)):
      expr = FloatExpr._to_expr_type(input)
      return RangeExpr()._bind(RangeBuilderBinding(expr, expr))
    elif isinstance(input, tuple) and isinstance(input[0], (int, float)) and isinstance(input[1], (int, float)):
      assert len(input) == 2
      return RangeExpr()._bind(RangeLiteralBinding((input[0], input[1])))
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
    return self._create_bool_op(self, RangeExpr._to_expr_type(item), BinaryBoolOp.subset)

  def contains(self, item: Union[RangeLike, FloatLike]) -> BoolExpr:
    if isinstance(item, (RangeExpr, tuple)):
      return RangeExpr._to_expr_type(item).within(self)
    elif isinstance(item, (int, float, FloatExpr)):
      return self._create_bool_op(FloatExpr._to_expr_type(item), self, BinaryBoolOp.subset)

  def intersect(self, other: RangeLike) -> RangeExpr:
    return self._create_binary_op(self._to_expr_type(other), self, ReductionOp.intersection)

  def hull(self, other: RangeLike) -> RangeExpr:
    return self._create_binary_op(self._to_expr_type(other), self, ReductionOp.hull)

  def lower(self) -> FloatExpr:
    return self._lower

  def upper(self) -> FloatExpr:
    return self._upper

  @classmethod
  def _create_range_float_binary_op(cls, lhs: RangeExpr, rhs: Union[RangeExpr, FloatExpr], op: BinaryNumOp) -> RangeExpr:
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
  def __mul__(self, rhs: ConstraintExprCastable) -> RangeExpr:
    if isinstance(rhs, (int, float)):  # TODO clean up w/ literal to expr pass, then type based on that
      rhs_cast: Union[FloatExpr, RangeExpr] = FloatExpr._to_expr_type(rhs)
    elif not isinstance(rhs, FloatExpr):
      rhs_cast = self._to_expr_type(rhs)  # type: ignore
    else:
      rhs_cast = rhs
    return self._create_range_float_binary_op(self, rhs_cast, BinaryNumOp.mul)

  # special option to allow range / float
  def __truediv__(self, rhs: ConstraintExprCastable) -> RangeExpr:
    if isinstance(rhs, (int, float)):  # TODO clean up w/ literal to expr pass, then type based on that
      rhs_cast: Union[FloatExpr, RangeExpr] = FloatExpr._to_expr_type(rhs)
    elif not isinstance(rhs, FloatExpr):
      rhs_cast = self._to_expr_type(rhs)  # type: ignore
    else:
      rhs_cast = rhs
    return self._create_range_float_binary_op(self, rhs_cast, BinaryNumOp.div)


StringLike = Union[str, 'StringExpr']
class StringExpr(ConstraintExpr['StringExpr', StringLike, str]):
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


class AssignExpr(ConstraintExpr['AssignExpr', None, None]):
  """String expression, can be used as a constraint"""
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
  def __rmul__(self, other: FloatLit) -> RangeExpr: ...
  @overload
  def __rmul__(self, other: RangeLit) -> RangeExpr: ...

  def __rmul__(self, other: Union[FloatLit, RangeLit]) -> RangeExpr:
    if isinstance(other, Number):
      values = [
        other * self.scale * (1 - self.tolerance),
        other * self.scale * (1 + self.tolerance)
      ]
    elif isinstance(other, tuple) and isinstance(other[0], Number) and isinstance(other[1], Number):
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
  def __rmul__(self, other: FloatLit) -> FloatExpr: ...

  @overload
  def __rmul__(self, other: RangeLit) -> RangeExpr: ...

  def __rmul__(self, other: Union[FloatLit, RangeLit]) -> Union[FloatExpr, RangeExpr]:
    if isinstance(other, (int, float)):
      return FloatExpr._to_expr_type(other * self.scale)
    elif isinstance(other, tuple) and isinstance(other[0], (int, float)) and isinstance(other[1], (int, float)):
      return RangeExpr._to_expr_type((other[0] * self.scale, other[1] * self.scale))
    else:
      raise TypeError(f"expected Float or Range Literal, got {other} of type {type(other)}")


# TODO this is a placeholder that just returns the constraint itself
# In the future, it should annotate the value with default-ness
DefaultType = TypeVar('DefaultType', bound=Union[BoolLike, FloatLike, RangeLike, StringLike])
def Default(constr: DefaultType) -> DefaultType:
  if isinstance(constr, ConstraintExpr):
    assert constr.initializer is not None, "default must have initialzier"
  return constr
