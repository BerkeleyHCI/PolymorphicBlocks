from __future__ import annotations

from abc import abstractmethod
from typing import *
from itertools import chain
import sys
from numbers import Real

from . import TransformUtil as tfu
from . import edgir


class IntervalLike():
  def upper(self) -> float: ...
  def lower(self) -> float: ...

  def __add__(self, rhs: Union[float, int, IntervalLike]) -> IntervalLike: ...

  def __radd__(self, lhs: Union[float, int, IntervalLike]) -> IntervalLike: ...

  def __sub__(self, rhs: Union[float, int, IntervalLike]) -> IntervalLike: ...

  def __rsub__(self, lhs: Union[float, int, IntervalLike]) -> IntervalLike: ...

  def __mul__(self, rhs: Union[float, int, IntervalLike]) -> IntervalLike: ...

  def __rmul__(self, lhs: Union[float, int, IntervalLike]) -> IntervalLike: ...

  def __truediv__(self, rhs: Union[float, int, IntervalLike]) -> IntervalLike: ...

  def __rtruediv__(self, lhs: Union[float, int, IntervalLike]) -> IntervalLike: ...

  def __eq__(self, other) -> bool: ...

  def __ne__(self, other) -> bool:
    return not self == other

  def intersect(self, other: IntervalLike) -> IntervalLike: ...

class Interval(IntervalLike):
  def __init__(self, lower: float, upper: float):
    assert lower <= upper
    self._lower = lower
    self._upper = upper

  def __repr__(self) -> str:
    return f'{type(self).__name__}({self._lower, self._upper})'

  def __hash__(self) -> int:
    return hash(type(self)) * hash(self._lower) * hash(self._upper)

  def __eq__(self, other) -> bool:
    return type(other) == type(self) and other._lower == self._lower and other._upper == self._upper

  def upper(self) -> float:
    return self._upper

  def lower(self) -> float:
    return self._lower

  def __add__(self, rhs: Union[float, int, IntervalLike]) -> Interval:
    if isinstance(rhs, (float, int)):
      return Interval(self._lower + rhs, self._upper + rhs)
    elif isinstance(rhs, Interval):
      return Interval(self._lower + rhs._lower, self._upper + rhs._upper)
    else:
      return NotImplemented

  def __radd__(self, lhs: Union[float, int, IntervalLike]) -> Interval:
    if isinstance(lhs, (float, int)):
      return self + lhs
    else:  # shouldn't need Interval-Interval reverse ops
      return NotImplemented

  def __sub__(self, rhs: Union[float, int, IntervalLike]) -> Interval:
    if isinstance(rhs, (float, int)):
      return Interval(self._lower - rhs, self._upper - rhs)
    elif isinstance(rhs, Interval):
      return Interval(self._lower - rhs._upper, self._upper - rhs._lower)
    else:
      return NotImplemented

  def __rsub__(self, lhs: Union[float, int, IntervalLike]) -> Interval:
    if isinstance(lhs, (float, int)):
      return Interval(-self._upper, -self._lower) + lhs
    else:  # shouldn't need Interval-Interval reverse ops
      return NotImplemented

  def __mul__(self, rhs: Union[float, int, IntervalLike]) -> Interval:
    if isinstance(rhs, (float, int)):
      if rhs < 0:
        return Interval(self._upper * rhs, self._lower * rhs)
      else:
        return Interval(self._lower * rhs, self._upper * rhs)
    elif isinstance(rhs, Interval):
      corners = [self._lower * rhs._lower, self._lower * rhs._upper, self._upper * rhs._lower, self._upper * rhs._upper]
      return Interval(min(corners), max(corners))
    else:
      return NotImplemented

  def __rmul__(self, lhs: Union[float, int, IntervalLike]) -> Interval:
    if isinstance(lhs, (float, int)):
      return self * lhs
    else:  # shouldn't need Interval-Interval reverse ops
      return NotImplemented

  def __truediv__(self, rhs: Union[float, int, IntervalLike]) -> Interval:
    if isinstance(rhs, (float, int)):
      if rhs < 0:
        return Interval(self._upper / rhs, self._lower / rhs)
      elif rhs == 0:
        if self._lower > 0 and self._upper > 0:
          return Interval(float('inf'), float('inf'))
        elif self._lower < 0 and self._upper > 0:
          return Interval(float('-inf'), float('inf'))
        elif self._lower < 0 and self._upper < 0:
          return Interval(float('-inf'), float('-inf'))
        else:
          raise ValueError("can't do 0/0")
      else:  # rhs > 0
        return Interval(self._lower / rhs, self._upper / rhs)
    elif isinstance(rhs, Interval):
      if rhs._lower == 0:
        if self._lower > 0:
          slc = float('inf')
        elif self._lower < 0:
          slc = float('-inf')
        else:
          raise ValueError("can't do 0/0")

        if self._upper > 0:
          suc = float('inf')
        elif self._upper < 0:
          suc = float('-inf')
        else:
          raise ValueError("can't do 0/0")

        rhs_lower_corners = [slc, suc]
      else:
        rhs_lower_corners = [self._lower / rhs._lower, self._upper / rhs._lower]

      if rhs._upper == 0:
        if self._lower > 0:
          slc = float('inf')
        elif self._lower < 0:
          slc = float('-inf')
        else:
          raise ValueError("can't do 0/0")

        if self._upper > 0:
          suc = float('inf')
        elif self._upper < 0:
          suc = float('-inf')
        else:
          raise ValueError("can't do 0/0")

        rhs_upper_corners = [slc, suc]
      else:
        rhs_upper_corners = [self._lower / rhs._upper, self._upper / rhs._upper]

      return Interval(min(rhs_lower_corners + rhs_upper_corners), max(rhs_lower_corners + rhs_upper_corners))
    else:
      return NotImplemented

  def __rtruediv__(self, lhs: Union[float, int, IntervalLike]) -> Interval:
    if isinstance(lhs, (float, int)):
      return Interval(lhs, lhs) / self
    else:  # shouldn't need Interval-Interval reverse ops
      return NotImplemented

  def __gt__(self, rhs: Union[float, int, IntervalLike]) -> bool:
    if isinstance(rhs, (float, int)):
      return self._lower > rhs
    elif isinstance(rhs, Interval):
      return self._lower> rhs._upper
    else:
      return rhs <= self

  def __ge__(self, rhs: Union[float, int, IntervalLike]) -> bool:
    if isinstance(rhs, (float, int)):
      return self._lower >= rhs
    elif isinstance(rhs, Interval):
      return self._lower >= rhs._upper
    else:
      return rhs < self

  def __lt__(self, rhs: Union[float, int, IntervalLike]) -> bool:
    if isinstance(rhs, (float, int)):
      return self._upper < rhs
    elif isinstance(rhs, Interval):
      return self._upper < rhs._lower
    else:
      return rhs >= self

  def __le__(self, rhs: Union[float, int, IntervalLike]) -> bool:
    if isinstance(rhs, (float, int)):
      return self._upper <= rhs
    elif isinstance(rhs, Interval):
      return self._upper <= rhs._lower
    else:
      return rhs > self

  def intersect(self, other: IntervalLike) -> IntervalLike:
    if isinstance(other, Interval):
      combined_min = max(self._lower, other._lower)
      combined_max = min(self._upper, other._upper)
      assert combined_min <= combined_max  # TODO need better empty range definition
      return Interval(combined_min, combined_max)
    else:
      return other.intersect(self)

  def is_subset(self, rhs: Interval) -> bool:
    if isinstance(rhs, Interval):
      return rhs._lower <= self._lower <= self._upper <= rhs._upper
    else:  # TODO handle this case
      raise ValueError


