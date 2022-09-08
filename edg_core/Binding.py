from __future__ import annotations

from abc import abstractmethod
from enum import Enum, auto
from itertools import chain
from typing import *

import edgir
from .Core import Refable
from .IdentityDict import IdentityDict
from .Range import Range

if TYPE_CHECKING:
  from .Ports import BasePort, Port
  from .Array import Vector
  from .Blocks import BaseBlock
  from .ConstraintExpr import ConstraintExpr, FloatExpr, BoolExpr

## These are split mostly to let us have some finer grained types on various
## binding helper functions.

class NumericOp(Enum):

  # Additive
  add = auto()
  negate = auto()
  sum = auto()

  # Multiplicative
  mul = auto()
  invert = auto()

class BoolOp(Enum):
  op_and = auto()
  op_not = auto()
  op_or = auto()
  op_xor = auto()
  implies = auto()

class EqOp(Enum):
  eq = auto()
  ne = auto()
  all_equal = auto()
  all_unique = auto()

class OrdOp(Enum):
  # Ordering
  ge = auto()
  gt = auto()
  le = auto()
  lt = auto()
  within = auto()

class RangeSetOp(Enum):
  # Range/Set
  max = auto()
  min = auto()

  # Range
  hull = auto()
  intersection = auto()
  center = auto()
  width = auto()

  # Set
  equal_any = auto()


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


