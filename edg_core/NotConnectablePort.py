from typing import cast, Generic
from .Ports import Port
from .HierarchyBlock import Block
from .Builder import builder
from .Exceptions import *


NotConnectablePortType = TypeVar('NotConnectablePortType', bound=Port, covariant=True)
class NotConnectableBlock(Block, Generic[NotConnectablePortType]):
  def __init__(self):
    super().__init__()
    self.port: NotConnectablePortType


class NotConnectablePort(Port):
  """Port that additionally supports not-connected() which instantiates a dummy block with a nop port
  and connects this port to it."""
  def __init__(self) -> None:
    super().__init__()
    self.not_connected_type: Type[NotConnectableBlock[Port]]  # TODO type check this!

  def not_connected(self) -> Block:
    """Marks this port as not connected; can either be done on a boundary port (for example, when subclassing
    a general interface where pins aren't used) or a port on an inner block (for example, when unused)."""
    # TODO should this be a more general infrastructural function?
    # TODO dedup w/ Port._convert
    context_block = builder.get_enclosing_block()
    if self._parent is None:
      raise UnconnectableError(f"{self} must be bound to mark not-connected")

    nc_block = context_block.Block(self.not_connected_type())
    if context_block is self._block_parent():
      context_block.manager.add_element(
        f"(not_connected){context_block._name_of(self)}",
        nc_block)
    elif context_block is self._block_parent().parent:
      context_block.manager.add_element(
        f"(not_connected){context_block._name_of(self._block_parent())}_{self._block_parent()._name_of(self)}",
        nc_block)
    else:
      raise UnconnectableError(f"can only mark not-connected on ports of the current block or inner block")

    context_block.connect(self, nc_block.port)  # instance variable not assigned to avoid naming conflicts
    return nc_block
