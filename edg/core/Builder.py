from __future__ import annotations

from typing import *

from deprecated import deprecated

from .. import edgir

if TYPE_CHECKING:
  from .Blocks import BaseBlock


class Builder:
  def __init__(self) -> None:
    self.stack: List[BaseBlock] = []

  def push_element(self, elt: BaseBlock) -> Optional[BaseBlock]:
    """Pushes a new element onto the context stack, returning the previous top element.
    Ignores if the element is already on top of the stack."""
    prev_elt = self.get_enclosing_block()
    if not self.stack or self.stack[-1] is not elt:  # prevent double-pushing
      self.stack.append(elt)
    return prev_elt

  def pop_to(self, prev: Optional[BaseBlock]) -> None:
    """Pops at most one element from stack, expecting prev to be at the top of the stack.
    The pattern should be one pop for one push, and allowing that duplicate pushes are ignored."""
    if (prev is None and not self.stack) or (prev is not None and self.stack[-1] is prev):
      return

    self.stack.pop()
    assert (prev is None and not self.stack) or (prev is not None and self.stack[-1] is prev)

  def get_enclosing_block(self) -> Optional[BaseBlock]:
    if not self.stack:
      return None
    else:
      return self.stack[-1]

  @deprecated("use get_enclosing_block() instead, context frames can only be blocks now")
  def get_curr_context(self) -> Optional[BaseBlock]:
    return self.get_enclosing_block()

  def elaborate_toplevel(self, block: BaseBlock, *,
                         is_generator: bool = False,
                         generate_values: Iterable[Tuple[edgir.LocalPath, edgir.ValueLit]] = []) -> edgir.HierarchyBlock:
    try:
      if is_generator:  # TODO this is kind of nasty =(
        elaborated = block._generated_def_to_proto(generate_values)
      else:  # TODO check is a GeneratorBlock w/o circular imports?
        elaborated = block._elaborated_def_to_proto()

      return elaborated
    except Exception as e:
      raise Exception(f"While elaborating {block.__class__}") from e


builder = Builder()