class SubsetInterval(IntervalLike):
  @classmethod
  def from_interval(cls, interval: Interval) -> SubsetInterval:
    return SubsetInterval(interval.lower(), interval.upper())

  def __init__(self, lower: float, upper: float):
    self._interval = Interval(lower, upper)

  def __repr__(self) -> str:
    return f'{type(self).__name__}({self._interval.lower(), self._interval.upper()})'

  def __hash__(self) -> int:
    return hash(type(self)) * hash(self._interval)

  def __eq__(self, other) -> bool:
    return type(other) == type(self) and self._interval == other._interval

  def upper(self) -> float:
    return self._interval.upper()

  def lower(self) -> float:
    return self._interval.lower()

  def __add__(self, rhs: Union[float, int, IntervalLike]) -> SubsetInterval:
    if isinstance(rhs, type(self)):
      return self.from_interval(self._interval + rhs._interval)
    elif isinstance(rhs, (float, int, Interval)):
      return self.from_interval(self._interval + rhs)
    else:
      return NotImplemented(f"can't do subset-interval op with other {type(rhs)}")

  def __radd__(self, lhs: Union[float, int, IntervalLike]) -> SubsetInterval:
    if isinstance(lhs, SubsetInterval):
      return self.from_interval(lhs._interval + self._interval)
    elif isinstance(lhs, (float, int, Interval)):
      return self.from_interval(lhs + self._interval)
    else:
      return NotImplemented(f"can't do subset-interval op with other {type(lhs)}")

  def __sub__(self, rhs: Union[float, int, IntervalLike]) -> SubsetInterval:
    if isinstance(rhs, SubsetInterval):
      return self.from_interval(self._interval - rhs._interval)
    elif isinstance(rhs, (float, int, Interval)):
      return self.from_interval(self._interval - rhs)
    else:
      return NotImplemented(f"can't do subset-interval op with other {type(rhs)}")

  def __rsub__(self, lhs: Union[float, int, IntervalLike]) -> SubsetInterval:
    if isinstance(lhs, SubsetInterval):
      return self.from_interval(lhs._interval - self._interval)
    elif isinstance(lhs, (float, int, Interval)):
      return self.from_interval(lhs - self._interval)
    else:
      return NotImplemented(f"can't do subset-interval op with other {type(lhs)}")

  def __mul__(self, rhs: Union[float, int, IntervalLike]) -> SubsetInterval:
    if isinstance(rhs, SubsetInterval):
      return self.from_interval(self._interval * rhs._interval)
    elif isinstance(rhs, (float, int, Interval)):
      return self.from_interval(self._interval * rhs)
    else:
      return NotImplemented(f"can't do subset-interval op with other {type(rhs)}")

  def __rmul__(self, lhs: Union[float, int, IntervalLike]) -> SubsetInterval:
    if isinstance(lhs, SubsetInterval):
      return self.from_interval(lhs._interval * self._interval)
    elif isinstance(lhs, (float, int, Interval)):
      return self.from_interval(lhs * self._interval)
    else:
      return NotImplemented(f"can't do subset-interval op with other {type(lhs)}")

  def __truediv__(self, rhs: Union[float, int, IntervalLike]) -> SubsetInterval:
    if isinstance(rhs, SubsetInterval):
      return self.from_interval(self._interval / rhs._interval)
    elif isinstance(rhs, (float, int, Interval)):
      return self.from_interval(self._interval / rhs)
    else:
      return NotImplemented(f"can't do subset-interval op with other {type(rhs)}")

  def __rtruediv__(self, lhs: Union[float, int, IntervalLike]) -> SubsetInterval:
    if isinstance(lhs, SubsetInterval):
      return self.from_interval(lhs._interval / self._interval)
    elif isinstance(lhs, (float, int, Interval)):
      return self.from_interval(lhs / self._interval)
    else:
      return NotImplemented(f"can't do subset-interval op with other {type(lhs)}")

  # Comparisons not implemented, since a subset may shrink and change the comparison result

  def intersect(self, other: IntervalLike) -> IntervalLike:
    combined_min = max(self.lower(), other.lower())
    combined_max = min(self.upper(), other.upper())
    assert combined_min <= combined_max, f"disjoint intersection {self}, {other}"  # TODO need better empty range definition
    return SubsetInterval(combined_min, combined_max)


class BaseErrorResult():
  pass


class ErrorResult(BaseErrorResult):
  def __init__(self, desc: str):
    self.desc = desc

  def __repr__(self) -> str:
    return f'{type(self).__name__}({self.desc})'

  def __hash__(self):
    return hash(type(self)) * hash(self.desc)

  def __eq__(self, other):
    return type(other) == type(self) and other.desc == self.desc


class PropagatedError(BaseErrorResult):
  """An error that occurred because an operand returned an error"""
  def __repr__(self) -> str:
    return type(self).__name__

  def __hash__(self):
    return hash(type(self))

  def __eq__(self, other):
    return type(other) == type(self)


ExprLitTypes = Union[float, str, bool, IntervalLike]  # TODO use edgir.LitTypes, but uses tuple interval representation
ExprResultElementTypes = Union[ExprLitTypes, BaseErrorResult]
ExprResult = Union[ExprResultElementTypes, List[ExprResultElementTypes]]


def expr_result_from_lit(value: edgir.LitTypes) -> ExprLitTypes:
  if isinstance(value, tuple) and isinstance(value[0], float) and isinstance(value[1], float):
    return Interval(value[0], value[1])
  elif isinstance(value, (str, float, bool)):
    return value
  else:
    raise TypeError(f"unknown lit value {value} of type {type(value)}")


def expr_result_to_str(result: Optional[ExprResult]) -> str:
  if isinstance(result, IntervalLike):
    return str(result)
  elif isinstance(result, BaseErrorResult):
    if isinstance(result, ErrorResult):
      return f'error({result.desc})'
    elif isinstance(result, PropagatedError):
      return f'propagated error'
    else:
      return f'unknown error {type(result)}'
  elif isinstance(result, list):
    contents = ', '.join([expr_result_to_str(elt) for elt in result])
    return f'[{contents}]'
  elif result is None:
    return 'none'
  else:  # assume a edgir.LitType
    return edgir.lit_to_string(result)


EvalFnType = Callable[[tfu.Path], Optional[ExprResult]]


class ScpError(BaseException):
  """Base exception for const prop errors"""

