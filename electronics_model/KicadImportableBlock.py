from abc import abstractmethod
from typing import TypeVar, Type, Dict

from edg_core import *


class KicadImportableBlock(Block):
  """A mixin for a Block that also defines a pin mapping for Kicad symbol(s),
  allowing this to be used in a schematic."""
  BlockSelfType = TypeVar('BlockSelfType', bound='KicadImportableBlock')

  @classmethod
  @abstractmethod
  def block_from_symbol(cls: Type[BlockSelfType], symbol_name: str, properties: Dict[str, str]) -> BlockSelfType:
    """Creates an instance of this block given a symbol name and its properties, for KiCad schematic import."""
    raise NotImplementedError  # implement me

  @abstractmethod
  def symbol_pinning(self) -> Dict[str, Port]:
    """Returns the symbol pin number to Block Port correspondence, for KiCad schematic import."""
    raise NotImplementedError  # implement me
