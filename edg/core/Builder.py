from __future__ import annotations

from typing import *

from deprecated import deprecated

from .. import edgir

if TYPE_CHECKING:
  from .Blocks import BaseBlock


class Builder:
  def __init__(self) -> None:
    self.stack: List[BaseBlock] = []

  def push_element(self, elt: BaseBlock) -> None:
    self.stack.append(elt)

  def pop_to(self, elt: Optional[BaseBlock]) -> None:
    self.stack.pop()
    assert self.get_curr_context() is elt

  @deprecated("use get_curr_context() instead, context frames can only be blocks now")
  def get_enclosing_block(self) -> Optional[BaseBlock]:
    return self.get_curr_context()

  def get_curr_context(self) -> Optional[BaseBlock]:
    if not self.stack:
      return None
    else:
      return self.stack[-1]

  def elaborate_toplevel(self, block: BaseBlock, *,
                         is_generator: bool = False,
                         generate_values: Iterable[Tuple[edgir.LocalPath, edgir.ValueLit]] = []) -> edgir.HierarchyBlock:
    assert self.get_curr_context() is None
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