class ScpExprError(ScpError):
  """The expression itself is invalid"""


class DesignInfo(NamedTuple):
  path_resolve: Callable[[edgir.LocalPath], Optional[tfu.Path]]
  vector_contents: Dict[tfu.Path, Set[str]]


class ScpExpr():
  """Abstract base class for something that can be evaluated to a ExprResult"""
  def __repr__(self) -> str:
    return f'{type(self).__name__}'

  @abstractmethod
  def eval(self, scp_info: EvalFnType) -> Optional[ExprResult]: ...


class ScpPath(ScpExpr):
  """Absolute path reference, not meant to be initialized from a ValueExpr"""
  def __init__(self, path: tfu.Path) -> None:
    self.path = path

  def __repr__(self) -> str:
    return f'{type(self).__name__}({self.path})'

  def __hash__(self):
    return hash(type(self)) * hash(self.path)

  def __eq__(self, other):
    return type(other) == type(self) and other.path == self.path

  def eval(self, eval_param_fn: EvalFnType) -> Optional[ExprResult]:
    return eval_param_fn(self.path)


class ScpRawLiteral(ScpExpr):
  def __init__(self, lit: ExprLitTypes) -> None:
    self.val = lit

  def __repr__(self) -> str:
    return f'{type(self).__name__}({self.val})'

  def __hash__(self):
    return hash(type(self)) * hash(self.val)

  def __eq__(self, other):
    return type(other) == type(self) and other.val == self.val

  def eval(self, eval_param_fn: EvalFnType) -> Optional[ExprResult]:
    return self.val


class ScpValueExpr(ScpExpr):
  @classmethod
  def from_value_expr(cls, expr: edgir.ValueExpr, context: tfu.TransformContext, design_info: DesignInfo) -> ScpValueExpr:
    if expr.HasField('literal'):
      return ScpLiteral(expr, context, design_info)
    elif expr.HasField('binary'):
      return ScpBinaryOp(expr, context, design_info)
    elif expr.HasField('ifThenElse'):
      return ScpIfThenElse(expr, context, design_info)
    elif expr.HasField('reduce'):
      return ScpReduceOp(expr, context, design_info)
    elif expr.HasField('map_extract'):
      return ScpMapExtract(expr, context, design_info)
    elif expr.HasField('ref'):
      if expr.ref.steps[-1].HasField('reserved_param') and expr.ref.steps[-1].reserved_param == edgir.IS_CONNECTED:
        expr_copy = edgir.ValueExpr()
        expr_copy.CopyFrom(expr)
        expr_copy.ref.steps.pop()
        return ScpIsConnected(expr_copy, context, design_info)
      else:
        return ScpRef(expr, context, design_info)
    else:
      raise ScpExprError(f"unknown expr {edgir.expr_to_string(expr)}")

  """Abstract base class for ValueExpr-based expression that can be evaluated"""
  @abstractmethod
  def __init__(self, expr: edgir.ValueExpr, context: tfu.TransformContext, design_info: DesignInfo) -> None:
    self.expr = expr
    self.context = context


class ScpLiteral(ScpValueExpr):
  def __init__(self, expr: edgir.ValueExpr, context: tfu.TransformContext, design_info: DesignInfo) -> None:
    super().__init__(expr, context, design_info)
    assert expr.HasField('literal')
    if expr.literal.HasField('boolean'):
      self.val: ExprResult = expr.literal.boolean.val
    elif expr.literal.HasField('floating'):
      self.val = expr.literal.floating.val
    elif expr.literal.HasField('text'):
      self.val = expr.literal.text.val
    else:
      self.val = ErrorResult(f"unknown literal expr")

  def __repr__(self) -> str:
    return f'{type(self).__name__}({self.val})'

  def __hash__(self):
    return hash(type(self)) * hash(self.val)

  def __eq__(self, other):
    return type(other) == type(self) and other.val == self.val

  def eval(self, eval_param_fn: EvalFnType) -> Optional[ExprResult]:
    return self.val


