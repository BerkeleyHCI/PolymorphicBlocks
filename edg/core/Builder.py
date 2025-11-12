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

  def pop_to(self, elt: Optional[BaseBlock]) -> None:
    while (elt is None and self.stack) or (elt is not None and self.stack[-1] is not elt):
      self.stack.pop()

  def get_enclosing_block(self) -> Optional[BaseBlock]:
    if not self.stack:
      return None
    else:
      return self.stack[-1]

  @deprecated("use get_enclosing_block() instead, context frames can only be blocks now")
  def get_curr_context(self) -> Optional[BaseBlock]:
    return self.get_enclosing_block()

  def curr_context_within_top(self, depth: int) -> bool:
    return len(self.stack) <= depth

  def is_top(self, elt: BaseBlock) -> bool:
    """Returns whether the argument elt is the top of the stack, the element being constructed.
    Inner elements can have simplified construction for optimization."""
    assert len(self.stack) >= 1
    return self.stack[0] is elt

  def is_top2(self, elt: BaseBlock) -> bool:
    """Returns whether the argument elt is the top or first-inner on the stack.
    Inner elements can have simplified construction for optimization."""
    assert len(self.stack) >= 1
    return self.stack[0] is elt or ((len(self.stack) >= 2) and self.stack[1] is elt)

  def elaborate_toplevel(self, block: BaseBlock, *,
                         is_generator: bool = False,
                         generate_values: Iterable[Tuple[edgir.LocalPath, edgir.ValueLit]] = []) -> edgir.HierarchyBlock:
    assert self.get_enclosing_block() is None
    self.push_element(block)
    try:
      if is_generator:  # TODO this is kind of nasty =(
        elaborated = block._generated_def_to_proto(generate_values)  # type: ignore
      else:  # TODO check is a GeneratorBlock w/o circular imports?
        elaborated = block._elaborated_def_to_proto()

      return elaborated
    except Exception as e:
      raise Exception(f"While elaborating {block.__class__}") from e
    finally:
      self.pop_to(None)


builder = Builder()
