from abc import abstractmethod
from typing import TypeVar, Type, Mapping

from edg_core import *


@non_library
class KiCadImportableBlock(Block):
  """A mixin for a Block that also defines a pin mapping for KiCad symbol(s),
  allowing this to be used in a schematic.
  The Block still must be instantiated via HDL, but the connectivity can be defined by a schematic."""

  @abstractmethod
  def symbol_pinning(self, symbol_name: str) -> Mapping[str, BasePort]:
    """Returns the symbol pin number to Block Port correspondence, for KiCad schematic import."""
    raise NotImplementedError  # implement me


@non_library
class KiCadInstantiableBlock(KiCadImportableBlock):
  """A mixin for a Block that allows the block to be instantiated from a KiCad symbol
  by parsing the symbol and properties.
  For obvious reasons this must also define symbol_pinning in KicadImportableBlocm"""
  BlockSelfType = TypeVar('BlockSelfType', bound=KiCadImportableBlock)

  @classmethod
  @abstractmethod
  def block_from_symbol(cls: Type[BlockSelfType], symbol_name: str, properties: Mapping[str, str]) -> BlockSelfType:
    """Creates an instance of this block given a symbol name and its properties, for KiCad schematic import."""
    raise NotImplementedError  # implement me