class ScpBinaryOp(ScpValueExpr):
  def __init__(self, expr: edgir.ValueExpr, context: tfu.TransformContext, design_info: DesignInfo) -> None:
    super().__init__(expr, context, design_info)
    assert expr.HasField('binary')
    self.lhs = self.from_value_expr(expr.binary.lhs, context, design_info)
    self.rhs = self.from_value_expr(expr.binary.rhs, context, design_info)
    self.op = expr.binary.op

  def __repr__(self) -> str:
    return f'{type(self).__name__}({self.op, self.lhs, self.rhs})'

  def __hash__(self):
    return hash(type(self)) * hash(self.lhs) * hash(self.rhs) * hash(self.op)

  def __eq__(self, other):
    return type(other) == type(self) and other.lhs == self.lhs and other.rhs == self.rhs and other.op == self.op

  def eval(self, eval_param_fn: EvalFnType) -> Optional[ExprResult]:
    lhs = self.lhs.eval(eval_param_fn)
    rhs = self.rhs.eval(eval_param_fn)
    if lhs is None and rhs is None:
      return None
    elif lhs is not None and rhs is None:  # for some (reduce-able) operations, discard unknown values
      if self.op in [edgir.BinaryExpr.ADD, edgir.BinaryExpr.MAX, edgir.BinaryExpr.MIN, edgir.BinaryExpr.INTERSECTION]:
        return lhs
      else:
        return None
    elif lhs is None and rhs is not None:
      if self.op in [edgir.BinaryExpr.ADD, edgir.BinaryExpr.MAX, edgir.BinaryExpr.MIN, edgir.BinaryExpr.INTERSECTION]:
        return rhs
      else:
        return None
    elif isinstance(lhs, bool) and isinstance(rhs, bool):
      if self.op == edgir.BinaryExpr.AND:
        return lhs and rhs
      elif self.op == edgir.BinaryExpr.OR:
        return lhs or rhs
      elif self.op == edgir.BinaryExpr.XOR:
        return lhs ^ rhs
      elif self.op == edgir.BinaryExpr.IMPLIES:
        return (not lhs) or (lhs and rhs)
      elif self.op == edgir.BinaryExpr.EQ:
        return lhs == rhs
      elif self.op == edgir.BinaryExpr.NEQ:
        return lhs != rhs
      else:
        return ErrorResult(f"unknown binary op {self.op} on bools")
    elif isinstance(lhs, float) and isinstance(rhs, float):
      if self.op == edgir.BinaryExpr.ADD:
        return lhs + rhs
      elif self.op == edgir.BinaryExpr.SUB:
        return lhs - rhs
      elif self.op == edgir.BinaryExpr.MULT:
        return lhs * rhs
      elif self.op == edgir.BinaryExpr.DIV:
        return lhs / rhs
      elif self.op == edgir.BinaryExpr.EQ:
        return lhs == rhs
      elif self.op == edgir.BinaryExpr.NEQ:
        return lhs != rhs
      elif self.op == edgir.BinaryExpr.GT:
        return lhs > rhs
      elif self.op == edgir.BinaryExpr.GTE:
        return lhs >= rhs
      elif self.op == edgir.BinaryExpr.LT:
        return lhs < rhs
      elif self.op == edgir.BinaryExpr.LTE:
        return lhs <= rhs
      elif self.op == edgir.BinaryExpr.MAX:
        return max(lhs, rhs)
      elif self.op == edgir.BinaryExpr.MIN:
        return min(lhs, rhs)
      elif self.op == edgir.BinaryExpr.RANGE:
        if not (lhs <= rhs):
          return ErrorResult(f"trying to construct range with lhs={lhs} not <= rhs={rhs}")
        return Interval(lhs, rhs)
      else:
        return ErrorResult(f"unknown binary op {self.op} on numeric")
    elif isinstance(lhs, (IntervalLike, float)) and isinstance(rhs, (IntervalLike, float)):
      if self.op == edgir.BinaryExpr.ADD:
        return lhs + rhs
      elif self.op == edgir.BinaryExpr.SUB:
        return lhs - rhs
      elif self.op == edgir.BinaryExpr.MULT:
        return lhs * rhs
      elif self.op == edgir.BinaryExpr.DIV:
        return lhs / rhs
      elif self.op == edgir.BinaryExpr.INTERSECTION and isinstance(lhs, IntervalLike) and isinstance(rhs, IntervalLike):
        return lhs.intersect(rhs)
      elif self.op == edgir.BinaryExpr.SUBSET and isinstance(lhs, Interval) and isinstance(rhs, Interval):
        return lhs.is_subset(rhs)
      elif self.op == edgir.BinaryExpr.SUBSET and isinstance(lhs, SubsetInterval) and isinstance(rhs, Interval):
        return lhs._interval.is_subset(rhs)
      elif isinstance(lhs, SubsetInterval) and isinstance(rhs, SubsetInterval):  # can't give a definite answer for these
        if self.op in {edgir.BinaryExpr.EQ, edgir.BinaryExpr.NEQ,
                       edgir.BinaryExpr.GT, edgir.BinaryExpr.GTE, edgir.BinaryExpr.LT, edgir.BinaryExpr.LTE}:
          return None
        else:
          return ErrorResult(f"unknown binary op {self.op} on subsets")
      elif isinstance(lhs, (float, Interval)) and isinstance(lhs, (float, Interval)):  # non-subsettable
        if self.op == edgir.BinaryExpr.GT:
          return lhs > rhs  # type: ignore
        elif self.op == edgir.BinaryExpr.GTE:
          return lhs >= rhs  # type: ignore
        elif self.op == edgir.BinaryExpr.LT:
          return lhs < rhs  # type: ignore
        elif self.op == edgir.BinaryExpr.LTE:
          return lhs <= rhs  # type: ignore
        else:
          return ErrorResult(f"unknown binary op {self.op} on non-subset interval-like")
      else:
        return ErrorResult(f"unknown binary op {self.op} on interval-like")
    elif isinstance(lhs, str) and isinstance(rhs, str):
      if self.op == edgir.BinaryExpr.EQ:
        return lhs == rhs
      elif self.op == edgir.BinaryExpr.NEQ:
        return lhs != rhs
      else:
        return ErrorResult(f"unknown binary op {self.op} on str")
    else:
      return ErrorResult(f"unknown binary operand types")


class ScpIfThenElse(ScpValueExpr):
  def __init__(self, expr: edgir.ValueExpr, context: tfu.TransformContext, design_info: DesignInfo) -> None:
    super().__init__(expr, context, design_info)
    assert expr.HasField('ifThenElse')
    self.cond = self.from_value_expr(expr.ifThenElse.cond, context, design_info)
    self.tru = self.from_value_expr(expr.ifThenElse.tru, context, design_info)
    self.fal = self.from_value_expr(expr.ifThenElse.fal, context, design_info)

  def __repr__(self) -> str:
    return f'{type(self).__name__}({self.cond, self.tru, self.fal})'

  def __hash__(self):
    return hash(type(self)) * hash(self.cond) * hash(self.tru) * hash(self.fal)

  def __eq__(self, other):
    return type(other) == type(self) and other.cond == self.cond and other.tru == self.tru and other.fal == self.fal

  def eval(self, eval_param_fn: EvalFnType) -> Optional[ExprResult]:
    cond = self.cond.eval(eval_param_fn)
    if cond is None:
      return None
    elif isinstance(cond, BaseErrorResult):
      return PropagatedError()
    elif isinstance(cond, bool):
      if cond:
        return self.tru.eval(eval_param_fn)
      else:
        return self.fal.eval(eval_param_fn)
    else:
      return ErrorResult("non-boolean condition for if-then-else")


class ScpReduceOp(ScpValueExpr):
  def __init__(self, expr: edgir.ValueExpr, context: tfu.TransformContext, design_info: DesignInfo) -> None:
    super().__init__(expr, context, design_info)
    assert expr.HasField('reduce')
    self.vals = self.from_value_expr(expr.reduce.vals, context, design_info)
    self.op = expr.reduce.op

  def __repr__(self) -> str:
    return f'{type(self).__name__}({self.op, self.vals})'

  def __hash__(self):
    return hash(type(self)) * hash(self.vals) * hash(self.op)

  def __eq__(self, other):
    return type(other) == type(self) and other.vals == self.vals and other.op == self.op

  def eval(self, eval_param_fn: EvalFnType) -> Optional[ExprResult]:
    vals = self.vals.eval(eval_param_fn)
    if vals is None or not vals:
      return None

    if isinstance(vals, BaseErrorResult) or (isinstance(vals, list) and PropagatedError() in vals):
      return PropagatedError()
    if isinstance(vals, Interval):
      if self.op == edgir.ReductionExpr.MAXIMUM:  # get-range-upper
        return vals.upper()
      elif self.op == edgir.ReductionExpr.MINIMUM:  # get-range-lower
        return vals.lower()
      else:
        return ErrorResult(f"unknown reduce op {self.op} on ranges")
    elif isinstance(vals, SubsetInterval):
      if self.op in {edgir.ReductionExpr.MAXIMUM, edgir.ReductionExpr.MINIMUM}:
        return None  # don't know enough to return a float - since it might change when it's an Interval later
      else:
        return ErrorResult(f"unknown reduce op {self.op} on subset ranges")
    elif isinstance(vals, list) and all([isinstance(val, bool) for val in vals]):
      vals_bool = cast(List[bool], vals)  # make the type checker happy
      if self.op == edgir.ReductionExpr.ALL_EQ:
        return all([val == vals_bool[0] for val in vals_bool])
      elif self.op == edgir.ReductionExpr.ANY_TRUE:
        return all(vals_bool)
      elif self.op == edgir.ReductionExpr.ALL_TRUE:
        return any(vals_bool)
      else:
        return ErrorResult(f"unknown reduce op {self.op} on list-of-bools")
    elif isinstance(vals, list) and all([isinstance(val, float) for val in vals]):
      vals_float = cast(List[float], vals)  # make the type checker happy
      if self.op == edgir.ReductionExpr.SUM:
        return sum(vals_float)
      elif self.op == edgir.ReductionExpr.ALL_EQ:
        return all([val == vals_float[0] for val in vals_float])
      elif self.op == edgir.ReductionExpr.ALL_UNIQUE:
        return len(vals_float) == len(set(vals_float))
      elif self.op == edgir.ReductionExpr.MAXIMUM:
        return max(vals_float)
      elif self.op == edgir.ReductionExpr.MINIMUM:
        return min(vals_float)
      else:
        return ErrorResult(f"unknown reduce op {self.op} on list-of-floats")
    elif isinstance(vals, list) and all([isinstance(val, IntervalLike) for val in vals]):
      vals_range = cast(List[IntervalLike], vals)
      if self.op == edgir.ReductionExpr.SUM:
        return sum(vals_range)
      elif self.op == edgir.ReductionExpr.ALL_EQ:
        return all([val == vals[0] for val in vals_range])
      elif self.op == edgir.ReductionExpr.ALL_UNIQUE:
        return len(vals_range) == len(set(vals_range))
      elif self.op == edgir.ReductionExpr.MAXIMUM:  # maximum of all ranges
        return max([val.upper() for val in vals_range])
      elif self.op == edgir.ReductionExpr.MINIMUM:  # maximum of all ranges
        return min([val.lower() for val in vals_range])
      elif self.op == edgir.ReductionExpr.INTERSECTION:
        intersection = vals_range[0]
        for val in vals_range[1:]:
          intersection = intersection.intersect(val)
        return intersection
        # return ErrorResult(f"intersection produces empty set")  # TODO return this instead of erroring out?
      else:
        return ErrorResult(f"unknown reduce op {self.op} on list-of-range")
    else:
      return ErrorResult(f"unknown reduce operand types")


