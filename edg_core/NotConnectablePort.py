from typing import cast
from .Ports import Port
from .HierarchyBlock import Block
from .Builder import builder
from .Exception import *


class NotConnectableBlock(Block):
  def __init__(self):
    super().__init__()
    self.port: Port


class NotConnectablePort(Port):
  """Port that additionally supports not-connected() which instantiates a dummy block with a nop port
  and connects this port to it."""
  def __init__(self) -> None:
    super().__init__()
    self.not_connected_type: Type[NotConnectableBlock]

  def not_connected(self) -> Block:
    """Marks this edge port as not connected, can be called on a boundary port only."""
    # TODO should this be a more general infrastructural function?
    # TODO dedup w/ Port._convert
    block_parent = cast(Block, self._block_parent())
    if block_parent is None or block_parent.parent is None:
      raise UnconnectableError(f"{self} must be bound to mark not-connected")
    if block_parent is not builder.get_curr_block():
      raise UnconnectableError(f"can only mark not-connected on ports of the current block")

    nc_block = block_parent.Block(self.not_connected_type())
    block_parent.manager.add_element(
      f"(not_connected){block_parent._name_of(self)}",
      nc_block)
    block_parent.connect(self, nc_block.port)  # we don't name it to avoid explicit name conflicts
    return nc_block
