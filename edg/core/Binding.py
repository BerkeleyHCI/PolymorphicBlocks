from __future__ import annotations

from abc import abstractmethod
from enum import Enum, auto
from itertools import chain
from typing import *

from typing_extensions import override

from .. import edgir
from .Core import Refable
from .IdentityDict import IdentityDict
from .Range import Range

if TYPE_CHECKING:
    from .Ports import BasePort, Port
    from .Array import Vector, BaseVector
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
    shrink_mul = auto()


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
    def populate_expr_proto(self, pb: edgir.ValueExpr, expr: ConstraintExpr, ref_map: Refable.RefMapType) -> None: ...

    @abstractmethod
    def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]: ...


ParamParentTypes = Union["Port", "BaseBlock"]  # creates a circular module dependency on Core


class ParamBinding(Binding):
    """Binding that indicates this is a parameter"""

    @override
    def __repr__(self) -> str:
        return f"Param({self.parent})"

    def __init__(self, parent: ParamParentTypes):
        super().__init__()
        self.parent = parent

    @override
    def get_subexprs(
        self,
    ) -> Iterable[Union[ConstraintExpr, BasePort]]:  # element should be returned by the containing ConstraintExpr
        return []

    @override
    def is_bound(self) -> bool:
        # TODO clarify binding logic
        from .Ports import Port

        if isinstance(self.parent, Port):  # ports can be a model
            return self.parent._is_bound()
        else:
            return True

    @override
    def populate_expr_proto(self, pb: edgir.ValueExpr, expr: ConstraintExpr, ref_map: Refable.RefMapType) -> None:
        pb.ref.CopyFrom(ref_map[expr])


class InitParamBinding(ParamBinding):
    """Binding that indicates this is a parameter from an __init__ argument.
    Can optionally take a value, which is the raw value passed into __init__."""

    def __init__(self, parent: ParamParentTypes, value: Optional[Any] = None):
        super().__init__(parent)
        self.value = value


class LiteralBinding(Binding):
    """Base class for literal bindings"""

    @override
    def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]:
        return []

    @abstractmethod
    def populate_literal_proto(self, pb: edgir.ValueLit) -> None:
        raise NotImplementedError

    @override
    def populate_expr_proto(self, pb: edgir.ValueExpr, expr: ConstraintExpr, ref_map: Refable.RefMapType) -> None:
        self.populate_literal_proto(pb.literal)


class BoolLiteralBinding(LiteralBinding):
    @override
    def __repr__(self) -> str:
        return f"Lit({self.value})"

    def __init__(self, value: bool):
        super().__init__()
        self.value = value

    @override
    def populate_literal_proto(self, pb: edgir.ValueLit) -> None:
        pb.boolean.val = self.value


class IntLiteralBinding(LiteralBinding):
    @override
    def __repr__(self) -> str:
        return f"Lit({self.value})"

    def __init__(self, value: int):
        self.value = value

    @override
    def populate_literal_proto(self, pb: edgir.ValueLit) -> None:
        pb.integer.val = self.value


class FloatLiteralBinding(LiteralBinding):
    @override
    def __repr__(self) -> str:
        return f"Lit({self.value})"

    def __init__(self, value: Union[float, int]):
        self.value: float = float(value)

    @override
    def populate_literal_proto(self, pb: edgir.ValueLit) -> None:
        pb.floating.val = self.value


class RangeLiteralBinding(LiteralBinding):
    @override
    def __repr__(self) -> str:
        return f"Lit({self.value})"

    def __init__(self, value: Range):
        self.value = value

    @override
    def populate_literal_proto(self, pb: edgir.ValueLit) -> None:
        pb.range.minimum.floating.val = self.value.lower
        pb.range.maximum.floating.val = self.value.upper


class StringLiteralBinding(LiteralBinding):
    @override
    def __repr__(self) -> str:
        return f"Lit({self.value})"

    def __init__(self, value: str):
        super().__init__()
        self.value = value

    @override
    def populate_literal_proto(self, pb: edgir.ValueLit) -> None:
        pb.text.val = self.value


class ArrayLiteralBinding(LiteralBinding):
    @override
    def __repr__(self) -> str:
        return f"Lit({self.values})"

    def __init__(self, values: Sequence[LiteralBinding]):
        super().__init__()
        self.values = values

    @override
    def populate_literal_proto(self, pb: edgir.ValueLit) -> None:
        pb.array.SetInParent()
        for value in self.values:
            value.populate_literal_proto(pb.array.elts.add())