class ScpMapExtract(ScpValueExpr):
  def __init__(self, expr: edgir.ValueExpr, context: tfu.TransformContext, design_info: DesignInfo) -> None:
    super().__init__(expr, context, design_info)
    assert expr.HasField('map_extract')
    if not expr.map_extract.container.HasField('ref'):
      raise ScpExprError(f"map_extract with non-ref container: {edgir.expr_to_string(expr)}")
    self.container_path = design_info.path_resolve(expr.map_extract.container.ref)
    self.extract_ref = expr.map_extract.path

    if self.container_path not in design_info.vector_contents:
      raise ScpExprError(f"container path {self.container_path} not in vector contents dict")

    elt_exprs: List[ScpValueExpr] = []
    for vector_elt in design_info.vector_contents[self.container_path]:
      elt_ref = edgir.ValueExpr()
      elt_ref.ref.CopyFrom(expr.map_extract.container.ref)
      elt_ref.ref.steps.add().name = vector_elt
      for extract_path_step in expr.map_extract.path.steps:
        elt_ref.ref.steps.add().CopyFrom(extract_path_step)
      elt_exprs.append(ScpValueExpr.from_value_expr(elt_ref, context, design_info))
    self.elt_exprs = frozenset(elt_exprs)

  def __repr__(self) -> str:
    return f"{type(self).__name__}({self.container_path}: {', '.join([str(elt_expr) for elt_expr in self.elt_exprs])})"

  def __hash__(self):
    return hash(type(self)) * hash(self.elt_exprs)

  def __eq__(self, other):
    return type(other) == type(self) and other.elt_exprs == self.elt_exprs

  def eval(self, eval_param_fn: EvalFnType) -> Optional[ExprResult]:
    eval_results = [elt_expr.eval(eval_param_fn) for elt_expr in self.elt_exprs]
    # type is broken since this can return an array type, but most exprs shouldn't
    # TODO maybe assert check this?
    return [eval_result for eval_result in eval_results if eval_result is not None]  # type: ignore


class ScpIsConnected(ScpValueExpr):
  def __init__(self, expr: edgir.ValueExpr, context: tfu.TransformContext, design_info: DesignInfo) -> None:
    super().__init__(expr, context, design_info)
    assert expr.HasField('ref')
    target = design_info.path_resolve(expr.ref)
    assert target is not None, f"could not resolve is-connected to {expr.ref}"  # TODO: assume is_connected is always on a legit port?
    self.target = target

  def __repr__(self) -> str:
    return f'{type(self).__name__}({self.target})'

  def __hash__(self):
    return hash(type(self)) * hash(self.target)

  def __eq__(self, other):
    return type(other) == type(self) and other.target == self.target

  def eval(self, eval_param_fn: EvalFnType) -> Optional[ExprResult]:
    return eval_param_fn(self.target)


class ScpRef(ScpValueExpr):
  def __init__(self, expr: edgir.ValueExpr, context: tfu.TransformContext, design_info: DesignInfo) -> None:
    super().__init__(expr, context, design_info)
    assert expr.HasField('ref')
    self.target = design_info.path_resolve(expr.ref)

  def __repr__(self) -> str:
    return f'{type(self).__name__}({self.target})'

  def __hash__(self):
    return hash(type(self)) * hash(self.target)

  def __eq__(self, other):
    return type(other) == type(self) and other.target == self.target

  def eval(self, eval_param_fn: EvalFnType) -> Optional[ExprResult]:
    if self.target is None:  # TODO better define semantics for missing link constraints
      return None
    else:
      return eval_param_fn(self.target)


class ScpConstraint():
  @classmethod
  def merge_results(cls, expr_vals: Iterable[Tuple[ScpConstraint, Optional[ExprResult]]]) -> Optional[ExprResult]:
    if not expr_vals:
      return None
    elif {val for expr, val in expr_vals if isinstance(val, BaseErrorResult)}:
      return PropagatedError()

    # we use sets to dedup same values
    vals_assign = {val for expr, val in expr_vals if isinstance(val, (bool, float, Interval, str))}
    vals_subset = {val for expr, val in expr_vals if isinstance(val, SubsetInterval)}
    vals_other = {val for expr, val in expr_vals if val is not None and
                  not isinstance(val, (bool, float, str, Interval, SubsetInterval))}

    if vals_other:
      return ErrorResult(f"unknown results to merge {vals_other}")

    if vals_assign:  # assigned values take precedence
      if len(vals_assign) != 1:
        return ErrorResult(f"multiple assign values {vals_assign}")
      else:
        return vals_assign.pop()
    elif vals_subset:
      intersection: IntervalLike = vals_subset.pop()  # TODO non-mutable version?
      while vals_subset:
        intersection = intersection.intersect(vals_subset.pop())
      return intersection
      # return ErrorResult(f"subset intersection lower {max_min} not <= upper {min_max}")  # TODO better non-crash error
    else:  # no information otherwise
      return None

  def __init__(self, expr: ScpExpr, name: str, source_locator: Optional[Tuple[str, int]]) -> None:
    self.expr = expr
    self.name = name
    self.source_locator = source_locator

  def __repr__(self) -> str:
    return f'{type(self).__name__}({self.expr})'

  def __hash__(self):
    return hash(type(self)) * hash(self.expr)

  def __eq__(self, other):
    return type(other) == type(self) and other.expr == self.expr

  @abstractmethod
  def eval(self, eval_param_fn: EvalFnType) -> Optional[ExprResult]: ...

  def get_name(self) -> str:
    return self.name

  def get_source_locator(self) -> Optional[Tuple[str, int]]:
    return self.source_locator


