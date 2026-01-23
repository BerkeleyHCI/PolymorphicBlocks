from typing import Any, Type, Union, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from edg import BaseBlock


class EdslUserError(Exception):
    """Base exception class where user error in writing EDSL is the likely cause."""

    def __init__(self, exc: str, resolution: str = ""):
        super().__init__(exc)


class EdgTypeError(EdslUserError):
    """Argument of the wrong type passed into a EDG core function."""

    def __init__(self, item_desc: str, object: Any, expected_type: Union[Type[Any], Tuple[Type[Any], ...]]):
        if isinstance(expected_type, tuple):
            expected_type_str = "/".join([t.__name__ for t in expected_type])
        else:
            expected_type_str = expected_type.__name__

        super().__init__(
            f"{item_desc} expected to be of type {expected_type_str}, got {object} of type {type(object).__name__}",
            f"ensure {item_desc} is of type {expected_type_str}",
        )


class EdgContextError(EdslUserError):
    """A context, like implicit scope, is used incorrectly"""

    pass


class ConnectError(Exception):
    """Base class for all errors that may occur during a connect statement"""


class UnconnectableError(Exception):
    """When a link cannot be inferred"""


class UnconnectedRequiredPortError(Exception):
    """When required ports in children are not connected during proto gen"""


class UnreachableParameterError(Exception):
    """When a parameter is referenced that can't be reached"""


class BlockDefinitionError(EdslUserError):
    """Base error for likely mistakes when writing a block definition"""

    def __init__(self, block_type: Type["BaseBlock"], exc: str, resolution: str = "") -> None:
        super().__init__(f"invalid block definition for {block_type}: {exc}", resolution)


class ChainError(BlockDefinitionError):
    """Base error for bad elements in a chain connect"""
