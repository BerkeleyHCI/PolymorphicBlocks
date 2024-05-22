from typing import Any, Type, TypeVar, Union, Tuple


class EdslUserError(Exception):
  """Base exception class where user error in writing EDSL is the likely cause."""
  def __init__(self, exc: str, resolution: str = ""):
    super().__init__(exc)


AssertedType = TypeVar('AssertedType')
def assert_cast(elt: Any, expected_type: Union[Type[AssertedType], Tuple[Type[AssertedType], ...]], item_desc: str) -> AssertedType:
  if not isinstance(elt, expected_type):
    raise EdgTypeError(item_desc, elt, expected_type)
  return elt


class EdgTypeError(EdslUserError):
  """Argument of the wrong type passed into a EDG core function."""
  def __init__(self, item_desc: str, object: Any, expected_type: Union[Type, Tuple[Type, ...]]):
    super().__init__(f"{item_desc} expected to be of type {expected_type}, got type {type(object)}",
                     f"make sure {item_desc} is of type {expected_type}")


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
  def __init__(self, block, exc: str, resolution: str = ''):
    super().__init__(f"invalid block definition for {type(block)}: {exc}", resolution)


class ChainError(BlockDefinitionError):
  """Base error for bad elements in a chain connect"""