class ScpAssign(ScpConstraint):
  def eval(self, eval_param_fn: EvalFnType) -> Optional[ExprResult]:
    return self.expr.eval(eval_param_fn)


class ScpSubset(ScpConstraint):
  def eval(self, eval_param_fn: EvalFnType) -> Optional[ExprResult]:
    expr_value = self.expr.eval(eval_param_fn)
    if expr_value is None:
      return None
    elif isinstance(expr_value, SubsetInterval):  # propagate subset results as-is
      return expr_value
    elif isinstance(expr_value, Interval):  # convert exact-range results into subset
      return SubsetInterval.from_interval(expr_value)
    else:
      return ErrorResult(f"can't subset {expr_value}")


class SimpleConstPropTransform(tfu.Transform):
  """Performs limited const prop on a fully instantiated design:
  - builds up an internal graph representation of certain parameter flows, mainly equals and subset constraints
  - allows querying to resolve parameters, given the current graph state
    - does memoization at this point for fully resolved parameters
  - allows incremental const prop, as generators are instantiated, but otherwise requires full instantiation to resolve
    constraint Paths
  """
  def __init__(self) -> None:
    super().__init__()
    # for each Param, track assigned values including directed parameter-parameter "equivalence"
    # (directed "equivalence" is needed to support Range subset initializers)
    # this forms a (possibly, even likely cyclic) graph structure, and is a restricted version of const prop
    # TODO support range subset differently from range equality
    self.param_exprs: Dict[tfu.Path, Set[ScpConstraint]] = {}  # param -> constraint
    self.constraints: Dict[tfu.Path, Dict[str, Set[ScpValueExpr]]] = {}  # block path -> constr name -> expr (=> bool)
    self.param_value_cache: Dict[tfu.Path, Optional[ExprResult]] = {}
    self.port_array_ports: Dict[tfu.Path, Set[str]] = {}  # needed for map-extract operations
    self.connects: Dict[tfu.Path, tfu.Path] = {}  # value is the next step towards the link, to resolve connected_link
    self.reverse_connects: Dict[tfu.Path, tfu.Path] = {}  # TODO: reaplce w/ MultiBiDict?

  def set_value(self, path: tfu.Path, value: edgir.LitTypes, name: str) -> None:
    self.param_exprs.setdefault(path, set()).add(ScpAssign(ScpRawLiteral(expr_result_from_lit(value)),
                                                           f"set {path} = {value}", None))

  def _get_subports(self, path: tfu.Path, port: edgir.PortTypes) -> Iterable[tfu.Path]:
    assert not isinstance(port, edgir.PortArray)  # use case shouldn't have arrays
    if isinstance(port, edgir.Port):
      return [path]
    elif isinstance(port, edgir.Bundle):
      return chain([path],
                   *[self._get_subports(path.append_port(name), edgir.resolve_portlike(subport))
                     for name, subport in port.ports.items()])
    else:
      raise ValueError(f"unknown port-like {port} at {path}")

  def _get_port_params_paths(self, path: tfu.Path, port: edgir.PortTypes) -> Iterable[tfu.Path]:
    assert not isinstance(port, edgir.PortArray)  # TODO PortArray does not support params
    all_params = [path.append_param(name) for name, param in port.params.items()]
    if isinstance(port, edgir.Port):
      return all_params
    elif isinstance(port, edgir.Bundle):
      return chain(all_params,
                   *[self._get_port_params_paths(path.append_port(name), edgir.resolve_portlike(subport))
                     for name, subport in port.ports.items()])
    else:
      raise ValueError(f"unknown port-like {port} at {path}")

  def _follow(self, context: tfu.TransformContext, dest: edgir.LocalPath, curr: edgir.EltTypes) -> Optional[tfu.Path]:
    """Follows a LocalPath from a starting absolute Path, resolving links where connected.
    The port to link connection must have already been resolved, which should be the case since links are
    defined at the hierarchical level above.
    Exception: it's possible to refer to own links using child port links"""
    path_unused, (dst_path, dst_elt) = context.path.follow_partial(dest, curr)
    if not path_unused:
      return dst_path
    elif path_unused[0].reserved_param == edgir.CONNECTED_LINK:
      link_port_path = self.get_port_link(dst_path)
      if link_port_path is None:  # no connected link
        return None
      link_path = link_port_path.link_component()
      _, link = tfu.Path.empty().follow(link_path.to_local_path(), context.design.contents)
      new_context = tfu.TransformContext(link_path, context.design)
      leftover_relpath = edgir.LocalPath()
      for path_comp in path_unused[1:]:
        leftover_relpath.steps.add().CopyFrom(path_comp)
      return self._follow(new_context, leftover_relpath, link)
    else:  # eg, IS_CONNECTED
      return None

  def _process_constraint(self, context: tfu.TransformContext, block: edgir.BlockLikeTypes, constraint: edgir.ValueExpr,
                          name: str, source_locator: Optional[Tuple[str, int]]):
    def path_resolve(ref: edgir.LocalPath) -> Optional[tfu.Path]:
      return self._follow(context, ref, block)

    if constraint.HasField('binary') and constraint.binary.op == edgir.BinaryExpr.AND:
      # AND is sometimes used to combine multiple constraints
      self._process_constraint(context, block, constraint.binary.lhs, name, source_locator)
      self._process_constraint(context, block, constraint.binary.rhs, name, source_locator)
    elif constraint.HasField('binary'):
      lhs_path = self._follow(context, constraint.binary.lhs.ref, block) if constraint.binary.lhs.HasField('ref') else None
      rhs_path = self._follow(context, constraint.binary.rhs.ref, block) if constraint.binary.rhs.HasField('ref') else None
      design_info = DesignInfo(path_resolve, self.port_array_ports)

      if lhs_path is not None and rhs_path is not None and constraint.binary.op == edgir.BinaryExpr.EQ:  # bidirectional assignment
        self.param_exprs.setdefault(lhs_path, set()).add(ScpAssign(ScpPath(rhs_path), name, source_locator))
        self.param_exprs.setdefault(rhs_path, set()).add(ScpAssign(ScpPath(lhs_path), name, source_locator))
      elif lhs_path is not None and rhs_path is not None and constraint.binary.op == edgir.BinaryExpr.SUBSET:  # bidirectional subset
        self.param_exprs.setdefault(lhs_path, set()).add(ScpSubset(ScpPath(rhs_path), name, source_locator))
        self.constraints.setdefault(context.path, {}).setdefault(name, set()).add(
          ScpValueExpr.from_value_expr(constraint, context, design_info))
      elif lhs_path is not None and constraint.binary.op == edgir.BinaryExpr.EQ:  # assignment to lhs
        self.param_exprs.setdefault(lhs_path, set()).add(
          ScpAssign(ScpValueExpr.from_value_expr(constraint.binary.rhs, context, design_info), name, source_locator))
      elif lhs_path is not None and constraint.binary.op == edgir.BinaryExpr.SUBSET:  # subset to lhs
        self.param_exprs.setdefault(lhs_path, set()).add(
          ScpSubset(ScpValueExpr.from_value_expr(constraint.binary.rhs, context, design_info), name, source_locator))
        self.constraints.setdefault(context.path, {}).setdefault(name, set()).add(
          ScpValueExpr.from_value_expr(constraint, context, design_info))
      elif rhs_path is not None and constraint.binary.op == edgir.BinaryExpr.EQ:  # assignment to rhs
        self.param_exprs.setdefault(rhs_path, set()).add(
          ScpAssign(ScpValueExpr.from_value_expr(constraint.binary.lhs, context, design_info), name, source_locator))
      else:
        self.constraints.setdefault(context.path, {}).setdefault(name, set()).add(
          ScpValueExpr.from_value_expr(constraint, context, design_info))
    elif constraint.HasField('ref') and constraint.ref.steps[-1].HasField('reserved_param') \
        and constraint.ref.steps[-1].reserved_param == edgir.IS_CONNECTED:
      pass  # TODO treat as boolean asserts
    elif constraint.HasField('reduce'):
      if constraint.reduce.op == edgir.ReductionExpr.Op.ANY_TRUE and constraint.reduce.vals.HasField('map_extract') \
          and constraint.reduce.vals.map_extract.path.steps[-1].reserved_param == edgir.IS_CONNECTED:
        pass  # ignore all is-connected constraints, since these are checked in the frontend
      else:
        print(f'unknown reduce constraint {edgir.expr_to_string(constraint)}')
      pass  # TODO treat as boolean asserts
    elif constraint.HasField('connected') or constraint.HasField('exported'):
      pass  # ignore these, are handled elsewhere
    else:
      print(f"unknown constraint {edgir.expr_to_string(constraint)}")

  def _process_connected(self, context: tfu.TransformContext, block: edgir.BlockLikeTypes, constraint: edgir.ValueExpr, name: str):
    if constraint.HasField('connected') or constraint.HasField('exported'):
      path = context.path
      # direct use of follow should be safe, since connections are simple
      if constraint.HasField('connected'):
        assert constraint.connected.block_port.HasField('ref')
        assert constraint.connected.link_port.HasField('ref')
        (src_path, port_example) = path.follow(constraint.connected.block_port.ref, block)
        dst_path = path.follow(constraint.connected.link_port.ref, block)[0]
        assert dst_path.links
      elif constraint.HasField('exported'):
        assert constraint.exported.internal_block_port.HasField('ref')
        assert constraint.exported.exterior_port.HasField('ref')
        (src_path, port_example) = path.follow(constraint.exported.internal_block_port.ref, block)
        dst_path = path.follow(constraint.exported.exterior_port.ref, block)[0]
        if isinstance(block, edgir.Link):  # directionality is flipped on link exports
          tmp_path = src_path
          src_path = dst_path
          dst_path = tmp_path
      # assert src_path not in self.connects, f"duplicate connect from {path}"

      # TODO this assumes stable ordering of IR elements, which should hold but might be non-ideal.
      assert isinstance(port_example, (edgir.Port, edgir.Bundle)), f"{constraint} connected {type(port_example)} = {port_example}"
      for src_subport_path, dst_subport_path in zip(
          self._get_subports(src_path, port_example), self._get_subports(dst_path, port_example),
      ):
        assert src_subport_path not in self.connects or self.connects[src_subport_path] == dst_subport_path, \
            f"overwriting connect {src_subport_path} => {self.connects[src_subport_path]} with {dst_subport_path} (constraint {name} at {context.path})"
        self.connects[src_subport_path] = dst_subport_path
        self.reverse_connects[dst_subport_path] = src_subport_path

      # NOTE - IS_CONNECTED resolved separately, since that needs graph traversal information to the link.
      # Exports are not directly treated as IS_CONNECTED since there may be no accessible link

      name = f"{name} (connect {src_path, dst_path})"
      # TODO this assumes stable ordering of IR elements, which should hold but might be non-ideal.
      # Ideally try some kind of dual simultaneous follow?
      for src_param_path, dst_param_path in zip(
          self._get_port_params_paths(src_path, port_example), self._get_port_params_paths(dst_path, port_example),
      ):
        self.param_exprs.setdefault(src_param_path, set()).add(ScpAssign(ScpPath(dst_param_path), name, None))  # TODO source locator from connect?
        self.param_exprs.setdefault(dst_param_path, set()).add(ScpAssign(ScpPath(src_param_path), name, None))
    else:
      pass  # ignore constraints we don't understand

  def _process_portlike(self, path: tfu.Path, port: edgir.PortLike) -> None:
    if port.HasField('array'):
      subport_set = set(port.array.ports.keys())
      if path in self.port_array_ports:
        assert self.port_array_ports[path] == subport_set
      else:
        self.port_array_ports[path] = subport_set

    # TODO dedup w/ _traverse_portlike?
    if port.HasField('array'):
      for name, subport in port.array.ports.items():
        self._process_portlike(path.append_port(name), subport)
    elif port.HasField('bundle'):
      for name, subport in edgir.ordered_ports(port.bundle):
        self._process_portlike(path.append_port(name), subport)

  def visit_block(self, context: tfu.TransformContext, block: edgir.HierarchyBlock) -> None:
    self.param_value_cache.clear()  # invalidate the cache

    # visit_portlike is post-visit_block, but vectors need to be resolved before constraints are
    for name, subport in sorted(block.ports.items()):
      self._process_portlike(context.path.append_port(name), subport)

    for name, constr in sorted(block.constraints.items()):  # must parse connectivity to resolve link targets
      self._process_connected(context, block, constr, f"{context.path}:{name}")
    for name, constr in sorted(block.constraints.items()):  # then process constraints
      self._process_constraint(context, block, constr, f"{context.path}:{name}", edgir.source_locator_of(block, name))

  def visit_link(self, context: tfu.TransformContext, link: edgir.Link) -> None:
    self.param_value_cache.clear()  # invalidate the cache

    # visit_portlike is post-visit_block, but vectors need to be resolved before constraints are
    for name, subport in sorted(link.ports.items()):
      self._process_portlike(context.path.append_port(name), subport)

    for name, constr in sorted(link.constraints.items()):  # must parse connectivity to resolve link targets
      self._process_connected(context, link, constr, f"{context.path}:{name}")
    for name, constr in sorted(link.constraints.items()):  # then process constraints
      self._process_constraint(context, link, constr, f"{context.path}:{name}", edgir.source_locator_of(link, name))

  @classmethod
  def backedge_of_constr(cls, path: tfu.Path, constr: ScpConstraint) -> Optional[ScpConstraint]:
    if isinstance(constr, ScpAssign):  # TODO can these not have a name?
      return ScpAssign(ScpPath(path), "backedge", None)
    else:
      return None

  def resolve_param(self, path: tfu.Path,
                    backedge: Optional[ScpConstraint] = None, seen: Set[tfu.Path] = set()) -> Optional[ExprResult]:
    if path.ports and not path.params:
      if path.links:
        return path in self.reverse_connects
      else:
        return self.get_port_link(path) is not None

    if path not in self.param_exprs:
      return None
    if path in self.param_value_cache:
      return self.param_value_cache[path]
    if path in seen:
      return ErrorResult(f"cyclic dependency in evaluating {path}, from {backedge} with seen {seen}")

    seen = seen.union([path])

    constrs = [constr for constr in self.param_exprs[path] if constr != backedge]
    constrs_vals = [(constr,
                     constr.eval(lambda eval_path: self.resolve_param(eval_path,
                                                                      self.backedge_of_constr(path, constr), seen)))
                     for constr in constrs]
    resolved = ScpConstraint.merge_results(constrs_vals)

    if backedge is None and not seen:  # only cache the true value that doesn't have pruned sub-graphs
      self.param_value_cache[path] = resolved
    return resolved

  def get_port_link(self, path: tfu.Path) -> Optional[tfu.Path]:
    """Returns a Path to the port of the deepest connected link, if any."""
    assert path.ports and not path.params  # quick sanity check
    assert not path.links

    def resolve_step(path: tfu.Path) -> Optional[tfu.Path]:
      if path in self.connects:
        return resolve_step(self.connects[path])
      else:
        # heuristic to check the link is the final destination by checking that it's the top-level port
        # (other than array elements)
        # TODO replace with something less heuristic?
        if path.links and (len(path.ports) == 1 or (len(path.ports) == 2 and path.ports[1].isnumeric())):
          return path
        else:
          return None

    return resolve_step(path)

  def get_block_solved_params(self, design: edgir.Design, path: tfu.Path, recurse_links: bool = True) -> \
      Iterable[Tuple[edgir.LocalPath, Union[edgir.LitTypes, BaseErrorResult]]]:
    """Returns all solved parameters accessible from a block and their value"""
    results: List[Tuple[edgir.LocalPath, Union[edgir.LitTypes, BaseErrorResult]]] = []

    def process_param(parent_path: tfu.Path, parent_relpath: edgir.LocalPath, param_name: str) -> None:
      # TODO taking parent path/relpath is nonuniform with process__* and ugly
      solved = self.resolve_param(parent_path.append_param(param_name))
      if solved is not None:
        assert not isinstance(solved, list)
        if isinstance(solved, (Interval, SubsetInterval)):
          results.append((edgir.localpath_concat(parent_relpath, param_name), (solved.lower(), solved.upper())))
        elif isinstance(solved, (float, bool, str, BaseErrorResult)):
          results.append((edgir.localpath_concat(parent_relpath, param_name), solved))
        else:
          raise TypeError(f"unknown solved value {solved} of type {type(solved)}")

    def process_port(path: tfu.Path, relpath: edgir.LocalPath, port: edgir.PortTypes) -> None:
      if not path.links:
        link_port_path = self.get_port_link(path)
        if link_port_path is not None:
          results.append((edgir.localpath_concat(relpath, edgir.IS_CONNECTED), True))
          if recurse_links:
            link_path = tfu.Path(blocks=link_port_path.blocks, links=link_port_path.links,
                                 ports=(), params=())  # discard port
            link_relpath = edgir.localpath_concat(relpath, edgir.CONNECTED_LINK)
            _, link = tfu.Path.empty().follow(link_path.to_local_path(), design.contents)
            assert isinstance(link, edgir.Link)
            processs_link(link_path, link_relpath, link)
        else:
          results.append((edgir.localpath_concat(relpath, edgir.IS_CONNECTED), False))

      if isinstance(port, (edgir.Port, edgir.Bundle)):
        for name, param in port.params.items():
          process_param(path, relpath, name)

      if isinstance(port, edgir.Bundle):
        for name, subport in port.ports.items():
          process_port(path.append_port(name), edgir.localpath_concat(relpath, name),
                       edgir.resolve_portlike(subport))

    def processs_link(path: tfu.Path, relpath: edgir.LocalPath, link: edgir.Link) -> None:
      for name, param in link.params.items():
        process_param(path, relpath, name)

    _, block = tfu.Path.empty().follow(path.to_local_path(), design.contents)
    assert isinstance(block, (edgir.HierarchyBlock, edgir.Link))
    relpath = edgir.LocalPath()
    for name, param in block.params.items():
      process_param(path, relpath, name)

    for name, port in block.ports.items():
      process_port(path.append_port(name), edgir.localpath_concat(relpath, name), edgir.resolve_portlike(port))

    return results