class RangeBuilderBinding(Binding):
    @override
    def __repr__(self) -> str:
        return f"RangeBuilder({self.lower}, {self.upper})"

    def __init__(self, lower: FloatExpr, upper: FloatExpr):
        super().__init__()
        self.lower = lower
        self.upper = upper

    @override
    def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]:
        return chain(self.lower._get_exprs(), self.lower._get_exprs())

    @override
    def populate_expr_proto(self, pb: edgir.ValueExpr, expr: ConstraintExpr, ref_map: Refable.RefMapType) -> None:
        pb.binary.op = edgir.BinaryExpr.RANGE
        self.lower._populate_expr_proto(pb.binary.lhs, ref_map)
        self.upper._populate_expr_proto(pb.binary.rhs, ref_map)


class ArrayBinding(Binding):
    @override
    def __repr__(self) -> str:
        return f"Array({self.values})"

    def __init__(self, values: Sequence[ConstraintExpr]):
        super().__init__()
        self.values = values

    @override
    def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]:
        return self.values

    @override
    def populate_expr_proto(self, pb: edgir.ValueExpr, expr: ConstraintExpr, ref_map: Refable.RefMapType) -> None:
        pb.array.SetInParent()
        for value in self.values:
            value._populate_expr_proto(pb.array.vals.add(), ref_map)


class UnaryOpBinding(Binding):
    @override
    def __repr__(self) -> str:
        return f"UnaryOp({self.op}, ...)"

    def __init__(self, src: ConstraintExpr, op: Union[NumericOp, BoolOp, RangeSetOp]):
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

    @override
    def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]:
        return chain(self.src._get_exprs())

    @override
    def populate_expr_proto(self, pb: edgir.ValueExpr, expr: ConstraintExpr, ref_map: Refable.RefMapType) -> None:
        pb.unary.op = self.op_map[self.op]
        self.src._populate_expr_proto(pb.unary.val, ref_map)


class UnarySetOpBinding(Binding):
    @override
    def __repr__(self) -> str:
        return f"UnarySetOp({self.op}, ...)"

    def __init__(self, src: ConstraintExpr, op: Union[NumericOp, BoolOp, EqOp, RangeSetOp]):
        self.op_map = {
            NumericOp.negate: edgir.UnarySetExpr.NEGATE,
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

    @override
    def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]:
        return chain(self.src._get_exprs())

    @override
    def populate_expr_proto(self, pb: edgir.ValueExpr, expr: ConstraintExpr, ref_map: Refable.RefMapType) -> None:
        pb.unary_set.op = self.op_map[self.op]
        self.src._populate_expr_proto(pb.unary_set.vals, ref_map)


class BinaryOpBinding(Binding):
    @override
    def __repr__(self) -> str:
        return f"BinaryOp({self.op}, ...)"

    def __init__(self, lhs: ConstraintExpr, rhs: ConstraintExpr, op: Union[NumericOp, BoolOp, EqOp, OrdOp, RangeSetOp]):
        self.op_map = {
            # Numeric
            NumericOp.add: edgir.BinaryExpr.ADD,
            NumericOp.mul: edgir.BinaryExpr.MULT,
            NumericOp.shrink_mul: edgir.BinaryExpr.SHRINK_MULT,
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

    @override
    def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]:
        return chain(self.lhs._get_exprs(), self.rhs._get_exprs())

    @override
    def populate_expr_proto(self, pb: edgir.ValueExpr, expr: ConstraintExpr, ref_map: Refable.RefMapType) -> None:
        pb.binary.op = self.op_map[self.op]
        self.lhs._populate_expr_proto(pb.binary.lhs, ref_map)
        self.rhs._populate_expr_proto(pb.binary.rhs, ref_map)


class BinarySetOpBinding(Binding):
    @override
    def __repr__(self) -> str:
        return f"BinaryOp({self.op}, ...)"

    def __init__(self, lhset: ConstraintExpr, rhs: ConstraintExpr, op: NumericOp):
        self.op_map = {
            # Numeric
            NumericOp.add: edgir.BinarySetExpr.ADD,
            NumericOp.mul: edgir.BinarySetExpr.MULT,
        }

        super().__init__()
        self.lhset = lhset
        self.rhs = rhs
        self.op = op

    @override
    def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]:
        return chain(self.lhset._get_exprs(), self.rhs._get_exprs())

    @override
    def populate_expr_proto(self, pb: edgir.ValueExpr, expr: ConstraintExpr, ref_map: Refable.RefMapType) -> None:
        pb.binary_set.op = self.op_map[self.op]
        self.lhset._populate_expr_proto(pb.binary_set.lhset, ref_map)
        self.rhs._populate_expr_proto(pb.binary_set.rhs, ref_map)