class InitParamBinding(ParamBinding):
  """Binding that indicates this is a parameter from an __init__ argument"""


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
    return f"Lit({self.value})"

  def __init__(self, value: Range):
    self.value = value

  def expr_to_proto(self, expr: ConstraintExpr, ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.ValueExpr:
    pb = edgir.ValueExpr()
    pb.literal.range.minimum.floating.val = self.value.lower
    pb.literal.range.maximum.floating.val = self.value.upper
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


class ArrayLiteralBinding(LiteralBinding):
  def __repr__(self) -> str:
    return f"Lit({self.values})"

  def __init__(self, values: Sequence[LiteralBinding]):
    super().__init__()
    self.values = values

  def expr_to_proto(self, expr: ConstraintExpr, ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.ValueExpr:
    pb = edgir.ValueExpr()
    pb.literal.array.SetInParent()
    for value in self.values:
      elt_value = value.expr_to_proto(expr, ref_map)
      assert elt_value.HasField('literal')
      pb.literal.array.elts.add().CopyFrom(elt_value.literal)
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


class ArrayBinding(LiteralBinding):
  def __repr__(self) -> str:
    return f"Array({self.values})"

  def __init__(self, values: Sequence[ConstraintExpr]):
    super().__init__()
    self.values = values

  def expr_to_proto(self, expr: ConstraintExpr, ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.ValueExpr:
    pb = edgir.ValueExpr()
    pb.array.SetInParent()
    for value in self.values:
      pb.array.vals.add().CopyFrom(value._expr_to_proto(ref_map))
    return pb


class UnaryOpBinding(Binding):
  def __repr__(self) -> str:
    return f"UnaryOp({self.op}, ...)"

  def __init__(self,
               src: ConstraintExpr,
               op: Union[NumericOp,BoolOp,RangeSetOp]):
    self.op_map = {
      NumericOp.negate: edgir.UnaryExpr.NEGATE,
      NumericOp.invert: edgir.UnaryExpr.INVERT,
      BoolOp.op_not: edgir.UnaryExpr.NOT,
      RangeSetOp.min: edgir.UnaryExpr.MIN,
      RangeSetOp.max: edgir.UnaryExpr.MAX,
      RangeSetOp.center: edgir.UnaryExpr.CENTER,
      RangeSetOp.width: edgir.UnaryExpr.WIDTH,
    }

    super().__init__()
    self.src = src
    self.op = op

  def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]:
    return chain(self.src._get_exprs())

  def expr_to_proto(self, expr: ConstraintExpr,
                    ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.ValueExpr:
    pb = edgir.ValueExpr()
    pb.unary.op = self.op_map[self.op]
    pb.unary.val.CopyFrom(self.src._expr_to_proto(ref_map))
    return pb

class UnarySetOpBinding(Binding):
  def __repr__(self) -> str:
    return f"UnarySetOp({self.op}, ...)"

  def __init__(self,
               src: ConstraintExpr,
               op: Union[NumericOp,BoolOp,EqOp,RangeSetOp]):
    self.op_map = {
      NumericOp.negate :edgir.UnarySetExpr.NEGATE,
      NumericOp.invert: edgir.UnarySetExpr.INVERT,
      NumericOp.sum: edgir.UnarySetExpr.SUM,
      BoolOp.op_and: edgir.UnarySetExpr.ALL_TRUE,
      BoolOp.op_or: edgir.UnarySetExpr.ANY_TRUE,
      EqOp.all_equal: edgir.UnarySetExpr.ALL_EQ,
      EqOp.all_unique: edgir.UnarySetExpr.ALL_UNIQUE,
      RangeSetOp.min: edgir.UnarySetExpr.MINIMUM,
      RangeSetOp.max: edgir.UnarySetExpr.MAXIMUM,
      RangeSetOp.intersection: edgir.UnarySetExpr.INTERSECTION,
      RangeSetOp.hull: edgir.UnarySetExpr.HULL,
      RangeSetOp.equal_any: edgir.UnarySetExpr.SET_EXTRACT,
    }

    super().__init__()
    self.src = src
    self.op = op

  def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]:
    return chain(self.src._get_exprs())

  def expr_to_proto(self, expr: ConstraintExpr,
                    ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.ValueExpr:
    pb = edgir.ValueExpr()
    pb.unary_set.op = self.op_map[self.op]
    pb.unary_set.vals.CopyFrom(self.src._expr_to_proto(ref_map))
    return pb

class BinaryOpBinding(Binding):
  def __repr__(self) -> str:
    return f"BinaryOp({self.op}, ...)"

  def __init__(self,
               lhs: ConstraintExpr,
               rhs: ConstraintExpr,
               op: Union[NumericOp,BoolOp,EqOp,OrdOp,RangeSetOp]):
    self.op_map = {
      # Numeric
      NumericOp.add: edgir.BinaryExpr.ADD,
      NumericOp.mul: edgir.BinaryExpr.MULT,
      # Boolean
      BoolOp.op_and: edgir.BinaryExpr.AND,
      BoolOp.op_or: edgir.BinaryExpr.OR,
      BoolOp.op_xor: edgir.BinaryExpr.XOR,
      BoolOp.implies: edgir.BinaryExpr.IMPLIES,
      # Equality
      EqOp.eq: edgir.BinaryExpr.EQ,
      EqOp.ne: edgir.BinaryExpr.NEQ,
      # Ordering
      OrdOp.lt: edgir.BinaryExpr.LT,
      OrdOp.le: edgir.BinaryExpr.LTE,
      OrdOp.gt: edgir.BinaryExpr.GT,
      OrdOp.ge: edgir.BinaryExpr.GTE,
      OrdOp.within: edgir.BinaryExpr.WITHIN,
      # Range/Set
      RangeSetOp.min: edgir.BinaryExpr.MIN,
      RangeSetOp.max: edgir.BinaryExpr.MAX,
      # Range
      RangeSetOp.intersection: edgir.BinaryExpr.INTERSECTION,
      RangeSetOp.hull: edgir.BinaryExpr.HULL,
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

class BinarySetOpBinding(Binding):
  def __repr__(self) -> str:
    return f"BinaryOp({self.op}, ...)"

  def __init__(self,
               lhset: ConstraintExpr,
               rhs: ConstraintExpr,
               op: NumericOp):
    self.op_map = {
      # Numeric
      NumericOp.add: edgir.BinarySetExpr.ADD,
      NumericOp.mul: edgir.BinarySetExpr.MULT,
    }

    super().__init__()
    self.lhset = lhset
    self.rhs = rhs
    self.op = op

  def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]:
    return chain(self.lhset._get_exprs(), self.rhs._get_exprs())

  def expr_to_proto(self, expr: ConstraintExpr, ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.ValueExpr:
    pb = edgir.ValueExpr()
    pb.binary_set.op = self.op_map[self.op]
    pb.binary_set.lhset.CopyFrom(self.lhset._expr_to_proto(ref_map))
    pb.binary_set.rhs.CopyFrom(self.rhs._expr_to_proto(ref_map))
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


class AllocatedBinding(Binding):
  def __repr__(self) -> str:
    return f"Allocated"

  def __init__(self, src: Vector):
    super().__init__()
    self.src = src

  def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]:
    return [self.src]

  def expr_to_proto(self, expr: ConstraintExpr, ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.ValueExpr:
    pb = edgir.ValueExpr()
    pb.ref.CopyFrom(ref_map[self.src])
    pb.ref.steps.add().reserved_param = edgir.ALLOCATED
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
