from typing import cast, Generic
from .Ports import Port
from .HierarchyBlock import Block
from .Builder import builder
from .EdslUserExceptions import *


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
    """Marks this port as not connected; can only be done on a boundary port (for example, when subclassing
    a general interface where pins aren't used)."""
    # TODO should this be a more general infrastructural function?
    # TODO dedup w/ Port._convert
    context_block = builder.get_enclosing_block()
    assert isinstance(context_block, Block)
    if not self._is_bound():
      raise UnconnectableError(f"{self} must be bound to mark not-connected")

    nc_block = context_block.Block(self.not_connected_type())
    if context_block is self._block_parent():
      context_block.manager.add_element(
        f"(not_connected){self._name_from(context_block)}",
        nc_block)
    else:
      raise UnconnectableError(f"can only mark not-connected on ports of the current block")

    context_block.connect(self, nc_block.port)  # instance variable not assigned to avoid naming conflicts
    return nc_block