class IfThenElseBinding(Binding):
    @override
    def __repr__(self) -> str:
        return f"IfThenElse(...)"

    def __init__(self, cond: BoolExpr, then_val: ConstraintExpr, else_val: ConstraintExpr):
        super().__init__()
        self.cond = cond
        self.then_val = then_val
        self.else_val = else_val

    @override
    def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]:
        return chain(self.cond._get_exprs(), self.then_val._get_exprs(), self.else_val._get_exprs())

    @override
    def populate_expr_proto(self, pb: edgir.ValueExpr, expr: ConstraintExpr, ref_map: Refable.RefMapType) -> None:
        self.cond._populate_expr_proto(pb.ifThenElse.cond, ref_map)
        self.then_val._populate_expr_proto(pb.ifThenElse.tru, ref_map)
        self.else_val._populate_expr_proto(pb.ifThenElse.fal, ref_map)


class IsConnectedBinding(Binding):
    @override
    def __repr__(self) -> str:
        return f"IsConnected"

    def __init__(self, src: Port):
        super().__init__()
        self.src = src

    @override
    def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]:
        return [self.src]

    @override
    def populate_expr_proto(self, pb: edgir.ValueExpr, expr: ConstraintExpr, ref_map: Refable.RefMapType) -> None:
        pb.ref.CopyFrom(ref_map[self.src])
        pb.ref.steps.add().reserved_param = edgir.IS_CONNECTED


class NameBinding(Binding):
    @override
    def __repr__(self) -> str:
        return f"Name"

    def __init__(self, src: Union[BaseBlock, BasePort]):
        super().__init__()
        self.src = src

    @override
    def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]:
        return []

    @override
    def populate_expr_proto(self, pb: edgir.ValueExpr, expr: ConstraintExpr, ref_map: Refable.RefMapType) -> None:
        pb.ref.CopyFrom(ref_map[self.src])
        pb.ref.steps.add().reserved_param = edgir.NAME


class LengthBinding(Binding):
    @override
    def __repr__(self) -> str:
        return f"Length"

    def __init__(self, src: BaseVector):
        super().__init__()
        self.src = src

    @override
    def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]:
        return [self.src]

    @override
    def populate_expr_proto(self, pb: edgir.ValueExpr, expr: ConstraintExpr, ref_map: Refable.RefMapType) -> None:
        pb.ref.CopyFrom(ref_map[self.src])
        pb.ref.steps.add().reserved_param = edgir.LENGTH


class AllocatedBinding(Binding):
    @override
    def __repr__(self) -> str:
        return f"Allocated"

    def __init__(self, src: BaseVector):
        super().__init__()
        self.src = src

    @override
    def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]:
        return [self.src]

    @override
    def populate_expr_proto(self, pb: edgir.ValueExpr, expr: ConstraintExpr, ref_map: Refable.RefMapType) -> None:
        pb.ref.CopyFrom(ref_map[self.src])
        pb.ref.steps.add().reserved_param = edgir.ALLOCATED


class AssignBinding(Binding):
    @staticmethod
    def populate_assign_proto(
        pb: edgir.ValueExpr, target: ConstraintExpr, value: ConstraintExpr, ref_map: Refable.RefMapType
    ) -> None:
        # Convenience method to make an assign expr without the rest of this proto infrastructure
        pb.assign.dst.CopyFrom(ref_map[target])
        value._populate_expr_proto(pb.assign.src, ref_map)

    @override
    def __repr__(self) -> str:
        return f"Assign({self.target}, ...)"

    def __init__(self, target: ConstraintExpr, value: ConstraintExpr):
        super().__init__()
        self.target = target
        self.value = value

    @override
    def get_subexprs(self) -> Iterable[Union[ConstraintExpr, BasePort]]:
        return [self.value]

    @override
    def populate_expr_proto(self, pb: edgir.ValueExpr, expr: ConstraintExpr, ref_map: Refable.RefMapType) -> None:
        pb.assign.dst.CopyFrom(ref_map[self.target])
        self.value._populate_expr_proto(pb.assign.src, ref_map)
