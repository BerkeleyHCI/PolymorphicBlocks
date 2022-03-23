from __future__ import annotations

from typing import *

import edgir

if TYPE_CHECKING:
  from .Core import Refable
  from .Blocks import BaseBlock


class Builder:
  def __init__(self) -> None:
    self.stack: List[Refable] = []

  def push_element(self, elt: Refable) -> None:
    self.stack.append(elt)

  def pop_to(self, elt: Optional[Refable]) -> None:
    self.stack.pop()
    assert self.get_curr_context() is elt

  def get_curr_block(self) -> BaseBlock:
    from .Blocks import BaseBlock
    elt = self.stack[-1]
    assert isinstance(elt, BaseBlock)
    return elt

  def get_curr_context(self) -> Optional[Refable]:
    if not self.stack:
      return None
    else:
      return self.stack[-1]

  def elaborate_toplevel(self, block: BaseBlock, exc_prefix: str, *,
                         is_generator: bool = False,
                         generate_values: Iterable[Tuple[edgir.LocalPath, edgir.LitTypes]] = []) -> edgir.HierarchyBlock:
    assert self.get_curr_context() is None
    self.push_element(block)
    try:
      if is_generator:  # TODO this is kind of nasty =(
        elaborated = block._generated_def_to_proto(generate_values)  # type: ignore
      else:  # TODO check is a GeneratorBlock w/o circular imports?
        elaborated = block._elaborated_def_to_proto()

      return elaborated
    finally:
      self.pop_to(None)


builder = Builder()
