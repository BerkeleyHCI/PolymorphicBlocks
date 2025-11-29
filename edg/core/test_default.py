import unittest
from typing import Any

from .. import edgir
from . import *


class BaseParamClass(Block):  # Base class containing no parameters or default
    pass


class NonDefaultParamClass(BaseParamClass):  # contains a single param without a default
    def __init__(self, nondefault_param: IntLike) -> None:
        super().__init__()


class NonDefaultParamSubClass(BaseParamClass):  # inherits defaults without adding anything
    pass


class EmptyDefaultParamClass(BaseParamClass):  # contains a single empty-default param
    def __init__(self, nondefault_param: IntLike = IntExpr()) -> None:
        super().__init__()


class DefaultParamSubClass(EmptyDefaultParamClass):  # adds a default param on top of the inherited params
    def __init__(self, default_param: IntLike = 42, **kwargs: Any) -> None:
        super().__init__(**kwargs)


class OverrideDefaultSubClass(DefaultParamSubClass):  # changes the default param of the parent
    def __init__(self, default_param: IntLike = 16, **kwargs: Any) -> None:
        super().__init__(default_param, **kwargs)


class CombinedParamSubClass(DefaultParamSubClass):  # adds a default param on top of the inherited params
    def __init__(
        self, nondefault_param2: FloatLike = FloatExpr(), default_param2: StringLike = "test", **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)


class DefaultTestCase(unittest.TestCase):
    def test_base(self) -> None:
        pb = BaseParamClass()._elaborated_def_to_proto()

        self.assertEqual(len(pb.param_defaults), 0)

    def test_non_default(self) -> None:
        pb = NonDefaultParamClass()._elaborated_def_to_proto()  # type: ignore

        self.assertEqual(len(pb.param_defaults), 0)

    def test_non_default_subclass(self) -> None:
        pb = NonDefaultParamSubClass()._elaborated_def_to_proto()

        self.assertEqual(len(pb.param_defaults), 0)

    def test_empty_default(self) -> None:
        pb = EmptyDefaultParamClass()._elaborated_def_to_proto()

        self.assertEqual(len(pb.param_defaults), 0)

    def test_default(self) -> None:
        pb = DefaultParamSubClass()._elaborated_def_to_proto()

        self.assertEqual(len(pb.param_defaults), 1)
        self.assertEqual(pb.param_defaults["default_param"], edgir.lit_to_expr(42))

    def test_override(self) -> None:
        pb = OverrideDefaultSubClass()._elaborated_def_to_proto()

        self.assertEqual(len(pb.param_defaults), 1)
        self.assertEqual(pb.param_defaults["default_param"], edgir.lit_to_expr(16))

    def test_combined(self) -> None:
        pb = CombinedParamSubClass()._elaborated_def_to_proto()

        self.assertEqual(len(pb.param_defaults), 2)
        self.assertEqual(pb.param_defaults["default_param"], edgir.lit_to_expr(42))
        self.assertEqual(pb.param_defaults["default_param2"], edgir.lit_to_expr("test"))