class CheckErrorsTransform(tfu.Transform):
  """Writes solved parameters as constraints to a design.
  Existing constraints with conflicting names will cause an error."""
  def __init__(self, scp: SimpleConstPropTransform) -> None:
    self.scp = scp


  def visit_block(self, context: tfu.TransformContext, block: edgir.BlockTypes) -> None:
    self._visit_blocklike(context, block)

  def visit_link(self, context: tfu.TransformContext, link: edgir.Link) -> None:
    self._visit_blocklike(context, link)

  def _visit_blocklike(self, context: tfu.TransformContext, block: edgir.BlockLikeTypes) -> None:
    for param_relpath, param_value in self.scp.get_block_solved_params(context.design, context.path,
                                                                       recurse_links=False):
      if isinstance(param_value, BaseErrorResult):
        if isinstance(param_value, ErrorResult):
          error_str = param_value.desc
        else:
          error_str = "(propagated)"
        block.meta.members.node['error'] \
          .members.node['params'] \
          .members.node[edgir.local_path_to_str(param_relpath)].text_leaf = error_str
    for name, scp_expr_set in self.scp.constraints.get(context.path, {}).items():
      for scp_expr in scp_expr_set:
        expr_val = scp_expr.eval(lambda eval_path: self.scp.resolve_param(eval_path))
        if expr_val is not True and expr_val is not None:
          block.meta.members.node['error'] \
            .members.node['constraints'] \
            .members.node[name].text_leaf = str(expr_val)


class WriteSolvedParamTransform(tfu.Transform):
  """Writes solved parameters as constraints to a design.
  Existing constraints with conflicting names will cause an error."""
  def __init__(self, scp: SimpleConstPropTransform) -> None:
    self.scp = scp

  def visit_block(self, context: tfu.TransformContext, block: edgir.HierarchyBlock) -> None:
    for param_relpath, param_value in self.scp.get_block_solved_params(context.design, context.path):
      if not isinstance(param_value, BaseErrorResult):
        constr_name = '(scp)' + edgir.local_path_to_str(param_relpath)
        assert constr_name not in block.constraints
        block.constraints[constr_name].binary.op = edgir.BinaryExpr.EQ
        block.constraints[constr_name].binary.lhs.ref.CopyFrom(param_relpath)
        block.constraints[constr_name].binary.rhs.CopyFrom(edgir.lit_to_expr(param_value))
